"""
UNIBOS CLI UI Components
Shared UI components for all CLI tools (unibos, unibos-dev, unibos-server)

Extracted from v527 main.py (commit: e053e28)
Reference: docs/development/cli_v527_reference.md
"""

from .colors import Colors
from .terminal import (
    clear_screen,
    get_terminal_size,
    move_cursor,
    hide_cursor,
    show_cursor,
    wrap_text,
    get_spinner_frame,
    print_centered,
)
from .splash import (
    show_splash_screen,
    show_compact_header,
)
from .input import (
    get_single_key,
    Keys,
)
from .menu import (
    MenuItem,
    MenuState,
)
from .layout import (
    draw_header,
    draw_sidebar_sections,
    draw_content_area,
    draw_footer,
    clear_content_area,
    draw_box,
)

__all__ = [
    'Colors',
    'clear_screen',
    'get_terminal_size',
    'move_cursor',
    'hide_cursor',
    'show_cursor',
    'wrap_text',
    'get_spinner_frame',
    'print_centered',
    'show_splash_screen',
    'show_compact_header',
    'get_single_key',
    'Keys',
    'MenuItem',
    'MenuState',
    'draw_header',
    'draw_sidebar_sections',
    'draw_content_area',
    'draw_footer',
    'clear_content_area',
    'draw_box',
]
