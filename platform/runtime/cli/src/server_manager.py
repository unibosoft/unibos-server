#!/usr/bin/env python3
"""
UNIBOS Server Manager - Enhanced with PostgreSQL Auto-Recovery
"""

import os
import sys
import time
import subprocess
import json
import psutil
import socket
from pathlib import Path
from datetime import datetime

class ServerManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.backend_path = self.base_path / 'backend'
        self.backend_script = self.backend_path / 'start_backend.sh'
        self.backend_pid_file = self.backend_path / '.backend.pid'
        self.backend_port = 8000
        
        # PostgreSQL configuration
        self.pg_user = "unibos_user"
        self.pg_pass = "unibos_password"
        self.pg_db = "unibos_db"
        self.pg_host = "localhost"
        self.pg_port = 5432
        
        # Colors for output
        self.RED = '\033[0;31m'
        self.GREEN = '\033[0;32m'
        self.YELLOW = '\033[1;33m'
        self.BLUE = '\033[0;34m'
        self.NC = '\033[0m'
        
    def colored_print(self, message, color=''):
        """Print colored message"""
        if color:
            print(f"{color}{message}{self.NC}")
        else:
            print(message)
    
    def check_postgresql(self):
        """Check if PostgreSQL is running and accessible"""
        try:
            # Try to connect to PostgreSQL port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.pg_host, self.pg_port))
            sock.close()
            
            if result != 0:
                return False
            
            # Try actual database connection
            env = os.environ.copy()
            env['PGPASSWORD'] = self.pg_pass
            
            result = subprocess.run(
                ['psql', '-h', self.pg_host, '-p', str(self.pg_port), 
                 '-U', self.pg_user, '-d', self.pg_db, '-c', 'SELECT 1;'],
                env=env,
                capture_output=True,
                timeout=5
            )
            
            return result.returncode == 0
        except Exception:
            return False
    
    def fix_postgresql(self):
        """Fix PostgreSQL issues automatically"""
        self.colored_print("🔧 Checking PostgreSQL status...", self.YELLOW)
        
        # Check if PostgreSQL is installed
        if not self._command_exists('psql'):
            self.colored_print("✗ PostgreSQL is not installed", self.RED)
            return False
        
        # macOS with Homebrew
        if self._command_exists('brew'):
            return self._fix_postgresql_brew()
        # Linux with systemctl
        elif self._command_exists('systemctl'):
            return self._fix_postgresql_systemctl()
        else:
            self.colored_print("⚠ Please start PostgreSQL manually", self.YELLOW)
            return False
    
    def _fix_postgresql_brew(self):
        """Fix PostgreSQL on macOS with Homebrew"""
        try:
            # Get PostgreSQL version
            result = subprocess.run(['brew', 'list', '--versions'], 
                                  capture_output=True, text=True)
            pg_version = None
            for line in result.stdout.split('\n'):
                if line.startswith('postgresql@'):
                    pg_version = line.split()[0]
                    break
            
            if not pg_version:
                pg_version = 'postgresql'
            
            # Check service status
            result = subprocess.run(['brew', 'services', 'list'], 
                                  capture_output=True, text=True)
            
            pg_status = None
            for line in result.stdout.split('\n'):
                if pg_version in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        pg_status = parts[1]
                    break
            
            if pg_status in ['error', 'stopped', 'none', None]:
                self.colored_print(f"⚠ PostgreSQL ({pg_version}) is not running properly", self.YELLOW)
                
                # Check for stale PID file
                pg_data_dirs = [
                    f"/opt/homebrew/var/{pg_version}",
                    f"/usr/local/var/{pg_version}"
                ]
                
                for pg_data_dir in pg_data_dirs:
                    pid_file = Path(pg_data_dir) / "postmaster.pid"
                    if pid_file.exists():
                        self.colored_print("🔍 Found PID file, checking process...", self.YELLOW)
                        try:
                            with open(pid_file, 'r') as f:
                                old_pid = int(f.readline().strip())
                            
                            # Check if process exists
                            if not psutil.pid_exists(old_pid):
                                self.colored_print("🧹 Removing stale PID file...", self.YELLOW)
                                pid_file.unlink()
                        except Exception:
                            pass
                
                # Restart PostgreSQL
                self.colored_print(f"🔄 Restarting PostgreSQL ({pg_version})...", self.YELLOW)
                subprocess.run(['brew', 'services', 'stop', pg_version], 
                             capture_output=True)
                time.sleep(2)
                subprocess.run(['brew', 'services', 'start', pg_version], 
                             capture_output=True)
                time.sleep(3)
                
                # Check if it's working now
                if self.check_postgresql():
                    self.colored_print("✓ PostgreSQL is now running", self.GREEN)
                    return True
                else:
                    self.colored_print("✗ Failed to start PostgreSQL", self.RED)
                    self.colored_print(f"Try: brew services restart {pg_version}", self.YELLOW)
                    return False
            
            elif pg_status == 'started':
                if self.check_postgresql():
                    self.colored_print("✓ PostgreSQL is running", self.GREEN)
                    return True
                else:
                    # Service running but not accepting connections
                    self.colored_print("⚠ PostgreSQL running but not accepting connections", self.YELLOW)
                    self.colored_print(f"🔄 Restarting PostgreSQL ({pg_version})...", self.YELLOW)
                    subprocess.run(['brew', 'services', 'restart', pg_version], 
                                 capture_output=True)
                    time.sleep(3)
                    
                    if self.check_postgresql():
                        self.colored_print("✓ PostgreSQL is now accepting connections", self.GREEN)
                        return True
                    else:
                        self.colored_print("✗ PostgreSQL still not accepting connections", self.RED)
                        return False
            
            return self.check_postgresql()
            
        except Exception as e:
            self.colored_print(f"Error fixing PostgreSQL: {e}", self.RED)
            return False
    
    def _fix_postgresql_systemctl(self):
        """Fix PostgreSQL on Linux with systemctl"""
        try:
            # Try to restart PostgreSQL
            self.colored_print("🔄 Restarting PostgreSQL service...", self.YELLOW)
            subprocess.run(['sudo', 'systemctl', 'restart', 'postgresql'], 
                         capture_output=True)
            time.sleep(3)
            
            if self.check_postgresql():
                self.colored_print("✓ PostgreSQL is now running", self.GREEN)
                return True
            else:
                self.colored_print("✗ Failed to start PostgreSQL", self.RED)
                return False
        except Exception:
            return False
    
    def _command_exists(self, command):
        """Check if a command exists"""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def check_backend_status(self):
        """Check if backend is running"""
        try:
            # Check PID file
            if self.backend_pid_file.exists():
                with open(self.backend_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Check if process exists and is Django
                if psutil.pid_exists(pid):
                    try:
                        proc = psutil.Process(pid)
                        cmdline = ' '.join(proc.cmdline())
                        if 'manage.py' in cmdline and 'runserver' in cmdline:
                            return True, pid
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            # Check port directly
            for proc in psutil.process_iter(['pid', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'manage.py' in cmdline and 'runserver' in cmdline:
                        for conn in proc.connections():
                            if conn.laddr.port == self.backend_port:
                                # Update PID file
                                with open(self.backend_pid_file, 'w') as f:
                                    f.write(str(proc.pid))
                                return True, proc.pid
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return False, None
        except Exception:
            return False, None
    
    def start_backend(self, silent=False):
        """Start backend using the shell script"""
        if not silent:
            self.colored_print("🚀 Starting UNIBOS Web Core...", self.BLUE)
        
        # First ensure PostgreSQL is running
        if not self.check_postgresql():
            if not self.fix_postgresql():
                self.colored_print("✗ Cannot start backend without PostgreSQL", self.RED)
                return False
        
        # Check if already running
        is_running, pid = self.check_backend_status()
        if is_running:
            if not silent:
                self.colored_print(f"✓ Backend already running (PID: {pid})", self.GREEN)
            return True
        
        # Use the shell script for consistency
        if self.backend_script.exists():
            result = subprocess.run(
                [str(self.backend_script), 'start'],
                cwd=str(self.backend_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                if not silent:
                    self.colored_print("✓ Backend started successfully", self.GREEN)
                return True
            else:
                if not silent:
                    self.colored_print("✗ Failed to start backend", self.RED)
                    if result.stderr:
                        print(result.stderr)
                return False
        else:
            self.colored_print(f"✗ Backend script not found: {self.backend_script}", self.RED)
            return False
    
    def stop_backend(self, silent=False):
        """Stop backend using the shell script"""
        if not silent:
            self.colored_print("⏹️ Stopping UNIBOS Web Core...", self.YELLOW)
        
        if self.backend_script.exists():
            result = subprocess.run(
                [str(self.backend_script), 'stop'],
                cwd=str(self.backend_path),
                capture_output=True,
                text=True
            )
            
            if not silent:
                if result.returncode == 0:
                    self.colored_print("✓ Backend stopped", self.GREEN)
                else:
                    self.colored_print("⚠ Backend stop completed", self.YELLOW)
            
            # Clean up orphaned processes
            self._cleanup_orphaned_processes()
            return True
        else:
            self.colored_print(f"✗ Backend script not found: {self.backend_script}", self.RED)
            return False
    
    def restart_backend(self, silent=False):
        """Restart backend"""
        if not silent:
            self.colored_print("🔄 Restarting UNIBOS Web Core...", self.BLUE)
        
        self.stop_backend(silent=True)
        time.sleep(2)
        return self.start_backend(silent=silent)
    
    def _cleanup_orphaned_processes(self):
        """Clean up orphaned Django processes"""
        try:
            for proc in psutil.process_iter(['pid', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'manage.py runserver' in cmdline:
                        proc.kill()
                        time.sleep(0.5)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
    
    def get_status(self):
        """Get detailed status of all services"""
        status = {
            'postgresql': False,
            'backend': False,
            'backend_pid': None,
            'api_healthy': False
        }
        
        # Check PostgreSQL
        status['postgresql'] = self.check_postgresql()
        
        # Check Backend
        is_running, pid = self.check_backend_status()
        status['backend'] = is_running
        status['backend_pid'] = pid
        
        # Check API health
        if status['backend']:
            try:
                import requests
                response = requests.get(f'http://localhost:{self.backend_port}/api/status/', 
                                      timeout=2)
                status['api_healthy'] = response.status_code == 200
            except Exception:
                status['api_healthy'] = False
        
        return status
    
    def auto_recovery(self):
        """Auto-recover all services"""
        self.colored_print("🔧 Running auto-recovery...", self.BLUE)
        
        # Fix PostgreSQL if needed
        if not self.check_postgresql():
            self.fix_postgresql()
        
        # Fix Backend if needed
        is_running, _ = self.check_backend_status()
        if not is_running:
            self.start_backend()
        else:
            # Check API health
            status = self.get_status()
            if not status['api_healthy']:
                self.colored_print("⚠ Backend running but API not healthy, restarting...", self.YELLOW)
                self.restart_backend()
        
        # Final status check
        status = self.get_status()
        if status['postgresql'] and status['backend'] and status['api_healthy']:
            self.colored_print("✓ All services are healthy", self.GREEN)
            return True
        else:
            self.colored_print("⚠ Some services may still have issues", self.YELLOW)
            return False

# CLI Integration functions
def start_web_core(silent=False):
    """Start web core - used by CLI"""
    manager = ServerManager()
    return manager.start_backend(silent=silent)

def stop_web_core(silent=False):
    """Stop web core - used by CLI"""
    manager = ServerManager()
    return manager.stop_backend(silent=silent)

def restart_web_core(silent=False):
    """Restart web core - used by CLI"""
    manager = ServerManager()
    return manager.restart_backend(silent=silent)

def get_web_core_status():
    """Get web core status - used by CLI"""
    manager = ServerManager()
    status = manager.get_status()
    return {
        'running': status['backend'],
        'pid': status['backend_pid'],
        'postgresql': status['postgresql'],
        'api_healthy': status['api_healthy']
    }

def auto_fix_web_core():
    """Auto-fix web core issues - used by CLI"""
    manager = ServerManager()
    return manager.auto_recovery()

if __name__ == "__main__":
    # For testing
    manager = ServerManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'start':
            manager.start_backend()
        elif command == 'stop':
            manager.stop_backend()
        elif command == 'restart':
            manager.restart_backend()
        elif command == 'status':
            status = manager.get_status()
            print(json.dumps(status, indent=2))
        elif command == 'auto-recovery':
            manager.auto_recovery()
        else:
            print("Usage: server_manager.py [start|stop|restart|status|auto-recovery]")
    else:
        # Default action
        status = manager.get_status()
        print(json.dumps(status, indent=2))