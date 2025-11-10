"""Code Forge submenu - Git and version control tools"""

import time
import sys

def draw_code_forge_menu():
    """Draw code forge menu in content area - exactly like administration menu"""
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
    print(f"{Colors.BOLD}{Colors.CYAN}# 📦 code forge{Colors.RESET}")
    
    move_cursor(content_x + 2, 5)
    print(f"{Colors.BOLD}{Colors.BLUE}## 🎯 git & version control{Colors.RESET}")
    move_cursor(content_x + 2, 6)
    print(f"{Colors.WHITE}manage repository, commits, and branches{Colors.RESET}")
    
    # Options
    y = 9
    move_cursor(content_x + 2, y)
    print(f"{Colors.BOLD}{Colors.BLUE}## 🛠️ available tools{Colors.RESET}")
    y += 1
    move_cursor(content_x + 2, y)
    print(f"{Colors.DIM}repository management and version control{Colors.RESET}")
    y += 2
    
    # Git operations
    options = get_code_forge_options()
    
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
            if i == menu_state.code_forge_index:
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

def get_code_forge_options():
    """Get code forge menu options"""
    return [
        ("header", "repository status", ""),
        ("git_status", "git status", "view current repository state"),
        ("git_diff", "git diff", "show uncommitted changes"),
        ("git_log", "git log", "view commit history"),
        ("separator", "", ""),
        ("header", "commit operations", ""),
        ("git_add", "git add", "stage files for commit"),
        ("git_commit", "git commit", "create new commit"),
        ("git_push", "git push", "push to remote repository"),
        ("git_pull", "git pull", "pull from remote repository"),
        ("separator", "", ""),
        ("header", "branch management", ""),
        ("git_branch", "branch list", "list all branches"),
        ("git_checkout", "switch branch", "checkout different branch"),
        ("git_merge", "merge branch", "merge branches"),
        ("separator", "", ""),
        ("git_manager", "🎮 launch git manager", "full git interface"),
    ]

def code_forge_menu():
    """Code forge submenu with git tools - exactly like administration_menu"""
    from main import (clear_screen, draw_header, draw_footer, draw_sidebar,
                      get_single_key, get_terminal_size, Colors, menu_state,
                      hide_cursor, draw_header_time_only, show_cursor, draw_main_screen)
    
    # Set submenu state
    menu_state.in_submenu = 'code_forge'
    if not hasattr(menu_state, 'code_forge_index'):
        menu_state.code_forge_index = 0
    
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
    
    # Draw code forge menu
    draw_code_forge_menu()
    draw_footer()
    
    # Hide cursor for better visual experience
    hide_cursor()
    
    # Track last footer update time for clock
    last_footer_update = time.time()
    
    
    while menu_state.in_submenu == 'code_forge':
        # Update header time every second
        current_time = time.time()
        if current_time - last_footer_update >= 1.0:
            draw_header_time_only()  # Use time-only update to prevent flickering
            last_footer_update = current_time
        
        # Non-blocking key check
        key = get_single_key(0.1)
        
        if key:
            # Get current options
            options = get_code_forge_options()
            # Filter out headers and separators for navigation
            selectable_options = [(k, n, d) for k, n, d in options if k not in ["header", "separator"]]
            
            if key in ['\x1b[A', 'k', 'K']:  # Up arrow or k
                if menu_state.code_forge_index > 0:
                    menu_state.code_forge_index -= 1
                    # Redraw header to prevent black spaces
                    draw_header()
                    draw_code_forge_menu()
            
            elif key in ['\x1b[B', 'j', 'J']:  # Down arrow or j
                if menu_state.code_forge_index < len(selectable_options) - 1:
                    menu_state.code_forge_index += 1
                    # Redraw header to prevent black spaces
                    draw_header()
                    draw_code_forge_menu()
            
            elif key == '\r' or key == '\x1b[C':  # Enter or Right arrow - FIXED
                if 0 <= menu_state.code_forge_index < len(selectable_options):
                    selected_key = selectable_options[menu_state.code_forge_index][0]
                    
                    if selected_key == "git_manager":
                        # Launch full git manager
                        try:
                            show_cursor()
                            clear_screen()
                            # Try to import git manager if available
                            try:
                                from git_manager import GitManager
                                git_manager = GitManager()
                                git_manager.show_git_menu()
                            except ImportError:
                                # Fallback to simple git status
                                import subprocess
                                move_cursor(2, 2)
                                print(f"{Colors.CYAN}Git Status:{Colors.RESET}")
                                result = subprocess.run(['git', 'status'], capture_output=True, text=True)
                                print(result.stdout)
                                move_cursor(2, 20)
                                print(f"{Colors.DIM}Press any key to continue...{Colors.RESET}")
                                get_single_key()
                            hide_cursor()
                        except Exception as e:
                            print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
                            time.sleep(2)
                        # Redraw menu after returning
                        clear_screen()
                        draw_header()
                        draw_sidebar()
                        draw_code_forge_menu()
                        draw_footer()
                    else:
                        # Execute git command
                        execute_git_command(selected_key)
                        # Redraw menu after command
                        draw_code_forge_menu()
            
            elif key in ['\x1b', '\x1b[D', 'q', 'Q']:  # ESC, Left Arrow, or q to exit
                # Exit code forge menu - CRITICAL STATE RESET
                menu_state.in_submenu = None  # Clear submenu state FIRST
                
                # Update navigation position
                menu_state.current_section = 1  # tools section
                menu_state.selected_index = 4  # code forge is at index 4 in tools
                
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

def execute_git_command(command_key):
    """Execute a git command and show result"""
    from main import Colors, get_terminal_size, move_cursor
    import subprocess
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear bottom area for output
    for y in range(lines - 10, lines - 2):
        move_cursor(content_x + 2, y)
        sys.stdout.write('\033[K')
    
    move_cursor(content_x + 2, lines - 10)
    
    try:
        if command_key == "git_status":
            result = subprocess.run(['git', 'status', '--short'], 
                                  capture_output=True, text=True)
            print(f"{Colors.YELLOW}Git Status:{Colors.RESET}")
            if result.stdout:
                for line in result.stdout.split('\n')[:5]:
                    if line:
                        move_cursor(content_x + 4, lines - 9 + result.stdout.split('\n').index(line))
                        print(f"{Colors.DIM}{line[:50]}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}Working tree clean{Colors.RESET}")
                
        elif command_key == "git_diff":
            result = subprocess.run(['git', 'diff', '--stat'], 
                                  capture_output=True, text=True)
            print(f"{Colors.YELLOW}Git Diff:{Colors.RESET}")
            if result.stdout:
                for line in result.stdout.split('\n')[:3]:
                    if line:
                        print(f"{Colors.DIM}{line[:50]}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}No changes{Colors.RESET}")
                
        elif command_key == "git_log":
            result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                                  capture_output=True, text=True)
            print(f"{Colors.YELLOW}Recent Commits:{Colors.RESET}")
            if result.stdout:
                for line in result.stdout.split('\n')[:5]:
                    if line:
                        print(f"{Colors.DIM}{line[:50]}{Colors.RESET}")
                        
        else:
            print(f"{Colors.YELLOW}Command '{command_key}' coming soon...{Colors.RESET}")
            
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
    
    time.sleep(2)