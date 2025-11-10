#!/usr/bin/env python3
"""
CLI Context Manager - Centralized UI State Management
======================================================
Provides a single source of truth for CLI UI state management,
similar to the web UI's context processors but for terminal interface.

This module centralizes:
- Sidebar content and state
- Content area management
- Module registration and info
- Navigation state
- Screen refresh logic
"""

import sys
import time
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

# Import colors from main (we'll use the existing color definitions)
try:
    from main import Colors
except ImportError:
    # Fallback color definitions
    class Colors:
        RESET = "\033[0m"
        BOLD = "\033[1m"
        DIM = "\033[2m"
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        GRAY = "\033[90m"
        ORANGE = "\033[38;5;208m"
        BG_GRAY = "\033[48;5;240m"
        BG_ORANGE = "\033[48;5;208m"
        BG_DARK = "\033[48;5;234m"
        BG_CONTENT = "\033[48;5;236m"


class UISection(Enum):
    """UI sections enum"""
    MODULES = 0
    TOOLS = 1
    DEV_TOOLS = 2


@dataclass
class MenuItem:
    """Represents a menu item in the sidebar"""
    key: str
    name: str
    description: str
    available: bool = True
    action: Optional[Callable] = None
    icon: str = ""
    
    def __hash__(self):
        return hash(self.key)


@dataclass
class UIState:
    """Represents the current UI state"""
    current_section: UISection = UISection.MODULES
    selected_index: int = 0
    in_submenu: Optional[str] = None
    submenu_index: int = 0
    is_language_menu: bool = False
    language_index: int = 0
    
    # Terminal dimensions
    cols: int = 80
    lines: int = 24
    
    # Layout constants
    sidebar_width: int = 25
    content_start_x: int = 27
    header_height: int = 3
    footer_height: int = 1
    
    # Caching for performance
    last_update_time: float = 0
    needs_full_redraw: bool = True
    sidebar_cache: Dict[str, str] = field(default_factory=dict)
    content_cache: Dict[str, Any] = field(default_factory=dict)


class ContentRenderer:
    """Base class for content renderers"""
    
    def render(self, context: 'CLIContext', x: int, y: int, width: int, height: int):
        """Render content in the specified area"""
        raise NotImplementedError
    
    def clear(self, x: int, y: int, width: int, height: int):
        """Clear the content area completely"""
        # Clear only the specified content area, not the entire screen
        # This prevents UI disruption while ensuring complete clearing
        
        # Clear each row in the specified area thoroughly
        for row in range(y, min(y + height + 5, 50)):  # Add buffer rows and reasonable limit
            # Move to position and write spaces to clear content
            sys.stdout.write(f"\033[{row};{x}H")  # Move to position
            sys.stdout.write(" " * width)  # Write spaces to clear visible content
            
            # Also use ANSI clear to end of line for complete clearing
            sys.stdout.write(f"\033[{row};{x}H\033[K")  # Move back and clear to end of line
        
        # Ensure cursor is positioned correctly after clearing
        sys.stdout.write(f"\033[{y};{x}H")
        sys.stdout.flush()


class ModuleInfoRenderer(ContentRenderer):
    """Default renderer for module information"""
    
    def render(self, context: 'CLIContext', x: int, y: int, width: int, height: int):
        """Render module information"""
        module = context.get_current_item()
        if not module:
            return
        
        # Clear area first
        self.clear(x, y, width, height)
        
        # Draw title with icon
        icon = module.icon if hasattr(module, 'icon') and module.icon else "📦"
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.CYAN}{icon} {module.name}{Colors.RESET}")
        sys.stdout.write(f"\033[{y + 1};{x}H{Colors.DIM}{'─' * min(40, width - 2)}{Colors.RESET}")
        
        # Draw description
        y_pos = y + 3
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.CYAN}{module.description}{Colors.RESET}")
        
        # Module info
        y_pos += 2
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}module information:{Colors.RESET}")
        y_pos += 1
        
        # Draw status
        status = "✓ ready" if module.available else "⏳ coming soon"
        color = Colors.GREEN if module.available else Colors.YELLOW
        sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}status:{Colors.RESET} {color}{status}{Colors.RESET}")
        y_pos += 1
        
        # Draw key
        sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}key:{Colors.RESET} {module.key}")
        y_pos += 1
        
        # Add a note about the module
        if module.available:
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}press enter to open this module{Colors.RESET}")
        else:
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}this module will be available soon{Colors.RESET}")
        
        # Navigation hints
        sys.stdout.write(f"\033[{y + height - 3};{x}H{Colors.BOLD}navigation:{Colors.RESET}")
        sys.stdout.write(f"\033[{y + height - 2};{x + 2}H{Colors.DIM}↑↓ browse | enter select | q quit{Colors.RESET}")
        
        sys.stdout.flush()


class CLIContext:
    """
    Central context manager for CLI UI
    Manages all UI state and provides methods for consistent rendering
    """
    
    def __init__(self):
        self.state = UIState()
        self.modules: List[MenuItem] = []
        self.tools: List[MenuItem] = []
        self.dev_tools: List[MenuItem] = []
        self.content_renderers: Dict[str, ContentRenderer] = {}
        self.default_renderer = ModuleInfoRenderer()
        
        # Performance optimization
        self._last_sidebar_key = None
        self._sidebar_buffer = []
        
        # Initialize default items
        self._initialize_default_items()
    
    def _initialize_default_items(self):
        """Initialize default menu items"""
        # Modules
        self.modules = [
            MenuItem("recaria", "recaria", "consciousness exploration", True, icon="🦋"),
            MenuItem("birlikteyiz", "birlikteyiz", "emergency mesh network", True, icon="🤝"),
            MenuItem("kisisel", "kişisel enflasyon", "personal inflation tracker", True, icon="📊"),
            MenuItem("currencies", "currencies", "live exchange rates", True, icon="💱"),
            MenuItem("wimm", "wimm", "financial manager", True, icon="💸"),
            MenuItem("wims", "wims", "stock manager", True, icon="📦"),
            MenuItem("cctv", "cctv", "camera system", True, icon="📹"),
            MenuItem("documents", "documents", "document manager", True, icon="📄"),
        ]
        
        # Tools
        self.tools = [
            MenuItem("system_info", "system information", "view system details", True, icon="📊"),
            MenuItem("security_tools", "security tools", "security utilities", True, icon="🔒"),
            MenuItem("web_interface", "web interface", "browser ui", True, icon="🌐"),
        ]
        
        # Dev tools
        self.dev_tools = [
            MenuItem("ai_builder", "ai builder", "ai development tools", True, icon="🤖"),
            MenuItem("web_forge", "web forge", "web development", True, icon="🌐"),
            MenuItem("version_manager", "version manager", "version control", True, icon="📊"),
        ]
    
    def register_module(self, item: MenuItem, section: UISection = UISection.MODULES):
        """Register a new module/tool"""
        if section == UISection.MODULES:
            if item not in self.modules:
                self.modules.append(item)
        elif section == UISection.TOOLS:
            if item not in self.tools:
                self.tools.append(item)
        elif section == UISection.DEV_TOOLS:
            if item not in self.dev_tools:
                self.dev_tools.append(item)
        
        self.state.needs_full_redraw = True
    
    def register_content_renderer(self, key: str, renderer: ContentRenderer):
        """Register a custom content renderer for a specific module/submenu"""
        self.content_renderers[key] = renderer
    
    def get_current_section_items(self) -> List[MenuItem]:
        """Get items for the current section"""
        if self.state.current_section == UISection.MODULES:
            return self.modules
        elif self.state.current_section == UISection.TOOLS:
            return self.tools
        else:
            return self.dev_tools
    
    def get_current_item(self) -> Optional[MenuItem]:
        """Get the currently selected item"""
        items = self.get_current_section_items()
        if 0 <= self.state.selected_index < len(items):
            return items[self.state.selected_index]
        return None
    
    def update_terminal_size(self):
        """Update terminal dimensions"""
        import shutil
        try:
            cols, lines = shutil.get_terminal_size((80, 24))
            if cols != self.state.cols or lines != self.state.lines:
                self.state.cols = cols
                self.state.lines = lines
                self.state.needs_full_redraw = True
        except:
            pass
    
    def move_cursor(self, x: int, y: int):
        """Move cursor to position"""
        sys.stdout.write(f"\033[{y};{x}H")
    
    def clear_line(self, y: int, start_x: int = 1, end_x: Optional[int] = None):
        """Clear a line from start_x to end_x"""
        if end_x is None:
            end_x = self.state.cols
        self.move_cursor(start_x, y)
        sys.stdout.write(' ' * (end_x - start_x))
    
    def render_sidebar(self):
        """Render the sidebar with current state"""
        # Check if we need to redraw
        cache_key = f"{self.state.current_section}_{self.state.selected_index}_{self.state.in_submenu}"
        
        if not self.state.needs_full_redraw and cache_key == self._last_sidebar_key:
            return  # No need to redraw
        
        self._last_sidebar_key = cache_key
        is_dimmed = self.state.in_submenu is not None
        
        # Build sidebar buffer
        buffer = []
        sidebar_width = self.state.sidebar_width
        
        # Clear sidebar area with background
        for y in range(3, self.state.lines - 1):
            buffer.append(f"\033[{y};1H{Colors.BG_DARK}{' ' * sidebar_width}{Colors.RESET}")
        
        # Render sections
        y_pos = 4
        
        # Modules section
        buffer.append(f"\033[{y_pos};2H{Colors.BG_DARK}{Colors.BOLD}{Colors.ORANGE if not is_dimmed else Colors.DIM} modules{Colors.RESET}")
        y_pos += 2
        
        for i, item in enumerate(self.modules):
            if y_pos >= self.state.lines - 1:
                break
            
            is_selected = (self.state.current_section == UISection.MODULES and 
                          i == self.state.selected_index and not is_dimmed)
            
            if is_selected:
                buffer.append(f"\033[{y_pos};1H{Colors.BG_ORANGE}{' ' * sidebar_width}{Colors.RESET}")
                buffer.append(f"\033[{y_pos};2H{Colors.BG_ORANGE}{Colors.WHITE} {item.name[:22]:<22}{Colors.RESET}")
            else:
                text_color = Colors.DIM if is_dimmed else Colors.WHITE
                buffer.append(f"\033[{y_pos};2H{Colors.BG_DARK}{text_color} {item.name[:22]:<22}{Colors.RESET}")
            y_pos += 1
        
        y_pos += 2  # Space between sections
        
        # Tools section
        if y_pos < self.state.lines - 1:
            buffer.append(f"\033[{y_pos};2H{Colors.BG_DARK}{Colors.BOLD}{Colors.ORANGE if not is_dimmed else Colors.DIM} tools{Colors.RESET}")
            y_pos += 2
            
            for i, item in enumerate(self.tools):
                if y_pos >= self.state.lines - 1:
                    break
                
                is_selected = (self.state.current_section == UISection.TOOLS and 
                              i == self.state.selected_index and not is_dimmed)
                
                if is_selected:
                    buffer.append(f"\033[{y_pos};1H{Colors.BG_ORANGE}{' ' * sidebar_width}{Colors.RESET}")
                    buffer.append(f"\033[{y_pos};2H{Colors.BG_ORANGE}{Colors.WHITE} {item.name[:22]:<22}{Colors.RESET}")
                else:
                    text_color = Colors.DIM if is_dimmed else Colors.WHITE
                    buffer.append(f"\033[{y_pos};2H{Colors.BG_DARK}{text_color} {item.name[:22]:<22}{Colors.RESET}")
                y_pos += 1
        
        y_pos += 2  # Space between sections
        
        # Dev tools section
        if y_pos < self.state.lines - 1:
            buffer.append(f"\033[{y_pos};2H{Colors.BG_DARK}{Colors.BOLD}{Colors.ORANGE if not is_dimmed else Colors.DIM} dev tools{Colors.RESET}")
            y_pos += 2
            
            for i, item in enumerate(self.dev_tools):
                if y_pos >= self.state.lines - 1:
                    break
                
                is_selected = (self.state.current_section == UISection.DEV_TOOLS and 
                              i == self.state.selected_index and not is_dimmed)
                
                if is_selected:
                    buffer.append(f"\033[{y_pos};1H{Colors.BG_ORANGE}{' ' * sidebar_width}{Colors.RESET}")
                    buffer.append(f"\033[{y_pos};2H{Colors.BG_ORANGE}{Colors.WHITE} {item.name[:22]:<22}{Colors.RESET}")
                else:
                    text_color = Colors.DIM if is_dimmed else Colors.WHITE
                    buffer.append(f"\033[{y_pos};2H{Colors.BG_DARK}{text_color} {item.name[:22]:<22}{Colors.RESET}")
                y_pos += 1
        
        # Write buffer
        sys.stdout.write(''.join(buffer))
        
        # Draw separator
        for y in range(3, self.state.lines - 1):
            sys.stdout.write(f"\033[{y};{sidebar_width + 1}H{Colors.DIM}│{Colors.RESET}")
        
        sys.stdout.flush()
    
    def render_content(self):
        """Render the content area based on current state"""
        x = self.state.content_start_x
        y = 3
        width = self.state.cols - x - 1
        height = self.state.lines - y - self.state.footer_height
        
        # Get appropriate renderer
        renderer = None
        
        # First check if we're in a submenu
        if self.state.in_submenu and self.state.in_submenu in self.content_renderers:
            renderer = self.content_renderers[self.state.in_submenu]
        else:
            # Try to get a preview renderer for the currently selected item
            current_item = self.get_current_item()
            if current_item and current_item.key in self.content_renderers:
                renderer = self.content_renderers[current_item.key]
            else:
                # Fall back to default renderer
                renderer = self.default_renderer
        
        # Render content
        renderer.render(self, x, y, width, height)
    
    def clear_content(self):
        """Clear the content area completely"""
        x = self.state.content_start_x
        width = self.state.cols - x - 1
        
        # Clear all lines in content area more thoroughly
        for y in range(3, min(self.state.lines - 1, 50)):  # Reasonable limit
            # Move to content start and clear to end of line
            sys.stdout.write(f"\033[{y};{x}H\033[K")
        
        # Redraw separator after clearing
        for y in range(3, min(self.state.lines - 1, 50)):
            sys.stdout.write(f"\033[{y};{self.state.sidebar_width + 1}H{Colors.DIM}│{Colors.RESET}")
        
        sys.stdout.flush()
    
    def navigate_up(self):
        """Navigate up in current section"""
        items = self.get_current_section_items()
        if items and self.state.selected_index > 0:
            self.state.selected_index -= 1
            return True
        return False
    
    def navigate_down(self):
        """Navigate down in current section"""
        items = self.get_current_section_items()
        if items and self.state.selected_index < len(items) - 1:
            self.state.selected_index += 1
            return True
        return False
    
    def switch_section(self):
        """Switch to next section"""
        sections = list(UISection)
        current_idx = sections.index(self.state.current_section)
        next_idx = (current_idx + 1) % len(sections)
        self.state.current_section = sections[next_idx]
        self.state.selected_index = 0
        return True
    
    def enter_submenu(self, submenu_key: str):
        """Enter a submenu"""
        self.state.in_submenu = submenu_key
        self.state.submenu_index = 0
    
    def exit_submenu(self):
        """Exit current submenu"""
        self.state.in_submenu = None
        self.state.submenu_index = 0
    
    def refresh(self):
        """Refresh the entire UI"""
        self.update_terminal_size()
        
        if self.state.needs_full_redraw:
            # Full redraw needed
            self.render_sidebar()
            self.render_content()
            self.state.needs_full_redraw = False
        else:
            # Partial update
            current_time = time.time()
            if current_time - self.state.last_update_time > 0.03:  # 30ms debounce
                self.render_sidebar()
                self.render_content()
                self.state.last_update_time = current_time


# Singleton instance
_context = None

def get_cli_context() -> CLIContext:
    """Get or create the singleton CLI context"""
    global _context
    if _context is None:
        _context = CLIContext()
    return _context