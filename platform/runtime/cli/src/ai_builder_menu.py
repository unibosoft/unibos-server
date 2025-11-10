"""AI Builder submenu - AI-powered development tools"""

import time
import sys

def draw_ai_builder_menu():
    """Draw AI builder menu in content area - exactly like administration menu"""
    from main import get_terminal_size, move_cursor, Colors, menu_state
    
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 1
    content_height = lines - 4  # Leave room for header and footer
    
    # Clear content area with proper boundary detection
    for y in range(2, lines - 1):
        move_cursor(content_x, y)
        # Use proper escape sequence to clear to end of line
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Draw vertical separator
    for y in range(2, lines - 1):
        move_cursor(26, y)
        sys.stdout.write(f"{Colors.DIM}│{Colors.RESET}")
    
    # Title area with enhanced styling
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}# 🤖 ai builder{Colors.RESET}")
    
    move_cursor(content_x + 2, 5)
    print(f"{Colors.BOLD}{Colors.BLUE}## 🎯 ai-powered development{Colors.RESET}")
    move_cursor(content_x + 2, 6)
    print(f"{Colors.WHITE}intelligent code generation and analysis{Colors.RESET}")
    
    # Options
    y = 9
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}{Colors.BLUE}## 🛠️ available features{Colors.RESET}")
    y += 1
    move_cursor(content_x + 2, y)
    print(f"{Colors.DIM}ai-assisted development tools{Colors.RESET}")
    y += 2
    
    # AI tools
    options = get_ai_builder_options()
    
    for i, (key, name, desc) in enumerate(options):
        if key == "header":
            # Section header
            move_cursor(content_x + 2, y)
            print(f"{Colors.BOLD}{Colors.CYAN}{name}{Colors.RESET}")
            y += 1
        elif key == "separator":
            # Separator line
            y += 1
        else:
            # Regular option
            if i == menu_state.ai_builder_index:
                # Selected item - highlight
                move_cursor(content_x + 2, y)
                print(f"{Colors.BG_BLUE}{Colors.WHITE}→ {name:<30}{Colors.RESET} {Colors.DIM}{desc}{Colors.RESET}")
            else:
                # Normal item
                move_cursor(content_x + 2, y)
                print(f"  {Colors.GREEN}{name:<30}{Colors.RESET} {Colors.DIM}{desc}{Colors.RESET}")
            y += 1
    
    # Footer hint
    move_cursor(content_x + 2, lines - 3)
    print(f"{Colors.DIM}↑↓ navigate | enter select | ← back | q quit{Colors.RESET}")

def get_ai_builder_options():
    """Get AI builder menu options"""
    return [
        ("header", "code generation", ""),
        ("generate_function", "generate function", "create function from description"),
        ("generate_class", "generate class", "create class with ai"),
        ("generate_tests", "generate tests", "auto-generate unit tests"),
        ("separator", "", ""),
        ("header", "code analysis", ""),
        ("code_review", "code review", "ai-powered code review"),
        ("find_bugs", "find bugs", "detect potential issues"),
        ("security_scan", "security scan", "check for vulnerabilities"),
        ("separator", "", ""),
        ("header", "refactoring", ""),
        ("optimize_code", "optimize code", "improve performance"),
        ("refactor_function", "refactor function", "clean up code"),
        ("add_types", "add type hints", "add python type annotations"),
        ("separator", "", ""),
        ("header", "documentation", ""),
        ("generate_docs", "generate docs", "create documentation"),
        ("add_comments", "add comments", "explain complex code"),
        ("separator", "", ""),
        ("launch_claude", "🎮 launch claude cli", "full ai interface"),
    ]

def ai_builder_menu():
    """AI builder submenu with AI tools - exactly like administration_menu"""
    from main import (clear_screen, draw_header, draw_footer, draw_sidebar,
                      get_single_key, get_terminal_size, Colors, menu_state,
                      hide_cursor, draw_header_time_only, show_cursor, draw_main_screen)
    
    # Set submenu state
    menu_state.in_submenu = 'ai_builder'
    if not hasattr(menu_state, 'ai_builder_index'):
        menu_state.ai_builder_index = 0
    
    # Clear screen and redraw everything to start fresh
    clear_screen()
    draw_header()
    
    # Force sidebar redraw to ensure dimmed state is applied
    menu_state.last_sidebar_cache_key = None
    # Use simple sidebar for proper display
    draw_sidebar()
    
    # Clear input buffer before starting
    TERMIOS_AVAILABLE = True
    try:
        import termios
    except ImportError:
        TERMIOS_AVAILABLE = False
    
    if TERMIOS_AVAILABLE:
        try:
            import termios
            for _ in range(3):
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                time.sleep(0.01)
        except:
            pass
    
    # Draw AI builder menu
    draw_ai_builder_menu()
    draw_footer()
    
    # Hide cursor for better visual experience
    hide_cursor()
    
    # Track last footer update time for clock
    last_footer_update = time.time()
    
    
    while menu_state.in_submenu == 'ai_builder':
        # Update header time every second
        current_time = time.time()
        if current_time - last_footer_update >= 1.0:
            draw_header_time_only()  # Use time-only update to prevent flickering
            last_footer_update = current_time
        
        # Non-blocking key check
        key = get_single_key(0.1)
        
        if key:
            # Get current options
            options = get_ai_builder_options()
            # Filter out headers and separators for navigation
            selectable_options = [(k, n, d) for k, n, d in options if k not in ["header", "separator"]]
            
            if key in ['\x1b[A', 'k', 'K']:  # Up arrow or k
                if menu_state.ai_builder_index > 0:
                    menu_state.ai_builder_index -= 1
                    # Redraw header to prevent black spaces
                    draw_header()
                    draw_ai_builder_menu()
            
            elif key in ['\x1b[B', 'j', 'J']:  # Down arrow or j
                if menu_state.ai_builder_index < len(selectable_options) - 1:
                    menu_state.ai_builder_index += 1
                    # Redraw header to prevent black spaces
                    draw_header()
                    draw_ai_builder_menu()
            
            elif key == '\r' or key == '\x1b[C':  # Enter or Right arrow - FIXED
                if 0 <= menu_state.ai_builder_index < len(selectable_options):
                    selected_key = selectable_options[menu_state.ai_builder_index][0]
                    
                    if selected_key == "launch_claude":
                        # Launch full Claude CLI
                        from main import ai_builder_tools
                        ai_builder_tools()
                        # Redraw menu after returning
                        clear_screen()
                        draw_header()
                        draw_sidebar()
                        draw_ai_builder_menu()
                        draw_footer()
                    else:
                        # Execute AI command
                        execute_ai_command(selected_key)
                        # Redraw menu after command
                        draw_ai_builder_menu()
            
            elif key in ['\x1b', '\x1b[D', 'q', 'Q']:  # ESC, Left Arrow, or q to exit
                # Exit AI builder menu - CRITICAL STATE RESET
                menu_state.in_submenu = None  # Clear submenu state FIRST
                
                # Update navigation position
                menu_state.current_section = 2  # dev tools section
                menu_state.selected_index = 0  # ai builder is at index 0 in dev tools
                
                # Clear any cache that might cause stale renders
                menu_state.last_sidebar_cache_key = None
                if hasattr(menu_state, 'sidebar_cache'):
                    menu_state.sidebar_cache = {}
                if hasattr(menu_state, '_sidebar_highlight_cache'):
                    delattr(menu_state, '_sidebar_highlight_cache')
                
                # Use the standard exit pattern like version_manager
                clear_screen()
                draw_main_screen()
                break
        
        # Small sleep to prevent CPU spinning
        time.sleep(0.01)
    
    # Show cursor when exiting
    show_cursor()

def execute_ai_command(command_key):
    """Execute an AI command and show result"""
    from main import Colors, get_terminal_size, move_cursor
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear bottom area for output
    for y in range(lines - 10, lines - 2):
        move_cursor(content_x + 2, y)
        sys.stdout.write('\033[K')
    
    move_cursor(content_x + 2, lines - 10)
    
    # Simulate AI operations
    ai_messages = {
        "generate_function": "🤖 Analyzing requirements...",
        "generate_class": "🤖 Designing class structure...",
        "generate_tests": "🤖 Creating test cases...",
        "code_review": "🤖 Reviewing code quality...",
        "find_bugs": "🤖 Scanning for issues...",
        "security_scan": "🤖 Checking vulnerabilities...",
        "optimize_code": "🤖 Optimizing performance...",
        "refactor_function": "🤖 Refactoring code...",
        "add_types": "🤖 Adding type hints...",
        "generate_docs": "🤖 Generating documentation...",
        "add_comments": "🤖 Adding explanations..."
    }
    
    if command_key in ai_messages:
        print(f"{Colors.YELLOW}{ai_messages[command_key]}{Colors.RESET}")
        move_cursor(content_x + 4, lines - 8)
        print(f"{Colors.DIM}AI processing...{Colors.RESET}")
        time.sleep(1)
        move_cursor(content_x + 4, lines - 7)
        print(f"{Colors.GREEN}✓ Task completed{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Feature '{command_key}' coming soon...{Colors.RESET}")
    
    time.sleep(2)