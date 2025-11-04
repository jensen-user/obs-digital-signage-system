"""
Content and scene management system.
Handles dynamic scene creation, media file processing, and content rotation.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import List, Dict, Optional, Set

from config.settings import Settings
from core.obs_manager import OBSManager


class MediaFile:
    """Represents a media file with metadata."""
    
    def __init__(self, file_path: Path, settings: Settings):
        self.file_path = file_path
        self.filename = file_path.name
        self.file_ext = file_path.suffix.lower()
        self.is_video = self._is_video_file(settings)
        self.is_image = self._is_image_file(settings)
        self.duration = 0.0  # Will be set later

        # Lightweight file metadata for change detection (instead of expensive MD5)
        try:
            stat = file_path.stat()
            self.file_size = stat.st_size
            self.file_mtime = stat.st_mtime
        except Exception:
            self.file_size = 0
            self.file_mtime = 0

    def _is_video_file(self, settings: Settings) -> bool:
        return self.file_ext in settings.SUPPORTED_VIDEO_FORMATS

    def _is_image_file(self, settings: Settings) -> bool:
        return self.file_ext in settings.SUPPORTED_IMAGE_FORMATS

    def get_scene_name(self) -> str:
        """Get OBS scene name for this media file."""
        return f"{self.filename}_scene"

    def get_source_name(self) -> str:
        """Get OBS source/input name for this media file."""
        return f"{self.filename}_source"
    
    def __str__(self) -> str:
        return f"MediaFile({self.filename}, video={self.is_video}, image={self.is_image})"


class ContentManager:
    """Manages content scanning, scene creation, and rotation."""
    
    def __init__(self, settings: Settings, obs_manager: OBSManager):
        self.settings = settings
        self.obs_manager = obs_manager
        self.logger = logging.getLogger(__name__)
        
        # Content state
        self.media_files: List[MediaFile] = []
        self.current_index = 0
        self.playback_start_time = 0.0
        self.current_scene: Optional[str] = None
        self.rotation_active = False
        
        # Tracking for cleanup
        self.managed_scenes: Set[str] = set()
        self.managed_inputs: Set[str] = set()
        
        # Content change detection
        self.content_hash = ""
        
    async def initialize(self) -> None:
        """Initialize content manager."""
        try:
            self.logger.info("Initializing Content Manager...")
            
            # Ensure content directory exists
            self.settings.CONTENT_DIR.mkdir(parents=True, exist_ok=True)
            
            # Create waiting scene if no content
            await self._create_waiting_scene()
            
            self.logger.info("Content Manager initialized")
            
        except Exception as e:
            self.logger.error(f"Content Manager initialization failed: {e}")
            raise
    
    async def scan_and_update_content(self) -> None:
        """Scan content directory and update OBS scenes."""
        try:
            self.logger.info("Scanning content directory...")
            
            # Get current content
            new_media_files = await self._scan_content_directory()
            
            # Check if content has changed
            new_content_hash = self._calculate_content_hash(new_media_files)
            if new_content_hash == self.content_hash and self.media_files:
                self.logger.debug("No content changes detected")
                return
            
            # Content has changed - update everything
            self.content_hash = new_content_hash
            
            # On first run or if no managed content, do full cleanup
            if not self.managed_scenes and not self.managed_inputs:
                await self._cleanup_all_digital_signage_content()
            else:
                # Normal cleanup of managed content
                await self._cleanup_old_content()
            
            # Update media files list
            self.media_files = new_media_files
            
            if not self.media_files:
                self.logger.warning("No valid media files found")
                await self._activate_waiting_scene()
                return
            
            # Sort files alphabetically
            self.media_files.sort(key=lambda x: x.filename.lower())

            # IMPORTANT: Calculate durations BEFORE creating OBS scenes
            # This ensures we know video lengths before adding them to OBS
            # Uses FFprobe to read video metadata directly from files
            await self._calculate_media_durations()

            # Now create OBS scenes with known durations
            await self._create_scenes_for_media()

            # Clean up any orphaned scenes (like 'J' or other user-created scenes)
            # This ensures only our managed scenes exist
            await self._cleanup_orphaned_scenes()

            # Reset rotation state
            self.current_index = 0
            self.rotation_active = True
            
            # Start with first piece of content
            if self.media_files:
                await self._switch_to_media(0)
                self.playback_start_time = time.time()
            
            self.logger.info(f"Content updated: {len(self.media_files)} media files")
            
        except Exception as e:
            self.logger.error(f"Content scan and update failed: {e}")
    
    async def _scan_content_directory(self) -> List[MediaFile]:
        """Scan directory for supported media files."""
        media_files = []
        
        try:
            for file_path in self.settings.CONTENT_DIR.iterdir():
                if file_path.is_file():
                    media_file = MediaFile(file_path, self.settings)
                    
                    # Only include video and image files (audio handled separately)
                    if media_file.is_video or media_file.is_image:
                        # Validate file is not corrupted
                        if await self._validate_media_file(media_file):
                            media_files.append(media_file)
                        else:
                            self.logger.warning(f"Skipping corrupted file: {file_path.name}")
            
        except Exception as e:
            self.logger.error(f"Error scanning content directory: {e}")
        
        return media_files
    
    async def _validate_media_file(self, media_file: MediaFile) -> bool:
        """Validate media file is not corrupted."""
        try:
            # Basic file size check
            if media_file.file_path.stat().st_size == 0:
                return False
            
            # For images and videos, basic validation
            return True
                
        except Exception as e:
            self.logger.warning(f"File validation error for {media_file.filename}: {e}")
            return False
    
    def _calculate_content_hash(self, media_files: List[MediaFile]) -> str:
        """Calculate hash of content for change detection using lightweight metadata."""
        content_data = []
        for media_file in media_files:
            # Use filename, size, and modification time (much faster than MD5)
            content_data.append(f"{media_file.filename}:{media_file.file_size}:{media_file.file_mtime}")

        return "|".join(sorted(content_data))
    
    async def _cleanup_old_content(self) -> None:
        """Clean up old scenes and inputs."""
        try:
            # Remove old managed scenes
            for scene_name in self.managed_scenes.copy():
                await self.obs_manager.remove_scene(scene_name)
                self.managed_scenes.discard(scene_name)
            
            # Remove old managed inputs
            for input_name in self.managed_inputs.copy():
                await self.obs_manager.remove_input(input_name)
                self.managed_inputs.discard(input_name)
                
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    async def _cleanup_all_digital_signage_content(self) -> None:
        """Clean up ALL existing digital signage scenes and inputs."""
        try:
            self.logger.info("Cleaning up existing digital signage content...")

            # First, get all inputs and remove matching ones
            all_inputs = await self.obs_manager.get_input_list()
            inputs_removed = 0
            for input_name in all_inputs:
                # Remove inputs that match our naming pattern
                if input_name.endswith('_source'):
                    try:
                        await self.obs_manager.remove_input(input_name)
                        inputs_removed += 1
                        self.logger.debug(f"Removed old input: {input_name}")
                    except Exception as e:
                        self.logger.warning(f"Could not remove input {input_name}: {e}")

            if inputs_removed > 0:
                self.logger.info(f"Removed {inputs_removed} old inputs")

            # Then, get all existing scenes and remove matching ones
            all_scenes = await self.obs_manager.get_scene_list()

            scenes_removed = 0
            for scene_name in all_scenes:
                # Remove scenes that match our naming pattern or are from previous runs
                if (scene_name.endswith('_scene') or
                    scene_name == 'waiting_for_content_scene' or
                    'slideshow' in scene_name.lower() or
                    'digital_signage' in scene_name.lower()):

                    try:
                        await self.obs_manager.remove_scene(scene_name)
                        scenes_removed += 1
                        self.logger.debug(f"Removed old scene: {scene_name}")
                    except Exception as e:
                        self.logger.warning(f"Could not remove scene {scene_name}: {e}")

            self.logger.info(f"Removed {scenes_removed} old scenes")

        except Exception as e:
            self.logger.error(f"Full cleanup error: {e}")

    async def _cleanup_orphaned_scenes(self) -> None:
        """
        Clean up orphaned scenes that don't match our managed content.

        This removes scenes like 'J' or any other user-created scenes that aren't
        part of our digital signage system. Ensures OBS only has our managed scenes.
        """
        try:
            # Get all scenes currently in OBS
            all_scenes = await self.obs_manager.get_scene_list()

            # Get list of scenes we should keep
            valid_scenes = set(self.managed_scenes)
            valid_scenes.add('waiting_for_content_scene')  # Always keep waiting scene

            orphaned_removed = 0
            for scene_name in all_scenes:
                # If scene is not in our managed list, remove it
                if scene_name not in valid_scenes:
                    try:
                        await self.obs_manager.remove_scene(scene_name)
                        orphaned_removed += 1
                        self.logger.info(f"Removed orphaned scene: {scene_name}")
                    except Exception as e:
                        self.logger.warning(f"Could not remove orphaned scene {scene_name}: {e}")

            if orphaned_removed > 0:
                self.logger.info(f"Cleaned up {orphaned_removed} orphaned scene(s)")

        except Exception as e:
            self.logger.error(f"Orphaned scene cleanup error: {e}")
    
    async def _create_scenes_for_media(self) -> None:
        """Create OBS scenes for all media files."""
        for media_file in self.media_files:
            try:
                await self._create_scene_for_media(media_file)
            except Exception as e:
                self.logger.error(f"Failed to create scene for {media_file.filename}: {e}")
    
    async def _create_scene_for_media(self, media_file: MediaFile) -> None:
        """Create OBS scene and source for a media file."""
        try:
            scene_name = media_file.get_scene_name()
            source_name = media_file.get_source_name()

            # Create scene
            await self.obs_manager.create_scene(scene_name)
            self.managed_scenes.add(scene_name)

            # Determine source type and settings
            if media_file.is_image:
                input_kind = "image_source"
                input_settings = {
                    "file": str(media_file.file_path),
                    "unload": False
                }
            elif media_file.is_video:
                input_kind = "ffmpeg_source"
                input_settings = {
                    "local_file": str(media_file.file_path),
                    "looping": False,
                    "restart_on_activate": True,
                    "clear_on_media_end": False
                }
            else:
                self.logger.error(f"Unsupported media type: {media_file.filename}")
                return

            # Create input and add to scene
            await self.obs_manager.create_input(
                scene_name=scene_name,
                input_name=source_name,
                input_kind=input_kind,
                input_settings=input_settings
            )
            self.managed_inputs.add(source_name)

            # Mute video audio if it's a video file
            if media_file.is_video:
                await self.obs_manager.set_input_mute(source_name, True)

            # Configure scene item transform for 1920x1080 canvas
            await self._configure_scene_item_transform(media_file)

            self.logger.debug(f"Created scene and source for: {media_file.filename}")

        except Exception as e:
            self.logger.error(f"Failed to create scene for {media_file.filename}: {e}")
    
    async def _configure_scene_item_transform(self, media_file: MediaFile) -> None:
        """Configure scene item to fit 1920x1080 canvas."""
        try:
            scene_name = media_file.get_scene_name()
            source_name = media_file.get_source_name()

            # Get scene item ID
            scene_item_id = await self.obs_manager.get_scene_item_id(scene_name, source_name)

            if scene_item_id is None:
                self.logger.error(f"Could not get scene item ID for {source_name}")
                return

            # Set transform to fit canvas and center
            transform = {
                "positionX": 0,
                "positionY": 0,
                "scaleX": 1.0,
                "scaleY": 1.0,
                "cropLeft": 0,
                "cropTop": 0,
                "cropRight": 0,
                "cropBottom": 0,
                "boundsType": "OBS_BOUNDS_SCALE_INNER",
                "boundsWidth": self.settings.VIDEO_WIDTH,
                "boundsHeight": self.settings.VIDEO_HEIGHT
            }

            await self.obs_manager.set_scene_item_transform(scene_name, scene_item_id, transform)

        except Exception as e:
            self.logger.error(f"Failed to configure transform for {media_file.filename}: {e}")
    
    async def _calculate_media_durations(self) -> None:
        """
        Calculate duration for each media file BEFORE creating OBS scenes.

        ARCHITECTURE IMPROVEMENT:
        - Durations are detected from video files directly using FFprobe
        - This happens BEFORE OBS scene creation (not after)
        - No dependency on OBS state or WebSocket API
        - Durations are stored in MediaFile objects for use during playback
        """
        self.logger.info("Detecting media durations using FFprobe...")

        for media_file in self.media_files:
            try:
                if media_file.is_image:
                    # Images use configured slide duration
                    media_file.duration = self.settings.SLIDE_TRANSITION_SECONDS
                    self.logger.debug(f"Image {media_file.filename}: {media_file.duration}s")

                elif media_file.is_video:
                    # Get video duration using FFprobe (industry-standard method)
                    duration_seconds = await self._get_video_duration_ffprobe(media_file.file_path)

                    if duration_seconds is not None:
                        # Apply maximum video duration limit
                        if duration_seconds > self.settings.MAX_VIDEO_DURATION:
                            self.logger.warning(
                                f"Video {media_file.filename} exceeds maximum duration "
                                f"({duration_seconds:.1f}s), capping at {self.settings.MAX_VIDEO_DURATION}s"
                            )
                            media_file.duration = self.settings.MAX_VIDEO_DURATION
                        else:
                            media_file.duration = duration_seconds

                        self.logger.info(
                            f"Video {media_file.filename}: {media_file.duration:.2f}s"
                        )
                    else:
                        # Fallback duration for videos
                        self.logger.warning(
                            f"Could not get duration for {media_file.filename}, using fallback (10s)"
                        )
                        media_file.duration = 10.0  # 10 second fallback

            except Exception as e:
                self.logger.error(f"Failed to calculate duration for {media_file.filename}: {e}")
                # Set fallback duration
                media_file.duration = 8.0 if media_file.is_image else 10.0

        self.logger.info(
            f"Duration detection complete: {len(self.media_files)} files processed"
        )

    async def _get_video_duration_ffprobe(self, file_path: Path) -> Optional[float]:
        """
        Get video duration using FFprobe (PROFESSIONAL INDUSTRY-STANDARD SOLUTION).

        WHY FFprobe:
        - OBS WebSocket GetMediaInputStatus returns null for inactive sources
        - FFprobe reads video file container metadata directly
        - Industry-standard method used by professional applications
        - Fast (<100ms), accurate, and reliable
        - No dependency on OBS state

        How it works:
        - Uses FFprobe (part of FFmpeg suite) to read video metadata
        - Reads duration from container format without decoding frames
        - Returns precise duration in seconds

        Args:
            file_path: Path to video file

        Returns:
            Duration in seconds, or None if unable to determine
        """
        try:
            import subprocess
            import json

            # FFprobe command to get duration in JSON format
            cmd = [
                'ffprobe',
                '-v', 'error',  # Only show errors
                '-show_entries', 'format=duration',  # Get duration from format
                '-of', 'json',  # Output as JSON
                str(file_path)
            ]

            # Run FFprobe asynchronously
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            )

            if result.returncode == 0:
                # Parse JSON output
                data = json.loads(result.stdout)
                duration_str = data.get('format', {}).get('duration')

                if duration_str:
                    duration_seconds = float(duration_str)
                    return duration_seconds
                else:
                    self.logger.warning(f"FFprobe returned no duration for {file_path.name}")
                    return None
            else:
                self.logger.warning(f"FFprobe failed for {file_path.name}: {result.stderr}")
                return None

        except FileNotFoundError:
            self.logger.error(
                "FFprobe not found! Please install FFmpeg:"
            )
            self.logger.error("  Windows: choco install ffmpeg  OR  winget install FFmpeg")
            self.logger.error("  Or download from: https://ffmpeg.org/download.html")
            self.logger.error("  Add FFmpeg/bin to your system PATH")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse FFprobe output for {file_path.name}: {e}")
            return None
        except subprocess.TimeoutExpired:
            self.logger.error(f"FFprobe timeout for {file_path.name} (file may be corrupted)")
            return None
        except Exception as e:
            self.logger.error(f"Error getting duration for {file_path.name}: {e}")
            return None

    async def _create_waiting_scene(self) -> None:
        """Create a 'waiting for content' scene."""
        try:
            waiting_scene_name = "waiting_for_content_scene"

            # Check if scene already exists
            existing_scenes = await self.obs_manager.get_scene_list()
            if waiting_scene_name in existing_scenes:
                return

            # Create simple empty scene (text sources are platform-specific and may not be available)
            await self.obs_manager.create_scene(waiting_scene_name)

            self.logger.info("Created waiting scene")

        except Exception as e:
            self.logger.error(f"Failed to create waiting scene: {e}")
    
    async def _activate_waiting_scene(self) -> None:
        """Activate the waiting for content scene."""
        try:
            await self.obs_manager.set_current_scene("waiting_for_content_scene")
            self.current_scene = "waiting_for_content_scene"
            self.rotation_active = False
            
        except Exception as e:
            self.logger.error(f"Failed to activate waiting scene: {e}")
    
    async def process_content_rotation(self) -> None:
        """Process content rotation logic."""
        if not self.rotation_active or not self.media_files:
            return
        
        try:
            current_time = time.time()
            elapsed_time = current_time - self.playback_start_time
            
            # Get current media file
            if self.current_index >= len(self.media_files):
                self.current_index = 0
            
            current_media = self.media_files[self.current_index]

            # MANUAL TRANSITION TIMING (configured in settings):
            # User controls exactly when transition starts via TRANSITION_START_OFFSET
            # Example: 2.0 = start transition 2 seconds before media ends
            transition_offset = self.settings.TRANSITION_START_OFFSET

            if current_media.is_video:
                # For videos: Start transition BEFORE video ends
                # This allows the stinger to play while video is still running
                # Video plays for (duration - offset), then transition starts
                switch_time = current_media.duration - transition_offset

                # Ensure switch_time is never negative
                if switch_time < 0:
                    switch_time = 0
            else:
                # For images: Display for FULL duration, then transition
                # Images are static, so they should show for the complete IMAGE_DISPLAY_TIME
                # The transition happens AFTER the full display time
                switch_time = current_media.duration

            # Debug logging for transition timing (only log near transition)
            if elapsed_time >= switch_time - 0.5:
                self.logger.debug(
                    f"Transition check: elapsed={elapsed_time:.1f}s, switch_time={switch_time:.1f}s, "
                    f"duration={current_media.duration}s, offset={transition_offset:.1f}s, "
                    f"current={current_media.filename}"
                )

            if elapsed_time >= switch_time:
                # Time to switch to next content
                next_index = (self.current_index + 1) % len(self.media_files)
                self.logger.info(f"Switching from {current_media.filename} to {self.media_files[next_index].filename}")
                await self._switch_to_media(next_index)
                self.current_index = next_index
                self.playback_start_time = current_time
                
        except Exception as e:
            self.logger.error(f"Content rotation error: {e}")
    
    async def _switch_to_media(self, index: int) -> None:
        """Switch to specific media file."""
        try:
            if index >= len(self.media_files):
                return

            media_file = self.media_files[index]
            scene_name = media_file.get_scene_name()

            # Switch to the scene
            await self.obs_manager.set_current_scene(scene_name)
            self.current_scene = scene_name

            self.logger.debug(f"Switched to: {media_file.filename}")

        except Exception as e:
            self.logger.error(f"Failed to switch to media {index}: {e}")
    
    async def on_content_change(self, file_path: Path) -> None:
        """Handle content change events from file monitor."""
        try:
            self.logger.info(f"Content change detected: {file_path}")

            # Trigger content rescan after a short delay
            await asyncio.sleep(2)  # Allow file operations to complete
            await self.scan_and_update_content()

        except Exception as e:
            self.logger.error(f"Error handling content change: {e}")

    async def on_file_deleted(self, filename: str) -> None:
        """Handle file deletion from WebDAV sync."""
        try:
            self.logger.info(f"Handling deletion for: {filename}")

            # Generate scene and source names based on filename
            scene_name = f"{filename}_scene"
            source_name = f"{filename}_source"

            # Remove the scene from OBS
            if scene_name in self.managed_scenes:
                await self.obs_manager.remove_scene(scene_name)
                self.managed_scenes.discard(scene_name)
                self.logger.info(f"Removed OBS scene: {scene_name}")

            # Remove the input from OBS
            if source_name in self.managed_inputs:
                await self.obs_manager.remove_input(source_name)
                self.managed_inputs.discard(source_name)
                self.logger.info(f"Removed OBS input: {source_name}")

            # Remove from media files list
            self.media_files = [mf for mf in self.media_files if mf.filename != filename]

            # If we removed the currently playing media, switch to next
            if self.current_scene == scene_name and self.media_files:
                self.current_index = 0
                await self._switch_to_media(0)
                self.playback_start_time = time.time()

        except Exception as e:
            self.logger.error(f"Error handling file deletion for {filename}: {e}")