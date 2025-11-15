"""
UNIBOS CLI Splash Screen
Animated welcome screen with ASCII art logo

Ported from v527 main.py (lines 7870-7995)
Reference: docs/development/cli_v527_reference.md
"""

import os
import sys
import time
import platform
from pathlib import Path

# Try termios for Unix, fallback for Windows
if platform.system() != 'Windows':
    try:
        import termios
        import tty
        TERMIOS_AVAILABLE = True
    except ImportError:
        TERMIOS_AVAILABLE = False
else:
    TERMIOS_AVAILABLE = False
    try:
        import msvcrt
    except ImportError:
        pass

from .colors import Colors
from .terminal import clear_screen, get_terminal_size, move_cursor
from core.version import __version__


def get_simple_key():
    """Get a single keypress (simple version for splash screen)"""
    if TERMIOS_AVAILABLE:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    elif platform.system() == 'Windows':
        try:
            import msvcrt
            return msvcrt.getch().decode('utf-8', errors='ignore')
        except:
            return input()
    else:
        # Fallback
        return input()


def show_splash_screen(quick: bool = False):
    """
    Show animated splash screen with UNIBOS logo

    Args:
        quick: If True, skip animations and show quickly
    """
    clear_screen()
    cols, lines = get_terminal_size()

    # Get version info
    version = f"v{__version__}"

    # Welcome box with UNIBOS branding
    welcome_box = [
        f"{Colors.ORANGE}╭{'─' * 24}╮{Colors.RESET}",
        f"{Colors.ORANGE}│{Colors.RESET} {Colors.BOLD}* welcome to unibos! *{Colors.RESET} {Colors.ORANGE}│{Colors.RESET}",
        f"{Colors.ORANGE}╰{'─' * 24}╯{Colors.RESET}"
    ]

    # ASCII art - Large UNIBOS logo
    logo_art = [
        "",
        f"{Colors.ORANGE}██╗   ██╗███╗   ██╗██╗██████╗  ██████╗ ███████╗{Colors.RESET}",
        f"{Colors.ORANGE}██║   ██║████╗  ██║██║██╔══██╗██╔═══██╗██╔════╝{Colors.RESET}",
        f"{Colors.ORANGE}██║   ██║██╔██╗ ██║██║██████╔╝██║   ██║███████╗{Colors.RESET}",
        f"{Colors.ORANGE}██║   ██║██║╚██╗██║██║██╔══██╗██║   ██║╚════██║{Colors.RESET}",
        f"{Colors.ORANGE}╚██████╔╝██║ ╚████║██║██████╔╝╚██████╔╝███████║{Colors.RESET}",
        f"{Colors.ORANGE} ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═════╝  ╚═════╝ ╚══════╝{Colors.RESET} {Colors.YELLOW}{version}{Colors.RESET}",
        ""
    ]

    # Calculate centering
    box_width = 26
    logo_width = 48

    # Center welcome box at top
    box_y = 4
    box_x = max(1, (cols - box_width) // 2)

    # Draw welcome box
    for i, line in enumerate(welcome_box):
        move_cursor(box_x, box_y + i)
        print(line, flush=True)
        if not quick:
            time.sleep(0.02)

    # Center the logo art
    logo_y = box_y + 6
    logo_x = max(1, (cols - logo_width) // 2)

    # Animate logo appearance
    animation_delay = 0 if quick else 0.05
    for i, line in enumerate(logo_art):
        move_cursor(logo_x, logo_y + i)
        print(line, end='', flush=True)
        if not quick:
            time.sleep(animation_delay)

    print()  # New line after logo

    # Show additional info below
    info_y = logo_y + len(logo_art) + 2
    location = "bitez, bodrum, muğla, türkiye"

    info_lines = [
        f"{Colors.DIM}unicorn bodrum operating system{Colors.RESET}",
        f"{Colors.DIM}build {__version__}{Colors.RESET}",
        "",
        f"{Colors.DIM}by berk hatırlı{Colors.RESET}",
        f"{Colors.DIM}{location}{Colors.RESET}"
    ]

    for i, line in enumerate(info_lines):
        # Adjust centering for longer location line
        if i == 4:  # Location line
            clean_loc = Colors.strip(location)
            text_x = max(1, (cols - len(clean_loc)) // 2)
        else:
            text_x = max(1, (cols - 45) // 2)
        move_cursor(text_x, info_y + i)
        print(line, flush=True)
        if not quick:
            time.sleep(0.03)

    if not quick:
        time.sleep(0.3)

    # Loading animation
    loading_y = info_y + len(info_lines) + 2
    loading_text = "initializing system components..."
    loading_x = max(1, (cols - len(loading_text)) // 2)

    # Show loading text
    move_cursor(loading_x, loading_y)
    print(f"{Colors.YELLOW}{loading_text}{Colors.RESET}", flush=True)

    if not quick:
        # Progress bar with animation
        progress_y = loading_y + 2
        progress_width = min(50, cols - 4)  # Adaptive width
        progress_x = max(1, (cols - progress_width) // 2)

        # Draw progress bar frame
        move_cursor(progress_x, progress_y)
        print(f"{Colors.DIM}[{' ' * (progress_width - 2)}]{Colors.RESET}", flush=True)

        # Animate progress bar with color stages
        for i in range(progress_width - 2):
            move_cursor(progress_x + 1 + i, progress_y)
            # Different colors for different stages
            if i < (progress_width - 2) // 3:
                color = Colors.MAGENTA
            elif i < 2 * (progress_width - 2) // 3:
                color = Colors.YELLOW
            else:
                color = Colors.GREEN
            print(f"{color}█{Colors.RESET}", end='', flush=True)
            # Varying speed for realistic loading
            if i % 5 == 0:
                time.sleep(0.03)
            else:
                time.sleep(0.01)

        # Keep progress bar visible
        time.sleep(0.5)

        # Clear loading text
        move_cursor(loading_x - 2, loading_y)
        print(' ' * (len(loading_text) + 4), end='', flush=True)

        # Show continue message
        continue_text = "press any key to continue..."
        continue_x = max(1, (cols - len(continue_text)) // 2)
        continue_y = progress_y + 3
        move_cursor(continue_x, continue_y)
        print(f"{Colors.BLUE}{continue_text}{Colors.RESET}", flush=True)

        # Wait for key press
        get_simple_key()
    else:
        # Quick mode - just a short pause
        time.sleep(0.5)

    clear_screen()


def show_compact_header(cli_name: str = "unibos"):
    """
    Show compact header for command mode

    Args:
        cli_name: Name of CLI (unibos, unibos-dev, unibos-server)
    """
    cols, _ = get_terminal_size()
    version = f"v{__version__}"

    # Single line header
    header = f"{Colors.ORANGE}🪐 {cli_name}{Colors.RESET} {Colors.YELLOW}{version}{Colors.RESET} {Colors.DIM}| unicorn bodrum operating system{Colors.RESET}"

    # Center it
    clean_header = Colors.strip(header)
    header_x = max(1, (cols - len(clean_header)) // 2)
    move_cursor(header_x, 2)
    print(header, flush=True)
    print()  # Add spacing
