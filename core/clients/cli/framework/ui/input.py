"""
UNIBOS CLI Keyboard Input
Cross-platform keyboard input handling with arrow key support

Extracted from v527 main.py (lines 1669-1820)
Reference: docs/development/cli_v527_reference.md
"""

import os
import sys
import time
import select
import platform

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
    import msvcrt


def get_single_key(timeout: float = 0.1) -> str:
    """
    Get a single keypress with arrow key support

    Args:
        timeout: Timeout in seconds (default 0.1)

    Returns:
        Key string:
        - '\x1b[A': UP arrow
        - '\x1b[B': DOWN arrow
        - '\x1b[C': RIGHT arrow
        - '\x1b[D': LEFT arrow
        - '\x1b[5~': Page Up
        - '\x1b[6~': Page Down
        - '\r': Enter
        - '\x1b': ESC
        - '0'-'9': Number keys
        - 'a'-'z': Letter keys
        - None: Timeout (no key pressed)
    """
    debug_mode = os.environ.get('UNIBOS_DEBUG', '').lower() == 'true'

    try:
        if platform.system() == 'Windows':
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
                            return key

                if time.time() - start_time > timeout:
                    return None
                time.sleep(0.01)
        else:
            # Unix/Linux/macOS
            if not TERMIOS_AVAILABLE:
                return None

            import termios, tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                # Set terminal to non-canonical mode with timeout
                new_settings = termios.tcgetattr(fd)
                new_settings[3] = new_settings[3] & ~termios.ICANON & ~termios.ECHO
                new_settings[6][termios.VMIN] = 0
                new_settings[6][termios.VTIME] = 0
                termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)

                # Check if input is available
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if not rlist:
                    return None

                # Read character
                ch = os.read(fd, 1).decode('utf-8', errors='ignore')

                if debug_mode:
                    with open('/tmp/unibos_key_debug.log', 'a') as f:
                        f.write(f"First char: {repr(ch)}\n")
                        f.flush()

                # Handle escape sequences (arrow keys, etc.)
                if ch == '\x1b':
                    # Set a very short timeout for subsequent reads
                    new_settings[6][termios.VTIME] = 1  # 0.1 second timeout
                    termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)

                    try:
                        ch2 = os.read(fd, 1).decode('utf-8', errors='ignore')
                        if debug_mode:
                            with open('/tmp/unibos_key_debug.log', 'a') as f:
                                f.write(f"Second char: {repr(ch2)}\n")
                                f.flush()

                        if ch2 == '[':
                            ch3 = os.read(fd, 1).decode('utf-8', errors='ignore')
                            if debug_mode:
                                with open('/tmp/unibos_key_debug.log', 'a') as f:
                                    f.write(f"Third char: {repr(ch3)}\n")
                                    f.flush()

                            # Standard arrow keys
                            if ch3 == 'A': return '\x1b[A'  # Up
                            elif ch3 == 'B': return '\x1b[B'  # Down
                            elif ch3 == 'C': return '\x1b[C'  # Right
                            elif ch3 == 'D': return '\x1b[D'  # Left
                            # Page Up/Down require additional read
                            elif ch3 in ['5', '6']:
                                ch4 = os.read(fd, 1).decode('utf-8', errors='ignore')
                                if ch4 == '~':
                                    if ch3 == '5': return '\x1b[5~'  # Page Up
                                    elif ch3 == '6': return '\x1b[6~'  # Page Down
                            else:
                                # Return full sequence
                                return '\x1b[' + ch3
                        else:
                            # ESC followed by something else
                            return '\x1b'
                    except:
                        return '\x1b'

                return ch

            finally:
                # Restore terminal settings
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    except Exception as e:
        if debug_mode:
            with open('/tmp/unibos_key_debug.log', 'a') as f:
                f.write(f"Exception: {e}\n")
                f.flush()
        return None


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
