"""
UNIBOS CLI Keyboard Input - Enhanced Version
Cross-platform keyboard input handling with better error handling

Enhanced from v527 with better terminal handling
"""

import os
import sys
import time
import platform
import select

# Platform-specific imports
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


def get_single_key(timeout: float = 0.1) -> str:
    """
    Get a single keypress with arrow key support

    Enhanced with better error handling for macOS terminal issues

    Args:
        timeout: Timeout in seconds (default 0.1)

    Returns:
        Key string or None if timeout
    """
    debug_mode = os.environ.get('UNIBOS_DEBUG', '').lower() == 'true'

    try:
        if platform.system() == 'Windows':
            return _get_key_windows(timeout)
        else:
            return _get_key_unix(timeout, debug_mode)
    except Exception as e:
        if debug_mode:
            with open('/tmp/unibos_key_debug.log', 'a') as f:
                f.write(f"Exception in get_single_key: {e}\n")
                f.flush()
        return None


def _get_key_windows(timeout: float) -> str:
    """Windows keyboard input handler"""
    import msvcrt

    # Clear any pending input
    while msvcrt.kbhit():
        msvcrt.getch()

    # Wait for key with timeout
    start_time = time.time()
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\xe0':  # Special key prefix
                key = msvcrt.getch()
                if key == b'H': return '\x1b[A'  # Up
                elif key == b'P': return '\x1b[B'  # Down
                elif key == b'K': return '\x1b[D'  # Left
                elif key == b'M': return '\x1b[C'  # Right
            elif key == b'\r': return '\r'
            elif key == b'\x1b': return '\x1b'
            elif key == b'\t': return '\t'
            elif key == b' ': return ' '
            else:
                try:
                    return key.decode('utf-8', errors='ignore')
                except:
                    return None

        if time.time() - start_time > timeout:
            return None
        time.sleep(0.01)


def _get_key_unix(timeout: float, debug_mode: bool) -> str:
    """Unix/Linux/macOS keyboard input handler with improved error handling"""
    if not TERMIOS_AVAILABLE:
        return None

    import termios
    import tty

    fd = sys.stdin.fileno()

    # Check if stdin is a terminal
    if not os.isatty(fd):
        # Not a terminal (maybe piped or redirected)
        # Try to use /dev/tty directly
        try:
            tty_file = open('/dev/tty', 'r')
            fd = tty_file.fileno()
        except:
            return None

    try:
        old_settings = termios.tcgetattr(fd)
    except termios.error as e:
        # Handle "Operation not supported by device" error
        if debug_mode:
            with open('/tmp/unibos_key_debug.log', 'a') as f:
                f.write(f"termios.tcgetattr error: {e}\n")
                f.flush()
        # Fall back to simple input
        return _get_key_simple(timeout)

    try:
        # Set terminal to raw mode
        tty.setraw(fd)

        # Check if input is available
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if not rlist:
            return None

        # Read character
        ch = sys.stdin.read(1)

        if debug_mode:
            with open('/tmp/unibos_key_debug.log', 'a') as f:
                f.write(f"First char: {repr(ch)}\n")
                f.flush()

        # Handle escape sequences
        if ch == '\x1b':
            # Check for more characters
            rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
            if rlist:
                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
                    if rlist:
                        ch3 = sys.stdin.read(1)
                        # Arrow keys
                        if ch3 == 'A': return '\x1b[A'  # Up
                        elif ch3 == 'B': return '\x1b[B'  # Down
                        elif ch3 == 'C': return '\x1b[C'  # Right
                        elif ch3 == 'D': return '\x1b[D'  # Left
                        # Page Up/Down
                        elif ch3 in ['5', '6']:
                            rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
                            if rlist:
                                ch4 = sys.stdin.read(1)
                                if ch4 == '~':
                                    if ch3 == '5': return '\x1b[5~'  # Page Up
                                    elif ch3 == '6': return '\x1b[6~'  # Page Down
            return '\x1b'  # Just ESC

        return ch

    finally:
        # Restore terminal settings
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            pass


def _get_key_simple(timeout: float) -> str:
    """
    Simple fallback for when terminal operations fail
    Uses basic input() with timeout simulation
    """
    import threading

    result = [None]

    def get_input():
        try:
            # This won't support arrow keys but at least allows basic interaction
            result[0] = sys.stdin.read(1) if sys.stdin in select.select([sys.stdin], [], [], 0)[0] else None
        except:
            pass

    thread = threading.Thread(target=get_input)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    return result[0]


# Key constants for easier comparison
class Keys:
    """Key code constants"""
    UP = '\x1b[A'
    DOWN = '\x1b[B'
    LEFT = '\x1b[D'
    RIGHT = '\x1b[C'
    PAGE_UP = '\x1b[5~'
    PAGE_DOWN = '\x1b[6~'
    ENTER = '\r'
    ESC = '\x1b'
    TAB = '\t'
    SPACE = ' '