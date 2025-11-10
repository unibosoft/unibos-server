#!/usr/bin/env python3
"""Test navigation with simplified get_single_key"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import get_single_key, Colors, clear_screen, move_cursor

def test_navigation():
    """Test arrow key navigation"""
    clear_screen()
    print(f"{Colors.CYAN}=== UNIBOS Navigation Test ==={Colors.RESET}\n")
    print("Press arrow keys to test navigation")
    print("Press 'q' to quit\n")
    print("Waiting for input...\n")
    
    while True:
        key = get_single_key(timeout=0.1)
        
        if key:
            move_cursor(0, 6)
            print(f"Key pressed: {repr(key)}        ")
            
            if key == '\x1b[A':
                print(f"{Colors.GREEN}UP ARROW detected ↑{Colors.RESET}    ")
            elif key == '\x1b[B':
                print(f"{Colors.GREEN}DOWN ARROW detected ↓{Colors.RESET}  ")
            elif key == '\x1b[C':
                print(f"{Colors.GREEN}RIGHT ARROW detected →{Colors.RESET} ")
            elif key == '\x1b[D':
                print(f"{Colors.GREEN}LEFT ARROW detected ←{Colors.RESET}  ")
            elif key == '\r':
                print(f"{Colors.YELLOW}ENTER detected{Colors.RESET}        ")
            elif key == '\x1b':
                print(f"{Colors.YELLOW}ESC detected{Colors.RESET}          ")
            elif key == '\t':
                print(f"{Colors.YELLOW}TAB detected{Colors.RESET}          ")
            elif key == ' ':
                print(f"{Colors.YELLOW}SPACE detected{Colors.RESET}        ")
            elif key and key.lower() == 'q':
                print(f"\n{Colors.RED}Quitting...{Colors.RESET}")
                break
            else:
                print(f"Other key: {repr(key)}      ")

if __name__ == "__main__":
    try:
        test_navigation()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Interrupted{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")