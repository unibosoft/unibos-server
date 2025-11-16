#!/usr/bin/env python3
"""
Test TUI functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent  # Go up to unibos-dev root
sys.path.insert(0, str(project_root))

def test_tui_basic():
    """Test basic TUI functionality"""
    print("Testing TUI imports...")

    try:
        from core.profiles.dev.tui import UnibosDevTUI
        print("✓ UnibosDevTUI imported successfully")

        # Create TUI instance
        tui = UnibosDevTUI()
        print("✓ TUI instance created")

        # Test menu sections
        sections = tui.get_menu_sections()
        print(f"✓ Found {len(sections)} menu sections")

        for section in sections:
            print(f"  - {section.label}: {len(section.items)} items")
            for item in section.items[:2]:  # Show first 2 items
                print(f"    • {item.label}")

        # Test action handlers
        print("\n✓ Action handlers registered:")
        for action_id in list(tui.action_handlers.keys())[:5]:
            print(f"  - {action_id}")

        print("\n✅ TUI test completed successfully!")
        print("\nTo run the full TUI, execute: unibos-dev")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tui_basic()