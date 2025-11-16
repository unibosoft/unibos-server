"""
UNIBOS TUI Sidebar Component
V527-style multi-section sidebar with navigation
"""

import sys
from typing import List, Optional

from core.clients.cli.framework.ui import Colors, get_terminal_size, move_cursor


class Sidebar:
    """Sidebar component for TUI"""

    def __init__(self, config):
        """Initialize sidebar with config"""
        self.config = config
        self.width = config.sidebar_width

    def draw(self, sections: List, current_section: int, selected_index: int,
             in_submenu: bool = False):
        """
        Draw multi-section sidebar

        Args:
            sections: List of MenuSection objects
            current_section: Currently active section index
            selected_index: Selected item within current section
            in_submenu: Whether in submenu (dims sidebar)
        """
        cols, lines = get_terminal_size()
        y = 3  # Start after header and blank line

        for i, section in enumerate(sections):
            if y >= lines - 1:  # Leave room for footer
                break

            is_current = (i == current_section)
            is_dimmed = in_submenu or not is_current

            # Draw section
            y = self._draw_section(
                y_start=y,
                section=section,
                selected_index=selected_index if is_current else -1,
                is_dimmed=is_dimmed
            )

            # Add spacing between sections
            y += 1

    def _draw_section(self, y_start: int, section, selected_index: int,
                      is_dimmed: bool) -> int:
        """
        Draw a single section

        Args:
            y_start: Starting Y position
            section: MenuSection object
            selected_index: Selected item index (-1 for none)
            is_dimmed: Whether section should be dimmed

        Returns:
            Next Y position after this section
        """
        cols, lines = get_terminal_size()

        # Section header
        move_cursor(1, y_start)
        title = section.label
        if self.config.lowercase_ui:
            title = title.lower()

        # Draw section header with icon
        header_text = f" {section.icon} {title}" if hasattr(section, 'icon') else f" {title}"
        header_text = header_text[:self.width - 2].ljust(self.width - 2)

        sys.stdout.write(
            f"{Colors.BG_DARK}{Colors.ORANGE}{Colors.BOLD}"
            f"{header_text}"
            f"{Colors.RESET}"
        )

        # Section items
        y = y_start + 1
        for i, item in enumerate(section.items):
            if y >= lines - 1:
                break

            # Get item text
            if hasattr(item, 'icon'):
                item_text = f" {item.icon} {item.label}"
            else:
                item_text = f"  {item.label}"

            if self.config.lowercase_ui:
                item_text = item_text.lower()

            # Truncate if too long
            max_len = self.width - 3
            if len(item_text) > max_len:
                item_text = item_text[:max_len - 3] + "..."

            # Determine colors
            if i == selected_index and not is_dimmed:
                bg = Colors.BG_ORANGE
                fg = Colors.WHITE + Colors.BOLD
            else:
                bg = Colors.BG_DARK
                if is_dimmed:
                    fg = Colors.DIM
                elif not item.enabled:
                    fg = Colors.DIM
                else:
                    fg = Colors.WHITE

            # Draw item background
            move_cursor(1, y)
            sys.stdout.write(f"{bg}{' ' * self.width}{Colors.RESET}")

            # Draw item text
            move_cursor(2, y)

            # Add item number for quick select (0-9)
            if i < 10 and not is_dimmed:
                number_fg = Colors.YELLOW if i != selected_index else fg
                sys.stdout.write(f"{bg}{number_fg}{i}{Colors.RESET} ")
                move_cursor(4, y)

            sys.stdout.write(f"{bg}{fg}{item_text}{Colors.RESET}")

            y += 1

        sys.stdout.flush()
        return y