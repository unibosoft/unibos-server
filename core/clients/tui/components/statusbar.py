"""
UNIBOS TUI Status Bar Component
Additional status bar for notifications and progress
"""

import sys
from typing import Optional

from core.clients.cli.framework.ui import Colors, get_terminal_size, move_cursor


class StatusBar:
    """Status bar component for notifications"""

    def __init__(self, config):
        """Initialize status bar with config"""
        self.config = config
        self.message = ""
        self.progress = None
        self.color = Colors.DIM

    def set_message(self, message: str, color: str = Colors.DIM):
        """Set status message"""
        self.message = message
        self.color = color
        self.draw()

    def set_progress(self, current: int, total: int, label: str = ""):
        """Set progress bar"""
        self.progress = (current, total, label)
        self.draw()

    def clear(self):
        """Clear status bar"""
        self.message = ""
        self.progress = None
        self.draw()

    def draw(self):
        """Draw status bar (line above footer)"""
        cols, lines = get_terminal_size()
        status_y = lines - 1  # One line above footer

        # Clear line
        move_cursor(1, status_y)
        sys.stdout.write(' ' * cols)

        if self.message:
            # Draw message
            move_cursor(2, status_y)
            text = self.message
            if self.config.lowercase_ui:
                text = text.lower()
            sys.stdout.write(f"{self.color}{text}{Colors.RESET}")

        elif self.progress:
            # Draw progress bar
            current, total, label = self.progress
            percentage = int((current / total) * 100) if total > 0 else 0

            # Progress bar width
            bar_width = 30
            filled = int((current / total) * bar_width) if total > 0 else 0

            # Build progress bar
            bar = "█" * filled + "░" * (bar_width - filled)

            # Draw
            move_cursor(2, status_y)
            text = f"{label} [{bar}] {percentage}% ({current}/{total})"
            if self.config.lowercase_ui:
                text = text.lower()
            sys.stdout.write(f"{Colors.CYAN}{text}{Colors.RESET}")

        sys.stdout.flush()