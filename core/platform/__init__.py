"""
UNIBOS Platform Detection Module

Provides cross-platform detection and capability identification for:
- Operating Systems (macOS, Linux, Windows, Raspberry Pi)
- Hardware (CPU, RAM, storage, GPU, sensors)
- Device Types (server, desktop, edge device)
- Capabilities (camera, LoRa, GPIO, etc.)
"""

from core.platform.detector import PlatformDetector, PlatformInfo

__all__ = ['PlatformDetector', 'PlatformInfo']
