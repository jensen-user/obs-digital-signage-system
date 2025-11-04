"""
WebDAV client for Synology NAS synchronization.
Handles automated content downloading and change detection.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Set, Dict
import time

from webdav4.client import Client

from config.settings import Settings


class WebDAVClient:
    """WebDAV client for content synchronization."""

    def __init__(self, settings: Settings, deletion_callback=None):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.deletion_callback = deletion_callback  # Callback for handling file deletions

        # WebDAV client configuration for webdav4
        self.client = Client(
            base_url=f"{settings.WEBDAV_HOST}:{settings.WEBDAV_PORT}",
            auth=(settings.WEBDAV_USERNAME, settings.WEBDAV_PASSWORD),
            timeout=settings.WEBDAV_TIMEOUT
        )

        # State tracking
        self.last_sync_time = 0.0
        self.remote_file_cache: Dict[str, Dict] = {}
        self.local_content_dir = settings.CONTENT_DIR
        
    async def test_connection(self) -> bool:
        """Test WebDAV connection to Synology NAS."""
        try:
            # Test connection with a simple list operation
            await asyncio.get_event_loop().run_in_executor(
                None, self.client.ls, self.settings.WEBDAV_ROOT_PATH
            )
            self.logger.info("WebDAV connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"WebDAV connection test failed: {e}")
            return False
    
    async def sync_content(self) -> bool:
        """Synchronize content from WebDAV to local directory."""
        try:
            self.logger.info("Starting WebDAV content synchronization...")

            # Ensure local directory exists
            self.local_content_dir.mkdir(parents=True, exist_ok=True)

            # Clean up files marked for deletion from previous session
            await self._cleanup_deletion_markers()
            
            # Get remote file list
            remote_files = await self._get_remote_file_list()
            if remote_files is None:
                return False

            # Update cache with current remote files
            self.remote_file_cache = remote_files

            # Get local file list
            local_files = self._get_local_file_list()

            # Determine what needs to be synced
            changes_detected = False

            # Download new or updated files
            for remote_file, remote_info in remote_files.items():
                # Just use the filename, not the full path
                local_path = self.local_content_dir / remote_file

                if await self._should_download_file(remote_file, remote_info, local_path):
                    if await self._download_file(remote_file, local_path):
                        changes_detected = True
                        self.logger.info(f"Downloaded: {remote_file}")

            # Remove local files that no longer exist remotely
            self.logger.debug(f"Checking for deletions: {len(local_files)} local files, {len(remote_files)} remote files")
            for local_file in local_files:
                if local_file not in remote_files:
                    local_path = self.local_content_dir / local_file
                    try:
                        self.logger.info(f"File removed from remote: {local_file}")

                        # First, notify via callback to remove OBS scenes (if callback provided)
                        if self.deletion_callback:
                            try:
                                await self.deletion_callback(local_file)
                                self.logger.info(f"OBS content removed for: {local_file}")
                            except Exception as e:
                                self.logger.error(f"Failed to remove OBS content for {local_file}: {e}")

                        # Then delete the local file
                        try:
                            local_path.unlink()
                            changes_detected = True
                            self.logger.info(f"Successfully deleted local file: {local_file}")
                        except PermissionError:
                            # File is locked - rename it to mark for deletion
                            deletion_marker = local_path.with_suffix(local_path.suffix + '.delete')
                            if not deletion_marker.exists():
                                local_path.rename(deletion_marker)
                                self.logger.warning(f"File locked, marked for deletion on next restart: {local_file}")
                            changes_detected = True

                    except Exception as e:
                        self.logger.error(f"Failed to remove {local_file}: {e}")
            
            self.last_sync_time = time.time()
            
            if changes_detected:
                self.logger.info("WebDAV synchronization completed with changes")
            else:
                self.logger.debug("WebDAV synchronization completed - no changes")
            
            return changes_detected
            
        except Exception as e:
            self.logger.error(f"WebDAV sync error: {e}")
            return False
    
    async def _get_remote_file_list(self) -> Optional[Dict[str, Dict]]:
        """Get list of remote files with metadata."""
        try:
            # Get file list from WebDAV root path
            remote_files = await asyncio.get_event_loop().run_in_executor(
                None, self.client.ls, self.settings.WEBDAV_ROOT_PATH
            )
            
            file_info = {}
            
            for file_item in remote_files:
                # Skip directory entries
                if file_item.get('type') == 'directory':
                    continue
                
                # Extract filename from path - remove any path prefixes
                filename = file_item.get('name', '')
                if not filename:
                    continue
                
                # Remove path prefix if present (e.g., "sunday_service_slideshow/file.jpg" -> "file.jpg")
                if '/' in filename:
                    filename = filename.split('/')[-1]
                
                # Only include supported media files
                if self._is_supported_media_file(filename):
                    try:
                        # Use file info from the ls response
                        file_info[filename] = {
                            'size': file_item.get('content_length', 0) or 0,
                            'modified': file_item.get('modified', ''),
                            'etag': file_item.get('etag', ''),
                            'path': file_item.get('href', f'/{filename}')
                        }
                        
                    except Exception as e:
                        self.logger.warning(f"Could not get info for {filename}: {e}")
            
            self.logger.debug(f"Found {len(file_info)} remote media files")
            return file_info
            
        except Exception as e:
            self.logger.error(f"Error getting remote file list: {e}")
            return None
    
    def _get_local_file_list(self) -> Set[str]:
        """Get set of local media files."""
        local_files = set()
        
        try:
            for file_path in self.local_content_dir.iterdir():
                if file_path.is_file() and self._is_supported_media_file(file_path.name):
                    local_files.add(file_path.name)
                    
        except Exception as e:
            self.logger.error(f"Error scanning local files: {e}")
        
        return local_files
    
    def _is_supported_media_file(self, filename: str) -> bool:
        """Check if file is a supported media format."""
        file_ext = Path(filename).suffix.lower()
        
        supported_formats = (
            self.settings.SUPPORTED_VIDEO_FORMATS |
            self.settings.SUPPORTED_IMAGE_FORMATS |
            self.settings.SUPPORTED_AUDIO_FORMATS
        )
        
        return file_ext in supported_formats
    
    async def _should_download_file(self, filename: str, remote_info: Dict, local_path: Path) -> bool:
        """Determine if file should be downloaded."""
        try:
            # File doesn't exist locally
            if not local_path.exists():
                return True
            
            # Check file size
            local_size = local_path.stat().st_size
            remote_size = remote_info.get('size', 0)
            
            if local_size != remote_size:
                self.logger.debug(f"Size mismatch for {filename}: local={local_size}, remote={remote_size}")
                return True
            
            return False  # File appears to be up to date
            
        except Exception as e:
            self.logger.error(f"Error checking if should download {filename}: {e}")
            return True  # Download on error to be safe
    
    async def _download_file(self, remote_filename: str, local_path: Path) -> bool:
        """Download file from WebDAV to local path."""
        try:
            # Use the full remote path from the file info
            remote_file_info = None
            for filename, info in self.remote_file_cache.items():
                if filename == remote_filename:
                    remote_file_info = info
                    break
            
            if not remote_file_info:
                # Construct the full path
                remote_path = f"{self.settings.WEBDAV_ROOT_PATH}/{remote_filename}"
            else:
                remote_path = remote_file_info['path']
            
            # Create temporary file path
            temp_path = local_path.with_suffix(local_path.suffix + '.tmp')
            
            # Download file
            await asyncio.get_event_loop().run_in_executor(
                None, self.client.download_file, remote_path, str(temp_path)
            )
            
            # Verify download completed successfully
            if temp_path.exists() and temp_path.stat().st_size > 0:
                # Move temp file to final location
                if local_path.exists():
                    local_path.unlink()
                temp_path.rename(local_path)
                
                self.logger.debug(f"Successfully downloaded: {remote_filename}")
                return True
            else:
                self.logger.error(f"Download failed or empty file: {remote_filename}")
                if temp_path.exists():
                    temp_path.unlink()
                return False
                
        except Exception as e:
            self.logger.error(f"Error downloading {remote_filename}: {e}")
            return False

    async def _cleanup_deletion_markers(self) -> None:
        """Remove files marked for deletion (with .delete extension)."""
        try:
            deleted_count = 0
            for file_path in self.local_content_dir.glob('*.delete'):
                try:
                    file_path.unlink()
                    deleted_count += 1
                    self.logger.info(f"Cleaned up deletion marker: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to delete {file_path.name}: {e}")

            if deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} file(s) marked for deletion")

        except Exception as e:
            self.logger.error(f"Error during deletion marker cleanup: {e}")