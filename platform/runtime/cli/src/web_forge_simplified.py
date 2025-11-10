# Simplified Web Forge functions for single Django server

def launch_django_web_ui():
    """Launch Django web UI in browser with automatic start"""
    show_server_action("🌐 Launching Web Interface", Colors.CYAN)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    # Check server status
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Checking server status...{Colors.RESET}")
    y += 2
    
    backend_running, backend_pid = check_backend_running()
    
    # Start server if needed
    if not backend_running:
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}Server is not running. Starting...{Colors.RESET}")
        y += 2
        
        # Check port 8000
        port_check = subprocess.run(['lsof', '-ti:8000'], capture_output=True, text=True)
        if port_check.returncode == 0 and port_check.stdout.strip():
            move_cursor(content_x, y)
            print(f"{Colors.YELLOW}⚠ Port 8000 is in use, cleaning up...{Colors.RESET}")
            y += 1
            try:
                pids = port_check.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(['kill', '-9', pid], capture_output=True)
                time.sleep(1)
            except:
                pass
        
        # Start Django server
        move_cursor(content_x, y)
        print(f"{Colors.CYAN}Starting Django server...{Colors.RESET}")
        y += 1
        
        start_web_backend()
        
        # Wait for startup
        move_cursor(content_x, y)
        print(f"{Colors.DIM}Waiting for server to initialize...{Colors.RESET}")
        time.sleep(3)
        
        # Check again
        backend_running, backend_pid = check_backend_running()
    
    # Show status
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}{Colors.CYAN}═══ Server Status ═══{Colors.RESET}")
    y += 2
    
    if backend_running:
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}✓ Django Server:{Colors.RESET} {Colors.BOLD}Running{Colors.RESET}")
        move_cursor(content_x + 2, y + 1)
        print(f"{Colors.DIM}PID: {backend_pid}{Colors.RESET}")
        move_cursor(content_x + 2, y + 2)
        print(f"{Colors.DIM}URL: http://localhost:8000{Colors.RESET}")
        y += 4
    else:
        move_cursor(content_x, y)
        print(f"{Colors.RED}✗ Server Failed to Start{Colors.RESET}")
        move_cursor(content_x, y + 1)
        print(f"{Colors.DIM}Check logs for details{Colors.RESET}")
        y += 3
    
    # Open browser
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}{Colors.CYAN}═══ Opening Browser ═══{Colors.RESET}")
    y += 2
    
    url = "http://localhost:8000"
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}🌐 Launching UNIBOS Web Interface{Colors.RESET}")
    move_cursor(content_x, y + 1)
    print(f"{Colors.DIM}   URL: {url}{Colors.RESET}")
    
    import webbrowser
    try:
        webbrowser.open(url)
        y += 3
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}✓ Browser launched successfully{Colors.RESET}")
    except Exception as e:
        y += 3
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}⚠ Could not auto-open browser{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"{Colors.DIM}Please open manually: {url}{Colors.RESET}")
    
    # Show instructions
    y += 3
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}Press any key to return to menu...{Colors.RESET}")
    
    # Wait for user input
    get_key()


def show_simple_web_status():
    """Show simplified server status"""
    show_server_action("📊 Server Status", Colors.CYAN)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    backend_running, backend_pid = check_backend_running()
    
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}{Colors.CYAN}═══ Django Server Status ═══{Colors.RESET}")
    y += 2
    
    if backend_running:
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}● Server Status: RUNNING{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"  PID: {backend_pid}")
        y += 1
        move_cursor(content_x, y)
        print(f"  URL: http://localhost:8000")
        y += 1
        move_cursor(content_x, y)
        print(f"  Settings: emergency")
    else:
        move_cursor(content_x, y)
        print(f"{Colors.RED}● Server Status: STOPPED{Colors.RESET}")
        y += 1
        move_cursor(content_x, y)
        print(f"  Use 'Start Server' to begin")
    
    y += 3
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}Available Endpoints:{Colors.RESET}")
    y += 1
    endpoints = [
        "/           - Main dashboard",
        "/documents/ - Document management",
        "/module/    - Module selector",
        "/admin/     - Admin panel (if enabled)"
    ]
    for endpoint in endpoints:
        move_cursor(content_x, y)
        print(f"  {Colors.DIM}{endpoint}{Colors.RESET}")
        y += 1
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}Press any key to return...{Colors.RESET}")
    get_key()


def run_django_migrations():
    """Run Django database migrations"""
    show_server_action("🗄️ Running Migrations", Colors.MAGENTA)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Running Django migrations...{Colors.RESET}")
    y += 2
    
    backend_path = os.path.join(get_project_root(), 'backend')
    
    # Run makemigrations
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}Creating migrations...{Colors.RESET}")
    y += 1
    
    result = subprocess.run(
        ['python', 'manage.py', 'makemigrations'],
        cwd=backend_path,
        env={**os.environ, 'DJANGO_SETTINGS_MODULE': 'unibos_backend.settings.emergency'},
        capture_output=True,
        text=True
    )
    
    if "No changes detected" in result.stdout:
        move_cursor(content_x, y)
        print(f"{Colors.DIM}No new migrations needed{Colors.RESET}")
    else:
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}✓ Migrations created{Colors.RESET}")
    
    y += 2
    
    # Run migrate
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}Applying migrations...{Colors.RESET}")
    y += 1
    
    result = subprocess.run(
        ['python', 'manage.py', 'migrate'],
        cwd=backend_path,
        env={**os.environ, 'DJANGO_SETTINGS_MODULE': 'unibos_backend.settings.emergency'},
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}✓ Migrations applied successfully{Colors.RESET}")
    else:
        move_cursor(content_x, y)
        print(f"{Colors.RED}✗ Migration failed{Colors.RESET}")
        if result.stderr:
            y += 1
            move_cursor(content_x, y)
            print(f"{Colors.DIM}{result.stderr[:100]}...{Colors.RESET}")
    
    y += 3
    move_cursor(content_x, y)
    print(f"{Colors.BOLD}Press any key to return...{Colors.RESET}")
    get_key()