#!/usr/bin/env python3
"""
Standardized submenu handler for consistent tab navigation
All submenus should use this for clean entry/exit behavior
"""

import sys
import time

def enter_submenu(menu_state, submenu_name, clear_screen, draw_header, draw_sidebar, draw_footer, hide_cursor):
    """
    Standard entry procedure for any submenu
    - Clears screen
    - Redraws header
    - Forces sidebar redraw with dimmed state
    - Clears input buffer
    - Hides cursor
    """
    # Set submenu state
    menu_state.in_submenu = submenu_name
    
    # Clear screen and redraw everything fresh
    clear_screen()
    draw_header()
    
    # Force sidebar redraw to ensure dimmed state is applied
    menu_state.last_sidebar_cache_key = None
    draw_sidebar()
    
    # Clear input buffer to prevent leftover characters
    try:
        import termios
        for _ in range(3):
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)
            time.sleep(0.01)
    except:
        pass
    
    # Draw footer
    draw_footer()
    
    # Hide cursor for clean display
    hide_cursor()
    
    return True

def exit_submenu(menu_state, section, index, clear_screen, draw_main_screen, show_cursor):
    """
    Standard exit procedure from any submenu
    - Clears submenu state
    - Sets correct section and index
    - Clears screen
    - Redraws main screen
    - Shows cursor
    """
    # Clear submenu state
    menu_state.in_submenu = None
    
    # Set correct section and index for sidebar highlighting
    menu_state.current_section = section
    menu_state.selected_index = index
    
    # Clear screen and redraw main screen
    clear_screen()
    draw_main_screen()
    
    # Show cursor when back in main menu
    show_cursor()
    
    return True

def update_submenu_clock(draw_header_time_only, last_update_time):
    """
    Standard clock update for submenus
    Uses draw_header_time_only to prevent flickering
    Returns new update time if updated
    """
    current_time = time.time()
    if current_time - last_update_time >= 1.0:
        draw_header_time_only()
        return current_time
    return last_update_time

def handle_submenu_navigation(key, menu_state, options, index_attr, draw_header, draw_menu):
    """
    Standard navigation handler for submenu items
    - Up/Down arrow navigation
    - Redraws header and menu to prevent artifacts
    """
    # Get current index
    current_index = getattr(menu_state, index_attr)
    
    # Filter out headers and separators
    selectable_options = [(k, n, d) for k, n, d in options if k not in ["header", "separator"]]
    
    if key in ['\x1b[A', 'k', 'K']:  # Up arrow or k
        if current_index > 0:
            setattr(menu_state, index_attr, current_index - 1)
            draw_header()
            draw_menu()
            return True
    
    elif key in ['\x1b[B', 'j', 'J']:  # Down arrow or j
        if current_index < len(selectable_options) - 1:
            setattr(menu_state, index_attr, current_index + 1)
            draw_header()
            draw_menu()
            return True
    
    return False

def redraw_after_action(menu_state, submenu_name, clear_screen, draw_header, draw_sidebar, draw_menu, draw_footer):
    """
    Standard redraw after returning from a submenu action
    """
    # Ensure we're still in the submenu
    menu_state.in_submenu = submenu_name
    
    # Clear caches to force fresh redraw
    menu_state.last_sidebar_cache_key = None
    if hasattr(menu_state, 'last_content_cache_key'):
        menu_state.last_content_cache_key = None
    
    # Clear and redraw everything
    clear_screen()
    draw_header()
    draw_sidebar()
    draw_menu()
    draw_footer()
    
    # Force flush
    sys.stdout.flush()