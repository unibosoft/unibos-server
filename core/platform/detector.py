"""
UNIBOS Platform Detector

Cross-platform detection system for identifying:
- Operating System and version
- Hardware specifications (CPU, RAM, storage, GPU)
- Device type (server, desktop, edge)
- Available capabilities (camera, sensors, GPIO, LoRa)
- Raspberry Pi specific detection
"""

import platform
import psutil
import subprocess
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
from pathlib import Path


@dataclass
class PlatformInfo:
    """Complete platform information"""

    # Operating System
    os_type: str           # darwin, linux, windows
    os_name: str           # macOS, Ubuntu, Debian, Windows
    os_version: str        # 14.6.0, 22.04, 11, etc.
    architecture: str      # x86_64, aarch64, armv7l

    # Device Classification
    device_type: str       # server, desktop, raspberry_pi, edge
    is_raspberry_pi: bool  # True if running on Raspberry Pi

    # Hardware Specs
    cpu_count: int         # Physical cores
    cpu_count_logical: int # Logical cores (with hyperthreading)
    cpu_freq_mhz: float    # Current CPU frequency
    ram_total_gb: float    # Total RAM in GB
    ram_available_gb: float # Available RAM in GB
    disk_total_gb: float   # Total disk space in GB
    disk_free_gb: float    # Free disk space in GB

    # Capabilities
    has_gpu: bool          # GPU available
    has_camera: bool       # Camera available
    has_gpio: bool         # GPIO pins (Raspberry Pi)
    has_lora: bool         # LoRa hardware detected

    # Network
    hostname: str          # Device hostname

    # Optional fields (must come after required fields)
    raspberry_pi_model: Optional[str] = None  # 4B, 5, Zero 2W, etc.
    local_ip: Optional[str] = None  # Local IP address

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    def is_suitable_for_server(self) -> bool:
        """Check if device is suitable as a server"""
        return (
            self.ram_total_gb >= 2.0 and
            self.disk_free_gb >= 10.0 and
            self.cpu_count >= 2
        )

    def is_suitable_for_edge(self) -> bool:
        """Check if device is suitable as an edge node"""
        return (
            self.ram_total_gb >= 1.0 and
            self.disk_free_gb >= 5.0
        )


class PlatformDetector:
    """Platform detection and capability identification"""

    @staticmethod
    def detect() -> PlatformInfo:
        """Detect complete platform information"""

        # OS Detection
        os_type = platform.system().lower()
        os_name = PlatformDetector._detect_os_name(os_type)
        os_version = platform.release()
        architecture = platform.machine()

        # Raspberry Pi Detection
        is_raspberry_pi = PlatformDetector._is_raspberry_pi()
        raspberry_pi_model = PlatformDetector._get_raspberry_pi_model() if is_raspberry_pi else None

        # Device Type Classification
        device_type = PlatformDetector._classify_device_type(
            os_type, is_raspberry_pi, raspberry_pi_model
        )

        # CPU Information
        cpu_count = psutil.cpu_count(logical=False) or 1
        cpu_count_logical = psutil.cpu_count(logical=True) or 1
        cpu_freq = psutil.cpu_freq()
        cpu_freq_mhz = cpu_freq.current if cpu_freq else 0.0

        # Memory Information
        mem = psutil.virtual_memory()
        ram_total_gb = mem.total / (1024 ** 3)
        ram_available_gb = mem.available / (1024 ** 3)

        # Disk Information
        disk = psutil.disk_usage('/')
        disk_total_gb = disk.total / (1024 ** 3)
        disk_free_gb = disk.free / (1024 ** 3)

        # Capabilities
        has_gpu = PlatformDetector._detect_gpu()
        has_camera = PlatformDetector._detect_camera()
        has_gpio = is_raspberry_pi  # GPIO available on Raspberry Pi
        has_lora = PlatformDetector._detect_lora()

        # Network
        hostname = platform.node()
        local_ip = PlatformDetector._get_local_ip()

        return PlatformInfo(
            os_type=os_type,
            os_name=os_name,
            os_version=os_version,
            architecture=architecture,
            device_type=device_type,
            is_raspberry_pi=is_raspberry_pi,
            raspberry_pi_model=raspberry_pi_model,
            cpu_count=cpu_count,
            cpu_count_logical=cpu_count_logical,
            cpu_freq_mhz=cpu_freq_mhz,
            ram_total_gb=round(ram_total_gb, 2),
            ram_available_gb=round(ram_available_gb, 2),
            disk_total_gb=round(disk_total_gb, 2),
            disk_free_gb=round(disk_free_gb, 2),
            has_gpu=has_gpu,
            has_camera=has_camera,
            has_gpio=has_gpio,
            has_lora=has_lora,
            hostname=hostname,
            local_ip=local_ip,
        )

    @staticmethod
    def _detect_os_name(os_type: str) -> str:
        """Detect specific OS name"""
        if os_type == 'darwin':
            return 'macOS'
        elif os_type == 'linux':
            # Try to detect Linux distribution
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('NAME='):
                            return line.split('=')[1].strip().strip('"')
            except FileNotFoundError:
                pass
            return 'Linux'
        elif os_type == 'windows':
            return 'Windows'
        else:
            return os_type.capitalize()

    @staticmethod
    def _is_raspberry_pi() -> bool:
        """Check if running on Raspberry Pi"""
        # Method 1: Check /proc/device-tree/model (most reliable)
        model_file = Path('/proc/device-tree/model')
        if model_file.exists():
            try:
                model = model_file.read_text().strip('\x00')
                return 'Raspberry Pi' in model
            except Exception:
                pass

        # Method 2: Check /proc/cpuinfo
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo:
                    return True
        except FileNotFoundError:
            pass

        return False

    @staticmethod
    def _get_raspberry_pi_model() -> Optional[str]:
        """Get Raspberry Pi model (4B, 5, Zero 2W, etc.)"""
        model_file = Path('/proc/device-tree/model')
        if model_file.exists():
            try:
                model = model_file.read_text().strip('\x00')
                # Extract model from string like "Raspberry Pi 4 Model B Rev 1.4"
                if 'Raspberry Pi' in model:
                    # Remove "Raspberry Pi" prefix
                    model = model.replace('Raspberry Pi ', '')
                    # Extract model number/name
                    parts = model.split()
                    if len(parts) > 0:
                        # Return first part (e.g., "4", "5", "Zero")
                        if parts[0] == 'Zero':
                            return 'Zero 2W' if '2' in model else 'Zero'
                        return parts[0] + (f' {parts[1]}' if len(parts) > 1 and parts[1] in ['Model', 'B'] else '')
            except Exception:
                pass
        return None

    @staticmethod
    def _classify_device_type(os_type: str, is_raspberry_pi: bool, pi_model: Optional[str]) -> str:
        """Classify device type based on characteristics"""
        if is_raspberry_pi:
            return 'raspberry_pi'

        # Check if running as server (no display, high uptime expected)
        mem = psutil.virtual_memory()
        ram_gb = mem.total / (1024 ** 3)

        if os_type == 'linux' and ram_gb >= 4.0:
            # Likely a server if Linux with 4GB+ RAM
            return 'server'
        elif os_type in ['darwin', 'windows']:
            return 'desktop'
        else:
            return 'edge'  # Low-spec Linux device

    @staticmethod
    def _detect_gpu() -> bool:
        """Detect GPU availability"""
        try:
            # Try nvidia-smi for NVIDIA GPUs
            result = subprocess.run(
                ['nvidia-smi'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=2
            )
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # On macOS, assume GPU exists (integrated)
        if platform.system().lower() == 'darwin':
            return True

        # On Raspberry Pi, check for VideoCore
        if Path('/dev/vchiq').exists():
            return True

        return False

    @staticmethod
    def _detect_camera() -> bool:
        """Detect camera availability"""
        # Check for video devices (Linux)
        video_devices = list(Path('/dev').glob('video*'))
        if video_devices:
            return True

        # macOS - assume camera exists on laptops
        if platform.system().lower() == 'darwin':
            return True

        return False

    @staticmethod
    def _detect_lora() -> bool:
        """Detect LoRa hardware (SX1276/SX1278)"""
        # Check for SPI devices (LoRa modules use SPI)
        spi_devices = list(Path('/dev').glob('spidev*'))
        if spi_devices:
            # TODO: More specific LoRa detection in Phase 5
            # For now, just check if SPI is available
            return True

        return False

    @staticmethod
    def _get_local_ip() -> Optional[str]:
        """Get local IP address"""
        try:
            import socket
            # Create a socket to detect local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return None
