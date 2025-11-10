#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Web Forge input handling
Run this to diagnose input issues
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import get_single_key, Colors
    print(f"{Colors.GREEN}✓ Successfully imported from main.py{Colors.RESET}")
except ImportError as e:
    print(f"✗ Failed to import from main.py: {e}")
    sys.exit(1)

def test_input_handling():
    """Test different input methods"""
    print(f"\n{Colors.CYAN}=== Web Forge Input Test ==={Colors.RESET}")
    print(f"\nThis will test the input handling mechanism used in Web Forge setup.")
    print(f"Press different keys to see how they're captured.\n")
    
    print(f"{Colors.YELLOW}Test 1: Basic key capture{Colors.RESET}")
    print("Press keys 1-4, or 'q' to quit this test:")
    
    while True:
        try:
            key = get_single_key(timeout=5.0)
            
            if key is None:
                print(".", end='', flush=True)  # Show we're still waiting
                continue
                
            print(f"\nReceived: {repr(key)} (ASCII: {ord(key) if len(key) == 1 else 'N/A'})")
            
            if key == 'q':
                break
            elif key in '1234':
                print(f"{Colors.GREEN}✓ Number key {key} working correctly!{Colors.RESET}")
            elif key == '\r':
                print(f"{Colors.YELLOW}Enter key pressed{Colors.RESET}")
            elif key == '\x1b':
                print(f"{Colors.YELLOW}Escape key pressed{Colors.RESET}")
            else:
                print(f"{Colors.DIM}Other key: {repr(key)}{Colors.RESET}")
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
            break
        except Exception as e:
            print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
            break
    
    print(f"\n{Colors.CYAN}Test 2: Web Forge specific test{Colors.RESET}")
    print("This simulates the Web Forge setup menu.")
    print("\nOptions:")
    print("1. Launch Web Forge")
    print("2. Re-run setup")
    print("3. View setup logs")
    print("4. Return to menu")
    print(f"\n{Colors.YELLOW}Select option (1-4): {Colors.RESET}", end='', flush=True)
    
    while True:
        try:
            key = get_single_key(timeout=5.0)
            
            if key is None:
                continue
                
            print(key, end='', flush=True)  # Echo the key
            
            if key == '1':
                print(f"\n{Colors.GREEN}✓ Option 1 selected - Would launch Web Forge{Colors.RESET}")
                break
            elif key == '2':
                print(f"\n{Colors.GREEN}✓ Option 2 selected - Would re-run setup{Colors.RESET}")
                print(f"{Colors.YELLOW}This is the option that was not working!{Colors.RESET}")
                break
            elif key == '3':
                print(f"\n{Colors.GREEN}✓ Option 3 selected - Would view logs{Colors.RESET}")
                break
            elif key == '4':
                print(f"\n{Colors.GREEN}✓ Option 4 selected - Would return to menu{Colors.RESET}")
                break
            else:
                print(f"\n{Colors.RED}Invalid option. Please select 1-4{Colors.RESET}")
                print(f"{Colors.YELLOW}Select option (1-4): {Colors.RESET}", end='', flush=True)
                
        except Exception as e:
            print(f"\n{Colors.RED}Error in input handling: {e}{Colors.RESET}")
            break
    
    print(f"\n{Colors.CYAN}=== Test Complete ==={Colors.RESET}")
    print("\nSummary:")
    print("- If all number keys (1-4) were detected correctly, the input system is working.")
    print("- If option 2 was detected, the Web Forge setup should now work properly.")
    print("- Check /Users/berkhatirli/Desktop/unibos/logs/setup/ for debug logs.")

if __name__ == "__main__":
    # Set up UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    
    test_input_handling()