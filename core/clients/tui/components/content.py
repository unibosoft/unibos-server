"""
UNIBOS TUI Content Area Component
Right side content area with scrolling support
"""

import sys
from typing import List, Optional, Any

from core.clients.cli.framework.ui import Colors, get_terminal_size, move_cursor, wrap_text


class ContentArea:
    """Content area component for TUI"""

    def __init__(self, config):
        """Initialize content area with config"""
        self.config = config
        self.scroll_position = 0

    def draw(self, title: str, content: str = "", item: Optional[Any] = None):
        """
        Draw content area

        Args:
            title: Content title
            content: Content text (can be multiline)
            item: Optional menu item for additional context
        """
        cols, lines = get_terminal_size()

        # Calculate content area dimensions
        content_x = self.config.sidebar_width + 2
        content_width = cols - content_x - 2
        content_y_start = 3
        content_height = lines - content_y_start - 2  # Leave room for footer

        # Clear content area first
        self.clear(content_x, content_y_start, content_width, content_height)

        # Apply lowercase if configured
        if self.config.lowercase_ui:
            title = title.lower()
            if content:
                content = content.lower()

        # Draw title
        move_cursor(content_x, content_y_start)
        sys.stdout.write(f"{Colors.CYAN}{Colors.BOLD}{title}{Colors.RESET}")

        # Draw separator line
        y = content_y_start + 1
        move_cursor(content_x, y)
        sys.stdout.write(f"{Colors.DIM}{'─' * min(len(title) + 10, content_width)}{Colors.RESET}")

        # Process content
        y = content_y_start + 3
        if content:
            # Split content into lines
            lines_list = content.split('\n')

            # Wrap long lines
            wrapped_lines = []
            for line in lines_list:
                if len(line) > content_width:
                    wrapped = wrap_text(line, content_width)
                    wrapped_lines.extend(wrapped.split('\n'))
                else:
                    wrapped_lines.append(line)

            # Draw content lines
            for line in wrapped_lines:
                if y >= content_y_start + content_height:
                    # Show scroll indicator
                    move_cursor(content_x, lines - 2)
                    sys.stdout.write(f"{Colors.DIM}... (more content below){Colors.RESET}")
                    break

                move_cursor(content_x, y)

                # Special formatting for certain patterns
                if line.startswith('✓'):
                    sys.stdout.write(f"{Colors.GREEN}{line}{Colors.RESET}")
                elif line.startswith('✗') or line.startswith('❌'):
                    sys.stdout.write(f"{Colors.RED}{line}{Colors.RESET}")
                elif line.startswith('⚠'):
                    sys.stdout.write(f"{Colors.YELLOW}{line}{Colors.RESET}")
                elif line.startswith('→') or line.startswith('▶'):
                    sys.stdout.write(f"{Colors.ORANGE}{line}{Colors.RESET}")
                elif line.startswith('#'):
                    # Header
                    sys.stdout.write(f"{Colors.BOLD}{line}{Colors.RESET}")
                elif line.startswith('  '):
                    # Indented (likely code or command)
                    sys.stdout.write(f"{Colors.DIM}{line}{Colors.RESET}")
                else:
                    sys.stdout.write(f"{Colors.WHITE}{line}{Colors.RESET}")

                y += 1

        # Draw item metadata if available
        if item and hasattr(item, 'metadata'):
            y += 1
            if y < lines - 2:
                move_cursor(content_x, y)
                sys.stdout.write(f"{Colors.DIM}───────────{Colors.RESET}")
                y += 1

            metadata = item.metadata
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    if y >= lines - 2:
                        break
                    move_cursor(content_x, y)
                    text = f"{key}: {value}"
                    if self.config.lowercase_ui:
                        text = text.lower()
                    sys.stdout.write(f"{Colors.DIM}{text}{Colors.RESET}")
                    y += 1

        sys.stdout.flush()

    def clear(self, x: int, y: int, width: int, height: int):
        """Clear content area"""
        for i in range(height):
            move_cursor(x, y + i)
            sys.stdout.write(' ' * width)