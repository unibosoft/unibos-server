#!/usr/bin/env python3
"""
Comprehensive test to verify the TUI navigation crash fix

This test specifically verifies the fix for the bug:
'list' object has no attribute 'split'

The bug was in content.py line 82 where wrap_text() returns a list,
but the code was calling .split('\n') on it.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.profiles.dev.tui import UnibosDevTUI
from core.clients.cli.framework.ui import Colors

def test_arrow_key_navigation():
    """
    Simulate arrow key navigation that was causing the crash
    """
    print("="*60)
    print("TEST: Arrow Key Navigation (Bug Reproduction)")
    print("="*60)

    tui = UnibosDevTUI()
    sections = tui.get_menu_sections()
    tui.state.sections = [s.to_dict() for s in sections]

    # Simulate pressing down arrow 10 times (this was crashing before)
    print("\nSimulating down arrow presses...")
    for i in range(10):
        # Get current item BEFORE navigation
        current_section = sections[tui.state.current_section]
        old_index = tui.state.selected_index

        # Navigate down (this triggers render)
        tui.state.navigate_down(len(current_section.items))
        new_index = tui.state.selected_index

        # Get the item we navigated to
        item = current_section.items[new_index]

        # This is where the crash occurred - rendering content with description
        try:
            # Simulate what happens during render
            tui.content_area.draw(
                title=item.label,
                content=item.description,
                item=item
            )
            print(f"  ✓ Press {i+1}: {old_index} -> {new_index} ({item.label})")
        except AttributeError as e:
            if "'list' object has no attribute 'split'" in str(e):
                print(f"  ❌ BUG FOUND at press {i+1}!")
                print(f"     Error: {e}")
                print(f"     Item: {item.label}")
                print(f"     Description type: {type(item.description)}")
                raise
            else:
                raise

    print("\n✅ Arrow key navigation test PASSED!")
    print("   No 'list' object has no attribute 'split' errors\n")

def test_long_content_wrapping():
    """
    Test content wrapping specifically (where the bug was)
    """
    print("="*60)
    print("TEST: Long Content Wrapping (Direct Bug Test)")
    print("="*60)

    tui = UnibosDevTUI()

    # Create a very long line that will trigger wrapping
    long_line = "This is a very long line that will definitely trigger the text wrapping functionality in the content area component. " * 5

    print("\nTesting long content wrapping...")
    try:
        tui.content_area.draw(
            title="Long Content Test",
            content=long_line,
            item=None
        )
        print("✓ Long content wrapped successfully")
    except AttributeError as e:
        if "'list' object has no attribute 'split'" in str(e):
            print(f"❌ BUG FOUND in wrapping!")
            print(f"   Error: {e}")
            raise
        else:
            raise

    # Test with multiline content that also has long lines
    multiline_long = "\n".join([
        "Short line",
        "This is a very long line that will trigger wrapping " * 10,
        "Another short line",
        "And another very long line with lots of text that needs to wrap properly " * 8
    ])

    print("Testing multiline with long lines...")
    try:
        tui.content_area.draw(
            title="Multiline Long Test",
            content=multiline_long,
            item=None
        )
        print("✓ Multiline with long lines wrapped successfully")
    except AttributeError as e:
        if "'list' object has no attribute 'split'" in str(e):
            print(f"❌ BUG FOUND in multiline wrapping!")
            print(f"   Error: {e}")
            raise
        else:
            raise

    print("\n✅ Content wrapping test PASSED!")
    print("   wrap_text() return value handled correctly\n")

def test_all_menu_items():
    """
    Test rendering ALL menu items to ensure none cause crashes
    """
    print("="*60)
    print("TEST: All Menu Items Rendering")
    print("="*60)

    tui = UnibosDevTUI()
    sections = tui.get_menu_sections()

    total_items = 0
    for section_idx, section in enumerate(sections):
        print(f"\nSection {section_idx}: {section.label} ({len(section.items)} items)")

        for item_idx, item in enumerate(section.items):
            try:
                tui.content_area.draw(
                    title=item.label,
                    content=item.description,
                    item=item
                )
                total_items += 1
                print(f"  ✓ Item {item_idx}: {item.label}")
            except AttributeError as e:
                if "'list' object has no attribute 'split'" in str(e):
                    print(f"  ❌ BUG FOUND in item: {item.label}")
                    print(f"     Description type: {type(item.description)}")
                    print(f"     Error: {e}")
                    raise
                else:
                    raise

    print(f"\n✅ All menu items test PASSED!")
    print(f"   Successfully rendered {total_items} items across {len(sections)} sections\n")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TUI NAVIGATION CRASH FIX VERIFICATION")
    print("="*60)
    print("\nBug: 'list' object has no attribute 'split'")
    print("Location: content.py line 82")
    print("Cause: wrap_text() returns list, not string")
    print("Fix: Check type and extend list directly")
    print("="*60 + "\n")

    try:
        # Test 1: Arrow key navigation (original bug reproduction)
        test_arrow_key_navigation()

        # Test 2: Content wrapping (direct bug location)
        test_long_content_wrapping()

        # Test 3: All menu items (comprehensive check)
        test_all_menu_items()

        # Final summary
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - BUG IS FIXED!")
        print("="*60)
        print("\nThe TUI can now handle:")
        print("  • Arrow key navigation without crashes")
        print("  • Long content that requires wrapping")
        print("  • All menu item descriptions")
        print("  • Mixed content types (strings and lists)")
        print("\nThe fix correctly handles wrap_text() returning a list")
        print("instead of incorrectly calling .split() on it.")
        print("="*60 + "\n")

        return 0

    except Exception as e:
        import traceback
        print("\n" + "="*60)
        print("❌ TEST FAILED - BUG STILL EXISTS!")
        print("="*60)
        print(f"\nError: {e}")
        print("\nTraceback:")
        traceback.print_exc()
        print("="*60 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
