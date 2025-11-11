#!/usr/bin/env python3
"""
OBS Digital Signage Automation System
Production-ready implementation with obsws-python integration
"""

import asyncio
import signal
import sys
import time
import logging
import os
from pathlib import Path
from typing import Optional
import platform

# Local imports
from config.settings import Settings
from core.obs_manager import OBSManager
from core.content_manager import ContentManager
from core.audio_manager import AudioManager
from core.webdav_client import WebDAVClient
from core.file_monitor import FileMonitor
from core.scheduler import Scheduler
from utils.logging_config import setup_logging
from utils.system_utils import SystemUtils


class DigitalSignageSystem:
    """Main automation system with obsws-python integration."""
    
    def __init__(self):
        self.settings = Settings()
        self.running = False
        self.startup_time = time.time()
        
        # Initialize logging first
        setup_logging(self.settings.LOG_LEVEL, self.settings.LOG_DIR)
        self.logger = logging.getLogger(__name__)
        
        # System components
        self.obs_manager: Optional[OBSManager] = None
        self.content_manager: Optional[ContentManager] = None
        self.audio_manager: Optional[AudioManager] = None
        self.webdav_client: Optional[WebDAVClient] = None
        self.file_monitor: Optional[FileMonitor] = None
        self.scheduler: Optional[Scheduler] = None
        
        # Setup signal handlers for graceful shutdown
        if platform.system() != "Windows":
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info(f"Digital Signage System initialized on {platform.system()}")
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.running = False
    
    async def initialize_components(self) -> bool:
        """Initialize all system components with error handling."""
        try:
            self.logger.info("Starting component initialization...")
            
            # 1. Initialize OBS Manager with obsws-python
            self.logger.info("Initializing OBS Studio connection...")
            self.obs_manager = OBSManager(self.settings)
            if not await self.obs_manager.initialize():
                raise Exception("Failed to initialize OBS Studio connection")

            # 2. Initialize Scheduler (if enabled)
            if self.settings.SCHEDULE_ENABLED:
                self.logger.info("Initializing scheduler...")
                self.scheduler = Scheduler(self.settings)

                # Get initial schedule
                initial_folder = self.scheduler.get_current_content_folder()
                initial_offset = self.scheduler.get_current_transition_offset()
                initial_transition = self.scheduler.get_current_transition_type()

                # Override content folder with scheduled folder
                self.settings.CONTENT_DIR = initial_folder

                # Set initial transition in OBS
                await self.obs_manager.set_transition(initial_transition)

                self.logger.info(f"Initial schedule active: {self.scheduler.current_schedule.name}")
                self.logger.info(f"  Content folder: {initial_folder}")
                self.logger.info(f"  Transition: {initial_transition}")
            else:
                # Scheduling is disabled
                if self.settings.MANUAL_CONTENT_FOLDER:
                    self.logger.info("Scheduling disabled - using manual content folder override")
                    self.logger.info(f"  Content folder: {self.settings.MANUAL_CONTENT_FOLDER}")
                else:
                    self.logger.info("Scheduling disabled - using default content folder")
                    self.logger.info(f"  Content folder: {self.settings.CONTENT_DIR}")

            # 3. Initialize Content Manager (before WebDAV so we can pass callback)
            self.logger.info("Initializing content management...")
            self.content_manager = ContentManager(self.settings, self.obs_manager)
            await self.content_manager.initialize()

            # 3. Initialize WebDAV Client for Synology NAS (with deletion callback)
            self.logger.info("Initializing WebDAV synchronization...")
            self.webdav_client = WebDAVClient(
                self.settings,
                deletion_callback=self.content_manager.on_file_deleted
            )
            if not await self.webdav_client.test_connection():
                self.logger.warning("WebDAV connection failed - running in offline mode")
            
            # 4. Initialize Audio Manager
            self.logger.info("Initializing background audio system...")
            self.audio_manager = AudioManager(self.settings)
            await self.audio_manager.initialize()
            
            # 5. Initialize File Monitor
            self.logger.info("Initializing file monitoring...")
            self.file_monitor = FileMonitor(
                self.settings.CONTENT_DIR,
                self.content_manager.on_content_change
            )
            
            # 6. Perform initial content sync and scan
            await self._initial_content_setup()
            
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Component initialization failed: {e}")
            return False
    
    async def _initial_content_setup(self) -> None:
        """Perform initial content synchronization and setup."""
        try:
            # Sync from WebDAV if available
            if self.webdav_client and await self.webdav_client.test_connection():
                self.logger.info("Performing initial WebDAV synchronization...")
                await self.webdav_client.sync_content()
            
            # Scan local content and setup OBS scenes
            self.logger.info("Scanning local content...")
            await self.content_manager.scan_and_update_content()
            
            # Initialize background audio
            self.logger.info("Setting up background audio...")
            await self.audio_manager.scan_and_start_audio()
            
            # Start file monitoring
            self.file_monitor.start()
            
        except Exception as e:
            self.logger.error(f"Initial content setup failed: {e}")
    
    async def run_main_loop(self) -> None:
        """Main automation loop with async task management."""
        self.running = True
        
        # Create async tasks for different system functions
        tasks = []
        
        # WebDAV synchronization task (every 30 seconds)
        tasks.append(asyncio.create_task(self._webdav_sync_loop()))
        
        # Content rotation task (continuous)
        tasks.append(asyncio.create_task(self._content_rotation_loop()))
        
        # System health monitoring task (every 60 seconds)
        tasks.append(asyncio.create_task(self._health_monitoring_loop()))
        
        # Audio monitoring task (every 30 seconds)
        tasks.append(asyncio.create_task(self._audio_monitoring_loop()))

        # Schedule monitoring task (if enabled)
        if self.settings.SCHEDULE_ENABLED and self.scheduler:
            tasks.append(asyncio.create_task(self._schedule_monitoring_loop()))

        try:
            # Run until shutdown signal
            while self.running:
                await asyncio.sleep(1)
                
                # Check if any tasks have failed and restart them
                for i, task in enumerate(tasks):
                    if task.done() and task.exception():
                        self.logger.error(f"Task {i} failed: {task.exception()}")
                        # Restart the failed task
                        if i == 0:  # WebDAV sync
                            tasks[0] = asyncio.create_task(self._webdav_sync_loop())
                        elif i == 1:  # Content rotation
                            tasks[1] = asyncio.create_task(self._content_rotation_loop())
                        elif i == 2:  # Health monitoring
                            tasks[2] = asyncio.create_task(self._health_monitoring_loop())
                        elif i == 3:  # Audio monitoring
                            tasks[3] = asyncio.create_task(self._audio_monitoring_loop())
                
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
            self.running = False
            
        finally:
            # Cancel all background tasks
            for task in tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
    
    async def _webdav_sync_loop(self) -> None:
        """WebDAV synchronization loop."""
        while self.running:
            try:
                if self.webdav_client and await self.webdav_client.test_connection():
                    changes_detected = await self.webdav_client.sync_content()
                    if changes_detected:
                        self.logger.info("Content changes detected, updating scenes...")
                        await self.content_manager.scan_and_update_content()
                        await self.audio_manager.scan_and_start_audio()
                
                await asyncio.sleep(30)  # 30-second sync interval
                
            except Exception as e:
                self.logger.error(f"WebDAV sync error: {e}")
                await asyncio.sleep(60)  # Longer delay on error
    
    async def _content_rotation_loop(self) -> None:
        """Content rotation management loop."""
        while self.running:
            try:
                if self.content_manager:
                    await self.content_manager.process_content_rotation()
                await asyncio.sleep(0.5)  # High-frequency loop for precise timing
                
            except Exception as e:
                self.logger.error(f"Content rotation error: {e}")
                await asyncio.sleep(5)
    
    async def _health_monitoring_loop(self) -> None:
        """System health monitoring."""
        while self.running:
            try:
                # Check OBS health
                if self.obs_manager and not await self.obs_manager.health_check():
                    self.logger.warning("OBS health check failed - attempting recovery")
                    await self.obs_manager.recover()
                
                await asyncio.sleep(60)  # Health check every minute
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(120)
    
    async def _audio_monitoring_loop(self) -> None:
        """Audio system monitoring."""
        while self.running:
            try:
                if self.audio_manager and not self.audio_manager.is_healthy():
                    self.logger.warning("Audio system unhealthy - attempting recovery")
                    await self.audio_manager.recover()

                await asyncio.sleep(30)  # Audio check every 30 seconds

            except Exception as e:
                self.logger.error(f"Audio monitoring error: {e}")
                await asyncio.sleep(60)

    async def _schedule_monitoring_loop(self) -> None:
        """Schedule monitoring and automatic content switching."""
        while self.running:
            try:
                if self.scheduler and self.scheduler.check_schedule_change():
                    # Schedule changed - switch content folder and transition
                    new_folder = self.scheduler.get_current_content_folder()
                    new_offset = self.scheduler.get_current_transition_offset()
                    new_transition = self.scheduler.get_current_transition_type()

                    self.logger.info(f"Schedule change detected:")
                    self.logger.info(f"  New schedule: {self.scheduler.current_schedule.name}")
                    self.logger.info(f"  Content folder: {new_folder}")
                    self.logger.info(f"  Transition: {new_transition}")
                    self.logger.info(f"  Transition offset: {new_offset}s")

                    # Set new transition in OBS
                    await self.obs_manager.set_transition(new_transition)

                    # Switch content folder
                    await self.content_manager.switch_content_folder(new_folder, new_offset)

                    # Resync background audio
                    await self.audio_manager.scan_and_start_audio()

                    self.logger.info("Schedule switch completed successfully")

                # Check every SCHEDULE_CHECK_INTERVAL seconds
                await asyncio.sleep(self.settings.SCHEDULE_CHECK_INTERVAL)

            except Exception as e:
                self.logger.error(f"Schedule monitoring error: {e}")
                await asyncio.sleep(60)  # Longer delay on error

    async def shutdown(self) -> None:
        """Graceful system shutdown."""
        self.logger.info("Starting graceful shutdown...")
        
        try:
            # Stop file monitoring
            if self.file_monitor:
                self.file_monitor.stop()
            
            # Stop audio system
            if self.audio_manager:
                await self.audio_manager.shutdown()
            
            # Disconnect from OBS
            if self.obs_manager:
                await self.obs_manager.shutdown()
            
            self.logger.info("Shutdown completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    async def run(self) -> int:
        """Run the complete system."""
        try:
            self.logger.info("Starting OBS Digital Signage Automation System")
            
            # Initialize all components
            if not await self.initialize_components():
                self.logger.critical("System initialization failed")
                return 1
            
            # Run main automation loop
            await self.run_main_loop()
            
            return 0
            
        except Exception as e:
            self.logger.critical(f"Critical system error: {e}")
            return 1
            
        finally:
            await self.shutdown()


async def main() -> None:
    """Application entry point."""
    system = DigitalSignageSystem()
    
    try:
        exit_code = await system.run()
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        await system.shutdown()
        sys.exit(0)
        
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Set event loop policy for Windows
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())