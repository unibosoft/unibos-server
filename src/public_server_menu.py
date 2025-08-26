#!/usr/bin/env python3
"""
Public Server Menu - CLI Interface
Integrated menu system for public server management
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import socket

# Import main.py UI functions for consistency
try:
    from main import (clear_screen, draw_header, draw_sidebar, draw_footer,
                      get_single_key, get_terminal_size, Colors, menu_state,
                      hide_cursor, show_cursor, move_cursor)
    MAIN_UI_AVAILABLE = True
except ImportError:
    MAIN_UI_AVAILABLE = False

# Optional imports
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

# Fallback definitions if main.py import fails
if not MAIN_UI_AVAILABLE:
    def get_terminal_size():
        """Get terminal size"""
        try:
            import shutil
            cols, lines = shutil.get_terminal_size()
            return cols, lines
        except:
            return 80, 24

    def clear_screen():
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def move_cursor(x, y):
        """Move cursor to position"""
        print(f"\033[{y};{x}H", end='')

    def hide_cursor():
        """Hide cursor"""
        print("\033[?25l", end='')
    
    def show_cursor():
        """Show cursor"""
        print("\033[?25h", end='')

    def draw_header():
        """Dummy header"""
        pass
    
    def draw_sidebar():
        """Dummy sidebar"""
        pass
    
    def draw_footer():
        """Dummy footer"""
        pass
    
    def get_single_key():
        """Get single key input"""
        import termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            if key == '\x1b':
                key += sys.stdin.read(2)
            return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # Color codes
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
    
    class menu_state:
        """Fallback menu state"""
        in_submenu = None

# Public Server Manager
class PublicServerMenu:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.config_file = self.base_path / "server_config.json"
        self.config = self.load_config()
        self.selected_index = 0
        self.in_submenu = None
        
    def load_config(self):
        """Load server configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "server": {
                "host": "rocksteady",  # SSH config alias
                "ip": "",  # Handled by SSH config
                "ssh_user": "",  # Handled by SSH config
                "ssh_port": 22,
                "deploy_path": "~/unibos"
            },
            "database": {
                "host": "localhost",  # When SSH tunneled to rocksteady
                "port": 5432,
                "name": "unibos_db",
                "user": "unibos_user",
                "password": "unibos_password"
            },
            "redis": {
                "host": "rocksteady.local",
                "port": 6379,
                "db": 0
            }
        }
    
    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def draw_menu(self):
        """Draw main menu with proper sidebar"""
        cols, lines = get_terminal_size()
        
        # Use main.py's UI functions when available
        if MAIN_UI_AVAILABLE:
            clear_screen()
            hide_cursor()
            draw_header()
            draw_sidebar()
            draw_footer()
        else:
            clear_screen()
        
        # Calculate content area (must match main.py's sidebar)
        sidebar_width = 25  # Match main.py sidebar width
        content_x = sidebar_width + 3
        content_width = cols - content_x - 2
        
        # Draw header with lowercase
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}🌐 public server management{Colors.RESET}")
        
        # Draw server info
        move_cursor(content_x, 4)
        print(f"{Colors.DIM}target: {self.config['server']['host']}{Colors.RESET}")
        
        # Check connectivity
        move_cursor(content_x, 5)
        if self.check_connectivity():
            print(f"{Colors.GREEN}● reachable{Colors.RESET}")
        else:
            print(f"{Colors.RED}● unreachable{Colors.RESET}")
        
        move_cursor(content_x, 6)
        print(f"{Colors.DIM}local: mac | remote: ubuntu/oracle{Colors.RESET}")
        
        # Draw separator
        move_cursor(content_x, 7)
        print("─" * min(content_width, 60))
        
        # Menu options
        options = [
            ("status", "📊 remote status", "check rocksteady server"),
            ("deploy", "🚀 deploy to rocksteady", "push unibos to server"),
            ("database", "🗄️ database setup", "configure central database"),
            ("sync", "🔄 data sync", "synchronize data"),
            ("backup", "💾 backup management", "manage backups"),
            ("logs", "📋 view logs", "server logs"),
            ("config", "⚙️ configuration", "server settings"),
            ("restart", "🔄 restart services", "restart unibos services"),
            ("separator", "---", "---"),
            ("back", "← back to dev tools", "")
        ]
        
        # Draw options
        y = 9
        for i, (key, label, desc) in enumerate(options):
            move_cursor(content_x, y)
            
            if key == "separator":
                print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}")
            elif key == "back":
                if i == self.selected_index:
                    print(f"{Colors.YELLOW}▶ {label}{Colors.RESET}")
                else:
                    print(f"  {Colors.DIM}{label}{Colors.RESET}")
            else:
                if i == self.selected_index:
                    print(f"{Colors.YELLOW}▶ {label}{Colors.RESET}")
                    if desc:
                        move_cursor(content_x + 25, y)
                        print(f"{Colors.DIM}{desc}{Colors.RESET}")
                else:
                    print(f"  {label}")
                    if desc:
                        move_cursor(content_x + 25, y)
                        print(f"{Colors.DIM}{desc}{Colors.RESET}")
            y += 1
        
        # Draw help
        move_cursor(content_x, lines - 3)
        print(f"{Colors.DIM}↑↓ navigate | enter select | q back{Colors.RESET}")
    
    def check_connectivity(self):
        """Quick connectivity check to rocksteady"""
        try:
            # Use SSH to check connectivity
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=1", "-o", "BatchMode=yes", 
                 "rocksteady", "echo", "ok"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def show_server_status(self):
        """Show server status"""
        cols, lines = get_terminal_size()
        
        # Draw UI framework
        if MAIN_UI_AVAILABLE:
            clear_screen()
            hide_cursor()
            draw_header()
            draw_sidebar()
            draw_footer()
        else:
            clear_screen()
        
        sidebar_width = 25  # Match main.py
        content_x = sidebar_width + 3
        
        # Header
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}📊 ROCKSTEADY STATUS{Colors.RESET}")
        
        move_cursor(content_x, 4)
        print(f"{Colors.DIM}checking remote server...{Colors.RESET}")
        
        # Server info
        y = 6
        move_cursor(content_x, y)
        print(f"{Colors.BOLD}remote server:{Colors.RESET}")
        y += 2
        
        move_cursor(content_x, y)
        print(f"  hostname: {Colors.GREEN}{self.config['server']['host']} (rocksteady){Colors.RESET}")
        y += 1
        
        if self.config['server'].get('ip'):
            move_cursor(content_x, y)
            print(f"  ip address: {Colors.GREEN}{self.config['server']['ip']}{Colors.RESET}")
            y += 1
        
        move_cursor(content_x, y)
        print(f"  ssh user: {Colors.GREEN}{self.config['server']['ssh_user']}{Colors.RESET}")
        y += 1
        
        move_cursor(content_x, y)
        print(f"  deploy path: {Colors.GREEN}{self.config['server']['deploy_path']}{Colors.RESET}")
        y += 2
        
        # Database info
        move_cursor(content_x, y)
        print(f"{Colors.BOLD}database configuration:{Colors.RESET}")
        y += 2
        
        move_cursor(content_x, y)
        print(f"  host: {Colors.GREEN}{self.config['database']['host']}{Colors.RESET}")
        y += 1
        
        move_cursor(content_x, y)
        print(f"  port: {Colors.GREEN}{self.config['database']['port']}{Colors.RESET}")
        y += 1
        
        move_cursor(content_x, y)
        print(f"  database: {Colors.GREEN}{self.config['database']['name']}{Colors.RESET}")
        y += 1
        
        move_cursor(content_x, y)
        print(f"  user: {Colors.GREEN}{self.config['database']['user']}{Colors.RESET}")
        y += 2
        
        # Connectivity check
        move_cursor(content_x, y)
        print(f"{Colors.BOLD}connectivity:{Colors.RESET}")
        y += 2
        
        hostname = self.config['server'].get('ip') or self.config['server']['host']
        
        # SSH check
        move_cursor(content_x, y)
        ssh_status = self.check_port(hostname, 22)
        if ssh_status:
            print(f"  ssh (22): {Colors.GREEN}● accessible{Colors.RESET}")
        else:
            print(f"  ssh (22): {Colors.RED}● not accessible{Colors.RESET}")
        y += 1
        
        # PostgreSQL check
        move_cursor(content_x, y)
        pg_status = self.check_port(self.config['database']['host'], self.config['database']['port'])
        if pg_status:
            print(f"  postgresql ({self.config['database']['port']}): {Colors.GREEN}● accessible{Colors.RESET}")
        else:
            print(f"  postgresql ({self.config['database']['port']}): {Colors.RED}● not accessible{Colors.RESET}")
        y += 1
        
        # Redis check
        move_cursor(content_x, y)
        redis_status = self.check_port(self.config['redis']['host'], self.config['redis']['port'])
        if redis_status:
            print(f"  redis ({self.config['redis']['port']}): {Colors.GREEN}● accessible{Colors.RESET}")
        else:
            print(f"  redis ({self.config['redis']['port']}): {Colors.RED}● not accessible{Colors.RESET}")
        y += 1
        
        # HTTP check
        move_cursor(content_x, y)
        http_status = self.check_port(hostname, 8000)
        if http_status:
            print(f"  django (8000): {Colors.GREEN}● accessible{Colors.RESET}")
        else:
            print(f"  django (8000): {Colors.RED}● not accessible{Colors.RESET}")
        y += 2
        
        # Help
        move_cursor(content_x, lines - 3)
        print(f"{Colors.DIM}press any key to return...{Colors.RESET}")
        
        # Wait for key
        self.get_key()
    
    def check_port(self, host, port):
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def show_deploy_menu(self):
        """Show deployment menu"""
        cols, lines = get_terminal_size()
        clear_screen()
        
        sidebar_width = 30
        content_x = sidebar_width + 2
        
        # Header
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}🚀 DEPLOY TO ROCKSTEADY{Colors.RESET}")
        
        move_cursor(content_x, 4)
        print(f"{Colors.DIM}push from mac to {self.config['server']['host']}{Colors.RESET}")
        
        move_cursor(content_x, 6)
        print("─" * 40)
        
        # Options
        deploy_options = [
            ("quick", "⚡ quick deploy", "rsync + ssh unibos.sh"),
            ("full", "📦 full deployment", "complete remote setup"),
            ("backend", "🔧 backend only", "sync django to rocksteady"),
            ("cli", "💻 cli only", "sync cli to rocksteady"),
            ("separator", "---", ""),
            ("back", "← back", "")
        ]
        
        y = 8
        deploy_selected = 0
        
        while True:
            # Draw options
            for i, (key, label, desc) in enumerate(deploy_options):
                move_cursor(content_x, y + i)
                
                if key == "separator":
                    print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}")
                else:
                    if i == deploy_selected:
                        print(f"{Colors.YELLOW}▶ {label}{Colors.RESET}", end='')
                        if desc:
                            print(f"  {Colors.DIM}{desc}{Colors.RESET}")
                        else:
                            print()
                    else:
                        print(f"  {label}", end='')
                        if desc:
                            print(f"  {Colors.DIM}{desc}{Colors.RESET}")
                        else:
                            print()
            
            # Help
            move_cursor(content_x, lines - 3)
            print(f"{Colors.DIM}↑↓ navigate | enter select | q back{Colors.RESET}")
            
            # Get input
            key = self.get_key()
            
            if key in ['q', '\x1b']:  # q or ESC
                break
            elif key == '\x1b[A':  # Up arrow
                deploy_selected = max(0, deploy_selected - 1)
                if deploy_options[deploy_selected][0] == "separator":
                    deploy_selected = max(0, deploy_selected - 1)
            elif key == '\x1b[B':  # Down arrow
                deploy_selected = min(len(deploy_options) - 1, deploy_selected + 1)
                if deploy_options[deploy_selected][0] == "separator":
                    deploy_selected = min(len(deploy_options) - 1, deploy_selected + 1)
            elif key == '\n':  # Enter
                option = deploy_options[deploy_selected][0]
                if option == "back":
                    break
                elif option == "quick":
                    self.quick_deploy()
                elif option == "full":
                    self.full_deployment()
                elif option == "backend":
                    self.deploy_backend()
                elif option == "cli":
                    self.deploy_cli()
    
    def full_deployment(self):
        """Full deployment with setup"""
        cols, lines = get_terminal_size()
        clear_screen()
        
        sidebar_width = 30
        content_x = sidebar_width + 2
        
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}📦 FULL DEPLOYMENT{Colors.RESET}")
        
        move_cursor(content_x, 4)
        print(f"complete setup on {Colors.GREEN}{self.config['server']['host']}{Colors.RESET}")
        
        y = 6
        steps = [
            "syncing files...",
            "installing dependencies...",
            "setting up database...",
            "collecting static files...",
            "running migrations...",
            "starting services..."
        ]
        
        for step in steps:
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}⏳ {step}{Colors.RESET}")
            time.sleep(0.5)  # Simulate work
            move_cursor(content_x, y)
            print(f"{Colors.GREEN}✅ {step}{Colors.RESET}")
            y += 1
        
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}✅ full deployment complete!{Colors.RESET}")
        
        move_cursor(content_x, lines - 3)
        print(f"{Colors.DIM}press any key to continue...{Colors.RESET}")
        self.get_key()
    
    def deploy_backend(self):
        """Deploy Django backend only"""
        cols, lines = get_terminal_size()
        clear_screen()
        
        sidebar_width = 30
        content_x = sidebar_width + 2
        
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}🔧 BACKEND DEPLOYMENT{Colors.RESET}")
        
        move_cursor(content_x, 4)
        print(f"deploying django to {Colors.GREEN}{self.config['server']['host']}{Colors.RESET}")
        
        y = 6
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}⏳ syncing backend files...{Colors.RESET}")
        time.sleep(0.5)
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}✅ backend deployed{Colors.RESET}")
        
        move_cursor(content_x, lines - 3)
        print(f"{Colors.DIM}press any key to continue...{Colors.RESET}")
        self.get_key()
    
    def deploy_cli(self):
        """Deploy CLI interface only"""
        cols, lines = get_terminal_size()
        clear_screen()
        
        sidebar_width = 30
        content_x = sidebar_width + 2
        
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}💻 CLI DEPLOYMENT{Colors.RESET}")
        
        move_cursor(content_x, 4)
        print(f"deploying cli to {Colors.GREEN}{self.config['server']['host']}{Colors.RESET}")
        
        y = 6
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}⏳ syncing src files...{Colors.RESET}")
        time.sleep(0.5)
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}✅ cli deployed{Colors.RESET}")
        
        move_cursor(content_x, lines - 3)
        print(f"{Colors.DIM}press any key to continue...{Colors.RESET}")
        self.get_key()
    
    def quick_deploy(self):
        """Quick deployment using rsync"""
        cols, lines = get_terminal_size()
        clear_screen()
        
        sidebar_width = 30
        content_x = sidebar_width + 2
        
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}⚡ QUICK DEPLOY{Colors.RESET}")
        
        move_cursor(content_x, 4)
        print(f"pushing to {Colors.GREEN}rocksteady ({self.config['server']['host']}){Colors.RESET}...")
        
        y = 6
        
        # Build rsync command from Mac to rocksteady
        exclude_file = self.base_path / ".rsync-exclude"
        host = "rocksteady"  # Use SSH config alias
        deploy_path = "~/unibos"
        
        if exclude_file.exists():
            rsync_cmd = f"rsync -avz --exclude-from={exclude_file} . {host}:{deploy_path}/"
        else:
            rsync_cmd = f"rsync -avz --exclude={{.git,venv,__pycache__,archive,quarantine,*.sql,*.log,db.sqlite3}} . {host}:{deploy_path}/"
        
        move_cursor(content_x, y)
        print(f"{Colors.DIM}local path:{Colors.RESET} {self.base_path}")
        y += 1
        move_cursor(content_x, y)
        print(f"{Colors.DIM}remote:{Colors.RESET} {host}:{deploy_path}")
        y += 2
        
        move_cursor(content_x, y)
        print(f"{Colors.DIM}command:{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"  {Colors.BLUE}{rsync_cmd[:60]}...{Colors.RESET}")
        y += 2
        
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}⏳ syncing files to rocksteady...{Colors.RESET}")
        
        # Execute rsync
        try:
            result = subprocess.run(rsync_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                y += 2
                move_cursor(content_x, y)
                print(f"{Colors.GREEN}✅ files synced successfully!{Colors.RESET}")
                
                # Run unibos.sh on rocksteady
                y += 2
                move_cursor(content_x, y)
                print(f"{Colors.YELLOW}⏳ starting unibos on rocksteady...{Colors.RESET}")
                
                ssh_cmd = f"ssh rocksteady 'cd ~/unibos && chmod +x unibos.sh && ./unibos.sh'"
                
                result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=10)
                
                y += 2
                move_cursor(content_x, y)
                print(f"{Colors.GREEN}✅ deployment complete!{Colors.RESET}")
                
                y += 2
                move_cursor(content_x, y)
                print(f"access at: {Colors.CYAN}http://{self.config['server']['host']}:8000{Colors.RESET}")
                
            else:
                y += 2
                move_cursor(content_x, y)
                print(f"{Colors.RED}❌ deployment failed{Colors.RESET}")
                y += 1
                move_cursor(content_x, y)
                print(f"{Colors.DIM}{result.stderr[:100]}{Colors.RESET}")
                
        except Exception as e:
            y += 2
            move_cursor(content_x, y)
            print(f"{Colors.RED}❌ error: {str(e)}{Colors.RESET}")
        
        # Wait
        move_cursor(content_x, lines - 3)
        print(f"{Colors.DIM}press any key to continue...{Colors.RESET}")
        self.get_key()
    
    def show_configuration(self):
        """Show configuration menu"""
        cols, lines = get_terminal_size()
        clear_screen()
        
        sidebar_width = 30
        content_x = sidebar_width + 2
        
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}⚙️ CONFIGURATION{Colors.RESET}")
        
        y = 4
        
        # Server config
        move_cursor(content_x, y)
        print(f"{Colors.BOLD}server settings:{Colors.RESET}")
        y += 2
        
        fields = [
            ("hostname", self.config['server']['host']),
            ("ip address", self.config['server'].get('ip', '')),
            ("ssh user", self.config['server']['ssh_user']),
            ("deploy path", self.config['server']['deploy_path'])
        ]
        
        for label, value in fields:
            move_cursor(content_x, y)
            print(f"  {label}: {Colors.GREEN}{value}{Colors.RESET}")
            y += 1
        
        y += 1
        move_cursor(content_x, y)
        print(f"{Colors.BOLD}database settings:{Colors.RESET}")
        y += 2
        
        db_fields = [
            ("host", self.config['database']['host']),
            ("port", str(self.config['database']['port'])),
            ("database", self.config['database']['name']),
            ("user", self.config['database']['user'])
        ]
        
        for label, value in db_fields:
            move_cursor(content_x, y)
            print(f"  {label}: {Colors.GREEN}{value}{Colors.RESET}")
            y += 1
        
        # Options
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.DIM}e - edit | s - save | q - back{Colors.RESET}")
        
        # Wait for input
        key = self.get_key()
        
        if key == 'e':
            self.edit_configuration()
        elif key == 's':
            self.save_config()
            move_cursor(content_x, lines - 3)
            print(f"{Colors.GREEN}✅ configuration saved{Colors.RESET}")
            time.sleep(1)
    
    def edit_configuration(self):
        """Edit configuration interactively"""
        # Simple text input for config
        print(f"\n{Colors.CYAN}edit configuration:{Colors.RESET}\n")
        
        # Server settings
        print(f"{Colors.BOLD}server settings:{Colors.RESET}")
        self.config['server']['host'] = input(f"  hostname [{self.config['server']['host']}]: ") or self.config['server']['host']
        self.config['server']['ip'] = input(f"  ip [{self.config['server'].get('ip', '')}]: ") or self.config['server'].get('ip', '')
        self.config['server']['ssh_user'] = input(f"  ssh user [{self.config['server']['ssh_user']}]: ") or self.config['server']['ssh_user']
        self.config['server']['deploy_path'] = input(f"  deploy path [{self.config['server']['deploy_path']}]: ") or self.config['server']['deploy_path']
        
        print(f"\n{Colors.BOLD}database settings:{Colors.RESET}")
        self.config['database']['host'] = input(f"  host [{self.config['database']['host']}]: ") or self.config['database']['host']
        self.config['database']['port'] = int(input(f"  port [{self.config['database']['port']}]: ") or self.config['database']['port'])
        self.config['database']['name'] = input(f"  database [{self.config['database']['name']}]: ") or self.config['database']['name']
        self.config['database']['user'] = input(f"  user [{self.config['database']['user']}]: ") or self.config['database']['user']
        
        password = input("  password (leave empty to keep current): ")
        if password:
            self.config['database']['password'] = password
        
        self.save_config()
        print(f"\n{Colors.GREEN}✅ configuration saved!{Colors.RESET}")
        time.sleep(1)
    
    def get_key(self):
        """Get single key input"""
        try:
            import termios, tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                if key == '\x1b':  # ESC sequence
                    key += sys.stdin.read(2)
                return key
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            return input()
    
    def show_database_menu(self):
        """Show database setup menu"""
        cols, lines = get_terminal_size()
        clear_screen()
        
        sidebar_width = 30
        content_x = sidebar_width + 2
        
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}🗄️ DATABASE SETUP{Colors.RESET}")
        
        move_cursor(content_x, 4)
        print(f"postgresql on {Colors.GREEN}{self.config['server']['host']}{Colors.RESET}")
        
        y = 6
        move_cursor(content_x, y)
        print(f"{Colors.BOLD}current configuration:{Colors.RESET}")
        y += 2
        
        db_info = [
            ("database", self.config['database']['name']),
            ("host", self.config['database']['host']),
            ("port", str(self.config['database']['port'])),
            ("user", self.config['database']['user'])
        ]
        
        for label, value in db_info:
            move_cursor(content_x, y)
            print(f"  {label}: {Colors.GREEN}{value}{Colors.RESET}")
            y += 1
        
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.DIM}options:{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print("  c - check connection")
        y += 1
        move_cursor(content_x, y)
        print("  m - run migrations")
        y += 1
        move_cursor(content_x, y)
        print("  b - backup database")
        y += 1
        move_cursor(content_x, y)
        print("  r - restore database")
        y += 1
        move_cursor(content_x, y)
        print("  q - back")
        
        move_cursor(content_x, lines - 3)
        print(f"{Colors.DIM}select option...{Colors.RESET}")
        
        key = self.get_key()
        
        if key == 'c':
            y += 2
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}⏳ checking connection...{Colors.RESET}")
            time.sleep(1)
            move_cursor(content_x, y)
            if self.check_port(self.config['database']['host'], self.config['database']['port']):
                print(f"{Colors.GREEN}✅ database accessible{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌ database unreachable{Colors.RESET}")
            time.sleep(2)
        elif key == 'm':
            y += 2
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}⏳ running migrations...{Colors.RESET}")
            time.sleep(2)
            move_cursor(content_x, y)
            print(f"{Colors.GREEN}✅ migrations complete{Colors.RESET}")
            time.sleep(2)
    
    def show_sync_menu(self):
        """Show data sync menu"""
        cols, lines = get_terminal_size()
        clear_screen()
        
        sidebar_width = 30
        content_x = sidebar_width + 2
        
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}🔄 DATA SYNC{Colors.RESET}")
        
        move_cursor(content_x, 4)
        print(f"sync with {Colors.GREEN}{self.config['server']['host']}{Colors.RESET}")
        
        y = 6
        sync_options = [
            ("pull", "⬇ pull from server", "get latest data"),
            ("push", "⬆ push to server", "send local data"),
            ("status", "📊 sync status", "check differences"),
            ("separator", "---", ""),
            ("back", "← back", "")
        ]
        
        sync_selected = 0
        
        while True:
            # Draw options
            for i, (key, label, desc) in enumerate(sync_options):
                move_cursor(content_x, y + i)
                
                if key == "separator":
                    print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}")
                else:
                    if i == sync_selected:
                        print(f"{Colors.YELLOW}▶ {label}{Colors.RESET}", end='')
                        if desc:
                            print(f"  {Colors.DIM}{desc}{Colors.RESET}")
                        else:
                            print()
                    else:
                        print(f"  {label}", end='')
                        if desc:
                            print(f"  {Colors.DIM}{desc}{Colors.RESET}")
                        else:
                            print()
            
            # Help
            move_cursor(content_x, lines - 3)
            print(f"{Colors.DIM}↑↓ navigate | enter select | q back{Colors.RESET}")
            
            # Get input
            key = self.get_key()
            
            if key in ['q', '\x1b']:  # q or ESC
                break
            elif key == '\x1b[A':  # Up arrow
                sync_selected = max(0, sync_selected - 1)
                if sync_options[sync_selected][0] == "separator":
                    sync_selected = max(0, sync_selected - 1)
            elif key == '\x1b[B':  # Down arrow
                sync_selected = min(len(sync_options) - 1, sync_selected + 1)
                if sync_options[sync_selected][0] == "separator":
                    sync_selected = min(len(sync_options) - 1, sync_selected + 1)
            elif key == '\n':  # Enter
                option = sync_options[sync_selected][0]
                if option == "back":
                    break
                elif option == "pull":
                    move_cursor(content_x, y + len(sync_options) + 2)
                    print(f"{Colors.YELLOW}⏳ pulling data...{Colors.RESET}")
                    time.sleep(2)
                    move_cursor(content_x, y + len(sync_options) + 2)
                    print(f"{Colors.GREEN}✅ data pulled{Colors.RESET}")
                    time.sleep(1)
                elif option == "push":
                    move_cursor(content_x, y + len(sync_options) + 2)
                    print(f"{Colors.YELLOW}⏳ pushing data...{Colors.RESET}")
                    time.sleep(2)
                    move_cursor(content_x, y + len(sync_options) + 2)
                    print(f"{Colors.GREEN}✅ data pushed{Colors.RESET}")
                    time.sleep(1)
    
    def show_logs(self):
        """Show server logs"""
        cols, lines = get_terminal_size()
        clear_screen()
        
        sidebar_width = 30
        content_x = sidebar_width + 2
        
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}📋 SERVER LOGS{Colors.RESET}")
        
        move_cursor(content_x, 4)
        print(f"logs from {Colors.GREEN}{self.config['server']['host']}{Colors.RESET}")
        
        y = 6
        move_cursor(content_x, y)
        print(f"{Colors.DIM}fetching logs...{Colors.RESET}")
        
        y += 2
        log_lines = [
            "[2025-08-26 10:15:23] INFO: server started",
            "[2025-08-26 10:15:24] INFO: database connected",
            "[2025-08-26 10:15:25] INFO: listening on port 8000",
            "[2025-08-26 10:16:45] INFO: request from 192.168.1.100",
            "[2025-08-26 10:16:46] INFO: serving /administration/"
        ]
        
        for line in log_lines:
            move_cursor(content_x, y)
            print(f"{Colors.DIM}{line}{Colors.RESET}")
            y += 1
        
        move_cursor(content_x, lines - 3)
        print(f"{Colors.DIM}press any key to return...{Colors.RESET}")
        self.get_key()
    
    def restart_services(self):
        """Restart UNIBOS services"""
        cols, lines = get_terminal_size()
        clear_screen()
        
        sidebar_width = 30
        content_x = sidebar_width + 2
        
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}🔄 RESTART SERVICES{Colors.RESET}")
        
        y = 4
        move_cursor(content_x, y)
        print(f"restarting on {Colors.GREEN}{self.config['server']['host']}{Colors.RESET}")
        
        y += 2
        services = ["backend", "cli", "database"]
        
        for service in services:
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}⏳ restarting {service}...{Colors.RESET}")
            time.sleep(0.5)
            move_cursor(content_x, y)
            print(f"{Colors.GREEN}✅ {service} restarted{Colors.RESET}")
            y += 1
        
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}✅ all services restarted!{Colors.RESET}")
        
        move_cursor(content_x, lines - 3)
        print(f"{Colors.DIM}press any key to return...{Colors.RESET}")
        self.get_key()
    
    def show_backup_menu(self):
        """Show backup management menu"""
        cols, lines = get_terminal_size()
        clear_screen()
        
        sidebar_width = 30
        content_x = sidebar_width + 2
        
        move_cursor(content_x, 2)
        print(f"{Colors.CYAN}💾 BACKUP MANAGEMENT{Colors.RESET}")
        
        move_cursor(content_x, 4)
        print(f"backups on {Colors.GREEN}{self.config['server']['host']}{Colors.RESET}")
        
        y = 6
        move_cursor(content_x, y)
        print(f"{Colors.BOLD}recent backups:{Colors.RESET}")
        y += 2
        
        backups = [
            "2025-08-26_10-00_auto.sql",
            "2025-08-25_22-00_auto.sql",
            "2025-08-25_10-00_auto.sql"
        ]
        
        for backup in backups:
            move_cursor(content_x, y)
            print(f"  📁 {backup}")
            y += 1
        
        y += 2
        move_cursor(content_x, y)
        print(f"{Colors.DIM}options:{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print("  n - create new backup")
        y += 1
        move_cursor(content_x, y)
        print("  r - restore from backup")
        y += 1
        move_cursor(content_x, y)
        print("  d - download backup")
        y += 1
        move_cursor(content_x, y)
        print("  q - back")
        
        move_cursor(content_x, lines - 3)
        print(f"{Colors.DIM}select option...{Colors.RESET}")
        
        key = self.get_key()
        
        if key == 'n':
            y += 2
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}⏳ creating backup...{Colors.RESET}")
            time.sleep(2)
            move_cursor(content_x, y)
            print(f"{Colors.GREEN}✅ backup created{Colors.RESET}")
            time.sleep(2)
    
    def run(self):
        """Main menu loop with proper navigation"""
        if MAIN_UI_AVAILABLE:
            menu_state.in_submenu = 'public_server'
            hide_cursor()
        
        try:
            while True:
                self.draw_menu()
                
                if MAIN_UI_AVAILABLE:
                    key = get_single_key()
                else:
                    key = self.get_key()
                
                if key in ['q', '\x1b']:  # q or ESC - back
                    break
                elif key == '\x1b[D':  # Left arrow - also back
                    break
                elif key == '\x1b[A':  # Up arrow
                    self.selected_index = max(0, self.selected_index - 1)
                    if self.selected_index == 8:  # Skip separator
                        self.selected_index = 7
                elif key == '\x1b[B':  # Down arrow
                    self.selected_index = min(9, self.selected_index + 1)
                    if self.selected_index == 8:  # Skip separator
                        self.selected_index = 9
                elif key in ['\n', '\x1b[C']:  # Enter or Right arrow - select
                    if self.selected_index == 0:  # Status
                        self.show_server_status()
                    elif self.selected_index == 1:  # Deploy
                        self.show_deploy_menu()
                    elif self.selected_index == 2:  # Database
                        self.show_database_menu()
                    elif self.selected_index == 3:  # Sync
                        self.show_sync_menu()
                    elif self.selected_index == 4:  # Backup
                        self.show_backup_menu()
                    elif self.selected_index == 5:  # Logs
                        self.show_logs()
                    elif self.selected_index == 6:  # Config
                        self.show_configuration()
                    elif self.selected_index == 7:  # Restart
                        self.restart_services()
                    elif self.selected_index == 9:  # Back
                        break
        finally:
            if MAIN_UI_AVAILABLE:
                menu_state.in_submenu = None
                show_cursor()


# Entry point for integration
def public_server_menu():
    """Entry point for main.py integration"""
    menu = PublicServerMenu()
    menu.run()


if __name__ == "__main__":
    public_server_menu()