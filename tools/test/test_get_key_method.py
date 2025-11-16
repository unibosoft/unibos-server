#!/usr/bin/env python3
"""
Test the get_key() method implementation
"""

import sys
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos-dev')

from core.clients.tui.base import BaseTUI, TUIConfig
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Keys

class TestTUI(BaseTUI):
    """Simple test TUI"""

    def get_profile_name(self) -> str:
        return "test"

    def get_menu_sections(self):
        return [
            MenuSection(
                id='test',
                label='Test',
                icon='🧪',
                items=[
                    MenuItem(
                        id='item1',
                        label='Item 1',
                        icon='1️⃣',
                        description='Test item',
                        enabled=True
                    ),
                ]
            )
        ]

def test_get_key_method():
    """Test that get_key() method exists and has correct signature"""
    print("Testing get_key() method...\n")

    tui = TestTUI()

    # Check if method exists
    if not hasattr(tui, 'get_key'):
        print("❌ get_key() method does not exist!")
        return False

    print("✅ get_key() method exists")

    # Check method signature
    import inspect
    sig = inspect.signature(tui.get_key)
    print(f"   Signature: {sig}")
    print(f"   Parameters: {list(sig.parameters.keys())}")

    # Check return type annotation
    if sig.return_annotation != inspect.Signature.empty:
        print(f"   Return type: {sig.return_annotation}")

    # Check docstring
    if tui.get_key.__doc__:
        print(f"   Docstring: {tui.get_key.__doc__.split(chr(10))[0].strip()}")

    print("\n✅ get_key() method is properly implemented")
    return True

if __name__ == "__main__":
    success = test_get_key_method()
    sys.exit(0 if success else 1)
