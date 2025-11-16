#!/usr/bin/env python3
"""
Test TUI navigation without full interactive mode
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.profiles.dev.tui import UnibosDevTUI
from core.clients.cli.framework.ui import MenuItem

def test_content_area_rendering():
    """Test ContentArea.draw() with various content types"""
    print("Testing ContentArea rendering...")

    tui = UnibosDevTUI()

    # Test 1: String content
    print("  Test 1: String content")
    tui.content_area.draw(
        title="Test Title",
        content="This is a test\nWith multiple lines\nAnd some more text",
        item=None
    )
    print("  ✓ String content works")

    # Test 2: List content
    print("  Test 2: List content")
    tui.content_area.draw(
        title="Test List",
        content=["Line 1", "Line 2", "Line 3"],
        item=None
    )
    print("  ✓ List content works")

    # Test 3: Long lines (triggers wrapping)
    print("  Test 3: Long lines (wrapping)")
    long_line = "This is a very long line that should trigger the text wrapping functionality in the content area component " * 3
    tui.content_area.draw(
        title="Test Wrapping",
        content=long_line,
        item=None
    )
    print("  ✓ Long line wrapping works")

    # Test 4: MenuItem with description
    print("  Test 4: MenuItem with description")
    item = MenuItem(
        id="test",
        label="Test Item",
        icon="🧪",
        description="Test description\nWith multiple lines",
        enabled=True
    )
    tui.content_area.draw(
        title=item.label,
        content=item.description,
        item=item
    )
    print("  ✓ MenuItem description works")

    print("\n✅ All ContentArea tests passed!")

def test_navigation_flow():
    """Test full navigation flow"""
    print("\nTesting navigation flow...")

    tui = UnibosDevTUI()
    sections = tui.get_menu_sections()
    tui.state.sections = [s.to_dict() for s in sections]

    # Navigate through first section
    print(f"  Section 0 has {len(sections[0].items)} items")
    for i in range(min(10, len(sections[0].items))):
        tui.state.navigate_down(len(sections[0].items))
        current_item = sections[0].items[tui.state.selected_index]

        # Try to render content for this item
        try:
            tui.content_area.draw(
                title=current_item.label,
                content=current_item.description,
                item=current_item
            )
            print(f"  ✓ Item {i}: {current_item.label}")
        except Exception as e:
            print(f"  ❌ Item {i} failed: {e}")
            raise

    print("\n✅ Navigation flow test passed!")

def test_update_content():
    """Test update_content method"""
    print("\nTesting update_content method...")

    tui = UnibosDevTUI()

    # Test with string
    print("  Test 1: update_content with string")
    tui.update_content("Test Title", ["Line 1", "Line 2"])
    assert tui.content_buffer['title'] == "Test Title"
    assert tui.content_buffer['lines'] == ["Line 1", "Line 2"]
    print("  ✓ String content stored correctly")

    # Test rendering the buffered content
    print("  Test 2: Render buffered content")
    tui.content_area.draw(
        title=tui.content_buffer['title'],
        content='\n'.join(tui.content_buffer['lines']),
        item=None
    )
    print("  ✓ Buffered content renders correctly")

    print("\n✅ update_content test passed!")

if __name__ == "__main__":
    try:
        test_content_area_rendering()
        test_navigation_flow()
        test_update_content()

        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)

    except Exception as e:
        import traceback
        print("\n" + "="*50)
        print(f"❌ TEST FAILED: {e}")
        print("="*50)
        traceback.print_exc()
        sys.exit(1)
