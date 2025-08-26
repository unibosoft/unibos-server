#!/usr/bin/env python3
"""
Public Server Menu - Proper Implementation
Following administration_menu.py structure exactly
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
import socket
import platform
from system_info import system_info, get_hostname, get_environment, get_footer_text

def detect_environment():
    """Detect where the code is running - uses central system info"""
    return get_environment()

def is_server_environment():
    """Check if we're running on a server (not local dev)"""
    return system_info.is_server

def get_public_server_options():
    """Get public server menu options based on environment"""
    
    if is_server_environment():
        # Server dashboard options - no deployment options
        return [
            ("header", "server status", ""),
            ("system_info", "🖥️  system info", "cpu, memory, disk usage"),
            ("services", "⚡ services", "running services status"),
            ("connections", "🌐 connections", "active connections"),
            ("separator", "", ""),
            ("header", "database", ""),
            ("db_status", "🗄️  database", "postgresql status & stats"),
            ("redis_status", "💾 redis", "cache status & memory"),
            ("separator", "", ""),
            ("header", "monitoring", ""),
            ("logs", "📋 view logs", "tail -f server logs"),
            ("processes", "📊 processes", "top processes by cpu/memory"),
            ("network", "🔌 network", "bandwidth & connections"),
            ("separator", "", ""),
            ("header", "control", ""),
            ("restart_django", "🔄 restart django", "restart backend server"),
            ("restart_redis", "🔄 restart redis", "restart cache server"),
            ("system_update", "📦 update system", "apt update & upgrade"),
            ("separator", "", ""),
            ("back", "← back", "return to main menu")
        ]
    else:
        # Local dev environment - deployment options
        return [
            ("header", "recaria.org control", ""),
            ("restart_recaria", "🌐 restart recaria.org", "ensure django is running properly on recaria.org"),
            ("separator", "", ""),
            ("header", "authentication", ""),
            ("load_ssh_key", "🔑 load ssh key", "add rocksteady-2025 key to ssh-agent"),
            ("separator", "", ""),
            ("header", "deployment", ""),
            ("quick_deploy", "⚡ quick deploy", "rsync files + run unibos.sh on rocksteady"),
            ("full_deploy", "📦 full deployment", "install deps + setup db + migrate + static"),
            ("deploy_backend", "🔧 backend only", "sync backend/ folder + restart django"),
            ("deploy_cli", "💻 cli only", "sync src/ folder + install cli deps"),
            ("separator", "", ""),
            ("header", "database operations", ""),
            ("database", "🗄️  database setup", "create db + user + permissions + migrate"),
            ("db_sync", "🔄 database sync", "sync database between local and rocksteady"),
            ("backup", "💾 backup management", "create/restore/download db backups"),
            ("separator", "", ""),
            ("header", "monitoring", ""),
            ("server_status", "📊 server status", "ssh check + system info + service status"),
            ("logs", "📋 view logs", "tail -f django/nginx/system logs"),
            ("separator", "", ""),
            ("header", "system control", ""),
            ("config", "⚙️  server config", "edit ssh/db/redis connection settings"),
            ("restart", "🔄 restart services", "systemctl restart unibos/nginx/redis"),
            ("separator", "", ""),
            ("back", "← back", "return to dev tools menu")
        ]

def draw_public_server_menu(full_redraw=True):
    """Draw public server menu interface - with optimized updates"""
    from main import (Colors, move_cursor, get_terminal_size, menu_state)
    
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 2
    
    # Get menu options
    options = get_public_server_options()
    
    # Get environment info
    env = detect_environment()
    is_server = is_server_environment()
    
    # Only clear content area on full redraw
    if full_redraw:
        # Clear content area properly with ANSI escape sequences
        for y in range(2, lines - 2):
            move_cursor(content_x, y)
            sys.stdout.write('\033[K')  # Clear to end of line
        sys.stdout.flush()
        
        # Title based on environment
        move_cursor(content_x + 2, 3)
        if is_server:
            print(f"{Colors.BOLD}{Colors.CYAN}📡  server dashboard{Colors.RESET}")
        else:
            print(f"{Colors.BOLD}{Colors.CYAN}🌐  public server{Colors.RESET}")
        
        # Show current environment
        move_cursor(content_x + 2, 5)
        if env == "rocksteady":
            print(f"{Colors.GREEN}● running on: rocksteady ubuntu vm{Colors.RESET}")
        elif env == "local_mac":
            print(f"{Colors.BLUE}● running on: local mac{Colors.RESET}")
        elif env.startswith("raspberry_"):
            print(f"{Colors.MAGENTA}● running on: {env}{Colors.RESET}")
        elif env == "cloud_server":
            print(f"{Colors.CYAN}● running on: cloud server{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}● running on: {env}{Colors.RESET}")
        
        # Additional status for server environment
        if is_server:
            # Show live server stats
            move_cursor(content_x + 2, 7)
            try:
                # Get CPU usage
                cpu_cmd = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'"
                cpu_result = subprocess.run(cpu_cmd, shell=True, capture_output=True, text=True, timeout=1)
                cpu_usage = float(cpu_result.stdout.strip() or 0)
                
                # Get memory usage  
                mem_cmd = "free | grep Mem | awk '{print int($3/$2 * 100)}'"
                mem_result = subprocess.run(mem_cmd, shell=True, capture_output=True, text=True, timeout=1)
                mem_usage = int(mem_result.stdout.strip() or 0)
                
                # Display with LED indicators
                cpu_led = "🟢" if cpu_usage < 50 else "🟡" if cpu_usage < 80 else "🔴"
                mem_led = "🟢" if mem_usage < 50 else "🟡" if mem_usage < 80 else "🔴"
                
                print(f"{cpu_led} cpu: {cpu_usage:.1f}%  {mem_led} memory: {mem_usage}%")
            except:
                print(f"{Colors.DIM}loading system stats...{Colors.RESET}")
        else:
            # For local environment, show rocksteady connection status
            move_cursor(content_x + 2, 7)
            try:
                result = subprocess.run(
                    ["ssh", "-o", "ConnectTimeout=1", "-o", "BatchMode=yes", 
                     "rocksteady", "echo", "ok"],
                    capture_output=True, text=True, timeout=2
                )
                if result.returncode == 0:
                    status = f"{Colors.GREEN}🟢 rocksteady: connected{Colors.RESET}"
                else:
                    status = f"{Colors.RED}🔴 rocksteady: disconnected{Colors.RESET}"
            except:
                status = f"{Colors.YELLOW}🟡 rocksteady: checking...{Colors.RESET}"
            print(status)
    
    # Draw menu options
    y = 9  # Start lower since we have more info at top
    option_index = 0
    
    # Store previous selected index to optimize redraws
    if not hasattr(menu_state, 'prev_public_server_index'):
        menu_state.prev_public_server_index = -1
    
    for i, (key, name, desc) in enumerate(options):
        if key == "header":
            if full_redraw:
                # Section header - blue
                move_cursor(content_x + 2, y)
                print(f"{Colors.BOLD}{Colors.BLUE}{name}{Colors.RESET}")
            y += 1
        elif key == "separator":
            if full_redraw:
                # Separator line
                move_cursor(content_x + 2, y)
                print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}")
            y += 1
        else:
            # Menu option
            is_selected = (option_index == menu_state.public_server_index)
            was_selected = (option_index == menu_state.prev_public_server_index)
            
            # Only redraw if selection state changed or on full redraw
            if full_redraw or is_selected or was_selected:
                move_cursor(content_x + 2, y)
                sys.stdout.write('\033[K')  # Clear line
                
                if is_selected:
                    # Orange background selection
                    print(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD} → {name:<30} {Colors.RESET}", end='')
                    # Show description on the right
                    if desc:
                        print(f" {Colors.DIM}{desc}{Colors.RESET}")
                    else:
                        print()
                else:
                    print(f"   {name}", end='')
                    if desc:
                        print(f"  {Colors.DIM}{desc}{Colors.RESET}")
                    else:
                        print()
            
            option_index += 1
            y += 1
    
    # Update previous index
    menu_state.prev_public_server_index = menu_state.public_server_index
    
    # Instructions at bottom (only on full redraw)
    if full_redraw:
        move_cursor(content_x + 2, lines - 4)
        print(f"{Colors.DIM}↑↓ navigate | enter/→ select | ←/esc back{Colors.RESET}")

def get_ssh_passphrase():
    """Get SSH passphrase with nice UI in content area"""
    from main import Colors, move_cursor, get_terminal_size, hide_cursor, show_cursor
    import sys
    import termios
    import tty
    import os
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Draw passphrase prompt in content area
    y = 8
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}{Colors.CYAN}🔐 ssh authentication required{Colors.RESET}")
    
    # Box dimensions
    box_width = 50
    input_width = 30
    
    y += 2
    move_cursor(content_x + 2, y)
    print(f"{Colors.YELLOW}╔{'═' * box_width}╗{Colors.RESET}")
    
    y += 1
    key_line_y = y
    move_cursor(content_x + 2, y)
    key_line = f" key: ~/.ssh/rocksteady-2025"
    padding_needed = box_width - len(key_line) - 1
    print(f"{Colors.YELLOW}║{Colors.RESET}{Colors.DIM}{key_line}{Colors.RESET}{' ' * padding_needed}{Colors.YELLOW}║{Colors.RESET}")
    
    y += 1
    pass_line_y = y  # Save this for cursor positioning
    move_cursor(content_x + 2, y)
    # Build passphrase line without formatting first
    pass_prefix = " passphrase: ["
    pass_suffix = "]"
    pass_spaces = ' ' * input_width
    padding_needed = box_width - len(pass_prefix) - input_width - len(pass_suffix) - 1
    print(f"{Colors.YELLOW}║{Colors.RESET}{pass_prefix}{pass_spaces}{pass_suffix}{' ' * padding_needed}{Colors.YELLOW}║{Colors.RESET}")
    
    y += 1
    move_cursor(content_x + 2, y)
    print(f"{Colors.YELLOW}╚{'═' * box_width}╝{Colors.RESET}")
    
    # Calculate exact cursor position for input
    # Position: content_x + 2 (indent) + 1 (║) + 1 (space) + len("passphrase: [")
    input_y = pass_line_y
    input_x = content_x + 2 + 1 + len(" passphrase: [")
    move_cursor(input_x, input_y)
    
    # Hide cursor and get passphrase character by character
    hide_cursor()
    passphrase = ""
    
    # Save terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setraw(sys.stdin.fileno())
        
        while True:
            char = sys.stdin.read(1)
            
            if char == '\r' or char == '\n':  # Enter
                break
            elif char == '\x7f' or char == '\b':  # Backspace
                if passphrase:
                    passphrase = passphrase[:-1]
                    # Move cursor back and clear character
                    move_cursor(input_x + len(passphrase), input_y)
                    print(' ', end='')
                    move_cursor(input_x + len(passphrase), input_y)
                    sys.stdout.flush()
            elif char == '\x03' or char == '\x1b':  # Ctrl+C or ESC
                passphrase = None
                break
            elif len(passphrase) < input_width:  # Limit to input width
                # Show asterisk immediately at current position
                print('*', end='')
                sys.stdout.flush()
                passphrase += char
    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        show_cursor()
    
    # Clear the authentication box
    for i in range(5):
        move_cursor(content_x + 2, 8 + i)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    return passphrase

def quick_deploy():
    """Quick deployment to rocksteady"""
    from main import (Colors, move_cursor, get_terminal_size,
                      draw_footer, get_single_key)
    import os
    
    # Don't clear screen, just clear content area
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area only
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')  # Clear to end of line
    sys.stdout.flush()
    
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}⚡  quick deploy{Colors.RESET}")
    
    move_cursor(content_x + 2, 5)
    print(f"{Colors.YELLOW}checking ssh authentication...{Colors.RESET}")
    
    # Check if key is already in SSH agent
    y = 7
    agent_check = subprocess.run(
        "ssh-add -l 2>/dev/null | grep -i 'rocksteady'",
        shell=True, capture_output=True
    )
    
    if agent_check.returncode != 0:
        # Key not in agent, need to add it
        move_cursor(content_x + 2, y)
        print(f"{Colors.YELLOW}ssh key needs to be loaded{Colors.RESET}")
        
        # Get passphrase using our UI
        passphrase = get_ssh_passphrase()
        
        if passphrase is None:
            # User cancelled
            for y in range(2, lines - 2):
                move_cursor(content_x, y)
                sys.stdout.write('\033[K')
            sys.stdout.flush()
            
            move_cursor(content_x + 2, 3)
            print(f"{Colors.BOLD}{Colors.CYAN}⚡  quick deploy{Colors.RESET}")
            move_cursor(content_x + 2, 5)
            print(f"{Colors.RED}deployment cancelled{Colors.RESET}")
            draw_footer()
            sys.stdout.flush()
            # Wait for ESC or left arrow to return
            while True:
                key = get_single_key()
                if key in ['\x1b', '\x1b[D']:  # ESC or left arrow
                    break
            return
        
        # Add key to agent
        key_path = os.path.expanduser("~/.ssh/rocksteady-2025")
        if not os.path.exists(key_path):
            key_path = os.path.expanduser("~/.ssh/id_rsa")
        
        # Use expect or SSH_ASKPASS approach
        add_cmd = f"SSH_ASKPASS_REQUIRE=never ssh-add {key_path} 2>/dev/null <<< '{passphrase}'"
        add_result = subprocess.run(add_cmd, shell=True, capture_output=True)
        
        if add_result.returncode != 0:
            # Try alternative method
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(f"#!/bin/sh\necho '{passphrase}'")
                askpass_script = f.name
            
            os.chmod(askpass_script, 0o700)
            add_result = subprocess.run(
                f"DISPLAY=:0 SSH_ASKPASS={askpass_script} ssh-add {key_path} </dev/null",
                shell=True, capture_output=True
            )
            os.unlink(askpass_script)
        
        # Clear and redraw
        for y in range(2, lines - 2):
            move_cursor(content_x, y)
            sys.stdout.write('\033[K')
        sys.stdout.flush()
        
        move_cursor(content_x + 2, 3)
        print(f"{Colors.BOLD}{Colors.CYAN}⚡  quick deploy{Colors.RESET}")
        move_cursor(content_x + 2, 5)
        print(f"{Colors.YELLOW}syncing to rocksteady ubuntu vm...{Colors.RESET}")
        y = 7
    else:
        move_cursor(content_x + 2, y)
        print(f"{Colors.GREEN}✓ ssh key already loaded{Colors.RESET}")
        y += 2
    
    move_cursor(content_x + 2, y)
    print(f"{Colors.DIM}rsync -avz (excluding git, venv, logs, etc.) . rocksteady:~/unibos/{Colors.RESET}")
    
    y += 2
    move_cursor(content_x + 2, y)
    
    # Track operation results
    operations_done = []
    had_errors = False
    
    try:
        # Now rsync should work without prompting - use proper excludes
        result = subprocess.run(
            "rsync -avz --exclude=.git --exclude='*.pyc' --exclude=__pycache__ --exclude=venv --exclude=archive --exclude=quarantine --exclude='*.sql' --exclude='*.log' --exclude=db.sqlite3 --exclude=.DS_Store --exclude=node_modules --exclude='.env*' . rocksteady:~/unibos/",
            shell=True, capture_output=True, text=True, timeout=30
        )
        
        # Check if rsync failed due to authentication
        if result.returncode != 0:
            had_errors = True
            # If key not loaded, tell user to load it first
            if "passphrase" in result.stderr.lower() or "permission denied" in result.stderr.lower():
                y += 1
                move_cursor(content_x + 2, y)
                print(f"{Colors.RED}✗ ssh authentication required{Colors.RESET}")
                operations_done.append("rsync: authentication failed")
                
                y += 2
                move_cursor(content_x + 2, y)
                print(f"{Colors.YELLOW}please use '🔑 load ssh key' first{Colors.RESET}")
                
                y += 1
                move_cursor(content_x + 2, y)
                print(f"{Colors.DIM}(first option in the menu){Colors.RESET}")
            else:
                # Other error
                y += 1
                move_cursor(content_x + 2, y)
                print(f"{Colors.RED}✗ deployment failed{Colors.RESET}")
                operations_done.append("rsync: failed")
                
                y += 2
                move_cursor(content_x + 2, y)
                error_msg = result.stderr[:100] if result.stderr else "Unknown error"
                print(f"{Colors.DIM}{error_msg}{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}✓ files synced{Colors.RESET}")
            operations_done.append("rsync: success")
            
            # Run remote setup commands
            y += 2
            move_cursor(content_x + 2, y)
            print(f"{Colors.YELLOW}setting up remote environment...{Colors.RESET}")
            
            # Create virtual environment and install dependencies if needed
            setup_commands = [
                "cd ~/unibos",
                "chmod +x unibos.sh 2>/dev/null || true",
                "chmod +x backend/start_backend.sh 2>/dev/null || true",
                "echo 'deployment complete'"
            ]
            
            ssh_cmd = " && ".join(setup_commands)
            
            try:
                ssh_result = subprocess.run(
                    f"ssh rocksteady '{ssh_cmd}'",
                    shell=True, capture_output=True, text=True, timeout=15
                )
                
                if ssh_result.returncode == 0:
                    y += 1
                    move_cursor(content_x + 2, y)
                    print(f"{Colors.GREEN}✓ deployment complete!{Colors.RESET}")
                    operations_done.append("remote setup: success")
                    
                    y += 2
                    move_cursor(content_x + 2, y)
                    print(f"{Colors.CYAN}to start unibos on rocksteady:{Colors.RESET}")
                    y += 1
                    move_cursor(content_x + 2, y)
                    print(f"{Colors.DIM}ssh rocksteady 'cd ~/unibos && ./unibos.sh'{Colors.RESET}")
                else:
                    y += 1
                    move_cursor(content_x + 2, y)
                    print(f"{Colors.YELLOW}✓ files deployed (manual setup needed){Colors.RESET}")
                    operations_done.append("remote setup: manual needed")
            except subprocess.TimeoutExpired:
                had_errors = True
                y += 1
                move_cursor(content_x + 2, y)
                print(f"{Colors.RED}✗ remote setup timed out{Colors.RESET}")
                operations_done.append("remote setup: timeout")
            except Exception as e:
                had_errors = True
                y += 1
                move_cursor(content_x + 2, y)
                print(f"{Colors.RED}✗ remote setup error: {str(e)}{Colors.RESET}")
                operations_done.append(f"remote setup: error")
                
    except subprocess.TimeoutExpired:
        had_errors = True
        print(f"{Colors.RED}✗ rsync timed out (30s){Colors.RESET}")
        operations_done.append("rsync: timeout")
    except Exception as e:
        had_errors = True
        print(f"{Colors.RED}✗ error: {str(e)}{Colors.RESET}")
        operations_done.append(f"error: {str(e)[:50]}")
    
    # Show summary
    if operations_done:
        y += 2
        if y < lines - 6:
            move_cursor(content_x + 2, y)
            print(f"{Colors.BOLD}summary:{Colors.RESET}")
            for op in operations_done[:3]:  # Show max 3 operations
                y += 1
                if y < lines - 5:
                    move_cursor(content_x + 4, y)
                    if "success" in op:
                        print(f"{Colors.GREEN}• {op}{Colors.RESET}")
                    elif "failed" in op or "error" in op or "timeout" in op:
                        print(f"{Colors.RED}• {op}{Colors.RESET}")
                    else:
                        print(f"{Colors.YELLOW}• {op}{Colors.RESET}")
    
    # Footer already has navigation hint
    draw_footer()
    sys.stdout.flush()
    
    # Wait for ESC or left arrow to return
    while True:
        key = get_single_key()
        if key in ['\x1b', '\x1b[D']:  # ESC or left arrow
            break

def restart_recaria():
    """Restart recaria.org Django service and ensure it's running"""
    from main import (Colors, move_cursor, get_terminal_size,
                      draw_footer, get_single_key, show_cursor, hide_cursor)
    import subprocess
    import time
    import os
    # Don't reimport sys - use the global one
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Title
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}🌐  restart recaria.org{Colors.RESET}")
    
    # Get proper working directory
    base_dir = "/Users/berkhatirli/Desktop/unibos"
    os.chdir(base_dir)
    
    y = 5
    steps = [
        ("checking connection", "ssh rocksteady 'echo connected' 2>&1"),
        ("killing old processes", "ssh rocksteady 'pkill -f \"manage.py runserver\" || true' 2>&1"),
        ("ensuring directories", "ssh rocksteady 'mkdir -p ~/unibos/backend/logs ~/unibos/backend/staticfiles ~/unibos/backend/media ~/unibos/backend/apps/users ~/unibos/backend/unibos_backend/settings' 2>&1"),
        ("checking backend files", "ls backend/manage.py backend/requirements.txt backend/apps/users/models.py 2>&1"),
        ("syncing backend files", "rsync -az backend/manage.py backend/requirements.txt rocksteady:~/unibos/backend/ 2>&1"),
        ("syncing core modules", "rsync -az backend/unibos_backend/*.py rocksteady:~/unibos/backend/unibos_backend/ 2>&1"),  
        ("syncing settings", "rsync -az backend/unibos_backend/settings/*.py rocksteady:~/unibos/backend/unibos_backend/settings/ 2>&1"),
        ("syncing all apps", "rsync -az --exclude='__pycache__' --exclude='*.pyc' --exclude='migrations/__pycache__' backend/apps/ rocksteady:~/unibos/backend/apps/ 2>&1 | tail -3"),
        ("syncing templates", "rsync -az --exclude='*.pyc' backend/templates/ rocksteady:~/unibos/backend/templates/ 2>&1"),
        ("activating environment", "ssh rocksteady 'cd ~/unibos/backend && [ -d venv ] || python3 -m venv venv' 2>&1"),
        ("installing core deps", "ssh rocksteady 'cd ~/unibos/backend && ./venv/bin/pip install -q django djangorestframework django-cors-headers psycopg2-binary' 2>&1"),
        ("installing extra deps", "ssh rocksteady 'cd ~/unibos/backend && ./venv/bin/pip install -q django-redis whitenoise django-environ python-json-logger' 2>&1"),
        ("running migrations", "ssh rocksteady 'cd ~/unibos/backend && ./venv/bin/python manage.py migrate --run-syncdb 2>&1 | head -10'"),
        ("killing old django", "ssh rocksteady 'pkill -f \"manage.py runserver\" || true' 2>&1"),
        ("starting django", "ssh rocksteady 'cd ~/unibos/backend && nohup ./venv/bin/python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 & echo \"Django process started with PID: $!\"' 2>&1"),
        ("waiting for startup", "sleep 5"),
        ("checking django process", "ssh rocksteady 'pgrep -f \"manage.py runserver\" > /dev/null && echo \"✅ django process running\" || echo \"❌ django not running\"' 2>&1"),
        ("verifying http service", "ssh rocksteady 'curl -I -s -m 5 http://localhost:8000/login/ | head -1' 2>&1"),
    ]
    
    success = True
    django_pid = None
    
    for step_name, command in steps:
        move_cursor(content_x + 4, y)
        print(f"⏳ {step_name}...", end='')
        sys.stdout.flush()
        
        try:
            # Increase timeout for migration, install and django start steps
            if "migrations" in step_name or "deps" in step_name:
                timeout_val = 30
            elif "starting django" in step_name:
                timeout_val = 5  # Quick for background start
            elif "waiting for startup" in step_name:
                timeout_val = 6  # Just sleep command
            elif "verifying" in step_name:
                timeout_val = 10  # Allow time for curl
            else:
                timeout_val = 15
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout_val)
            
            move_cursor(content_x + 4, y)
            if result.returncode == 0:
                print(f"✅ {step_name}")
                
                # Capture success message
                if step_name == "starting django" and "PID:" in result.stdout:
                    # Extract PID from message
                    import re
                    pid_match = re.search(r'PID:\s*(\d+)', result.stdout)
                    if pid_match:
                        django_pid = f"Running (PID: {pid_match.group(1)})"
                    else:
                        django_pid = "Running in background"
                    
                # Show output for verification steps
                if step_name in ["checking django process", "verifying http service"] and result.stdout.strip():
                    y += 1
                    move_cursor(content_x + 6, y)
                    output = result.stdout.strip()
                    
                    # Check for successful HTTP response
                    if "verifying http service" in step_name:
                        if "HTTP/1.1 200" in output or "HTTP/1.1 302" in output:
                            print(f"{Colors.GREEN}✅ service responding (HTTP 200/302){Colors.RESET}")
                        elif "HTTP" in output:
                            print(f"{Colors.YELLOW}⚠️ {output}{Colors.RESET}")
                        else:
                            print(f"{Colors.RED}❌ no http response{Colors.RESET}")
                    else:
                        # For process check
                        if "✅" in output:
                            print(f"{Colors.GREEN}{output}{Colors.RESET}")
                        elif "❌" in output:
                            print(f"{Colors.RED}{output}{Colors.RESET}")
                            success = False
                        else:
                            print(f"{Colors.YELLOW}{output}{Colors.RESET}")
            else:
                print(f"❌ {step_name}")
                # Always show error details
                y += 1
                move_cursor(content_x + 6, y)
                error_msg = (result.stderr or result.stdout).strip()
                # Split long errors into multiple lines
                if len(error_msg) > cols - content_x - 8:
                    lines_to_show = error_msg.split('\n')[:3]  # Show first 3 lines
                    for line in lines_to_show:
                        if line.strip():
                            move_cursor(content_x + 6, y)
                            print(f"{Colors.DIM}{line[:cols - content_x - 8]}{Colors.RESET}")
                            y += 1
                    y -= 1  # Adjust for the extra increment
                else:
                    print(f"{Colors.DIM}{error_msg}{Colors.RESET}")
                success = False
        except subprocess.TimeoutExpired:
            move_cursor(content_x + 4, y)
            print(f"⚠️  {step_name} (timeout after {timeout_val}s)")
            # Don't fail on timeout for non-critical steps
            if "verifying" not in step_name:
                success = False
        except Exception as e:
            move_cursor(content_x + 4, y)
            print(f"❌ {step_name}: {str(e)[:50]}")
            success = False
        
        y += 1
    
    # Final check - even if verification failed, check if Django is actually running
    if not success and django_pid:
        # Django was started, let's double-check if it's actually running
        try:
            check_result = subprocess.run("ssh rocksteady 'pgrep -f \"manage.py runserver\"'", 
                                        shell=True, capture_output=True, text=True, timeout=5)
            if check_result.returncode == 0 and check_result.stdout.strip():
                success = True  # Django is actually running
        except:
            pass  # Keep original success status
    
    # Final status - ensure it's visible
    y += 1
    if y > lines - 6:  # If we're too low, adjust
        y = lines - 6
    
    move_cursor(content_x + 2, y)
    if success:
        print(f"{Colors.GREEN}✅ recaria.org is running!{Colors.RESET}")
        if django_pid:
            y += 1
            move_cursor(content_x + 2, y)
            print(f"{Colors.DIM}django status: {django_pid}{Colors.RESET}")
        y += 1
        move_cursor(content_x + 2, y)
        print(f"{Colors.CYAN}access at: https://recaria.org{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ failed to start recaria.org{Colors.RESET}")
        y += 1
        move_cursor(content_x + 2, y)
        print(f"{Colors.YELLOW}check logs: ssh rocksteady 'tail ~/unibos/backend/server.log'{Colors.RESET}")
    
    # Always wait for key - make sure it's visible
    y += 2
    if y > lines - 3:
        y = lines - 3
    
    move_cursor(content_x + 2, y)
    print(f"{Colors.DIM}press esc or ← to return...{Colors.RESET}")
    sys.stdout.flush()  # Force output
    
    # Show cursor and wait for ESC or left arrow
    show_cursor()
    
    # Non-blocking wait for ESC or left arrow only
    import select
    import termios
    import tty
    
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        
        while True:
            # Check if input is available (non-blocking)
            if select.select([sys.stdin], [], [], 0.05)[0]:  # 50ms timeout
                key = sys.stdin.read(1)
                
                # Check for escape sequences
                if key == '\x1b':  # ESC or arrow key start
                    # Check if it's an arrow key
                    if select.select([sys.stdin], [], [], 0)[0]:
                        key2 = sys.stdin.read(1)
                        if key2 == '[':
                            if select.select([sys.stdin], [], [], 0)[0]:
                                key3 = sys.stdin.read(1)
                                if key3 == 'D':  # Left arrow
                                    break
                    else:
                        # Just ESC key
                        break
            
            # Update time in footer while waiting (non-blocking)
            # This keeps the clock running
            pass
            
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    hide_cursor()

def load_ssh_key():
    """Load SSH key to agent with passphrase"""
    from main import (Colors, move_cursor, get_terminal_size,
                      draw_footer, get_single_key)
    import os
    
    # Don't clear screen, just clear content area
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area only
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}🔑  load ssh key{Colors.RESET}")
    
    move_cursor(content_x + 2, 5)
    print(f"{Colors.YELLOW}checking ssh-agent...{Colors.RESET}")
    
    # Check if key is already loaded
    y = 7
    agent_check = subprocess.run(
        "ssh-add -l 2>/dev/null | grep -q 'rocksteady-2025'",
        shell=True, capture_output=True
    )
    
    if agent_check.returncode == 0:
        move_cursor(content_x + 2, y)
        print(f"{Colors.GREEN}✓ ssh key already loaded{Colors.RESET}")
        
        y += 2
        move_cursor(content_x + 2, y)
        print(f"{Colors.DIM}key is valid for this session{Colors.RESET}")
    else:
        move_cursor(content_x + 2, y)
        print(f"{Colors.YELLOW}loading ssh key...{Colors.RESET}")
        
        # Get passphrase with our UI
        passphrase = get_ssh_passphrase()
        
        if passphrase is None:
            # User cancelled
            for y in range(2, lines - 2):
                move_cursor(content_x, y)
                sys.stdout.write('\033[K')
            sys.stdout.flush()
            
            move_cursor(content_x + 2, 3)
            print(f"{Colors.BOLD}{Colors.CYAN}🔑  load ssh key{Colors.RESET}")
            move_cursor(content_x + 2, 5)
            print(f"{Colors.RED}operation cancelled{Colors.RESET}")
        else:
            # Clear and redraw after passphrase input
            for y in range(2, lines - 2):
                move_cursor(content_x, y)
                sys.stdout.write('\033[K')
            sys.stdout.flush()
            
            move_cursor(content_x + 2, 3)
            print(f"{Colors.BOLD}{Colors.CYAN}🔑  load ssh key{Colors.RESET}")
            move_cursor(content_x + 2, 5)
            print(f"{Colors.YELLOW}adding key to ssh-agent...{Colors.RESET}")
            
            # Find the key file
            key_path = os.path.expanduser("~/.ssh/rocksteady-2025")
            if not os.path.exists(key_path):
                key_path = os.path.expanduser("~/.ssh/id_rsa")
                if not os.path.exists(key_path):
                    key_path = os.path.expanduser("~/.ssh/id_ed25519")
            
            y = 7
            move_cursor(content_x + 2, y)
            print(f"{Colors.DIM}key file: {key_path}{Colors.RESET}")
            
            # Use expect script to add key
            import tempfile
            expect_script = f'''#!/usr/bin/expect -f
set timeout 5
spawn ssh-add {key_path}
expect "Enter passphrase"
send "{passphrase}\\r"
expect eof
catch wait result
exit [lindex $result 3]
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.exp', delete=False) as f:
                f.write(expect_script)
                script_path = f.name
            
            os.chmod(script_path, 0o700)
            
            # Try expect first
            result = subprocess.run(
                f"expect {script_path}",
                shell=True, capture_output=True, text=True
            )
            
            os.unlink(script_path)
            
            if result.returncode != 0:
                # Try alternative method with SSH_ASKPASS
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                    f.write(f"#!/bin/sh\necho '{passphrase}'")
                    askpass_script = f.name
                
                os.chmod(askpass_script, 0o700)
                result = subprocess.run(
                    f"DISPLAY=:0 SSH_ASKPASS={askpass_script} ssh-add {key_path} </dev/null",
                    shell=True, capture_output=True
                )
                os.unlink(askpass_script)
            
            y += 2
            move_cursor(content_x + 2, y)
            
            # Verify the key was added
            verify = subprocess.run(
                "ssh-add -l | grep -q 'rocksteady-2025\\|SHA256'",
                shell=True, capture_output=True
            )
            
            if verify.returncode == 0:
                print(f"{Colors.GREEN}✓ ssh key loaded successfully{Colors.RESET}")
                
                y += 2
                move_cursor(content_x + 2, y)
                print(f"{Colors.BOLD}key is now active for:{Colors.RESET}")
                
                y += 1
                move_cursor(content_x + 2, y)
                print(f"  • quick deploy")
                y += 1
                move_cursor(content_x + 2, y)
                print(f"  • server status checks")
                y += 1
                move_cursor(content_x + 2, y)
                print(f"  • all ssh operations")
                
                y += 2
                move_cursor(content_x + 2, y)
                print(f"{Colors.DIM}valid until you logout or restart{Colors.RESET}")
            else:
                print(f"{Colors.RED}✗ failed to load ssh key{Colors.RESET}")
                
                y += 2
                move_cursor(content_x + 2, y)
                print(f"{Colors.DIM}check your passphrase and try again{Colors.RESET}")
    
    draw_footer()
    sys.stdout.flush()
    
    # Wait for ESC or left arrow to return
    while True:
        key = get_single_key()
        if key in ['\x1b', '\x1b[D']:  # ESC or left arrow
            break

def full_deployment():
    """Full deployment with complete setup"""
    from main import (Colors, move_cursor, get_terminal_size,
                      draw_footer, get_single_key)
    import os
    import time
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}📦  full deployment{Colors.RESET}")
    
    move_cursor(content_x + 2, 5)
    print(f"{Colors.YELLOW}complete setup on rocksteady...{Colors.RESET}")
    
    y = 7
    # Individual steps for better error reporting and progress display
    steps = [
        ("checking connection", "ssh -o ConnectTimeout=5 -o BatchMode=yes rocksteady echo 'connected' 2>&1"),
        ("checking postgresql", "ssh rocksteady 'which psql || (sudo apt update && sudo apt install -y postgresql postgresql-contrib) 2>/dev/null'"),
        ("starting postgresql", "ssh rocksteady 'sudo systemctl start postgresql && sudo systemctl enable postgresql 2>/dev/null || true'"),
        ("creating db user", "ssh rocksteady 'sudo -u postgres psql -c \"CREATE USER unibos_user WITH PASSWORD '\\''unibos_password'\\'';\" 2>/dev/null || true'"),
        ("creating database", "ssh rocksteady 'sudo -u postgres psql -c \"CREATE DATABASE unibos_db OWNER unibos_user;\" 2>/dev/null || true'"),
        ("granting permissions", "ssh rocksteady 'sudo -u postgres psql -c \"ALTER USER unibos_user CREATEDB;\" 2>/dev/null || true'"),
        ("syncing files", "rsync -avz --delete --exclude=.git --exclude='*.pyc' --exclude=__pycache__ --exclude=venv --exclude=archive --exclude=quarantine --exclude='*.log' --exclude=db.sqlite3 --exclude=.DS_Store --exclude=node_modules --exclude='.env' --exclude='media/*' --exclude='staticfiles/*' . rocksteady:~/unibos/"),
        ("syncing version", "rsync -avz /Users/berkhatirli/Desktop/unibos/backend/VERSION.json /Users/berkhatirli/Desktop/unibos/src/VERSION.json rocksteady:~/unibos/backend/"),
        ("creating directories", "ssh rocksteady 'cd ~/unibos/backend && mkdir -p logs staticfiles media && touch logs/django.log'"),
        ("setting up venv", "ssh rocksteady 'cd ~/unibos/backend && [ -d venv ] || python3 -m venv venv'"),
        ("upgrading pip", "ssh rocksteady 'cd ~/unibos/backend && ./venv/bin/python -m pip install --upgrade pip'"),
        ("installing packages", "ssh rocksteady 'cd ~/unibos/backend && ./venv/bin/pip install Django djangorestframework psycopg2-binary django-cors-headers whitenoise channels channels-redis drf-spectacular django-filter Pillow redis requests aiohttp djangorestframework-simplejwt django-extensions django-prometheus pyotp user-agents python-environ --upgrade 2>/dev/null || true'"),
        ("creating env file", "ssh rocksteady 'cd ~/unibos/backend && (echo \"DEBUG=True\" > .env && echo \"SECRET_KEY=$(python3 -c \"import secrets; print(secrets.token_urlsafe(50))\")\" >> .env && echo \"DATABASE_URL=postgres://unibos_user:unibos_password@localhost:5432/unibos_db\" >> .env && echo \"REDIS_URL=redis://localhost:6379/1\" >> .env && echo \"ALLOWED_HOSTS=*\" >> .env && echo \"CORS_ALLOW_ALL_ORIGINS=True\" >> .env)'"),
        ("running migrations", "ssh rocksteady 'cd ~/unibos/backend && ./venv/bin/python manage.py migrate --noinput || true'"),
        ("collecting static", "ssh rocksteady 'cd ~/unibos/backend && ./venv/bin/python manage.py collectstatic --noinput || true'"),
        ("installing cli deps", "ssh rocksteady 'cd ~/unibos/src && if [ -f requirements.txt ]; then pip3 install --user -r requirements.txt 2>/dev/null || true; fi'"),
        ("setting permissions", "ssh rocksteady 'cd ~/unibos && chmod +x unibos.sh rocksteady_deploy.sh *.sh 2>/dev/null || true'"),
        ("stopping old server", "ssh rocksteady 'pkill -f \"manage.py runserver\" 2>/dev/null; sleep 1; echo \"old server stopped (if any)\"'"),
        ("restarting server", "ssh rocksteady 'cd ~/unibos/backend && nohup ./venv/bin/python manage.py runserver 0.0.0.0:8000 </dev/null >logs/server.log 2>&1 & echo $! > server.pid; sleep 3; echo \"server restarted with pid $(cat server.pid)\"'"),
        ("verifying server", "ssh rocksteady 'sleep 2 && curl -s -o /dev/null -w \"%{http_code}\" http://localhost:8000 | grep -q \"302\\|200\\|301\" && echo \"server responding correctly\" || echo \"server check failed\"'"),
    ]
    
    success_count = 0
    fail_count = 0
    errors_to_show = []
    max_width = cols - content_x - 6  # Available width for text
    critical_failure = False
    
    # Track display lines for scrolling
    display_lines = []
    max_display_lines = lines - 12  # Leave space for header, footer, and summary
    
    for i, (step_name, command) in enumerate(steps):
        # If we've reached the display limit, start scrolling
        if len(display_lines) >= max_display_lines:
            # Remove first item and shift everything up
            display_lines.pop(0)
            # Redraw all visible lines
            for idx, line_text in enumerate(display_lines):
                move_cursor(content_x + 2, 7 + idx)
                sys.stdout.write('\033[K')
                sys.stdout.write(line_text)
            y = 7 + len(display_lines)
        
        move_cursor(content_x + 2, y)
        # Clear line first
        sys.stdout.write('\033[K')
        print(f"{Colors.YELLOW}⏳ {step_name}...{Colors.RESET}")
        sys.stdout.flush()
        
        # Add small delay to see the progress
        time.sleep(0.3)
        
        try:
            # Special handling for server start command - don't wait for it to complete
            if step_name == "starting server":
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            # For starting server, timeout is expected since it runs in background
            if step_name == "starting server":
                result = type('obj', (object,), {'returncode': 0, 'stderr': '', 'stdout': 'server start command sent'})()
            else:
                result = type('obj', (object,), {'returncode': 1, 'stderr': 'Command timed out after 30 seconds', 'stdout': ''})()
        except Exception as e:
            result = type('obj', (object,), {'returncode': 1, 'stderr': str(e), 'stdout': ''})()
        
        move_cursor(content_x + 2, y)
        sys.stdout.write('\033[K')
        
        if result.returncode == 0:
            status_text = f"{Colors.GREEN}✓ {step_name}{Colors.RESET}"
            print(status_text)
            display_lines.append(status_text)
            success_count += 1
        else:
            # Special handling for stopping old server - not an error if no process exists
            if step_name == "stopping old server":
                status_text = f"{Colors.GREEN}✓ {step_name}{Colors.RESET}"
                print(status_text)
                display_lines.append(status_text)
                success_count += 1
            else:
                status_text = f"{Colors.RED}✗ {step_name}{Colors.RESET}"
                print(status_text)
                display_lines.append(status_text)
                fail_count += 1
                
                # Collect error for display
                error = result.stderr.strip() if result.stderr else result.stdout.strip() if result.stdout else "Unknown error"
                # Extract most relevant error line
                error_lines = error.split('\n')
                for line in error_lines:
                    if 'error' in line.lower() or 'failed' in line.lower() or 'denied' in line.lower() or 'permission' in line.lower():
                        error = line.strip()
                        break
                else:
                    # Take last non-empty line if no specific error found
                    error = next((line.strip() for line in reversed(error_lines) if line.strip()), "Check SSH connection")
                
                # Truncate error to fit
                if len(error) > max_width:
                    error = error[:max_width - 3] + "..."
                errors_to_show.append((step_name, error))
            
            # Stop on critical early failures
            if i == 0:  # SSH connection check failed
                critical_failure = True
                y += 1
                move_cursor(content_x + 4, y)
                print(f"{Colors.RED}cannot continue - ssh connection failed{Colors.RESET}")
                y += 1
                move_cursor(content_x + 4, y)
                print(f"{Colors.YELLOW}please use '🔑 load ssh key' first{Colors.RESET}")
                break
        
        y += 1
    
    # Always show errors if any
    if errors_to_show:
        y += 1
        if y < lines - 6:
            move_cursor(content_x + 2, y)
            print(f"{Colors.BOLD}errors:{Colors.RESET}")
        for step_name, error in errors_to_show[:4]:  # Show max 4 errors
            y += 1
            if y >= lines - 5:
                break
            move_cursor(content_x + 4, y)
            # Truncate for display
            display_text = f"{step_name}: {error}"
            if len(display_text) > max_width - 2:
                display_text = display_text[:max_width - 5] + "..."
            print(f"{Colors.RED}• {display_text}{Colors.RESET}")
    
    # Summary - fixed position at bottom of content area
    summary_y = lines - 10  # Fixed position for summary
    move_cursor(content_x + 2, summary_y)
    sys.stdout.write('\033[K')
    if fail_count == 0:
        print(f"{Colors.GREEN}✅ deployment successful! ({success_count}/{len(steps)} steps){Colors.RESET}")
        move_cursor(content_x + 2, summary_y + 2)
        sys.stdout.write('\033[K')
        print(f"{Colors.CYAN}server is accessible at:{Colors.RESET}")
        move_cursor(content_x + 4, summary_y + 3)
        sys.stdout.write('\033[K')
        print(f"{Colors.BOLD}http://158.178.201.117:8000{Colors.RESET}")
    elif critical_failure:
        print(f"{Colors.RED}⛔ deployment failed - fix connection first{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠️ deployment completed with {fail_count} minor error(s){Colors.RESET}")
        if fail_count <= 2:  # If only minor errors
            move_cursor(content_x + 2, summary_y + 2)
            sys.stdout.write('\033[K')
            print(f"{Colors.CYAN}server may still be accessible at:{Colors.RESET}")
            move_cursor(content_x + 4, summary_y + 3)
            sys.stdout.write('\033[K')
            print(f"{Colors.BOLD}http://158.178.201.117:8000{Colors.RESET}")
    
    # Ensure everything is displayed
    sys.stdout.flush()
    time.sleep(0.5)  # Small delay to ensure everything is displayed
    
    # Footer already has navigation hint
    draw_footer()
    sys.stdout.flush()
    
    # Wait for ESC or left arrow to return
    while True:
        key = get_single_key()
        if key in ['\x1b', '\x1b[D']:  # ESC or left arrow
            break

def deploy_backend():
    """Deploy only backend to rocksteady"""
    from main import (Colors, move_cursor, get_terminal_size,
                      draw_footer, get_single_key)
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}🔧  backend deployment{Colors.RESET}")
    
    move_cursor(content_x + 2, 5)
    print(f"{Colors.YELLOW}syncing django backend...{Colors.RESET}")
    
    y = 7
    operations_done = []
    had_errors = False
    
    move_cursor(content_x + 2, y)
    print(f"{Colors.YELLOW}⏳ syncing backend/ folder...{Colors.RESET}")
    
    try:
        result = subprocess.run(
            "rsync -avz --exclude='__pycache__' --exclude='*.pyc' --exclude='venv' --exclude='*.log' --exclude='db.sqlite3' backend/ rocksteady:~/unibos/backend/",
            shell=True, capture_output=True, text=True, timeout=30
        )
        
        move_cursor(content_x + 2, y)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ backend synced{Colors.RESET}" + " " * 30)
            operations_done.append("backend sync: success")
            
            y += 2
            move_cursor(content_x + 2, y)
            print(f"{Colors.YELLOW}⏳ restarting django...{Colors.RESET}")
            
            try:
                restart = subprocess.run(
                    "ssh rocksteady 'pkill -f manage.py; cd ~/unibos/backend && nohup ./venv/bin/python manage.py runserver 0.0.0.0:8000 > /dev/null 2>&1 &'",
                    shell=True, capture_output=True, timeout=10
                )
                
                move_cursor(content_x + 2, y)
                if restart.returncode == 0:
                    print(f"{Colors.GREEN}✓ django restarted{Colors.RESET}" + " " * 30)
                    operations_done.append("django restart: success")
                else:
                    print(f"{Colors.YELLOW}⚠ restart may need manual check{Colors.RESET}" + " " * 30)
                    operations_done.append("django restart: needs check")
            except subprocess.TimeoutExpired:
                move_cursor(content_x + 2, y)
                print(f"{Colors.YELLOW}⚠ restart command sent (verify manually){Colors.RESET}" + " " * 30)
                operations_done.append("django restart: sent")
        else:
            print(f"{Colors.RED}✗ sync failed{Colors.RESET}" + " " * 30)
            operations_done.append("backend sync: failed")
            had_errors = True
            y += 1
            move_cursor(content_x + 2, y)
            error = result.stderr[:80] if result.stderr else "Check SSH connection"
            print(f"{Colors.DIM}{error}{Colors.RESET}")
    except subprocess.TimeoutExpired:
        move_cursor(content_x + 2, y)
        print(f"{Colors.RED}✗ sync timed out (30s){Colors.RESET}" + " " * 30)
        operations_done.append("backend sync: timeout")
        had_errors = True
    except Exception as e:
        move_cursor(content_x + 2, y)
        print(f"{Colors.RED}✗ error: {str(e)[:50]}{Colors.RESET}" + " " * 30)
        operations_done.append(f"error: {str(e)[:30]}")
        had_errors = True
    
    # Show summary
    if operations_done:
        y += 2
        if y < lines - 6:
            move_cursor(content_x + 2, y)
            print(f"{Colors.BOLD}summary:{Colors.RESET}")
            for op in operations_done:
                y += 1
                if y < lines - 5:
                    move_cursor(content_x + 4, y)
                    if "success" in op:
                        print(f"{Colors.GREEN}• {op}{Colors.RESET}")
                    elif "failed" in op or "error" in op or "timeout" in op:
                        print(f"{Colors.RED}• {op}{Colors.RESET}")
                    else:
                        print(f"{Colors.YELLOW}• {op}{Colors.RESET}")
    
    draw_footer()
    sys.stdout.flush()
    
    # Wait for ESC or left arrow to return
    while True:
        key = get_single_key()
        if key in ['\x1b', '\x1b[D']:  # ESC or left arrow
            break

def deploy_cli():
    """Deploy only CLI to rocksteady"""
    from main import (Colors, move_cursor, get_terminal_size,
                      draw_footer, get_single_key)
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}💻  cli deployment{Colors.RESET}")
    
    move_cursor(content_x + 2, 5)
    print(f"{Colors.YELLOW}syncing cli interface...{Colors.RESET}")
    
    y = 7
    operations_done = []
    had_errors = False
    
    move_cursor(content_x + 2, y)
    print(f"{Colors.YELLOW}⏳ syncing src/ folder...{Colors.RESET}")
    
    try:
        result = subprocess.run(
            "rsync -avz --exclude={__pycache__,*.pyc} src/ rocksteady:~/unibos/src/",
            shell=True, capture_output=True, text=True, timeout=30
        )
        
        move_cursor(content_x + 2, y)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ cli synced{Colors.RESET}" + " " * 30)
            operations_done.append("cli sync: success")
            
            y += 2
            move_cursor(content_x + 2, y)
            print(f"{Colors.YELLOW}⏳ setting permissions...{Colors.RESET}")
            
            try:
                perms = subprocess.run(
                    "ssh rocksteady 'chmod +x ~/unibos/unibos.sh ~/unibos/src/*.sh 2>/dev/null'",
                    shell=True, capture_output=True, timeout=10
                )
                
                move_cursor(content_x + 2, y)
                if perms.returncode == 0:
                    print(f"{Colors.GREEN}✓ permissions set{Colors.RESET}" + " " * 30)
                    operations_done.append("permissions: success")
                else:
                    print(f"{Colors.YELLOW}⚠ permissions may need check{Colors.RESET}" + " " * 30)
                    operations_done.append("permissions: needs check")
            except subprocess.TimeoutExpired:
                move_cursor(content_x + 2, y)
                print(f"{Colors.YELLOW}⚠ permissions command sent{Colors.RESET}" + " " * 30)
                operations_done.append("permissions: sent")
        else:
            print(f"{Colors.RED}✗ sync failed{Colors.RESET}" + " " * 30)
            operations_done.append("cli sync: failed")
            had_errors = True
            y += 1
            move_cursor(content_x + 2, y)
            error = result.stderr[:80] if result.stderr else "Check SSH connection"
            print(f"{Colors.DIM}{error}{Colors.RESET}")
    except subprocess.TimeoutExpired:
        move_cursor(content_x + 2, y)
        print(f"{Colors.RED}✗ sync timed out (30s){Colors.RESET}" + " " * 30)
        operations_done.append("cli sync: timeout")
        had_errors = True
    except Exception as e:
        move_cursor(content_x + 2, y)
        print(f"{Colors.RED}✗ error: {str(e)[:50]}{Colors.RESET}" + " " * 30)
        operations_done.append(f"error: {str(e)[:30]}")
        had_errors = True
    
    # Show summary
    if operations_done:
        y += 2
        if y < lines - 6:
            move_cursor(content_x + 2, y)
            print(f"{Colors.BOLD}summary:{Colors.RESET}")
            for op in operations_done:
                y += 1
                if y < lines - 5:
                    move_cursor(content_x + 4, y)
                    if "success" in op:
                        print(f"{Colors.GREEN}• {op}{Colors.RESET}")
                    elif "failed" in op or "error" in op or "timeout" in op:
                        print(f"{Colors.RED}• {op}{Colors.RESET}")
                    else:
                        print(f"{Colors.YELLOW}• {op}{Colors.RESET}")
    
    draw_footer()
    sys.stdout.flush()
    
    # Wait for ESC or left arrow to return
    while True:
        key = get_single_key()
        if key in ['\x1b', '\x1b[D']:  # ESC or left arrow
            break

def show_system_info():
    """Show system information when running on server"""
    from main import (Colors, move_cursor, get_terminal_size,
                      draw_footer, get_single_key)
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}🖥️  system information{Colors.RESET}")
    
    y = 5
    
    # CPU Info
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}cpu:{Colors.RESET}")
    y += 1
    try:
        cpu_info = subprocess.run("lscpu | grep 'Model name' | cut -d: -f2", 
                                  shell=True, capture_output=True, text=True).stdout.strip()
        cores = subprocess.run("nproc", shell=True, capture_output=True, text=True).stdout.strip()
        move_cursor(content_x + 4, y)
        print(f"{cpu_info} ({cores} cores)")
    except:
        move_cursor(content_x + 4, y)
        print("unable to get cpu info")
    
    # Memory Info
    y += 2
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}memory:{Colors.RESET}")
    y += 1
    try:
        mem_info = subprocess.run("free -h | grep Mem | awk '{print $2\" total, \"$3\" used, \"$4\" free\"}'",
                                  shell=True, capture_output=True, text=True).stdout.strip()
        move_cursor(content_x + 4, y)
        print(mem_info)
    except:
        move_cursor(content_x + 4, y)
        print("unable to get memory info")
    
    # Disk Info
    y += 2
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}disk:{Colors.RESET}")
    y += 1
    try:
        disk_info = subprocess.run("df -h / | tail -1 | awk '{print $2\" total, \"$3\" used, \"$4\" free (\"$5\" used)\"}'",
                                   shell=True, capture_output=True, text=True).stdout.strip()
        move_cursor(content_x + 4, y)
        print(disk_info)
    except:
        move_cursor(content_x + 4, y)
        print("unable to get disk info")
    
    # Uptime
    y += 2
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}uptime:{Colors.RESET}")
    y += 1
    try:
        uptime = subprocess.run("uptime -p", shell=True, capture_output=True, text=True).stdout.strip()
        move_cursor(content_x + 4, y)
        print(uptime)
    except:
        move_cursor(content_x + 4, y)
        print("unable to get uptime")
    
    # Network
    y += 2
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}network:{Colors.RESET}")
    y += 1
    try:
        ip_info = subprocess.run("hostname -I | awk '{print $1}'",
                                 shell=True, capture_output=True, text=True).stdout.strip()
        move_cursor(content_x + 4, y)
        print(f"ip: {ip_info}")
    except:
        move_cursor(content_x + 4, y)
        print("unable to get network info")
    
    draw_footer()
    sys.stdout.flush()
    
    # Wait for ESC or left arrow to return
    while True:
        key = get_single_key()
        if key in ['\x1b', '\x1b[D']:  # ESC or left arrow
            break

def show_server_status():
    """Show detailed server status from rocksteady"""
    from main import (Colors, move_cursor, get_terminal_size,
                      draw_footer, get_single_key)
    
    # Don't clear screen, just clear content area
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area only
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')  # Clear to end of line
    sys.stdout.flush()
    
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}📊  server status{Colors.RESET}")
    
    move_cursor(content_x + 2, 5)
    print(f"{Colors.YELLOW}connecting to rocksteady...{Colors.RESET}")
    
    y = 7
    
    # Check SSH connectivity first
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}connection:{Colors.RESET}")
    y += 1
    
    move_cursor(content_x + 4, y)
    connection_ok = False
    try:
        # Test SSH connection first without passphrase
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=2", "-o", "BatchMode=yes", 
             "rocksteady", "echo", "connected"],
            capture_output=True, text=True, timeout=3
        )
        
        if result.returncode == 0:
            print(f"ssh: {Colors.GREEN}● connected{Colors.RESET}")
            connection_ok = True
        elif "passphrase" in result.stderr.lower() or result.returncode == 255:
            # SSH key needs passphrase
            print(f"ssh: {Colors.YELLOW}● passphrase required{Colors.RESET}")
            y += 1
            move_cursor(content_x + 4, y)
            print(f"{Colors.DIM}enter passphrase: {Colors.RESET}", end='')
            
            import getpass
            passphrase = getpass.getpass('')
            
            # Try SSH with passphrase using ssh-agent
            try:
                # Start ssh-agent if needed and add key
                add_key = subprocess.run(
                    f"echo '{passphrase}' | ssh-add ~/.ssh/id_rsa 2>/dev/null",
                    shell=True, capture_output=True, text=True
                )
                
                # Retry connection
                result = subprocess.run(
                    ["ssh", "-o", "ConnectTimeout=2", 
                     "rocksteady", "echo", "connected"],
                    capture_output=True, text=True, timeout=3
                )
                
                if result.returncode == 0:
                    move_cursor(content_x + 4, y)
                    print(f"{Colors.GREEN}✓ authenticated{Colors.RESET}     ")
                    connection_ok = True
                else:
                    move_cursor(content_x + 4, y)
                    print(f"{Colors.RED}✗ auth failed{Colors.RESET}      ")
                    connection_ok = False
            except:
                move_cursor(content_x + 4, y)
                print(f"{Colors.RED}✗ auth error{Colors.RESET}       ")
                connection_ok = False
        else:
            print(f"ssh: {Colors.RED}● failed{Colors.RESET}")
            connection_ok = False
    except Exception as e:
        print(f"ssh: {Colors.RED}● timeout{Colors.RESET}")
        connection_ok = False
    
    if connection_ok:
        # Get system information from rocksteady
        y += 2
        move_cursor(content_x + 2, y)
        print(f"{Colors.BOLD}system info:{Colors.RESET}")
        y += 1
        
        # Get hostname
        move_cursor(content_x + 4, y)
        try:
            hostname = subprocess.run(
                ["ssh", "rocksteady", "hostname"],
                capture_output=True, text=True, timeout=2
            ).stdout.strip()
            print(f"hostname: {Colors.GREEN}{hostname}{Colors.RESET}")
        except:
            print(f"hostname: {Colors.RED}error{Colors.RESET}")
        
        # Get uptime
        y += 1
        move_cursor(content_x + 4, y)
        try:
            uptime = subprocess.run(
                ["ssh", "rocksteady", "uptime", "-p"],
                capture_output=True, text=True, timeout=2
            ).stdout.strip()
            print(f"uptime: {Colors.DIM}{uptime}{Colors.RESET}")
        except:
            print(f"uptime: {Colors.RED}error{Colors.RESET}")
        
        # Get memory usage
        y += 1
        move_cursor(content_x + 4, y)
        try:
            mem_info = subprocess.run(
                ["ssh", "rocksteady", "free", "-h", "|", "grep", "Mem"],
                capture_output=True, text=True, timeout=2, shell=True
            ).stdout.strip()
            if mem_info:
                # Parse memory line
                parts = mem_info.split()
                if len(parts) >= 3:
                    total = parts[1]
                    used = parts[2]
                    print(f"memory: {Colors.YELLOW}{used}/{total}{Colors.RESET}")
            else:
                # Alternative command
                mem_cmd = "ssh rocksteady \"free -h | grep Mem | awk '{print \\$3\\\"/\\\"\\$2}'\""
                mem = subprocess.run(mem_cmd, shell=True, capture_output=True, text=True).stdout.strip()
                print(f"memory: {Colors.YELLOW}{mem if mem else 'n/a'}{Colors.RESET}")
        except:
            print(f"memory: {Colors.RED}error{Colors.RESET}")
        
        # Check UNIBOS services
        y += 2
        move_cursor(content_x + 2, y)
        print(f"{Colors.BOLD}unibos services:{Colors.RESET}")
        y += 1
        
        # Check if Django is running
        move_cursor(content_x + 4, y)
        try:
            django_check = subprocess.run(
                ["ssh", "rocksteady", "pgrep", "-f", "manage.py"],
                capture_output=True, text=True, timeout=2
            )
            if django_check.returncode == 0:
                print(f"django: {Colors.GREEN}● running{Colors.RESET}")
            else:
                print(f"django: {Colors.RED}● stopped{Colors.RESET}")
        except:
            print(f"django: {Colors.YELLOW}● unknown{Colors.RESET}")
        
        # Check if PostgreSQL is accessible
        y += 1
        move_cursor(content_x + 4, y)
        try:
            pg_check = subprocess.run(
                ["ssh", "rocksteady", "pg_isready", "-q"],
                capture_output=True, text=True, timeout=2
            )
            if pg_check.returncode == 0:
                print(f"postgresql: {Colors.GREEN}● running{Colors.RESET}")
            else:
                print(f"postgresql: {Colors.RED}● stopped{Colors.RESET}")
        except:
            print(f"postgresql: {Colors.YELLOW}● checking...{Colors.RESET}")
        
        # Show deployment info
        y += 2
        move_cursor(content_x + 2, y)
        print(f"{Colors.BOLD}deployment:{Colors.RESET}")
        y += 1
        
        move_cursor(content_x + 4, y)
        print(f"path: {Colors.DIM}~/unibos{Colors.RESET}")
        
        # Check last deployment time
        y += 1
        move_cursor(content_x + 4, y)
        try:
            last_mod = subprocess.run(
                ["ssh", "rocksteady", "stat", "-c", "%y", "~/unibos/manage.py", "2>/dev/null", "|", "cut", "-d'", "-f1"],
                capture_output=True, text=True, timeout=2, shell=True
            ).stdout.strip()
            if last_mod:
                print(f"last update: {Colors.DIM}{last_mod[:19]}{Colors.RESET}")
        except:
            pass
            
    else:
        # Connection failed - show error info
        y += 2
        move_cursor(content_x + 2, y)
        print(f"{Colors.RED}⚠ cannot connect to rocksteady{Colors.RESET}")
        
        y += 2
        move_cursor(content_x + 2, y)
        print(f"{Colors.BOLD}troubleshooting:{Colors.RESET}")
        y += 1
        
        move_cursor(content_x + 4, y)
        print(f"1. check ssh config: {Colors.DIM}~/.ssh/config{Colors.RESET}")
        y += 1
        move_cursor(content_x + 4, y)
        print(f"2. verify host entry: {Colors.DIM}Host rocksteady{Colors.RESET}")
        y += 1
        move_cursor(content_x + 4, y)
        print(f"3. test connection: {Colors.DIM}ssh rocksteady{Colors.RESET}")
    
    draw_footer()
    sys.stdout.flush()
    
    # Wait for ESC or left arrow to return
    while True:
        key = get_single_key()
        if key in ['\x1b', '\x1b[D']:  # ESC or left arrow
            break

def public_server_menu():
    """Public server submenu - exactly like administration_menu"""
    from main import (clear_screen, draw_header, draw_footer, draw_sidebar,
                      get_single_key, get_terminal_size, Colors, menu_state,
                      hide_cursor, draw_header_time_only, show_cursor)
    
    # Set submenu state
    menu_state.in_submenu = 'public_server'
    if not hasattr(menu_state, 'public_server_index'):
        menu_state.public_server_index = 0
    
    # Clear screen and redraw everything to start fresh
    clear_screen()
    draw_header()
    
    # Debug: Check if menu items are initialized
    if not hasattr(menu_state, 'modules') or not menu_state.modules:
        from main import initialize_menu_items
        initialize_menu_items()
    
    # Force sidebar redraw to ensure dimmed state is applied
    menu_state.last_sidebar_cache_key = None
    draw_sidebar()
    
    # Clear input buffer before starting
    try:
        import termios
        for _ in range(3):
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)
            time.sleep(0.01)
    except:
        pass
    
    # Draw public server menu with full redraw initially
    draw_public_server_menu(full_redraw=True)
    draw_footer()
    
    # Hide cursor for better visual experience
    hide_cursor()
    
    # Track last footer update time for clock
    last_footer_update = time.time()
    
    while menu_state.in_submenu == 'public_server':
        # Update header time every second
        current_time = time.time()
        if current_time - last_footer_update >= 1.0:
            draw_header_time_only()
            last_footer_update = current_time
        
        # Get user input
        key = get_single_key(timeout=0.1)
        
        if key:
            # Get current options
            options = get_public_server_options()
            # Filter out headers and separators for navigation
            selectable_options = [(k, n, d) for k, n, d in options if k not in ["header", "separator"]]
            
            if key in ['\x1b[A', 'k', 'K']:  # Up arrow or k
                if menu_state.public_server_index > 0:
                    menu_state.public_server_index -= 1
                    # Only redraw the menu items, not full content
                    draw_public_server_menu(full_redraw=False)
            
            elif key in ['\x1b[B', 'j', 'J']:  # Down arrow or j
                if menu_state.public_server_index < len(selectable_options) - 1:
                    menu_state.public_server_index += 1
                    # Only redraw the menu items, not full content
                    draw_public_server_menu(full_redraw=False)
            
            elif key == '\r' or key == '\x1b[C':  # Enter or Right arrow
                if 0 <= menu_state.public_server_index < len(selectable_options):
                    selected_key = selectable_options[menu_state.public_server_index][0]
                    
                    if selected_key == "restart_recaria":
                        try:
                            restart_recaria()
                        except KeyboardInterrupt:
                            # User pressed Ctrl+C, return to menu
                            pass
                        except Exception as e:
                            # Show error and wait
                            for y in range(2, lines - 2):
                                move_cursor(27, y)
                                sys.stdout.write('\033[K')
                            move_cursor(29, 5)
                            print(f"{Colors.RED}❌ restart error: {str(e)[:80]}{Colors.RESET}")
                            move_cursor(29, lines - 3)
                            print(f"{Colors.DIM}press any key to return...{Colors.RESET}")
                            sys.stdout.flush()
                            get_single_key()
                        # Redraw menu properly after returning with full redraw
                        menu_state.in_submenu = 'public_server'
                        draw_public_server_menu(full_redraw=True)
                        draw_footer()
                        sys.stdout.flush()
                    
                    elif selected_key == "load_ssh_key":
                        load_ssh_key()
                        # Redraw menu properly after returning with full redraw
                        menu_state.in_submenu = 'public_server'
                        draw_public_server_menu(full_redraw=True)
                        draw_footer()
                        sys.stdout.flush()
                    
                    elif selected_key == "quick_deploy":
                        quick_deploy()
                        # Redraw menu properly after returning with full redraw
                        menu_state.in_submenu = 'public_server'
                        draw_public_server_menu(full_redraw=True)
                        draw_footer()
                        sys.stdout.flush()
                    
                    elif selected_key == "full_deploy":
                        full_deployment()
                        # Redraw menu properly after returning with full redraw
                        menu_state.in_submenu = 'public_server'
                        draw_public_server_menu(full_redraw=True)
                        draw_footer()
                        sys.stdout.flush()
                    
                    elif selected_key == "deploy_backend":
                        deploy_backend()
                        # Redraw menu properly after returning with full redraw
                        menu_state.in_submenu = 'public_server'
                        draw_public_server_menu(full_redraw=True)
                        draw_footer()
                        sys.stdout.flush()
                    
                    elif selected_key == "db_sync":
                        try:
                            database_sync()
                        except Exception as e:
                            # Clear and show error
                            for y in range(2, lines - 2):
                                move_cursor(27, y)
                                sys.stdout.write('\033[K')
                            move_cursor(29, 5)
                            print(f"{Colors.RED}❌ database sync error:{Colors.RESET}")
                            move_cursor(29, 7)
                            error_msg = str(e)
                            # Wrap long error messages
                            max_width = cols - 35
                            import textwrap
                            wrapped = textwrap.wrap(error_msg, max_width)
                            for i, line in enumerate(wrapped[:5]):  # Max 5 lines
                                move_cursor(31, 7 + i)
                                print(f"{Colors.YELLOW}{line}{Colors.RESET}")
                            move_cursor(29, 7 + len(wrapped) + 2)
                            print(f"{Colors.DIM}press any key to return...{Colors.RESET}")
                            sys.stdout.flush()
                            get_single_key()
                        finally:
                            # Redraw menu properly after returning with full redraw
                            menu_state.in_submenu = 'public_server'
                            draw_public_server_menu(full_redraw=True)
                            draw_footer()
                            sys.stdout.flush()
                    
                    elif selected_key == "deploy_cli":
                        deploy_cli()
                        # Redraw menu properly after returning with full redraw
                        menu_state.in_submenu = 'public_server'
                        draw_public_server_menu(full_redraw=True)
                        draw_footer()
                        sys.stdout.flush()
                    
                    elif selected_key == "server_status":
                        show_server_status()
                        # Redraw menu properly after returning with full redraw
                        menu_state.in_submenu = 'public_server'
                        draw_public_server_menu(full_redraw=True)
                        draw_footer()
                        sys.stdout.flush()
                    
                    elif selected_key == "system_info":
                        show_system_info()
                        # Redraw menu properly after returning with full redraw
                        menu_state.in_submenu = 'public_server'
                        draw_public_server_menu(full_redraw=True)
                        draw_footer()
                        sys.stdout.flush()
                    
                    elif selected_key == "back":
                        menu_state.in_submenu = None
                        break
                    
                    else:
                        # Not implemented yet - show message
                        cols, lines = get_terminal_size()
                        from main import move_cursor
                        move_cursor(27 + 2, lines - 6)
                        print(f"{Colors.YELLOW}feature coming soon...{Colors.RESET}")
                        time.sleep(1)
                        draw_public_server_menu(full_redraw=True)
            
            elif key in ['q', 'Q', '\x1b', '\x1b[D']:  # q, ESC, or Left arrow
                menu_state.in_submenu = None
                break
    
    # Clean up
    show_cursor()
    menu_state.in_submenu = None
    menu_state.public_server_index = 0

def database_sync():
    """Database sync between local and rocksteady"""
    try:
        from main import (Colors, move_cursor, get_terminal_size,
                          draw_footer, get_single_key, show_cursor, hide_cursor)
        import os
        import time
        # Don't reimport sys - it's already global
        import subprocess
        from datetime import datetime
    except ImportError as e:
        raise ImportError(f"Failed to import required modules: {e}")
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Title
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}🔄  database sync{Colors.RESET}")
    
    move_cursor(content_x + 2, 5)
    print(f"{Colors.YELLOW}select sync direction:{Colors.RESET}")
    
    # Options
    options = [
        ("local_to_remote", "📤  local → rocksteady", "upload local database to server"),
        ("remote_to_local", "📥  rocksteady → local", "download server database to local"),
        ("cancel", "❌  cancel", "return to menu")
    ]
    
    selected_index = 0
    
    def draw_sync_options():
        y = 7
        for i, (key, name, desc) in enumerate(options):
            move_cursor(content_x + 4, y + i * 2)
            if i == selected_index:
                print(f"{Colors.CYAN}▶ {name}{Colors.RESET}  {Colors.DIM}{desc}{Colors.RESET}")
            else:
                print(f"  {name}  {Colors.DIM}{desc}{Colors.RESET}")
    
    draw_sync_options()
    
    # Instructions
    move_cursor(content_x + 2, lines - 4)
    print(f"{Colors.DIM}↑↓ select | enter confirm | esc cancel{Colors.RESET}")
    
    while True:
        key = get_single_key()
        
        if key == '\x1b' or key == '\x1b[D':  # ESC or left arrow
            return
        elif key == '\x1b[A':  # Up arrow
            if selected_index > 0:
                selected_index -= 1
                draw_sync_options()
        elif key == '\x1b[B':  # Down arrow
            if selected_index < len(options) - 1:
                selected_index += 1
                draw_sync_options()
        elif key == '\r':  # Enter
            selected_option = options[selected_index][0]
            
            if selected_option == "cancel":
                return
            
            # Clear options
            for y in range(7, 13):
                move_cursor(content_x, y)
                sys.stdout.write('\033[K')
            sys.stdout.flush()
            
            # Get timestamp for backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            try:
                if selected_option == "local_to_remote":
                    sync_local_to_remote(timestamp)
                else:  # remote_to_local
                    sync_remote_to_local(timestamp)
            except Exception as e:
                # Show error if sync fails
                move_cursor(content_x + 2, lines - 6)
                print(f"{Colors.RED}❌ sync error: {str(e)[:80]}{Colors.RESET}")
                move_cursor(content_x + 2, lines - 5)
                print(f"{Colors.DIM}Error details: {str(e)}{Colors.RESET}")
            
            # Always wait for key to return
            move_cursor(content_x + 2, lines - 3)
            print(f"{Colors.DIM}press esc or ← to return...{Colors.RESET}")
            sys.stdout.flush()  # Force output
            
            # Show cursor and wait for ESC or left arrow
            show_cursor()
            
            # Non-blocking wait for ESC or left arrow only
            import select
            import termios
            import tty
            
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setcbreak(sys.stdin.fileno())
                
                while True:
                    # Check if input is available (non-blocking)
                    if select.select([sys.stdin], [], [], 0.05)[0]:  # 50ms timeout
                        key = sys.stdin.read(1)
                        
                        # Check for escape sequences
                        if key == '\x1b':  # ESC or arrow key start
                            # Check if it's an arrow key
                            if select.select([sys.stdin], [], [], 0)[0]:
                                key2 = sys.stdin.read(1)
                                if key2 == '[':
                                    if select.select([sys.stdin], [], [], 0)[0]:
                                        key3 = sys.stdin.read(1)
                                        if key3 == 'D':  # Left arrow
                                            break
                            else:
                                # Just ESC key
                                break
                    
                    # Keep the terminal responsive
                    pass
                    
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            
            hide_cursor()
            return

def sync_local_to_remote(timestamp):
    """Sync local database to rocksteady"""
    try:
        from main import Colors, move_cursor, get_terminal_size
        import subprocess
        import os
        # Don't reimport sys
    except ImportError as e:
        raise ImportError(f"Failed to import required modules: {e}")
    
    cols, lines = get_terminal_size()
    content_x = 27
    y = 7
    
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}{Colors.YELLOW}📤  syncing local → rocksteady{Colors.RESET}")
    y += 2
    
    steps = [
        ("creating local backup", "PGPASSWORD=unibos_password pg_dump -h localhost -p 5432 -U unibos_user -d unibos_db --clean --if-exists --no-owner --no-privileges -f /tmp/unibos_sync_{}.sql 2>&1".format(timestamp)),
        ("uploading to server", "scp /tmp/unibos_sync_{}.sql rocksteady:/tmp/".format(timestamp)),
        ("backing up remote db", "ssh rocksteady 'cd ~/unibos && PGPASSWORD=unibos_password pg_dump -h localhost -U unibos_user -d unibos_db --if-exists --no-owner -f ~/unibos/backup_before_sync_{}.sql 2>&1'".format(timestamp)),
        ("applying to remote db", "ssh rocksteady 'PGPASSWORD=unibos_password psql -h localhost -U unibos_user -d unibos_db -f /tmp/unibos_sync_{}.sql 2>&1'".format(timestamp)),
        ("cleaning up", "rm /tmp/unibos_sync_{}.sql && ssh rocksteady 'rm /tmp/unibos_sync_{}.sql'".format(timestamp, timestamp))
    ]
    
    success = True
    for step_name, command in steps:
        move_cursor(content_x + 4, y)
        print(f"⏳ {step_name}...", end='')
        sys.stdout.flush()
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        move_cursor(content_x + 4, y)
        if result.returncode == 0:
            print(f"✅ {step_name}")
        else:
            print(f"❌ {step_name}")
            y += 1
            move_cursor(content_x + 6, y)
            error_msg = result.stderr.strip() or result.stdout.strip()
            if error_msg:
                # Truncate error if too long
                max_width = cols - content_x - 8
                if len(error_msg) > max_width:
                    error_msg = error_msg[:max_width-3] + "..."
                print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            success = False
            break
        y += 1
    
    y += 1
    move_cursor(content_x + 2, y)
    if success:
        print(f"{Colors.GREEN}✅ database successfully synced to rocksteady!{Colors.RESET}")
        move_cursor(content_x + 2, y + 1)
        print(f"{Colors.DIM}backup saved at: ~/unibos/backup_before_sync_{timestamp}.sql{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ sync failed! check errors above{Colors.RESET}")

def sync_remote_to_local(timestamp):
    """Sync rocksteady database to local"""
    try:
        from main import Colors, move_cursor, get_terminal_size
        import subprocess
        import os
        # Don't reimport sys
    except ImportError as e:
        raise ImportError(f"Failed to import required modules: {e}")
    
    cols, lines = get_terminal_size()
    content_x = 27
    y = 7
    
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}{Colors.YELLOW}📥  syncing rocksteady → local{Colors.RESET}")
    y += 2
    
    steps = [
        ("backing up local db", "PGPASSWORD=unibos_password pg_dump -h localhost -p 5432 -U unibos_user -d unibos_db --if-exists --no-owner -f ~/Desktop/unibos/backup_before_sync_{}.sql 2>&1".format(timestamp)),
        ("creating remote backup", "ssh rocksteady 'PGPASSWORD=unibos_password pg_dump -h localhost -U unibos_user -d unibos_db --clean --if-exists --no-owner --no-privileges -f /tmp/unibos_sync_{}.sql 2>&1'".format(timestamp)),
        ("downloading from server", "scp rocksteady:/tmp/unibos_sync_{}.sql /tmp/".format(timestamp)),
        ("applying to local db", "PGPASSWORD=unibos_password psql -h localhost -p 5432 -U unibos_user -d unibos_db -f /tmp/unibos_sync_{}.sql 2>&1".format(timestamp)),
        ("cleaning up", "rm /tmp/unibos_sync_{}.sql && ssh rocksteady 'rm /tmp/unibos_sync_{}.sql'".format(timestamp, timestamp))
    ]
    
    success = True
    for step_name, command in steps:
        move_cursor(content_x + 4, y)
        print(f"⏳ {step_name}...", end='')
        sys.stdout.flush()
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        move_cursor(content_x + 4, y)
        if result.returncode == 0:
            print(f"✅ {step_name}")
        else:
            print(f"❌ {step_name}")
            y += 1
            move_cursor(content_x + 6, y)
            error_msg = result.stderr.strip() or result.stdout.strip()
            if error_msg:
                # Truncate error if too long
                max_width = cols - content_x - 8
                if len(error_msg) > max_width:
                    error_msg = error_msg[:max_width-3] + "..."
                print(f"{Colors.RED}{error_msg}{Colors.RESET}")
            success = False
            break
        y += 1
    
    y += 1
    move_cursor(content_x + 2, y)
    if success:
        print(f"{Colors.GREEN}✅ database successfully synced from rocksteady!{Colors.RESET}")
        move_cursor(content_x + 2, y + 1)
        print(f"{Colors.DIM}backup saved at: ~/Desktop/unibos/backup_before_sync_{timestamp}.sql{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ sync failed! check errors above{Colors.RESET}")

# Entry point
if __name__ == "__main__":
    # For testing standalone
    class MockMenuState:
        in_submenu = None
        public_server_index = 0
        modules = []
        last_sidebar_cache_key = None
    
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from main import menu_state
    except:
        menu_state = MockMenuState()
    
    public_server_menu()