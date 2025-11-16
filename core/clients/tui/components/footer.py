"""
UNIBOS TUI Footer Component
V527-style footer with navigation hints and system status
"""

import sys
import socket
from datetime import datetime
from typing import Dict, Any, Optional

from core.clients.cli.framework.ui import Colors, get_terminal_size, move_cursor


class Footer:
    """Footer component for TUI"""

    def __init__(self, config):
        """Initialize footer with config"""
        self.config = config

    def draw(self, hints: str = "", status: Optional[Dict[str, Any]] = None):
        """
        Draw v527-style footer with hints and status

        Args:
            hints: Navigation hints text
            status: System status dict with hostname, time, date, online
        """
        cols, lines = get_terminal_size()

        # Full dark background
        move_cursor(1, lines)
        sys.stdout.write(f"{Colors.BG_DARK}{' ' * cols}{Colors.RESET}")

        # Left side: Navigation hints
        if not hints:
            hints = "↑↓ navigate | enter/→ select | esc/← back | tab switch | q quit"

        # Apply lowercase if configured
        if self.config.lowercase_ui:
            hints = hints.lower()

        move_cursor(2, lines)
        sys.stdout.write(f"{Colors.BG_DARK}{Colors.DIM}{hints}{Colors.RESET}")

        # Right side: Status information
        right_elements = []

        if status:
            # Hostname
            if self.config.show_hostname and 'hostname' in status:
                hostname = status['hostname']
                if self.config.lowercase_ui:
                    hostname = hostname.lower()
                right_elements.append(hostname)

            # Location
            if self.config.location:
                location = self.config.location
                if self.config.lowercase_ui:
                    location = location.lower()
                right_elements.append(location)

            # Date
            if 'date' in status:
                right_elements.append(status['date'])

            # Time
            if 'time' in status:
                right_elements.append(status['time'])

            # Online status
            if self.config.show_status_led and 'online' in status:
                if status['online']:
                    status_text = "online"
                    status_led = "●"  # Green LED
                    led_color = Colors.GREEN
                else:
                    status_text = "offline"
                    status_led = "●"  # Red LED
                    led_color = Colors.RED

                if self.config.lowercase_ui:
                    status_text = status_text.lower()
        else:
            # Default status
            hostname = socket.gethostname()
            if self.config.lowercase_ui:
                hostname = hostname.lower()
            right_elements.append(hostname)

            location = self.config.location
            if self.config.lowercase_ui:
                location = location.lower()
            right_elements.append(location)

            right_elements.append(datetime.now().strftime("%Y-%m-%d"))
            right_elements.append(datetime.now().strftime("%H:%M:%S"))

            status_text = "online"
            status_led = "●"
            led_color = Colors.GREEN

        # Build right side text
        if right_elements:
            right_text = " | ".join(right_elements)
            if self.config.show_status_led:
                right_text += f" | {status_text} "

            # Calculate position
            right_len = len(right_text) + 1  # +1 for LED
            right_pos = cols - right_len - 2
            right_pos = max(2, right_pos)

            # Draw right side
            move_cursor(right_pos, lines)
            sys.stdout.write(f"{Colors.BG_DARK}{Colors.WHITE}{right_text}")
            if self.config.show_status_led:
                sys.stdout.write(f"{led_color}{status_led}{Colors.RESET}")
            else:
                sys.stdout.write(Colors.RESET)

        sys.stdout.flush()