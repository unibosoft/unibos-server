#!/usr/bin/env python3
"""
Documents Module Handler for unibos cli
Handles documents submenu with invoice processor integration
"""

import sys
import os

def show_documents_menu(menu_state, Colors):
    """Show documents submenu with invoice processor"""
    from cli_content_renderers import DocumentsMenuRenderer, InvoiceProcessorRenderer
    from cli_context_manager import CLIContext
    
    # Clear screen
    sys.stdout.write("\033[2J\033[H")
    
    # Create context
    context = CLIContext()
    
    # Document submenu items
    submenu_items = [
        ("1", "browse documents", "view and manage documents"),
        ("2", "search", "full-text document search"),
        ("3", "upload", "upload new documents"),
        ("4", "ocr scanner", "extract text from images"),
        ("5", "invoice processor", "process invoices with ai"),
        ("6", "tag manager", "manage document tags"),
        ("7", "analytics", "document statistics"),
    ]
    
    selected_index = 0
    
    while True:
        # Get terminal size
        try:
            cols, lines = os.get_terminal_size()
        except:
            cols, lines = 80, 24
        
        # Draw header
        sys.stdout.write(f"\033[1;1H{Colors.BG_DARK}{' ' * cols}{Colors.RESET}")
        sys.stdout.write(f"\033[1;2H{Colors.CYAN}📄 documents module{Colors.RESET}")
        sys.stdout.write(f"\033[2;1H{Colors.DIM}{'─' * cols}{Colors.RESET}")
        
        # Draw menu items
        y_pos = 4
        for i, (key, name, desc) in enumerate(submenu_items):
            if i == selected_index:
                # Highlighted item
                sys.stdout.write(f"\033[{y_pos};2H{Colors.BG_ORANGE}{Colors.WHITE} [{key}] {name:<30} {Colors.RESET}")
                sys.stdout.write(f"\033[{y_pos + 1};6H{Colors.DIM}{desc}{Colors.RESET}")
            else:
                # Normal item
                sys.stdout.write(f"\033[{y_pos};2H [{key}] {name:<30}")
                sys.stdout.write(f"\033[{y_pos + 1};6H{Colors.DIM}{desc}{Colors.RESET}")
            y_pos += 3
        
        # Draw footer
        sys.stdout.write(f"\033[{lines - 2};2H{Colors.DIM}↑↓ navigate | enter select | esc back to main menu{Colors.RESET}")
        sys.stdout.flush()
        
        # Get key input
        key = get_key()
        
        if key == '\x1b':  # ESC
            break
        elif key == 'q':  # Quit
            break
        elif key == '\x1b[A':  # Up arrow
            selected_index = max(0, selected_index - 1)
        elif key == '\x1b[B':  # Down arrow
            selected_index = min(len(submenu_items) - 1, selected_index + 1)
        elif key == '\r' or key == '\n':  # Enter
            # Handle selection
            if selected_index == 4:  # Invoice processor
                show_invoice_processor(menu_state, Colors)
            else:
                # Show placeholder for other options
                sys.stdout.write(f"\033[{lines - 4};2H{Colors.YELLOW}Feature '{submenu_items[selected_index][1]}' coming soon!{Colors.RESET}")
                sys.stdout.flush()
                import time
                time.sleep(2)
        elif key in '1234567':
            # Direct number selection
            idx = int(key) - 1
            if 0 <= idx < len(submenu_items):
                selected_index = idx
                if idx == 4:  # Invoice processor
                    show_invoice_processor(menu_state, Colors)
                else:
                    sys.stdout.write(f"\033[{lines - 4};2H{Colors.YELLOW}Feature '{submenu_items[idx][1]}' coming soon!{Colors.RESET}")
                    sys.stdout.flush()
                    import time
                    time.sleep(2)

def show_invoice_processor(menu_state, Colors):
    """Show invoice processor interface"""
    from invoice_processor_cli import InvoiceProcessorCLI
    
    # Create and run invoice processor
    processor = InvoiceProcessorCLI()
    processor.run()

def get_key():
    """Get single key press"""
    import termios, tty
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        
        # Handle escape sequences
        if key == '\x1b':
            key2 = sys.stdin.read(1)
            if key2 == '[':
                key3 = sys.stdin.read(1)
                return f'\x1b[{key3}'
            else:
                # Put back the second char
                return '\x1b'
        
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)