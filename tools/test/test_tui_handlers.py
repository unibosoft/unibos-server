#!/usr/bin/env python3
"""
Test script to verify all TUI handlers are properly registered
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.profiles.dev.tui import UnibosDevTUI

def test_handlers():
    """Test that all handlers are registered"""
    print("Testing UnibosDevTUI handler registration...\n")

    # Create TUI instance
    tui = UnibosDevTUI()

    # Expected handlers
    expected_handlers = [
        # TOOLS section
        'system_scrolls',
        'castle_guard',
        'forge_smithy',
        'anvil_repair',
        'code_forge',
        'web_ui',
        'administration',
        # DEV TOOLS section
        'ai_builder',
        'database_setup',
        'public_server',
        'sd_card',
        'version_manager',
    ]

    # Check each handler
    results = []
    for handler_id in expected_handlers:
        is_registered = handler_id in tui.action_handlers
        status = "✓" if is_registered else "✗"
        results.append((handler_id, is_registered))
        print(f"{status} {handler_id:20} {'REGISTERED' if is_registered else 'MISSING'}")

    # Summary
    print("\n" + "="*60)
    total = len(expected_handlers)
    registered = sum(1 for _, r in results if r)
    print(f"Total handlers: {total}")
    print(f"Registered: {registered}")
    print(f"Missing: {total - registered}")

    if registered == total:
        print("\n✓ All handlers are properly registered!")
        return True
    else:
        print("\n✗ Some handlers are missing!")
        return False

def test_menu_structure():
    """Test menu structure"""
    print("\n" + "="*60)
    print("Testing menu structure...\n")

    tui = UnibosDevTUI()
    sections = tui.get_menu_sections()

    print(f"Total sections: {len(sections)}\n")

    for section in sections:
        print(f"Section: {section.icon} {section.label}")
        print(f"  Items: {len(section.items)}")
        for item in section.items[:3]:  # Show first 3 items
            print(f"    - {item.icon} {item.label}")
        if len(section.items) > 3:
            print(f"    ... and {len(section.items) - 3} more")
        print()

    return True

if __name__ == '__main__':
    try:
        success1 = test_handlers()
        success2 = test_menu_structure()

        if success1 and success2:
            print("\n" + "="*60)
            print("✓ All tests passed!")
            sys.exit(0)
        else:
            print("\n" + "="*60)
            print("✗ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
