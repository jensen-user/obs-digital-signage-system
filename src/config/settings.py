"""
Cross-platform configuration management.
Handles Windows development and Ubuntu production environments.
"""

import os
import platform
from pathlib import Path
from typing import Optional, Set


class Settings:
    """Cross-platform configuration management."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self._load_environment_config()
        self._setup_paths()
        self._setup_obs_settings()
        self._setup_webdav_settings()
        self._setup_media_settings()
        self._setup_system_settings()
        
    def _load_environment_config(self) -> None:
        """Load configuration from environment variables."""
        # Determine environment (development or production)
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        
        # Load environment-specific variables
        env_file = self._get_env_file()
        if env_file.exists():
            self._load_env_file(env_file)
    
    def _get_env_file(self) -> Path:
        """Get environment configuration file."""
        config_dir = Path(__file__).parent.parent.parent / "config"
        
        if self.ENVIRONMENT == "production":
            return config_dir / "ubuntu_prod.env"
        else:
            return config_dir / "windows_test.env"
    
    def _load_env_file(self, env_file: Path) -> None:
        """Load environment variables from file."""
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Remove inline comments
                        if '#' in value:
                            value = value.split('#')[0].strip()
                        os.environ[key.strip()] = value.strip()
        except Exception:
            pass  # Ignore errors, use defaults
    
    def _setup_paths(self) -> None:
        """Setup platform-specific paths."""
        # Base directories  
        if self.platform == "windows":
            base_dir = Path(os.getenv("CONTENT_BASE_DIR", "C:/Users/User/Desktop/obs-slideshow"))
        else:
            base_dir = Path(os.getenv("CONTENT_BASE_DIR", "/opt/digital-signage"))
        
        # Ensure base directory exists
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure directories exist
        self.CONTENT_DIR = base_dir / "content"
        self.LOG_DIR = base_dir / "logs"
        self.CONFIG_DIR = base_dir / "config"
        
        # Create directories
        for directory in [self.CONTENT_DIR, self.LOG_DIR, self.CONFIG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _setup_obs_settings(self) -> None:
        """Setup OBS WebSocket configuration."""
        self.OBS_HOST = os.getenv("OBS_HOST", "localhost")
        self.OBS_PORT = int(os.getenv("OBS_PORT", "4455"))
        self.OBS_PASSWORD = os.getenv("OBS_PASSWORD", "")
        self.OBS_TIMEOUT = int(os.getenv("OBS_TIMEOUT", "10"))
        self.OBS_STARTUP_DELAY = int(os.getenv("OBS_STARTUP_DELAY", "15"))
    
    def _setup_webdav_settings(self) -> None:
        """Setup WebDAV/Synology NAS configuration."""
        self.WEBDAV_HOST = os.getenv("WEBDAV_HOST", "")
        self.WEBDAV_PORT = int(os.getenv("WEBDAV_PORT", "5006"))
        self.WEBDAV_USERNAME = os.getenv("WEBDAV_USERNAME", "")
        self.WEBDAV_PASSWORD = os.getenv("WEBDAV_PASSWORD", "")
        self.WEBDAV_TIMEOUT = int(os.getenv("WEBDAV_TIMEOUT", "30"))
        self.WEBDAV_SYNC_INTERVAL = int(os.getenv("WEBDAV_SYNC_INTERVAL", "30"))
        # Corrected Synology NAS path - convert Windows path to WebDAV format
        self.WEBDAV_ROOT_PATH = os.getenv("WEBDAV_ROOT_PATH", "/sunday_service_slideshow")
    
    def _setup_media_settings(self) -> None:
        """Setup media file and display settings."""
        # Display settings
        self.VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1920"))
        self.VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1080"))
        self.VIDEO_FPS = float(os.getenv("VIDEO_FPS", "30"))
        
        # Media timing
        self.IMAGE_DISPLAY_TIME = int(os.getenv("IMAGE_DISPLAY_TIME", "8"))  # seconds
        self.MAX_VIDEO_DURATION = int(os.getenv("MAX_VIDEO_DURATION", "900"))  # 15 minutes
        self.SLIDE_TRANSITION_SECONDS = int(os.getenv("SLIDE_TRANSITION_SECONDS", "8"))  # configurable slide timing

        # Transition timing - manual control over when transition starts
        # Number of seconds before media ends to trigger the transition
        # Example: 2.0 = start transition 2 seconds before video/image ends
        self.TRANSITION_START_OFFSET = float(os.getenv("TRANSITION_START_OFFSET", "2.0"))
        
        # Audio settings
        self.AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "44100"))
        self.AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "2"))
        self.AUDIO_BUFFER_SIZE = int(os.getenv("AUDIO_BUFFER_SIZE", "1024"))
        
        # Supported file formats
        self.SUPPORTED_VIDEO_FORMATS: Set[str] = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.webm', '.m4v'}
        self.SUPPORTED_IMAGE_FORMATS: Set[str] = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        self.SUPPORTED_AUDIO_FORMATS: Set[str] = {'.mp3', '.wav', '.ogg', '.flac', '.m4a'}
    
    def _setup_system_settings(self) -> None:
        """Setup system and logging settings."""
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
        self.LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
        
        # System monitoring
        self.HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))  # seconds
        self.MAX_RESTART_ATTEMPTS = int(os.getenv("MAX_RESTART_ATTEMPTS", "3"))
        
        # File monitoring
        self.FILE_MONITOR_DELAY = float(os.getenv("FILE_MONITOR_DELAY", "2.0"))  # seconds