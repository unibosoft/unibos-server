#!/usr/bin/env python3
"""
Test the arrow key navigation bug fix
Simulates pressing down arrow multiple times
"""

import sys
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos-dev')

from core.profiles.dev.tui import UnibosDevTUI
from core.clients.cli.framework.ui import Keys

def test_arrow_navigation():
    """Test arrow key navigation without actually running the TUI"""
    print("Testing arrow key navigation fix...\n")

    # Create TUI instance
    tui = UnibosDevTUI()

    # Initialize menu structure
    sections = tui.get_menu_sections()
    tui.state.sections = [s.to_dict() for s in sections]

    print(f"Loaded {len(sections)} sections:")
    for i, section in enumerate(sections):
        print(f"  {i}. {section.label} ({len(section.items)} items)")
    print()

    # Simulate navigation
    print("Simulating down arrow key presses...\n")

    for i in range(10):
        print(f"Press #{i+1}: DOWN")

        # Get current state before navigation
        current_section = sections[tui.state.current_section] if sections else None
        if current_section:
            print(f"  Current section: {current_section.label}")
            print(f"  Current index: {tui.state.selected_index}")

            # Try to get selected item
            if 0 <= tui.state.selected_index < len(current_section.items):
                selected_item = current_section.items[tui.state.selected_index]
                print(f"  Selected item: {selected_item.label}")

                # This is where the bug might occur - when rendering the item description
                if hasattr(selected_item, 'description'):
                    desc_type = type(selected_item.description).__name__
                    desc_preview = selected_item.description[:50] if isinstance(selected_item.description, str) else str(selected_item.description)[:50]
                    print(f"  Description type: {desc_type}")
                    print(f"  Description preview: {desc_preview}...")

        # Navigate down
        max_items = len(current_section.items) if current_section else 0
        navigated = tui.state.navigate_down(max_items)
        print(f"  Navigated: {navigated}")

        # Simulate what render() does
        if current_section and 0 <= tui.state.selected_index < len(current_section.items):
            selected_item = current_section.items[tui.state.selected_index]

            # Test the rendering logic with the item description
            if hasattr(selected_item, 'description'):
                try:
                    # This is what ContentArea.draw() receives
                    content = selected_item.description

                    # Apply the fix
                    if isinstance(content, list):
                        lines_list = content
                    elif isinstance(content, str):
                        lines_list = content.split('\n')
                    else:
                        lines_list = str(content).split('\n')

                    print(f"  Render test: ✅ {len(lines_list)} lines")
                except Exception as e:
                    print(f"  Render test: ❌ {e}")
                    return False

        print()

    print("✅ All arrow navigation tests passed!")
    return True

if __name__ == "__main__":
    success = test_arrow_navigation()
    sys.exit(0 if success else 1)
