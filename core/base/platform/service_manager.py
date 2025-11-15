"""
UNIBOS Service Manager

Cross-platform service management abstraction layer.
Supports systemd (Linux), launchd (macOS), and Windows Services.
"""

import subprocess
import platform
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ServiceStatus(Enum):
    """Service status enumeration"""
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    UNKNOWN = "unknown"


class ServiceManager(Enum):
    """Service manager types"""
    SYSTEMD = "systemd"      # Linux, Raspberry Pi
    LAUNCHD = "launchd"      # macOS
    WINDOWS = "windows"      # Windows Services
    SUPERVISOR = "supervisor"  # Fallback
    MANUAL = "manual"        # Development mode


@dataclass
class ServiceInfo:
    """Service information"""
    name: str
    status: ServiceStatus
    pid: Optional[int] = None
    uptime: Optional[str] = None
    manager: Optional[ServiceManager] = None

    def is_running(self) -> bool:
        """Check if service is running"""
        return self.status == ServiceStatus.RUNNING


class PlatformServiceManager:
    """
    Cross-platform service manager

    Provides unified interface for managing services across different platforms.
    """

    def __init__(self):
        """Initialize service manager"""
        self.platform = platform.system().lower()
        self.manager = self._detect_service_manager()

    def _detect_service_manager(self) -> ServiceManager:
        """Detect which service manager is available"""
        if self.platform == "darwin":
            return ServiceManager.LAUNCHD
        elif self.platform == "linux":
            # Check for systemd
            try:
                result = subprocess.run(
                    ["systemctl", "--version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=2
                )
                if result.returncode == 0:
                    return ServiceManager.SYSTEMD
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

            # Check for supervisor
            try:
                result = subprocess.run(
                    ["supervisorctl", "version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=2
                )
                if result.returncode == 0:
                    return ServiceManager.SUPERVISOR
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

            return ServiceManager.MANUAL

        elif self.platform == "windows":
            return ServiceManager.WINDOWS

        return ServiceManager.MANUAL

    def start(self, service_name: str) -> bool:
        """
        Start a service

        Args:
            service_name: Name of the service

        Returns:
            bool: True if successful
        """
        if self.manager == ServiceManager.SYSTEMD:
            return self._systemd_start(service_name)
        elif self.manager == ServiceManager.LAUNCHD:
            return self._launchd_start(service_name)
        elif self.manager == ServiceManager.SUPERVISOR:
            return self._supervisor_start(service_name)
        else:
            raise NotImplementedError(f"Service manager {self.manager} not implemented for start")

    def stop(self, service_name: str) -> bool:
        """
        Stop a service

        Args:
            service_name: Name of the service

        Returns:
            bool: True if successful
        """
        if self.manager == ServiceManager.SYSTEMD:
            return self._systemd_stop(service_name)
        elif self.manager == ServiceManager.LAUNCHD:
            return self._launchd_stop(service_name)
        elif self.manager == ServiceManager.SUPERVISOR:
            return self._supervisor_stop(service_name)
        else:
            raise NotImplementedError(f"Service manager {self.manager} not implemented for stop")

    def restart(self, service_name: str) -> bool:
        """
        Restart a service

        Args:
            service_name: Name of the service

        Returns:
            bool: True if successful
        """
        if self.manager == ServiceManager.SYSTEMD:
            return self._systemd_restart(service_name)
        elif self.manager == ServiceManager.LAUNCHD:
            return self._launchd_restart(service_name)
        elif self.manager == ServiceManager.SUPERVISOR:
            return self._supervisor_restart(service_name)
        else:
            raise NotImplementedError(f"Service manager {self.manager} not implemented for restart")

    def status(self, service_name: str) -> ServiceInfo:
        """
        Get service status

        Args:
            service_name: Name of the service

        Returns:
            ServiceInfo: Service information
        """
        if self.manager == ServiceManager.SYSTEMD:
            return self._systemd_status(service_name)
        elif self.manager == ServiceManager.LAUNCHD:
            return self._launchd_status(service_name)
        elif self.manager == ServiceManager.SUPERVISOR:
            return self._supervisor_status(service_name)
        else:
            return ServiceInfo(
                name=service_name,
                status=ServiceStatus.UNKNOWN,
                manager=self.manager
            )

    # ===== systemd (Linux, Raspberry Pi) =====

    def _systemd_start(self, service_name: str) -> bool:
        """Start service with systemd"""
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "start", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _systemd_stop(self, service_name: str) -> bool:
        """Stop service with systemd"""
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "stop", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _systemd_restart(self, service_name: str) -> bool:
        """Restart service with systemd"""
        try:
            result = subprocess.run(
                ["sudo", "systemctl", "restart", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _systemd_status(self, service_name: str) -> ServiceInfo:
        """Get service status from systemd"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )

            output = result.stdout.decode().strip()

            if output == "active":
                status = ServiceStatus.RUNNING
            elif output == "inactive":
                status = ServiceStatus.STOPPED
            elif output == "failed":
                status = ServiceStatus.FAILED
            else:
                status = ServiceStatus.UNKNOWN

            return ServiceInfo(
                name=service_name,
                status=status,
                manager=ServiceManager.SYSTEMD
            )
        except Exception:
            return ServiceInfo(
                name=service_name,
                status=ServiceStatus.UNKNOWN,
                manager=ServiceManager.SYSTEMD
            )

    # ===== launchd (macOS) =====

    def _launchd_start(self, service_name: str) -> bool:
        """Start service with launchd"""
        try:
            result = subprocess.run(
                ["launchctl", "start", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _launchd_stop(self, service_name: str) -> bool:
        """Stop service with launchd"""
        try:
            result = subprocess.run(
                ["launchctl", "stop", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _launchd_restart(self, service_name: str) -> bool:
        """Restart service with launchd"""
        # launchd doesn't have restart, use stop + start
        self._launchd_stop(service_name)
        return self._launchd_start(service_name)

    def _launchd_status(self, service_name: str) -> ServiceInfo:
        """Get service status from launchd"""
        try:
            result = subprocess.run(
                ["launchctl", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )

            output = result.stdout.decode()

            # Check if service is in list
            if service_name in output:
                status = ServiceStatus.RUNNING
            else:
                status = ServiceStatus.STOPPED

            return ServiceInfo(
                name=service_name,
                status=status,
                manager=ServiceManager.LAUNCHD
            )
        except Exception:
            return ServiceInfo(
                name=service_name,
                status=ServiceStatus.UNKNOWN,
                manager=ServiceManager.LAUNCHD
            )

    # ===== Supervisor (fallback) =====

    def _supervisor_start(self, service_name: str) -> bool:
        """Start service with supervisor"""
        try:
            result = subprocess.run(
                ["supervisorctl", "start", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _supervisor_stop(self, service_name: str) -> bool:
        """Stop service with supervisor"""
        try:
            result = subprocess.run(
                ["supervisorctl", "stop", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _supervisor_restart(self, service_name: str) -> bool:
        """Restart service with supervisor"""
        try:
            result = subprocess.run(
                ["supervisorctl", "restart", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _supervisor_status(self, service_name: str) -> ServiceInfo:
        """Get service status from supervisor"""
        try:
            result = subprocess.run(
                ["supervisorctl", "status", service_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )

            output = result.stdout.decode()

            if "RUNNING" in output:
                status = ServiceStatus.RUNNING
            elif "STOPPED" in output:
                status = ServiceStatus.STOPPED
            elif "FATAL" in output or "FAILED" in output:
                status = ServiceStatus.FAILED
            else:
                status = ServiceStatus.UNKNOWN

            return ServiceInfo(
                name=service_name,
                status=status,
                manager=ServiceManager.SUPERVISOR
            )
        except Exception:
            return ServiceInfo(
                name=service_name,
                status=ServiceStatus.UNKNOWN,
                manager=ServiceManager.SUPERVISOR
            )


# Convenience functions
def get_service_manager() -> PlatformServiceManager:
    """Get platform-appropriate service manager"""
    return PlatformServiceManager()
