"""
UNIBOS TUI Header Component
V527-style header with orange background and system info
"""

import sys
from datetime import datetime
from typing import Optional

from core.clients.cli.framework.ui import Colors, get_terminal_size, move_cursor


class Header:
    """Header component for TUI"""

    def __init__(self, config):
        """Initialize header with config"""
        self.config = config

    def draw(self, breadcrumb: str = "", username: str = ""):
        """
        Draw v527-style header with orange background

        Args:
            breadcrumb: Navigation breadcrumb
            username: Current username
        """
        cols, _ = get_terminal_size()

        # Clear header line
        sys.stdout.write('\033[1;1H\033[2K')

        # Full orange background
        move_cursor(1, 1)
        sys.stdout.write(f"{Colors.BG_ORANGE}{' ' * cols}{Colors.RESET}")
        sys.stdout.flush()

        # Left side: Icon + Title + Version + Breadcrumb
        title_text = f"  🪐 {self.config.title}"
        if self.config.version:
            title_text += f" {self.config.version}"
        if breadcrumb and self.config.show_breadcrumbs:
            # Make breadcrumb lowercase if config says so
            if self.config.lowercase_ui:
                breadcrumb = breadcrumb.lower()
            title_text += f"  ›  {breadcrumb}"

        # Apply lowercase if configured
        if self.config.lowercase_ui:
            title_text = title_text.lower()

        move_cursor(1, 1)
        sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD}{title_text}{Colors.RESET}")

        # Right side elements
        right_elements = []

        # Time (if enabled)
        if self.config.show_time:
            time_str = datetime.now().strftime("%H:%M")
            right_elements.append(time_str)

        # Username
        if username:
            right_elements.append(username)

        # Window controls (decorative)
        right_elements.append("[_] [□] [X]")

        # Draw right side
        if right_elements:
            right_text = " | ".join(right_elements)
            right_pos = cols - len(right_text) - 2
            move_cursor(right_pos, 1)
            sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.BLACK}{right_text}{Colors.RESET}")

        sys.stdout.flush()