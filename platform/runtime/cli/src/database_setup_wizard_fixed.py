#!/usr/bin/env python3
"""
Cross-platform Database Setup Wizard
Works on macOS, Ubuntu, Raspberry Pi, and other Linux distributions
"""

import os
import sys
import subprocess
import platform
import time
import json
from pathlib import Path

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    BG_ORANGE = '\033[48;5;202m'
    BLACK = '\033[30m'

class CrossPlatformDatabaseSetup:
    """Cross-platform database setup wizard"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.hostname = platform.node().lower()
        self.is_raspberry_pi = self.detect_raspberry_pi()
        self.package_manager = self.detect_package_manager()
        
    def detect_raspberry_pi(self):
        """Detect if running on Raspberry Pi"""
        # Check multiple indicators
        if 'raspberry' in self.hostname or 'rpi' in self.hostname:
            return True
        if 'arm' in self.machine or 'aarch64' in self.machine:
            # Check for Raspberry Pi specific files
            if os.path.exists('/proc/device-tree/model'):
                try:
                    with open('/proc/device-tree/model', 'r') as f:
                        model = f.read().lower()
                        if 'raspberry' in model:
                            return True
                except:
                    pass
        return False
    
    def detect_package_manager(self):
        """Detect the system's package manager"""
        if self.system == "darwin":  # macOS
            # Check for Homebrew
            if self.command_exists('brew'):
                return 'brew'
            # Check for MacPorts
            elif self.command_exists('port'):
                return 'macports'
            else:
                return None
        
        elif self.system == "linux":
            # Check for various package managers
            if self.command_exists('apt-get') or self.command_exists('apt'):
                return 'apt'  # Debian/Ubuntu/Raspberry Pi OS
            elif self.command_exists('dnf'):
                return 'dnf'  # Fedora
            elif self.command_exists('yum'):
                return 'yum'  # CentOS/RHEL
            elif self.command_exists('pacman'):
                return 'pacman'  # Arch
            elif self.command_exists('zypper'):
                return 'zypper'  # openSUSE
            elif self.command_exists('apk'):
                return 'apk'  # Alpine
            else:
                return None
        
        elif self.system == "windows":
            if self.command_exists('choco'):
                return 'chocolatey'
            elif self.command_exists('winget'):
                return 'winget'
            else:
                return None
        
        return None
    
    def command_exists(self, command):
        """Check if a command exists"""
        try:
            if self.system == "windows":
                result = subprocess.run(['where', command], 
                                      capture_output=True, text=True, shell=True)
            else:
                result = subprocess.run(['which', command], 
                                      capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def get_system_info(self):
        """Get detailed system information"""
        info = {
            'system': self.system,
            'machine': self.machine,
            'hostname': self.hostname,
            'platform': platform.platform(),
            'is_raspberry_pi': self.is_raspberry_pi,
            'package_manager': self.package_manager
        }
        
        # Get Linux distribution info
        if self.system == "linux":
            try:
                if os.path.exists('/etc/os-release'):
                    with open('/etc/os-release') as f:
                        for line in f:
                            if line.startswith('ID='):
                                info['distro'] = line.strip().split('=')[1].strip('"')
                            elif line.startswith('VERSION_ID='):
                                info['version'] = line.strip().split('=')[1].strip('"')
            except:
                pass
        
        return info
    
    def install_postgresql(self):
        """Install PostgreSQL based on detected system"""
        print(f"\n{Colors.CYAN}🗄️  installing postgresql...{Colors.RESET}")
        
        # Show system info
        info = self.get_system_info()
        print(f"{Colors.DIM}system: {info['platform']}{Colors.RESET}")
        print(f"{Colors.DIM}package manager: {self.package_manager or 'not detected'}{Colors.RESET}")
        
        if self.is_raspberry_pi:
            print(f"{Colors.MAGENTA}🍓 raspberry pi detected!{Colors.RESET}")
        
        # Route to appropriate installer
        if self.system == "darwin":
            return self.install_postgresql_macos()
        elif self.system == "linux":
            if self.is_raspberry_pi:
                return self.install_postgresql_raspberry()
            else:
                return self.install_postgresql_linux()
        elif self.system == "windows":
            return self.install_postgresql_windows()
        else:
            print(f"{Colors.RED}❌ unsupported system: {self.system}{Colors.RESET}")
            return False
    
    def install_postgresql_macos(self):
        """Install PostgreSQL on macOS"""
        print(f"\n{Colors.BLUE}🍎 macos installation{Colors.RESET}")
        
        if self.package_manager == 'brew':
            print("   using homebrew...")
            
            # Update Homebrew
            print("   updating homebrew...")
            subprocess.run(['brew', 'update'], capture_output=True)
            
            # Install PostgreSQL
            print("   installing postgresql...")
            result = subprocess.run(['brew', 'install', 'postgresql@15'],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✓ postgresql installed{Colors.RESET}")
                
                # Start service
                print("   starting postgresql service...")
                subprocess.run(['brew', 'services', 'start', 'postgresql@15'])
                print(f"   {Colors.GREEN}✓ service started{Colors.RESET}")
                
                return True
            else:
                print(f"   {Colors.RED}✗ installation failed{Colors.RESET}")
                if "already installed" in result.stderr:
                    print("   postgresql already installed")
                    return True
                return False
        
        elif self.package_manager == 'macports':
            print("   using macports...")
            cmds = [
                ['sudo', 'port', 'install', 'postgresql15-server']
            ]
            return self.run_commands(cmds)
        
        else:
            print(f"{Colors.YELLOW}⚠️  no package manager found{Colors.RESET}")
            print("\ninstall homebrew first:")
            print('  /bin/bash -c "$(curl -fsSL https://brew.sh/install.sh)"')
            return False
    
    def install_postgresql_linux(self):
        """Install PostgreSQL on Linux"""
        print(f"\n{Colors.CYAN}🐧 linux installation{Colors.RESET}")
        
        if self.package_manager == 'apt':
            print("   using apt (debian/ubuntu)...")
            cmds = [
                ['sudo', 'apt', 'update'],
                ['sudo', 'apt', 'install', '-y', 'postgresql', 'postgresql-contrib']
            ]
            
            if self.run_commands(cmds):
                # Start service
                print("   starting postgresql service...")
                subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'])
                subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'])
                print(f"   {Colors.GREEN}✓ service started{Colors.RESET}")
                return True
            return False
        
        elif self.package_manager == 'dnf':
            print("   using dnf (fedora)...")
            cmds = [
                ['sudo', 'dnf', 'install', '-y', 'postgresql', 'postgresql-server']
            ]
            
            if self.run_commands(cmds):
                # Initialize DB
                subprocess.run(['sudo', 'postgresql-setup', '--initdb'])
                # Start service
                subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'])
                subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'])
                return True
            return False
        
        elif self.package_manager == 'yum':
            print("   using yum (centos/rhel)...")
            cmds = [
                ['sudo', 'yum', 'install', '-y', 'postgresql-server', 'postgresql-contrib']
            ]
            
            if self.run_commands(cmds):
                subprocess.run(['sudo', 'postgresql-setup', 'initdb'])
                subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'])
                subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'])
                return True
            return False
        
        elif self.package_manager == 'pacman':
            print("   using pacman (arch)...")
            cmds = [
                ['sudo', 'pacman', '-S', '--noconfirm', 'postgresql']
            ]
            
            if self.run_commands(cmds):
                subprocess.run(['sudo', '-u', 'postgres', 'initdb', '-D', '/var/lib/postgres/data'])
                subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'])
                subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'])
                return True
            return False
        
        else:
            print(f"{Colors.YELLOW}⚠️  package manager not supported: {self.package_manager}{Colors.RESET}")
            print("\nmanual installation required:")
            print("  https://www.postgresql.org/download/linux/")
            return False
    
    def install_postgresql_raspberry(self):
        """Install PostgreSQL on Raspberry Pi"""
        print(f"\n{Colors.MAGENTA}🍓 raspberry pi installation{Colors.RESET}")
        
        # Raspberry Pi typically uses Debian-based OS
        print("   optimizing for raspberry pi...")
        
        cmds = [
            ['sudo', 'apt', 'update'],
            ['sudo', 'apt', 'install', '-y', 'postgresql', 'postgresql-contrib'],
            # Install lighter version if available
            ['sudo', 'apt', 'install', '-y', 'postgresql-client']
        ]
        
        print("   installing postgresql (this may take a while)...")
        if self.run_commands(cmds):
            # Configure for low memory
            print("   configuring for raspberry pi...")
            
            # Reduce shared_buffers and work_mem for Pi
            config_cmds = [
                "sudo sed -i 's/shared_buffers = .*/shared_buffers = 32MB/' /etc/postgresql/*/main/postgresql.conf",
                "sudo sed -i 's/work_mem = .*/work_mem = 1MB/' /etc/postgresql/*/main/postgresql.conf"
            ]
            
            for cmd in config_cmds:
                subprocess.run(cmd, shell=True, capture_output=True)
            
            # Start service
            print("   starting postgresql service...")
            subprocess.run(['sudo', 'systemctl', 'restart', 'postgresql'])
            subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'])
            
            print(f"   {Colors.GREEN}✓ postgresql configured for raspberry pi{Colors.RESET}")
            return True
        
        return False
    
    def install_postgresql_windows(self):
        """Install PostgreSQL on Windows"""
        print(f"\n{Colors.YELLOW}🪟 windows installation{Colors.RESET}")
        
        if self.package_manager == 'chocolatey':
            print("   using chocolatey...")
            result = subprocess.run(['choco', 'install', 'postgresql', '-y'],
                                  capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✓ postgresql installed{Colors.RESET}")
                return True
            else:
                print(f"   {Colors.RED}✗ installation failed{Colors.RESET}")
                return False
        
        elif self.package_manager == 'winget':
            print("   using winget...")
            result = subprocess.run(['winget', 'install', 'PostgreSQL.PostgreSQL'],
                                  capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✓ postgresql installed{Colors.RESET}")
                return True
            else:
                print(f"   {Colors.RED}✗ installation failed{Colors.RESET}")
                return False
        
        else:
            print(f"{Colors.YELLOW}⚠️  no package manager found{Colors.RESET}")
            print("\nmanual installation required:")
            print("  1. visit: https://www.postgresql.org/download/windows/")
            print("  2. download the installer")
            print("  3. run the installer")
            print("  4. remember your password!")
            return False
    
    def run_commands(self, commands):
        """Run a list of commands"""
        for cmd in commands:
            print(f"   {Colors.DIM}$ {' '.join(cmd)}{Colors.RESET}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"   {Colors.RED}✗ command failed{Colors.RESET}")
                if "Permission denied" in result.stderr or "sudo" in result.stderr:
                    print("   try running with sudo")
                return False
        
        return True
    
    def test_connection(self):
        """Test PostgreSQL connection"""
        print(f"\n{Colors.CYAN}🔌 testing connection...{Colors.RESET}")
        
        try:
            # Try to connect
            result = subprocess.run(['psql', '-U', 'postgres', '-c', 'SELECT version();'],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✓ postgresql is running{Colors.RESET}")
                return True
            else:
                print(f"   {Colors.YELLOW}⚠️  connection failed{Colors.RESET}")
                return False
        except FileNotFoundError:
            print(f"   {Colors.RED}✗ psql command not found{Colors.RESET}")
            return False
    
    def create_database(self):
        """Create UNIBOS database and user"""
        print(f"\n{Colors.CYAN}🗄️  creating database...{Colors.RESET}")
        
        # Database configuration
        db_name = "unibos_db"
        db_user = "unibos_user"
        db_password = "unibos_password"
        
        # Create user and database
        commands = [
            f"CREATE USER {db_user} WITH PASSWORD '{db_password}';",
            f"CREATE DATABASE {db_name} OWNER {db_user};",
            f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"
        ]
        
        for cmd in commands:
            print(f"   {Colors.DIM}{cmd[:50]}...{Colors.RESET}")
            
            if self.system == "windows":
                result = subprocess.run(['psql', '-U', 'postgres', '-c', cmd],
                                      capture_output=True, text=True, shell=True)
            else:
                result = subprocess.run(['sudo', '-u', 'postgres', 'psql', '-c', cmd],
                                      capture_output=True, text=True)
            
            if result.returncode != 0:
                if "already exists" in result.stderr:
                    print(f"   {Colors.YELLOW}⚠️  already exists{Colors.RESET}")
                else:
                    print(f"   {Colors.RED}✗ failed{Colors.RESET}")
                    return False
        
        print(f"   {Colors.GREEN}✓ database created{Colors.RESET}")
        return True
    
    def run(self):
        """Run the setup wizard"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══ cross-platform database setup ═══{Colors.RESET}")
        
        # Show system info
        info = self.get_system_info()
        print(f"\n{Colors.BOLD}system information:{Colors.RESET}")
        print(f"  platform: {info['platform']}")
        print(f"  package manager: {info['package_manager'] or 'none'}")
        if self.is_raspberry_pi:
            print(f"  device: {Colors.MAGENTA}raspberry pi{Colors.RESET}")
        
        # Install PostgreSQL
        if self.install_postgresql():
            time.sleep(2)
            
            # Test connection
            if self.test_connection():
                # Create database
                self.create_database()
                
                print(f"\n{Colors.GREEN}✅ setup complete!{Colors.RESET}")
                print(f"\n{Colors.BOLD}connection details:{Colors.RESET}")
                print(f"  host: localhost")
                print(f"  port: 5432")
                print(f"  database: unibos_db")
                print(f"  user: unibos_user")
                print(f"  password: unibos_password")
                
                return True
            else:
                print(f"\n{Colors.YELLOW}⚠️  postgresql installed but not running{Colors.RESET}")
                print("try starting it manually:")
                
                if self.system == "darwin":
                    print("  brew services start postgresql@15")
                elif self.system == "linux":
                    print("  sudo systemctl start postgresql")
                
                return False
        else:
            print(f"\n{Colors.RED}❌ installation failed{Colors.RESET}")
            return False

# Entry point
if __name__ == "__main__":
    wizard = CrossPlatformDatabaseSetup()
    wizard.run()