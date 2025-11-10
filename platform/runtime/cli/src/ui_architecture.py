#!/usr/bin/env python3
"""
UNIBOS UI Architecture - Clean, Modular Design
==============================================
This module provides a complete redesign of the unibos cli UI with:
- Clear separation of concerns
- No colored boxes/borders in content areas
- Proper screen refresh and rendering
- Modular architecture (header, sidebar, content, footer)
- Fix for Web Forge menu rendering issues
"""

import sys
import os
import time
import shutil
from typing import List, Tuple, Optional, Dict, Any

# ANSI color codes
class Colors:
    # Reset
    RESET = '\033[0m'
    
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    ORANGE = '\033[38;5;208m'
    
    # Bright text colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_ORANGE = '\033[48;5;208m'
    BG_GRAY = '\033[48;5;236m'
    BG_DARK = '\033[48;5;234m'  # Changed from 232 (black) to 234 (dark gray)
    
    # Text styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'

# UI Layout Constants
class Layout:
    HEADER_HEIGHT = 3
    SIDEBAR_WIDTH = 25
    SEPARATOR_WIDTH = 1
    CONTENT_START_X = SIDEBAR_WIDTH + SEPARATOR_WIDTH + 1
    FOOTER_HEIGHT = 1
    
    @staticmethod
    def get_terminal_size() -> Tuple[int, int]:
        """Get terminal dimensions safely"""
        try:
            cols, lines = shutil.get_terminal_size((80, 24))
            return max(80, cols), max(24, lines)
        except:
            return 80, 24
    
    @staticmethod
    def get_content_dimensions() -> Tuple[int, int, int, int]:
        """Get content area dimensions (x, y, width, height)"""
        cols, lines = Layout.get_terminal_size()
        x = Layout.CONTENT_START_X
        y = Layout.HEADER_HEIGHT + 1
        width = cols - x - 1  # Leave 1 column margin on right
        height = lines - Layout.HEADER_HEIGHT - Layout.FOOTER_HEIGHT - 1
        return x, y, width, height


class UIRenderer:
    """Base class for UI rendering with common utilities"""
    
    @staticmethod
    def move_cursor(x: int, y: int):
        """Move cursor to specific position"""
        sys.stdout.write(f'\033[{y};{x}H')
    
    @staticmethod
    def clear_line(y: int, start_x: int = 1, end_x: Optional[int] = None):
        """Clear a line from start_x to end_x"""
        cols, _ = Layout.get_terminal_size()
        if end_x is None:
            end_x = cols
        
        UIRenderer.move_cursor(start_x, y)
        sys.stdout.write(' ' * (end_x - start_x + 1))
    
    @staticmethod
    def clear_screen():
        """Clear entire screen"""
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()
    
    @staticmethod
    def hide_cursor():
        """Hide terminal cursor"""
        sys.stdout.write('\033[?25l')
    
    @staticmethod
    def show_cursor():
        """Show terminal cursor"""
        sys.stdout.write('\033[?25h')
    
    @staticmethod
    def flush():
        """Flush stdout buffer"""
        sys.stdout.flush()


class HeaderRenderer(UIRenderer):
    """Handles header rendering (lines 1-3)"""
    
    def __init__(self, title: str = "UNIBOS - Universal Basic Operating System", 
                 version: str = ""):
        self.title = title
        self.version = version
    
    def render(self):
        """Render the header"""
        cols, _ = Layout.get_terminal_size()
        
        # Line 1: Empty line (nothing)
        self.move_cursor(1, 1)
        sys.stdout.write(' ' * cols)
        
        # Line 2: Title and version with FULL orange background
        self.move_cursor(1, 2)
        sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{' ' * cols}{Colors.RESET}")
        
        # Center the title with proper format
        title_with_version = f"{self.title} {self.version}" if self.version else self.title
        title_len = len(title_with_version)
        title_x = max(1, (cols - title_len) // 2)
        
        self.move_cursor(title_x, 2)
        sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD}{title_with_version}{Colors.RESET}")
        
        # Add time on the right
        time_str = time.strftime("%H:%M:%S")
        time_x = cols - len(time_str) - 2
        self.move_cursor(time_x, 2)
        sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{time_str}{Colors.RESET}")
        
        # Line 3: Empty line as separator
        self.move_cursor(1, 3)
        sys.stdout.write(' ' * cols)
        
        self.flush()
    
    def update_time(self):
        """Update only the time in the header"""
        cols, _ = Layout.get_terminal_size()
        time_str = time.strftime("%H:%M:%S")
        time_x = cols - len(time_str) - 2
        
        # First clear the time area with orange background
        self.move_cursor(time_x, 2)
        sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{' ' * (len(time_str) + 2)}{Colors.RESET}")
        
        # Then write the new time
        self.move_cursor(time_x, 2)
        sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{time_str}{Colors.RESET}")
        self.flush()


class SidebarRenderer(UIRenderer):
    """Handles sidebar rendering (columns 1-25)"""
    
    def __init__(self):
        self.sections = []
        self.selected_section = 0
        self.selected_index = 0
        self.is_dimmed = False
    
    def add_section(self, title: str, items: List[Tuple[str, str]]):
        """Add a section to the sidebar"""
        self.sections.append({
            'title': title,
            'items': items
        })
    
    def render(self):
        """Render the sidebar"""
        cols, lines = Layout.get_terminal_size()
        
        # Clear sidebar area with dark background FROM THE BEGINNING (line 4)
        for y in range(4, lines - Layout.FOOTER_HEIGHT):
            self.move_cursor(1, y)
            sys.stdout.write(f"{Colors.BG_DARK}{' ' * Layout.SIDEBAR_WIDTH}{Colors.RESET}")
        
        # Render sections starting from line 5
        y_pos = 5
        
        for section_idx, section in enumerate(self.sections):
            # Section title
            if y_pos < lines - Layout.FOOTER_HEIGHT:
                self.move_cursor(2, y_pos)
                title_color = Colors.DIM if self.is_dimmed else Colors.ORANGE
                sys.stdout.write(f"{Colors.BG_DARK}{Colors.BOLD}{title_color} {section['title']} {Colors.RESET}")
                y_pos += 2
            
            # Section items
            for item_idx, (key, name) in enumerate(section['items']):
                if y_pos >= lines - Layout.FOOTER_HEIGHT:
                    break
                
                is_selected = (section_idx == self.selected_section and 
                             item_idx == self.selected_index and 
                             not self.is_dimmed)
                
                if is_selected:
                    # Selected item with orange background
                    self.move_cursor(1, y_pos)
                    sys.stdout.write(f"{Colors.BG_ORANGE}{' ' * Layout.SIDEBAR_WIDTH}{Colors.RESET}")
                    self.move_cursor(2, y_pos)
                    sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.WHITE} {name[:22]:<22}{Colors.RESET}")
                else:
                    # Normal item
                    text_color = Colors.DIM if self.is_dimmed else Colors.WHITE
                    self.move_cursor(2, y_pos)
                    sys.stdout.write(f"{Colors.BG_DARK}{text_color} {name[:22]:<22}{Colors.RESET}")
                
                y_pos += 1
            
            y_pos += 2  # Space between sections
        
        # Draw separator line
        for y in range(Layout.HEADER_HEIGHT + 1, lines - Layout.FOOTER_HEIGHT):
            self.move_cursor(Layout.SIDEBAR_WIDTH + 1, y)
            sys.stdout.write(f"{Colors.DIM}│{Colors.RESET}")
        
        self.flush()
    
    def update_selection(self, section: int, index: int):
        """Update selected item and re-render only affected lines"""
        old_section = self.selected_section
        old_index = self.selected_index
        
        self.selected_section = section
        self.selected_index = index
        
        # Re-render old selection
        self._render_item(old_section, old_index, False)
        
        # Re-render new selection
        self._render_item(section, index, True)
        
        self.flush()
    
    def _render_item(self, section_idx: int, item_idx: int, is_selected: bool):
        """Render a single sidebar item"""
        if section_idx >= len(self.sections):
            return
        
        section = self.sections[section_idx]
        if item_idx >= len(section['items']):
            return
        
        # Calculate Y position
        y_pos = Layout.HEADER_HEIGHT + 2
        for s_idx in range(section_idx):
            y_pos += 2  # Title
            y_pos += len(self.sections[s_idx]['items'])  # Items
            y_pos += 2  # Space
        
        y_pos += 2  # Current section title
        y_pos += item_idx  # Item position
        
        # Render the item
        _, name = section['items'][item_idx]
        
        if is_selected and not self.is_dimmed:
            self.move_cursor(1, y_pos)
            sys.stdout.write(f"{Colors.BG_ORANGE}{' ' * Layout.SIDEBAR_WIDTH}{Colors.RESET}")
            self.move_cursor(2, y_pos)
            sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.WHITE} {name[:22]:<22}{Colors.RESET}")
        else:
            self.move_cursor(1, y_pos)
            sys.stdout.write(f"{Colors.BG_DARK}{' ' * Layout.SIDEBAR_WIDTH}{Colors.RESET}")
            self.move_cursor(2, y_pos)
            text_color = Colors.DIM if self.is_dimmed else Colors.WHITE
            sys.stdout.write(f"{Colors.BG_DARK}{text_color} {name[:22]:<22}{Colors.RESET}")


class ContentRenderer(UIRenderer):
    """Handles content area rendering"""
    
    def clear(self):
        """Clear content area only, preserving sidebar"""
        x, y, width, height = Layout.get_content_dimensions()
        
        for line_y in range(y, y + height):
            self.move_cursor(x, line_y)
            sys.stdout.write(' ' * width)
        
        self.flush()
    
    def render_text(self, text: str, y_offset: int = 0, color: str = Colors.WHITE):
        """Render text in content area"""
        x, y, width, height = Layout.get_content_dimensions()
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if i + y_offset >= height:
                break
            
            self.move_cursor(x, y + y_offset + i)
            # Truncate line if too long
            if len(line) > width:
                line = line[:width-3] + '...'
            sys.stdout.write(f"{color}{line}{Colors.RESET}")
        
        self.flush()
    
    def render_menu(self, title: str, items: List[Tuple[str, str]], 
                    selected_index: int = 0, show_descriptions: bool = True):
        """Render a menu in the content area without boxes"""
        self.clear()
        
        x, y, width, height = Layout.get_content_dimensions()
        
        # Title
        self.move_cursor(x + 2, y)
        sys.stdout.write(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
        
        # Menu items
        y_offset = 2
        for i, (key, name) in enumerate(items):
            if y_offset >= height - 1:
                break
            
            self.move_cursor(x + 2, y + y_offset)
            
            if i == selected_index:
                # Selected item - no background, just arrow and bold text
                sys.stdout.write(f"{Colors.BOLD}{Colors.WHITE}▶ {name}{Colors.RESET}")
            else:
                sys.stdout.write(f"  {Colors.WHITE}{name}{Colors.RESET}")
            
            y_offset += 1
        
        self.flush()
    
    def render_web_forge_menu(self, options: List[Tuple[str, str, str]], 
                              selected_index: int = 0, env_status: Dict[str, Any] = None,
                              backend_status: Tuple[bool, Optional[int]] = (False, None),
                              frontend_status: Tuple[bool, Optional[int]] = (False, None)):
        """Render Web Forge menu without colored boxes - FIXED positioning"""
        self.clear()
        
        x, y, width, height = Layout.get_content_dimensions()
        
        # Title
        self.move_cursor(x + 2, y)
        sys.stdout.write(f"{Colors.BOLD}{Colors.BLUE}Web Forge{Colors.RESET}")
        
        # Server status (environment status removed per requirements)
        self.move_cursor(x + 2, y + 2)
        sys.stdout.write(f"{Colors.BOLD}Server Status:{Colors.RESET}")
        
        # Backend
        backend_running, backend_pid = backend_status
        backend_icon = "●" if backend_running else "○"
        backend_color = Colors.GREEN if backend_running else Colors.RED
        self.move_cursor(x + 20, y + 2)
        sys.stdout.write(f"{backend_color}{backend_icon}{Colors.RESET} Backend: {backend_color}{'Running' if backend_running else 'Stopped'}{Colors.RESET}")
        if backend_running and backend_pid:
            sys.stdout.write(f" {Colors.DIM}[{backend_pid}]{Colors.RESET}")
        
        # Frontend
        frontend_running, frontend_pid = frontend_status
        frontend_icon = "●" if frontend_running else "○"
        frontend_color = Colors.GREEN if frontend_running else Colors.RED
        self.move_cursor(x + 50, y + 2)
        sys.stdout.write(f"{frontend_color}{frontend_icon}{Colors.RESET} Frontend: {frontend_color}{'Running' if frontend_running else 'Stopped'}{Colors.RESET}")
        if frontend_running and frontend_pid:
            sys.stdout.write(f" {Colors.DIM}[{frontend_pid}]{Colors.RESET}")
        
        # Menu options with FIXED positioning
        y_offset = 4
        actual_index = 0
        
        # Pre-calculate all positions to ensure consistency
        menu_positions = {}  # Store position for each selectable item
        
        for key, title, desc in options:
            if y_offset >= height - 1:
                break
            
            if key == "separator":
                # Draw separator
                self.move_cursor(x + 2, y + y_offset)
                sys.stdout.write(f"{Colors.DIM}{'─' * min(width - 4, 60)}{Colors.RESET}")
                y_offset += 1
            elif key == "header":
                # Section header
                if y_offset > 5:  # Add space before headers
                    y_offset += 1
                self.move_cursor(x + 2, y + y_offset)
                sys.stdout.write(f"{Colors.BOLD}{Colors.YELLOW}{title}{Colors.RESET}")
                y_offset += 1  # Space after headers
            else:
                # Menu item - indent under headers for better hierarchy
                self.move_cursor(x + 4, y + y_offset)  # Indent menu items
                
                # Clear the entire line first to prevent overlap
                sys.stdout.write(' ' * (width - 6))  # Clear full line width
                self.move_cursor(x + 4, y + y_offset)  # Move back to start
                
                if actual_index == selected_index:
                    # Selected item - no background
                    # Fixed width display to prevent shifting
                    display_title = title[:30]  # Truncate if too long
                    padding = ' ' * (32 - len(display_title))
                    sys.stdout.write(f"{Colors.BOLD}{Colors.WHITE}▶ {display_title}{padding}{Colors.RESET}")
                else:
                    # Fixed width display to prevent shifting
                    display_title = title[:30]  # Truncate if too long
                    padding = ' ' * (32 - len(display_title))
                    sys.stdout.write(f"  {display_title}{padding}")
                
                actual_index += 1
            
            y_offset += 1  # ALWAYS increment y_offset after processing ANY option type
        
        self.flush()


class FooterRenderer(UIRenderer):
    """Handles footer rendering (last line)"""
    
    def render(self, hint_text: str = "↑↓:Navigate ←→:Switch Tab:Next Section Enter:Select Q:Quit"):
        """Render the footer"""
        cols, lines = Layout.get_terminal_size()
        
        # Clear footer line
        self.move_cursor(1, lines)
        sys.stdout.write(' ' * cols)
        
        # Render hint text centered
        hint_len = len(hint_text)
        hint_x = max(1, (cols - hint_len) // 2)
        
        self.move_cursor(hint_x, lines)
        sys.stdout.write(f"{Colors.DIM}{hint_text}{Colors.RESET}")
        
        self.flush()


class UnibosUI:
    """Main UI controller that coordinates all renderers"""
    
    def __init__(self):
        self.header = HeaderRenderer()
        self.sidebar = SidebarRenderer()
        self.content = ContentRenderer()
        self.footer = FooterRenderer()
        
        # Don't initialize with default sections - let main.py populate them
        # self._init_sidebar()  # Removed to prevent duplicate items
    
    def render_full_screen(self):
        """Render the complete UI"""
        UIRenderer.clear_screen()
        UIRenderer.hide_cursor()
        
        self.header.render()
        self.sidebar.render()
        self.footer.render()
        
        # Show default content
        self.content.render_text("Welcome to UNIBOS\n\nSelect a module from the sidebar to begin.", 2)
    
    def update_time(self):
        """Update only the time in the header"""
        self.header.update_time()
    
    def navigate(self, direction: str):
        """Handle navigation"""
        if direction == "up":
            if self.sidebar.selected_index > 0:
                self.sidebar.selected_index -= 1
            else:
                # Move to previous section
                if self.sidebar.selected_section > 0:
                    self.sidebar.selected_section -= 1
                    section = self.sidebar.sections[self.sidebar.selected_section]
                    self.sidebar.selected_index = len(section['items']) - 1
        
        elif direction == "down":
            section = self.sidebar.sections[self.sidebar.selected_section]
            if self.sidebar.selected_index < len(section['items']) - 1:
                self.sidebar.selected_index += 1
            else:
                # Move to next section
                if self.sidebar.selected_section < len(self.sidebar.sections) - 1:
                    self.sidebar.selected_section += 1
                    self.sidebar.selected_index = 0
        
        elif direction == "tab":
            # Move to next section
            self.sidebar.selected_section = (self.sidebar.selected_section + 1) % len(self.sidebar.sections)
            self.sidebar.selected_index = 0
        
        # Update sidebar
        self.sidebar.render()
    
    def show_web_forge(self):
        """Show Web Forge menu"""
        # Dim the sidebar
        self.sidebar.is_dimmed = True
        self.sidebar.render()
        
        # Sample Web Forge options
        options = [
            ("header", "━━━ Server Controls ━━━", ""),
            ("start_all", "Start All Services", "Launch backend and frontend"),
            ("stop_all", "Stop All Services", "Stop all running services"),
            ("separator", "", ""),
            ("header", "━━━ Individual Services ━━━", ""),
            ("start_backend", "Start Backend Only", "Django server on port 8000"),
            ("start_frontend", "Start Frontend Only", "Next.js on port 3000"),
            ("separator", "", ""),
            ("header", "━━━ Development Tools ━━━", ""),
            ("setup_wizard", "Setup Wizard", "Configure environment"),
            ("view_logs", "View Logs", "Show server logs"),
        ]
        
        # Render Web Forge menu
        self.content.render_web_forge_menu(
            options=options,
            selected_index=0,
            env_status={'all_good': True, 'summary': 'All dependencies installed'},
            backend_status=(True, 12345),
            frontend_status=(False, None)
        )
    
    def exit_submenu(self):
        """Exit from submenu and restore main view"""
        # Un-dim the sidebar
        self.sidebar.is_dimmed = False
        self.sidebar.render()
        
        # Clear content and show default
        self.content.clear()
        self.content.render_text("Welcome back to UNIBOS\n\nSelect a module from the sidebar to continue.", 2)
    
    def cleanup(self):
        """Cleanup UI on exit"""
        UIRenderer.clear_screen()
        UIRenderer.show_cursor()
        UIRenderer.move_cursor(1, 1)


# Example usage
if __name__ == "__main__":
    ui = UnibosUI()
    
    try:
        # Initial render
        ui.render_full_screen()
        
        # Simulate some interactions
        import time
        time.sleep(1)
        
        # Navigate down
        ui.navigate("down")
        time.sleep(0.5)
        
        # Show Web Forge
        ui.show_web_forge()
        time.sleep(2)
        
        # Exit submenu
        ui.exit_submenu()
        time.sleep(1)
        
    finally:
        ui.cleanup()