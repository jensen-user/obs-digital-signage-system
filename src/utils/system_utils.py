"""
System utility functions.
"""

import platform
import psutil
import logging
from typing import Dict, Any


class SystemUtils:
    """Cross-platform system utilities."""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_free': psutil.disk_usage('/').free if platform.system() != 'Windows' else psutil.disk_usage('C:').free
        }
    
    @staticmethod
    def log_system_info() -> None:
        """Log system information for debugging."""
        logger = logging.getLogger(__name__)
        info = SystemUtils.get_system_info()
        
        logger.info("=== System Information ===")
        for key, value in info.items():
            if 'memory' in key or 'disk' in key:
                # Convert bytes to MB
                value_mb = value / (1024 * 1024)
                logger.info(f"{key}: {value_mb:.1f} MB")
            else:
                logger.info(f"{key}: {value}")
        logger.info("=========================")