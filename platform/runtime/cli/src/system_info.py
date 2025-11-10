#!/usr/bin/env python3
"""
Central system information module for UNIBOS
Provides hostname and environment details to all components
"""

import os
import socket
import platform
import json
from pathlib import Path
from datetime import datetime

class SystemInfo:
    """Central repository for system information"""
    
    _instance = None
    _info_cache = None
    _cache_file = Path.home() / '.unibos' / 'system_info.json'
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemInfo, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._info_cache is None:
            self.refresh()
    
    def refresh(self):
        """Refresh system information"""
        self._info_cache = {
            'hostname': socket.gethostname(),
            'fqdn': socket.getfqdn(),
            'platform': platform.system().lower(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'environment': self._detect_environment(),
            'display_name': self._get_display_name(),
            'last_updated': datetime.now().isoformat()
        }
        self._save_cache()
    
    def _detect_environment(self):
        """Detect the runtime environment"""
        hostname = socket.gethostname().lower()
        system = platform.system().lower()
        
        # Check for specific known hosts
        if hostname == "rocksteady":
            return "rocksteady"
        elif "raspberry" in hostname or "rpi" in hostname:
            return "raspberry_pi"
        elif system == "darwin":
            return "local_mac"
        elif system == "linux":
            # Check if running in cloud
            if os.path.exists('/sys/hypervisor/uuid'):
                return "cloud_server"
            return "linux_server"
        else:
            return "unknown"
    
    def _get_display_name(self):
        """Get a user-friendly display name"""
        hostname = socket.gethostname()
        env = self._detect_environment()
        
        if env == "rocksteady":
            return "rocksteady server"
        elif env == "raspberry_pi":
            return f"raspberry pi ({hostname})"
        elif env == "local_mac":
            return f"mac ({hostname})"
        elif env == "cloud_server":
            return f"cloud ({hostname})"
        elif env == "linux_server":
            return f"linux ({hostname})"
        else:
            return hostname
    
    def _save_cache(self):
        """Save system info to cache file"""
        try:
            self._cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._cache_file, 'w') as f:
                json.dump(self._info_cache, f, indent=2)
        except Exception:
            pass  # Fail silently if can't write cache
    
    def _load_cache(self):
        """Load system info from cache file"""
        try:
            if self._cache_file.exists():
                with open(self._cache_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    @property
    def hostname(self):
        """Get the system hostname"""
        return self._info_cache['hostname']
    
    @property
    def fqdn(self):
        """Get the fully qualified domain name"""
        return self._info_cache['fqdn']
    
    @property
    def platform(self):
        """Get the platform (darwin, linux, windows)"""
        return self._info_cache['platform']
    
    @property
    def environment(self):
        """Get the environment type"""
        return self._info_cache['environment']
    
    @property
    def display_name(self):
        """Get user-friendly display name"""
        return self._info_cache['display_name']
    
    @property
    def is_server(self):
        """Check if running on a server"""
        return self.environment in ['rocksteady', 'raspberry_pi', 'cloud_server', 'linux_server']
    
    @property
    def is_local(self):
        """Check if running locally"""
        return self.environment in ['local_mac']
    
    @property
    def is_raspberry_pi(self):
        """Check if running on Raspberry Pi"""
        return self.environment == 'raspberry_pi'
    
    @property
    def is_rocksteady(self):
        """Check if running on rocksteady"""
        return self.environment == 'rocksteady'
    
    def get_info(self):
        """Get all system information"""
        return self._info_cache.copy()
    
    def get_footer_text(self):
        """Get formatted text for footer display"""
        return f"host: {self.hostname} | env: {self.environment}"

# Singleton instance
system_info = SystemInfo()

# Convenience functions
def get_hostname():
    """Get current hostname"""
    return system_info.hostname

def get_environment():
    """Get current environment"""
    return system_info.environment

def get_display_name():
    """Get display name"""
    return system_info.display_name

def get_footer_text():
    """Get footer text"""
    return system_info.get_footer_text()

def is_server():
    """Check if running on server"""
    return system_info.is_server

def is_local():
    """Check if running locally"""
    return system_info.is_local