#!/usr/bin/env python3
"""
Test script for Manager TUI
Verifies the manager profile TUI loads correctly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_manager_tui_import():
    """Test that ManagerTUI can be imported"""
    try:
        from core.profiles.manager.tui import ManagerTUI
        print("✅ ManagerTUI import successful")
        return True
    except Exception as e:
        print(f"❌ ManagerTUI import failed: {e}")
        return False

def test_manager_tui_creation():
    """Test that ManagerTUI can be instantiated"""
    try:
        from core.profiles.manager.tui import ManagerTUI
        tui = ManagerTUI()
        print("✅ ManagerTUI instantiation successful")
        return True
    except Exception as e:
        print(f"❌ ManagerTUI instantiation failed: {e}")
        return False

def test_manager_menu_structure():
    """Test that ManagerTUI has correct menu structure"""
    try:
        from core.profiles.manager.tui import ManagerTUI
        tui = ManagerTUI()
        sections = tui.get_menu_sections()

        # Should have 3 sections
        if len(sections) != 3:
            print(f"❌ Expected 3 sections, got {len(sections)}")
            return False

        # Check section IDs
        section_ids = [s.id for s in sections]
        expected_ids = ['targets', 'operations', 'monitoring']

        if section_ids != expected_ids:
            print(f"❌ Expected sections {expected_ids}, got {section_ids}")
            return False

        # Check section item counts
        print(f"  → Targets section: {len(sections[0].items)} items")
        print(f"  → Operations section: {len(sections[1].items)} items")
        print(f"  → Monitoring section: {len(sections[2].items)} items")

        print("✅ ManagerTUI menu structure correct")
        return True
    except Exception as e:
        print(f"❌ Menu structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manager_handlers():
    """Test that all handlers are registered"""
    try:
        from core.profiles.manager.tui import ManagerTUI
        tui = ManagerTUI()

        # Get all menu items
        sections = tui.get_menu_sections()
        all_items = []
        for section in sections:
            all_items.extend(section.items)

        # Check each item has a handler
        missing_handlers = []
        for item in all_items:
            if item.id not in tui.action_handlers:
                missing_handlers.append(item.id)

        if missing_handlers:
            print(f"❌ Missing handlers for: {missing_handlers}")
            return False

        print(f"✅ All {len(all_items)} handlers registered correctly")
        return True
    except Exception as e:
        print(f"❌ Handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manager_profile_name():
    """Test that profile name is correct"""
    try:
        from core.profiles.manager.tui import ManagerTUI
        tui = ManagerTUI()
        profile = tui.get_profile_name()

        if profile != "manager":
            print(f"❌ Expected profile 'manager', got '{profile}'")
            return False

        print(f"✅ Profile name correct: {profile}")
        return True
    except Exception as e:
        print(f"❌ Profile name test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("UNIBOS Manager TUI Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Import Test", test_manager_tui_import),
        ("Instantiation Test", test_manager_tui_creation),
        ("Menu Structure Test", test_manager_menu_structure),
        ("Handler Registration Test", test_manager_handlers),
        ("Profile Name Test", test_manager_profile_name),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 60)
        result = test_func()
        results.append(result)
        print()

    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
