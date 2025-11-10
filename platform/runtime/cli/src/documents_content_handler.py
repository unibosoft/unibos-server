#!/usr/bin/env python3
"""
Documents Content Handler for unibos cli
Displays documents submenu in the content area (right side)
"""

import sys
import os
import time

def draw_documents_submenu(menu_state, Colors):
    """Draw documents submenu in content area"""
    from invoice_processor_cli import InvoiceProcessorCLI
    
    # Get terminal size
    try:
        cols, lines = os.get_terminal_size()
    except:
        cols, lines = 80, 24
    
    content_x = 27  # After sidebar
    content_width = cols - content_x - 1
    
    # Clear content area
    clear_content_area(content_x, content_width, lines)
    
    # Title
    move_cursor(content_x + 2, 4)
    print(f"{Colors.BOLD}{Colors.BLUE}📄 documents{Colors.RESET}")
    
    # Subtitle
    move_cursor(content_x + 2, 5)
    print(f"{Colors.DIM}intelligent document management{Colors.RESET}")
    
    # Document submenu options
    options = [
        ("1", "browse documents", "view and manage documents"),
        ("2", "search", "full-text document search"),
        ("3", "upload", "upload new documents"),
        ("4", "ocr scanner", "extract text from images"),
        ("5", "invoice processor", "process invoices with ai"),
        ("6", "tag manager", "manage document tags"),
        ("7", "analytics", "document statistics"),
    ]
    
    # Get selected index from menu_state
    if not hasattr(menu_state, 'documents_index'):
        menu_state.documents_index = 0
    
    # Display options
    y_pos = 7
    for i, (key, name, desc) in enumerate(options):
        move_cursor(content_x + 2, y_pos)
        
        if i == menu_state.documents_index:
            # Selected item - highlight with orange background
            print(f"{Colors.BG_ORANGE}{Colors.WHITE} [{key}] {name:<30} {Colors.RESET}")
        else:
            # Normal item
            print(f" [{key}] {name:<30}")
        
        # Description below
        move_cursor(content_x + 6, y_pos + 1)
        print(f"{Colors.DIM}{desc}{Colors.RESET}")
        
        y_pos += 3
    
    # Instructions at bottom
    move_cursor(content_x + 2, lines - 3)
    print(f"{Colors.DIM}↑↓ navigate | enter select | esc back{Colors.RESET}")
    
    sys.stdout.flush()

def handle_documents_navigation(menu_state, key, Colors):
    """Handle navigation within documents submenu"""
    options_count = 7  # Number of menu items
    
    if key == '\x1b[A':  # Up arrow
        if menu_state.documents_index > 0:
            menu_state.documents_index -= 1
            draw_documents_submenu(menu_state, Colors)
            
    elif key == '\x1b[B':  # Down arrow
        if menu_state.documents_index < options_count - 1:
            menu_state.documents_index += 1
            draw_documents_submenu(menu_state, Colors)
            
    elif key == '\r' or key == '\n':  # Enter
        # Handle selection
        if menu_state.documents_index == 4:  # Invoice processor
            launch_invoice_processor(menu_state, Colors)
        else:
            # Show coming soon message
            show_temp_message(f"Feature coming soon!", Colors)
            
    elif key in '1234567':
        # Direct number selection
        idx = int(key) - 1
        if 0 <= idx < options_count:
            menu_state.documents_index = idx
            draw_documents_submenu(menu_state, Colors)
            
            # Auto-select if it's a number key
            if idx == 4:  # Invoice processor
                launch_invoice_processor(menu_state, Colors)
            else:
                show_temp_message(f"Feature coming soon!", Colors)
                
    elif key == '\x1b' or key == 'q':  # ESC or q to exit
        menu_state.in_submenu = None
        return False  # Exit submenu
        
    return True  # Continue in submenu

def launch_invoice_processor(menu_state, Colors):
    """Launch the invoice processor"""
    try:
        # Clear screen and run invoice processor
        sys.stdout.write("\033[2J\033[H")
        from invoice_processor_cli import InvoiceProcessorCLI
        processor = InvoiceProcessorCLI()
        processor.run()
        
        # Return to documents menu after
        sys.stdout.write("\033[2J\033[H")
        # The main loop will redraw everything
        
    except Exception as e:
        show_temp_message(f"Error: {e}", Colors)

def show_temp_message(msg, Colors):
    """Show temporary message in content area"""
    cols, lines = os.get_terminal_size()
    content_x = 27
    
    move_cursor(content_x + 2, lines - 5)
    print(f"{Colors.YELLOW}{msg}{Colors.RESET}")
    sys.stdout.flush()
    time.sleep(2)
    
def clear_content_area(content_x, content_width, lines):
    """Clear the content area"""
    for y in range(3, lines - 1):
        move_cursor(content_x, y)
        print(' ' * content_width, end='')
    sys.stdout.flush()

def move_cursor(x, y):
    """Move cursor to position"""
    sys.stdout.write(f"\033[{y};{x}H")
    sys.stdout.flush()