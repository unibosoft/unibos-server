"""
UNIBOS Platform Detection Module

Provides cross-platform detection and capability identification for:
- Operating Systems (macOS, Linux, Windows, Raspberry Pi)
- Hardware (CPU, RAM, storage, GPU, sensors)
- Device Types (server, desktop, edge device)
- Capabilities (camera, LoRa, GPIO, etc.)
- Service Management (systemd, launchd, supervisor)
"""

from core.platform.detector import PlatformDetector, PlatformInfo
from core.platform.service_manager import (
    PlatformServiceManager,
    ServiceInfo,
    ServiceStatus,
    ServiceManager,
    get_service_manager
)

__all__ = [
    'PlatformDetector',
    'PlatformInfo',
    'PlatformServiceManager',
    'ServiceInfo',
    'ServiceStatus',
    'ServiceManager',
    'get_service_manager',
]
