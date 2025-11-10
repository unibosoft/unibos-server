#!/usr/bin/env python3
"""
UNIBOS System Scrolls - Cross-Platform System Information Module
Gathers comprehensive system information for display in System Scrolls feature
Supports Windows, macOS, and Linux with graceful fallbacks
"""

import platform
import socket
import datetime
import os
import sys
import json
import subprocess
from typing import Dict, Any, List, Optional, Tuple

# Try to import psutil, provide fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Silent fallback - don't print warnings that mess up the UI


class SystemScrolls:
    """Cross-platform system information gatherer"""
    
    def __init__(self):
        self.os_type = platform.system()
        self.is_windows = self.os_type == "Windows"
        self.is_macos = self.os_type == "Darwin"
        self.is_linux = self.os_type == "Linux"
    
    def get_all_info(self) -> Dict[str, Any]:
        """Get all system information"""
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "os": self.get_os_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
            "system": self.get_system_info(),
            "python": self.get_python_info()
        }
    
    def get_os_info(self) -> Dict[str, str]:
        """Get operating system information"""
        info = {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "platform": platform.platform()
        }
        
        # Add OS-specific details
        if self.is_windows:
            try:
                info["edition"] = platform.win32_edition()
                info["win_version"] = platform.win32_ver()[0]
            except:
                pass
        elif self.is_macos:
            try:
                info["mac_version"] = platform.mac_ver()[0]
            except:
                pass
        elif self.is_linux:
            try:
                # Try to get Linux distribution info
                if hasattr(platform, 'freedesktop_os_release'):
                    distro_info = platform.freedesktop_os_release()
                    info["distribution"] = distro_info.get('NAME', 'Unknown')
                    info["distro_version"] = distro_info.get('VERSION', 'Unknown')
            except:
                pass
        
        return info
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        info = {}
        
        if PSUTIL_AVAILABLE:
            # Physical and logical CPU counts
            info["physical_cores"] = psutil.cpu_count(logical=False) or "Unknown"
            info["logical_cores"] = psutil.cpu_count(logical=True) or "Unknown"
            
            # CPU usage
            info["usage_percent"] = psutil.cpu_percent(interval=1)
            info["per_cpu_usage"] = psutil.cpu_percent(interval=1, percpu=True)
            
            # CPU frequency
            try:
                freq = psutil.cpu_freq()
                if freq:
                    info["frequency"] = {
                        "current": round(freq.current, 2),
                        "min": round(freq.min, 2),
                        "max": round(freq.max, 2),
                        "unit": "MHz"
                    }
            except:
                pass
            
            # CPU times
            try:
                times = psutil.cpu_times()
                info["times"] = {
                    "user": round(times.user, 2),
                    "system": round(times.system, 2),
                    "idle": round(times.idle, 2)
                }
            except:
                pass
        else:
            # Fallback methods
            try:
                # Try multiprocessing for CPU count
                import multiprocessing
                info["logical_cores"] = multiprocessing.cpu_count()
            except:
                info["logical_cores"] = "Unknown"
            
            # Platform-specific fallbacks
            if self.is_linux:
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo = f.read()
                        # Count processor entries
                        processors = cpuinfo.count('processor\t:')
                        info["logical_cores"] = processors if processors > 0 else "Unknown"
                        
                        # Try to get model name
                        for line in cpuinfo.split('\n'):
                            if 'model name' in line:
                                info["model"] = line.split(':')[1].strip()
                                break
                except:
                    pass
            elif self.is_macos:
                try:
                    # Use sysctl on macOS
                    result = subprocess.run(['sysctl', '-n', 'hw.logicalcpu'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        info["logical_cores"] = int(result.stdout.strip())
                    
                    # Get physical cores
                    result = subprocess.run(['sysctl', '-n', 'hw.physicalcpu'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        info["physical_cores"] = int(result.stdout.strip())
                    
                    # Get CPU model
                    result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        info["model"] = result.stdout.strip()
                    
                    # Get CPU frequency (in Hz, convert to MHz)
                    result = subprocess.run(['sysctl', '-n', 'hw.cpufrequency'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        freq_hz = int(result.stdout.strip())
                        info["frequency"] = {
                            "current": round(freq_hz / 1000000, 2),  # Convert to MHz
                            "unit": "MHz"
                        }
                except:
                    pass
        
        return info
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        info = {}
        
        if PSUTIL_AVAILABLE:
            # Virtual memory
            vm = psutil.virtual_memory()
            info["virtual"] = {
                "total": self._format_bytes(vm.total),
                "available": self._format_bytes(vm.available),
                "used": self._format_bytes(vm.used),
                "free": self._format_bytes(vm.free),
                "percent": round(vm.percent, 1),
                "total_bytes": vm.total
            }
            
            # Swap memory
            try:
                swap = psutil.swap_memory()
                info["swap"] = {
                    "total": self._format_bytes(swap.total),
                    "used": self._format_bytes(swap.used),
                    "free": self._format_bytes(swap.free),
                    "percent": round(swap.percent, 1)
                }
            except:
                pass
        else:
            # Platform-specific fallbacks
            if self.is_linux:
                try:
                    with open('/proc/meminfo', 'r') as f:
                        meminfo = f.read()
                        for line in meminfo.split('\n'):
                            if line.startswith('MemTotal:'):
                                total = int(line.split()[1]) * 1024  # Convert KB to bytes
                                info["total"] = self._format_bytes(total)
                            elif line.startswith('MemAvailable:'):
                                available = int(line.split()[1]) * 1024
                                info["available"] = self._format_bytes(available)
                except:
                    pass
            elif self.is_macos:
                try:
                    # First try simple sysctl approach
                    result = subprocess.run(['sysctl', '-n', 'hw.memsize'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        total_bytes = int(result.stdout.strip())
                        
                        # Get memory pressure for better accuracy
                        vm_result = subprocess.run(['vm_stat'], capture_output=True, text=True)
                        if vm_result.returncode == 0:
                            lines = vm_result.stdout.strip().split('\n')
                            try:
                                # Parse page size from first line
                                page_size_match = lines[0].split()
                                page_size = int(page_size_match[7]) if len(page_size_match) > 7 else 4096
                                
                                stats = {}
                                for line in lines[1:]:
                                    if ':' in line:
                                        key, value = line.split(':', 1)
                                        # Remove trailing period and convert to int
                                        stats[key.strip()] = int(value.strip().rstrip('.'))
                                
                                # Calculate memory values
                                free_pages = stats.get('Pages free', 0)
                                active_pages = stats.get('Pages active', 0)
                                inactive_pages = stats.get('Pages inactive', 0)
                                wired_pages = stats.get('Pages wired down', 0)
                                
                                free = free_pages * page_size
                                active = active_pages * page_size
                                inactive = inactive_pages * page_size
                                wired = wired_pages * page_size
                                
                                used = total_bytes - free
                                available = free + inactive  # Approximation
                                
                                info["virtual"] = {
                                    "total": self._format_bytes(total_bytes),
                                    "free": self._format_bytes(free),
                                    "used": self._format_bytes(used),
                                    "available": self._format_bytes(available),
                                    "percent": round((used / total_bytes) * 100, 1) if total_bytes > 0 else 0,
                                    "total_bytes": total_bytes
                                }
                            except:
                                # Fallback if parsing fails
                                info["virtual"] = {
                                    "total": self._format_bytes(total_bytes),
                                    "total_bytes": total_bytes
                                }
                        else:
                            # Just total memory
                            info["virtual"] = {
                                "total": self._format_bytes(total_bytes),
                                "total_bytes": total_bytes
                            }
                except:
                    pass
        
        return info
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk information"""
        info = {"partitions": []}
        
        if PSUTIL_AVAILABLE:
            # Disk partitions
            try:
                partitions = psutil.disk_partitions(all=False)
                for partition in partitions:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        partition_info = {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": self._format_bytes(usage.total),
                            "used": self._format_bytes(usage.used),
                            "free": self._format_bytes(usage.free),
                            "percent": round(usage.percent, 1)
                        }
                        info["partitions"].append(partition_info)
                    except PermissionError:
                        # Skip partitions we can't access
                        continue
            except:
                pass
            
            # Disk I/O statistics
            try:
                io = psutil.disk_io_counters()
                if io:
                    info["io"] = {
                        "read_count": io.read_count,
                        "write_count": io.write_count,
                        "read_bytes": self._format_bytes(io.read_bytes),
                        "write_bytes": self._format_bytes(io.write_bytes)
                    }
            except:
                pass
        else:
            # Platform-specific fallbacks
            if self.is_windows:
                try:
                    import string
                    from ctypes import windll
                    
                    drives = []
                    bitmask = windll.kernel32.GetLogicalDrives()
                    for letter in string.ascii_uppercase:
                        if bitmask & 1:
                            drives.append(f"{letter}:\\")
                        bitmask >>= 1
                    
                    info["drives"] = drives
                except:
                    pass
            elif self.is_linux or self.is_macos:
                try:
                    # Use df command
                    result = subprocess.run(['df', '-h'], capture_output=True, text=True)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')[1:]  # Skip header
                        for line in lines:
                            parts = line.split()
                            if len(parts) >= 6 and not parts[0].startswith('tmpfs'):
                                partition_info = {
                                    "device": parts[0],
                                    "total": parts[1],
                                    "used": parts[2],
                                    "free": parts[3],
                                    "percent": parts[4],
                                    "mountpoint": parts[5]
                                }
                                info["partitions"].append(partition_info)
                except:
                    pass
        
        return info
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        info = {
            "hostname": socket.gethostname(),
            "interfaces": []
        }
        
        # Get FQDN
        try:
            info["fqdn"] = socket.getfqdn()
        except:
            pass
        
        if PSUTIL_AVAILABLE:
            # Network interfaces
            try:
                interfaces = psutil.net_if_addrs()
                for iface_name, addresses in interfaces.items():
                    iface_info = {
                        "name": iface_name,
                        "addresses": []
                    }
                    for addr in addresses:
                        addr_info = {
                            "family": str(addr.family),
                            "address": addr.address
                        }
                        if addr.netmask:
                            addr_info["netmask"] = addr.netmask
                        if addr.broadcast:
                            addr_info["broadcast"] = addr.broadcast
                        iface_info["addresses"].append(addr_info)
                    info["interfaces"].append(iface_info)
                
                # Network statistics
                stats = psutil.net_if_stats()
                for iface in info["interfaces"]:
                    if iface["name"] in stats:
                        stat = stats[iface["name"]]
                        iface["is_up"] = stat.isup
                        iface["speed"] = stat.speed
            except:
                pass
            
            # Network I/O counters
            try:
                io = psutil.net_io_counters()
                info["io"] = {
                    "bytes_sent": self._format_bytes(io.bytes_sent),
                    "bytes_recv": self._format_bytes(io.bytes_recv),
                    "packets_sent": io.packets_sent,
                    "packets_recv": io.packets_recv
                }
            except:
                pass
        else:
            # Basic network info without psutil
            try:
                # Get local IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                info["local_ip"] = s.getsockname()[0]
                s.close()
            except:
                info["local_ip"] = "127.0.0.1"
        
        return info
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information"""
        info = {}
        
        if PSUTIL_AVAILABLE:
            # Boot time and uptime
            try:
                boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
                info["boot_time"] = boot_time.isoformat()
                uptime = datetime.datetime.now() - boot_time
                info["uptime"] = str(uptime).split('.')[0]  # Remove microseconds
                info["uptime_seconds"] = int(uptime.total_seconds())
            except:
                pass
            
            # Process count
            try:
                info["process_count"] = len(psutil.pids())
            except:
                pass
            
            # Users
            try:
                users = psutil.users()
                info["users"] = []
                for user in users:
                    user_info = {
                        "name": user.name,
                        "terminal": user.terminal or "N/A",
                        "started": datetime.datetime.fromtimestamp(user.started).isoformat()
                    }
                    if hasattr(user, 'pid'):
                        user_info["pid"] = user.pid
                    info["users"].append(user_info)
            except:
                pass
        else:
            # Platform-specific fallbacks
            if self.is_linux:
                try:
                    # Uptime from /proc/uptime
                    with open('/proc/uptime', 'r') as f:
                        uptime_seconds = float(f.readline().split()[0])
                        info["uptime_seconds"] = int(uptime_seconds)
                        uptime = datetime.timedelta(seconds=int(uptime_seconds))
                        info["uptime"] = str(uptime)
                except:
                    pass
            elif self.is_macos:
                try:
                    # Get boot time using sysctl
                    result = subprocess.run(['sysctl', '-n', 'kern.boottime'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        # Parse the output
                        import re
                        match = re.search(r'sec = (\d+)', result.stdout)
                        if match:
                            boot_timestamp = int(match.group(1))
                            boot_time = datetime.datetime.fromtimestamp(boot_timestamp)
                            info["boot_time"] = boot_time.isoformat()
                            uptime = datetime.datetime.now() - boot_time
                            info["uptime"] = str(uptime).split('.')[0]
                except:
                    pass
        
        # Current user
        try:
            info["current_user"] = os.getlogin()
        except:
            info["current_user"] = os.environ.get('USER', 'Unknown')
        
        # Environment
        info["environment"] = {
            "path_separator": os.pathsep,
            "line_separator": repr(os.linesep),
            "env_vars_count": len(os.environ)
        }
        
        return info
    
    def get_python_info(self) -> Dict[str, Any]:
        """Get Python environment information"""
        info = {
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro,
                "releaselevel": sys.version_info.releaselevel
            },
            "implementation": platform.python_implementation(),
            "compiler": platform.python_compiler(),
            "build": platform.python_build(),
            "executable": sys.executable,
            "prefix": sys.prefix,
            "path": sys.path[:5]  # First 5 paths
        }
        
        # Virtual environment check
        info["is_virtual_env"] = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        return info
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def display_info(self, info: Optional[Dict[str, Any]] = None) -> None:
        """Display system information in a formatted way"""
        if info is None:
            info = self.get_all_info()
        
        print("\n" + "="*60)
        print(" "*20 + "UNIBOS SYSTEM SCROLLS")
        print("="*60)
        
        # OS Information
        print("\n[OPERATING SYSTEM]")
        os_info = info.get("os", {})
        print(f"  System: {os_info.get('system', 'Unknown')} {os_info.get('release', '')}")
        print(f"  Platform: {os_info.get('platform', 'Unknown')}")
        print(f"  Architecture: {os_info.get('machine', 'Unknown')}")
        print(f"  Hostname: {info.get('network', {}).get('hostname', 'Unknown')}")
        
        # CPU Information
        print("\n[CPU]")
        cpu_info = info.get("cpu", {})
        print(f"  Cores: {cpu_info.get('physical_cores', 'Unknown')} physical, "
              f"{cpu_info.get('logical_cores', 'Unknown')} logical")
        if "usage_percent" in cpu_info:
            print(f"  Usage: {cpu_info['usage_percent']}%")
        if "frequency" in cpu_info:
            freq = cpu_info["frequency"]
            print(f"  Frequency: {freq['current']} MHz (min: {freq['min']}, max: {freq['max']})")
        if "model" in cpu_info:
            print(f"  Model: {cpu_info['model']}")
        
        # Memory Information
        print("\n[MEMORY]")
        mem_info = info.get("memory", {})
        if "virtual" in mem_info:
            vm = mem_info["virtual"]
            print(f"  Total: {vm['total']}")
            print(f"  Used: {vm['used']} ({vm['percent']}%)")
            print(f"  Available: {vm['available']}")
        if "swap" in mem_info:
            swap = mem_info["swap"]
            print(f"  Swap: {swap['total']} total, {swap['used']} used ({swap['percent']}%)")
        
        # Disk Information
        print("\n[DISK]")
        disk_info = info.get("disk", {})
        partitions = disk_info.get("partitions", [])
        for partition in partitions[:3]:  # Show first 3 partitions
            print(f"  {partition['device']}:")
            print(f"    Mount: {partition['mountpoint']}")
            print(f"    Total: {partition['total']}, Used: {partition['used']} ({partition['percent']}%)")
        if len(partitions) > 3:
            print(f"  ... and {len(partitions) - 3} more partitions")
        
        # Network Information
        print("\n[NETWORK]")
        net_info = info.get("network", {})
        print(f"  Hostname: {net_info.get('hostname', 'Unknown')}")
        if "local_ip" in net_info:
            print(f"  Local IP: {net_info['local_ip']}")
        if "io" in net_info:
            io = net_info["io"]
            print(f"  Traffic: Sent {io['bytes_sent']}, Received {io['bytes_recv']}")
        
        # System Information
        print("\n[SYSTEM]")
        sys_info = info.get("system", {})
        if "uptime" in sys_info:
            print(f"  Uptime: {sys_info['uptime']}")
        if "process_count" in sys_info:
            print(f"  Processes: {sys_info['process_count']}")
        print(f"  Current User: {sys_info.get('current_user', 'Unknown')}")
        
        # Python Information
        print("\n[PYTHON]")
        py_info = info.get("python", {})
        ver = py_info.get("version_info", {})
        print(f"  Version: {ver.get('major', 0)}.{ver.get('minor', 0)}.{ver.get('micro', 0)}")
        print(f"  Implementation: {py_info.get('implementation', 'Unknown')}")
        print(f"  Virtual Env: {'Yes' if py_info.get('is_virtual_env', False) else 'No'}")
        
        print("\n" + "="*60)
        print(f"Report generated at: {info.get('timestamp', 'Unknown')}")
        print("="*60 + "\n")
    
    def export_json(self, filename: str = "system_info.json") -> None:
        """Export system information to JSON file"""
        info = self.get_all_info()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        print(f"System information exported to: {filename}")
    
    def get_summary(self) -> str:
        """Get a brief summary of system information"""
        info = self.get_all_info()
        
        os_info = info.get("os", {})
        cpu_info = info.get("cpu", {})
        mem_info = info.get("memory", {}).get("virtual", {})
        
        summary = f"{os_info.get('system', 'Unknown')} {os_info.get('release', '')}"
        summary += f" | {cpu_info.get('logical_cores', '?')} CPU cores"
        if "usage_percent" in cpu_info:
            summary += f" @ {cpu_info['usage_percent']}%"
        if "total" in mem_info:
            summary += f" | RAM: {mem_info['total']}"
            if "percent" in mem_info:
                summary += f" ({mem_info['percent']}% used)"
        
        return summary


def main():
    """Main function for testing"""
    scrolls = SystemScrolls()
    
    # Display full information
    scrolls.display_info()
    
    # Show summary
    print("\nQuick Summary:", scrolls.get_summary())
    
    # Test JSON export
    if "--export" in sys.argv:
        scrolls.export_json("unibos_system_info.json")


if __name__ == "__main__":
    main()