"""
UNIBOS CLI Terminal Utilities
Cross-platform terminal manipulation functions

Extracted from v527 main.py
Reference: docs/development/cli_v527_reference.md
"""

import os
import sys
import platform
from typing import Tuple, List


def clear_screen():
    """Clear the terminal screen with enhanced clearing"""
    # Use ANSI escape sequences for more thorough clearing
    sys.stdout.write('\033[2J')  # Clear entire screen
    sys.stdout.write('\033[H')   # Move cursor to top-left
    sys.stdout.write('\033[3J')  # Clear scrollback buffer (supported terminals)
    sys.stdout.flush()

    # Also use OS-specific clear command as fallback
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    sys.stdout.flush()  # Ensure screen is fully cleared before continuing


def get_terminal_size() -> Tuple[int, int]:
    """
    Get terminal dimensions

    Returns:
        Tuple of (columns, lines)
    """
    try:
        import shutil
        columns, lines = shutil.get_terminal_size((80, 24))
        return columns, lines
    except Exception:
        return 80, 24


def move_cursor(x: int, y: int):
    """
    Move cursor to position (1-indexed)

    Args:
        x: Column position (1-indexed)
        y: Row position (1-indexed)
    """
    print(f"\033[{y};{x}H", end='', flush=True)


def hide_cursor():
    """Hide the terminal cursor"""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    """Show the terminal cursor"""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def get_spinner_frame(index: int) -> str:
    """
    Get a spinner animation frame

    Args:
        index: Frame index

    Returns:
        Unicode spinner character
    """
    spinners = ['', '', '9', '8', '<', '4', '&', ''', '', '']
    return spinners[index % len(spinners)]


def wrap_text(text: str, width: int) -> List[str]:
    """
    Wrap text to fit within specified width

    Args:
        text: Text to wrap
        width: Maximum line width

    Returns:
        List of wrapped lines
    """
    if not text:
        return []

    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)
        if current_length + word_length + len(current_line) <= width:
            current_line.append(word)
            current_length += word_length
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_length

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def print_centered(text: str, y: int = None):
    """
    Print text centered on the screen

    Args:
        text: Text to print
        y: Optional Y position
    """
    cols, _ = get_terminal_size()

    # Strip ANSI codes for length calculation
    from .colors import Colors
    clean_text = Colors.strip(text)
    text_width = len(clean_text)

    x = max(1, (cols - text_width) // 2)

    if y is not None:
        move_cursor(x, y)

    print(text, flush=True)
