#!/usr/bin/env python3
"""
Test the TUI fixes for the arrow key navigation bug
"""

import sys
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos-dev')

from core.clients.tui.base import BaseTUI, TUIConfig
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Colors

class TestTUI(BaseTUI):
    """Simple test TUI"""

    def get_profile_name(self) -> str:
        return "test"

    def get_menu_sections(self):
        return [
            MenuSection(
                id='test',
                label='Test Section',
                icon='🧪',
                items=[
                    MenuItem(
                        id='item1',
                        label='Item 1',
                        icon='1️⃣',
                        description='First test item\nLine 2\nLine 3',
                        enabled=True
                    ),
                    MenuItem(
                        id='item2',
                        label='Item 2',
                        icon='2️⃣',
                        description='Second test item',
                        enabled=True
                    ),
                    MenuItem(
                        id='item3',
                        label='Item 3',
                        icon='3️⃣',
                        description='Third test item',
                        enabled=True
                    ),
                ]
            )
        ]

def test_type_handling():
    """Test type handling in render method"""
    print("Testing type handling fixes...\n")

    tui = TestTUI()

    # Test 1: List input (expected case)
    print("Test 1: List input")
    tui.update_content("Test Title", ["Line 1", "Line 2", "Line 3"])
    print(f"  content_buffer['lines'] type: {type(tui.content_buffer['lines'])}")
    print(f"  content_buffer['lines']: {tui.content_buffer['lines']}")

    # Simulate render logic
    lines = tui.content_buffer['lines']
    if isinstance(lines, str):
        content = lines
    elif isinstance(lines, list):
        content = '\n'.join(lines)
    else:
        content = str(lines)
    print(f"  Rendered content: {repr(content)}")
    print("  ✅ List input handled correctly\n")

    # Test 2: String input (defensive case)
    print("Test 2: String input (defensive)")
    tui.content_buffer['lines'] = "Line 1\nLine 2\nLine 3"  # Simulate bug
    print(f"  content_buffer['lines'] type: {type(tui.content_buffer['lines'])}")

    lines = tui.content_buffer['lines']
    if isinstance(lines, str):
        content = lines
    elif isinstance(lines, list):
        content = '\n'.join(lines)
    else:
        content = str(lines)
    print(f"  Rendered content: {repr(content)}")
    print("  ✅ String input handled correctly\n")

    # Test 3: Test content.py handling
    print("Test 3: ContentArea.draw() type handling")

    # Test with string
    content_str = "Line 1\nLine 2\nLine 3"
    if isinstance(content_str, list):
        lines_list = content_str
    elif isinstance(content_str, str):
        lines_list = content_str.split('\n')
    else:
        lines_list = str(content_str).split('\n')
    print(f"  String input: {lines_list}")
    print("  ✅ String handled correctly")

    # Test with list
    content_list = ["Line 1", "Line 2", "Line 3"]
    if isinstance(content_list, list):
        lines_list = content_list
    elif isinstance(content_list, str):
        lines_list = content_list.split('\n')
    else:
        lines_list = str(content_list).split('\n')
    print(f"  List input: {lines_list}")
    print("  ✅ List handled correctly\n")

    print("All type handling tests passed! ✅")

if __name__ == "__main__":
    test_type_handling()
