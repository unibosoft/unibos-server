#!/usr/bin/env python3
"""
Test TUI interactive mode with simulated inputs
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent  # Go up to unibos-dev root
sys.path.insert(0, str(project_root))

def test_action_handlers():
    """Test individual action handlers"""
    print("Testing action handlers...\n")

    from core.profiles.dev.tui import UnibosDevTUI
    from core.clients.cli.framework.ui import MenuItem

    tui = UnibosDevTUI()

    # Test git status handler
    print("Testing git_status handler...")
    item = MenuItem(
        id='git_status',
        label='git status',
        icon='📊',
        description='Show git status'
    )

    try:
        # Mock the show_command_output method for testing
        def mock_show(result):
            print(f"Command output (return code: {result.returncode}):")
            if result.stdout:
                print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)

        tui.show_command_output = mock_show

        # Test the handler
        result = tui.handle_git_status(item)
        print(f"✓ git_status handler returned: {result}\n")

    except Exception as e:
        print(f"❌ Error in git_status handler: {e}\n")

    # Test platform status handler
    print("Testing platform_status handler...")
    item = MenuItem(
        id='platform_status',
        label='system status',
        icon='📊',
        description='Show system status'
    )

    try:
        result = tui.handle_platform_status(item)
        print(f"✓ platform_status handler returned: {result}\n")
    except Exception as e:
        print(f"❌ Error in platform_status handler: {e}\n")

if __name__ == "__main__":
    test_action_handlers()
    print("\n✅ Handler tests completed!")
    print("\nTo run the full interactive TUI, execute: unibos-dev")