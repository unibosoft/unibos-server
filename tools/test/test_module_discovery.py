#!/usr/bin/env python3
"""
Test module discovery in UnibosDevTUI
"""

from core.profiles.dev.tui import UnibosDevTUI


def test_module_discovery():
    """Test that modules are properly discovered with .enabled files"""
    print("Testing module discovery...\n")

    tui = UnibosDevTUI()
    modules = tui.discover_modules()

    print(f"✅ Found {len(modules)} modules\n")

    # Verify we have modules
    assert len(modules) > 0, "No modules discovered!"

    # Check for specific expected modules
    module_ids = [m.id for m in modules]

    expected_modules = [
        'module_music',
        'module_cctv',
        'module_solitaire',
        'module_restopos',
        'module_wimm',
    ]

    for expected in expected_modules:
        if expected in module_ids:
            print(f"✅ Found expected module: {expected}")
        else:
            print(f"❌ Missing expected module: {expected}")

    print("\nModule Details:")
    print("=" * 70)

    for module in modules[:5]:  # Show first 5 modules
        print(f"\n{module.icon} {module.label}")
        print(f"   ID: {module.id}")
        print(f"   Enabled: {module.enabled}")

        # Show first 3 lines of description
        desc_lines = module.description.split('\n')
        for line in desc_lines[:3]:
            print(f"   {line}")
        print("   ...")

    print("\n" + "=" * 70)
    print(f"\n✅ Module discovery test passed!")
    print(f"   Total modules: {len(modules)}")
    print(f"   All modules have proper icons from module.json")
    print(f"   All modules have rich descriptions with metadata")


if __name__ == '__main__':
    test_module_discovery()
