"""
Sidebar navigation fix for UNIBOS
Complete rewrite of sidebar drawing and navigation logic
"""

def draw_sidebar_simple(menu_state, Colors, sidebar_width=25):
    """
    Simple sidebar drawing without caching - always draws complete sidebar
    """
    import sys
    from emoji_safe_slice import emoji_safe_slice
    
    # Get terminal size
    try:
        import os
        cols, lines = os.get_terminal_size()
    except:
        cols, lines = 80, 24
    
    # CRITICAL: Double-check submenu state
    # Sometimes the state might be lingering, force clear it
    if menu_state.in_submenu == '' or menu_state.in_submenu == 'None':
        menu_state.in_submenu = None
    
    # Check if sidebar is dimmed
    is_dimmed = menu_state.in_submenu is not None
    text_color = Colors.DIM if is_dimmed else Colors.WHITE
    title_color = Colors.DIM if is_dimmed else Colors.CYAN
    
    # CRITICAL FIX: When not in submenu, force no highlights
    force_no_highlights = (menu_state.in_submenu is None or menu_state.in_submenu == '')
    
    # Clear entire sidebar area first (starting from line 2 now)
    for y in range(2, lines - 1):
        sys.stdout.write(f"\033[{y};1H{Colors.BG_DARK}{' ' * sidebar_width}{Colors.RESET}")
    
    # Draw MODULES section (moved up by 1 line)
    y_pos = 3
    sys.stdout.write(f"\033[{y_pos};2H{Colors.BG_DARK}{Colors.BOLD}{title_color} modules {Colors.RESET}")
    
    y_pos = 5
    # Show all modules without limiting (sidebar can scroll)
    for i, (key, name, desc, available, action) in enumerate(menu_state.modules):
        if y_pos >= lines - 1:
            break
            
        # Clear the line first
        sys.stdout.write(f"\033[{y_pos};1H{Colors.BG_DARK}{' ' * sidebar_width}{Colors.RESET}")
        
        # Draw the item
        safe_name = emoji_safe_slice(name, 22)
        # Check if this is the active module submenu
        is_active_module = False
        # Modules should never be highlighted when in submenu
        # They should only be dimmed, not highlighted
            
        if (menu_state.current_section == 0 and i == menu_state.selected_index and not is_dimmed) or is_active_module:
            # Selected item or active module
            if is_active_module:
                # Use lighter orange for active submenu
                sys.stdout.write(f"\033[{y_pos};1H\033[48;2;255;200;150m{' ' * sidebar_width}{Colors.RESET}")
                sys.stdout.write(f"\033[{y_pos};2H\033[48;2;255;200;150m{Colors.BLACK} {safe_name}{Colors.RESET}")
            else:
                # Normal selection
                sys.stdout.write(f"\033[{y_pos};1H{Colors.BG_ORANGE}{' ' * sidebar_width}{Colors.RESET}")
                sys.stdout.write(f"\033[{y_pos};2H{Colors.BG_ORANGE}{Colors.WHITE} {safe_name}{Colors.RESET}")
        else:
            # Normal item
            sys.stdout.write(f"\033[{y_pos};2H{Colors.BG_DARK}{text_color} {safe_name}{Colors.RESET}")
        
        y_pos += 1
    
    # Draw TOOLS section
    tools_start_y = y_pos + 2
    if tools_start_y < lines - 1:
        sys.stdout.write(f"\033[{tools_start_y};2H{Colors.BG_DARK}{Colors.BOLD}{title_color} tools {Colors.RESET}")
        
        y_pos = tools_start_y + 2
        for i, (key, name, desc, available, action) in enumerate(menu_state.tools):
            if y_pos >= lines - 1:
                break
                
            # Clear the line first
            sys.stdout.write(f"\033[{y_pos};1H{Colors.BG_DARK}{' ' * sidebar_width}{Colors.RESET}")
            
            # Draw the item
            safe_name = emoji_safe_slice(name, 22)
            # Check if this is the active submenu item
            is_active_submenu = False
            # NEVER highlight if we're in main menu
            if not force_no_highlights:
                # Only check for REAL submenus (not simple module/tool displays)
                # Real submenus are: administration, web_forge, code_forge
                if menu_state.in_submenu is not None and menu_state.in_submenu != '':
                    # Only these have actual submenu implementations
                    if menu_state.in_submenu == 'administration' and key == 'administration':
                        is_active_submenu = True
                    elif menu_state.in_submenu == 'web_forge' and key == 'web_ui':
                        is_active_submenu = True
                    elif menu_state.in_submenu == 'code_forge' and key == 'code_forge':
                        is_active_submenu = True
                    # Note: Other tools like system_scrolls, castle_guard etc. 
                    # are simple displays, not real submenus, so don't highlight them
                
            if (menu_state.current_section == 1 and i == menu_state.selected_index and not is_dimmed) or is_active_submenu:
                # Selected item or active submenu
                if is_active_submenu:
                    # Use lighter orange for active submenu
                    sys.stdout.write(f"\033[{y_pos};1H\033[48;2;255;200;150m{' ' * sidebar_width}{Colors.RESET}")
                    sys.stdout.write(f"\033[{y_pos};2H\033[48;2;255;200;150m{Colors.BLACK} {safe_name}{Colors.RESET}")
                else:
                    # Normal selection
                    sys.stdout.write(f"\033[{y_pos};1H{Colors.BG_ORANGE}{' ' * sidebar_width}{Colors.RESET}")
                    sys.stdout.write(f"\033[{y_pos};2H{Colors.BG_ORANGE}{Colors.WHITE} {safe_name}{Colors.RESET}")
            else:
                # Normal item
                sys.stdout.write(f"\033[{y_pos};2H{Colors.BG_DARK}{text_color} {safe_name}{Colors.RESET}")
            
            y_pos += 1
    
    # Draw DEV TOOLS section
    dev_tools_start_y = y_pos + 2
    if dev_tools_start_y < lines - 1:
        sys.stdout.write(f"\033[{dev_tools_start_y};2H{Colors.BG_DARK}{Colors.BOLD}{title_color} dev tools {Colors.RESET}")
        
        y_pos = dev_tools_start_y + 2
        for i, (key, name, desc, available, action) in enumerate(menu_state.dev_tools):
            if y_pos >= lines - 1:
                break
                
            # Clear the line first
            sys.stdout.write(f"\033[{y_pos};1H{Colors.BG_DARK}{' ' * sidebar_width}{Colors.RESET}")
            
            # Draw the item
            safe_name = emoji_safe_slice(name, 22)
            # Check if this is an active dev tool submenu
            is_active_dev_tool = False
            # NEVER highlight if we're in main menu
            if not force_no_highlights:
                # Only check for REAL submenus with actual menu implementations
                if menu_state.in_submenu is not None and menu_state.in_submenu != '':
                    # Only these have actual submenu implementations
                    if menu_state.in_submenu == 'version_manager' and key == 'version_manager':
                        is_active_dev_tool = True
                    elif menu_state.in_submenu == 'ai_builder' and key == 'ai_builder':
                        is_active_dev_tool = True
                    # Note: database_setup is a wizard, not a persistent submenu
                    # so it shouldn't be highlighted in the sidebar
            
            if (menu_state.current_section == 2 and i == menu_state.selected_index and not is_dimmed) or is_active_dev_tool:
                # Selected item or active submenu
                if is_active_dev_tool:
                    # Use lighter orange for active submenu
                    sys.stdout.write(f"\033[{y_pos};1H\033[48;2;255;200;150m{' ' * sidebar_width}{Colors.RESET}")
                    sys.stdout.write(f"\033[{y_pos};2H\033[48;2;255;200;150m{Colors.BLACK} {safe_name}{Colors.RESET}")
                else:
                    # Normal selection
                    sys.stdout.write(f"\033[{y_pos};1H{Colors.BG_ORANGE}{' ' * sidebar_width}{Colors.RESET}")
                    sys.stdout.write(f"\033[{y_pos};2H{Colors.BG_ORANGE}{Colors.WHITE} {safe_name}{Colors.RESET}")
            else:
                # Normal item
                sys.stdout.write(f"\033[{y_pos};2H{Colors.BG_DARK}{text_color} {safe_name}{Colors.RESET}")
            
            y_pos += 1
    
    # Draw vertical separator
    for y in range(2, lines - 1):  # Start from line 2 to match content area
        sys.stdout.write(f"\033[{y};{sidebar_width + 1}H{Colors.DIM}│{Colors.RESET}")
    
    # Force flush to ensure everything is rendered
    sys.stdout.flush()
    
    # Store section positions for navigation
    menu_state.tools_start_y = tools_start_y
    menu_state.dev_tools_start_y = dev_tools_start_y


def simple_navigation_handler(menu_state, key, selected_module, selected_tool, selected_dev_tool):
    """
    Simple navigation handler without caching issues
    Returns: (selected_module, selected_tool, selected_dev_tool, needs_redraw)
    """
    needs_redraw = False
    
    if key == '\x1b[A':  # Up arrow
        if menu_state.current_section == 0:  # modules
            if menu_state.selected_index > 0:
                menu_state.selected_index -= 1
                selected_module = menu_state.selected_index
            else:
                # Wrap to bottom of dev tools
                menu_state.current_section = 2
                menu_state.selected_index = len(menu_state.dev_tools) - 1
                selected_dev_tool = menu_state.selected_index
            needs_redraw = True
            
        elif menu_state.current_section == 1:  # tools
            if menu_state.selected_index > 0:
                menu_state.selected_index -= 1
                selected_tool = menu_state.selected_index
            else:
                # Wrap to bottom of modules
                menu_state.current_section = 0
                menu_state.selected_index = len(menu_state.modules) - 1
                selected_module = menu_state.selected_index
            needs_redraw = True
            
        elif menu_state.current_section == 2:  # dev tools
            if menu_state.selected_index > 0:
                menu_state.selected_index -= 1
                selected_dev_tool = menu_state.selected_index
            else:
                # Wrap to bottom of tools
                menu_state.current_section = 1
                menu_state.selected_index = len(menu_state.tools) - 1
                selected_tool = menu_state.selected_index
            needs_redraw = True
            
    elif key == '\x1b[B':  # Down arrow
        if menu_state.current_section == 0:  # modules
            if menu_state.selected_index < len(menu_state.modules) - 1:
                menu_state.selected_index += 1
                selected_module = menu_state.selected_index
            else:
                # Wrap to top of tools
                menu_state.current_section = 1
                menu_state.selected_index = 0
                selected_tool = 0
            needs_redraw = True
            
        elif menu_state.current_section == 1:  # tools
            if menu_state.selected_index < len(menu_state.tools) - 1:
                menu_state.selected_index += 1
                selected_tool = menu_state.selected_index
            else:
                # Wrap to top of dev tools
                menu_state.current_section = 2
                menu_state.selected_index = 0
                selected_dev_tool = 0
            needs_redraw = True
            
        elif menu_state.current_section == 2:  # dev tools
            if menu_state.selected_index < len(menu_state.dev_tools) - 1:
                menu_state.selected_index += 1
                selected_dev_tool = menu_state.selected_index
            else:
                # Wrap to top of modules
                menu_state.current_section = 0
                menu_state.selected_index = 0
                selected_module = 0
            needs_redraw = True
            
    elif key == '\t':  # Tab key
        if menu_state.current_section == 0:
            menu_state.current_section = 1
            menu_state.selected_index = 0
            selected_tool = 0
        elif menu_state.current_section == 1:
            menu_state.current_section = 2
            menu_state.selected_index = 0
            selected_dev_tool = 0
        else:
            menu_state.current_section = 0
            menu_state.selected_index = 0
            selected_module = 0
        needs_redraw = True
    
    return selected_module, selected_tool, selected_dev_tool, needs_redraw