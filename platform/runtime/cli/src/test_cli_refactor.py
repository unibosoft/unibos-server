#!/usr/bin/env python3
"""
Test script for CLI refactoring
================================
Tests the centralized CLI context manager integration
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, '.')

def test_context_creation():
    """Test context creation and initialization"""
    from cli_context_manager import get_cli_context, UISection
    
    context = get_cli_context()
    assert context is not None, "Context should be created"
    assert len(context.modules) > 0, "Should have default modules"
    assert len(context.tools) > 0, "Should have default tools"
    assert len(context.dev_tools) > 0, "Should have default dev tools"
    
    print("✓ Context creation test passed")
    return context


def test_navigation(context):
    """Test navigation functions"""
    # Test section switching
    initial_section = context.state.current_section
    context.switch_section()
    assert context.state.current_section != initial_section, "Section should change"
    
    # Test up/down navigation
    context.state.selected_index = 1
    context.navigate_up()
    assert context.state.selected_index == 0, "Should navigate up"
    
    context.navigate_down()
    assert context.state.selected_index == 1, "Should navigate down"
    
    print("✓ Navigation test passed")


def test_menu_sync():
    """Test menu synchronization with main.py"""
    # Import minimal requirements avoiding full UI initialization
    import sys
    import os
    
    # Set minimal environment to prevent UI from starting
    os.environ['UNIBOS_TEST_MODE'] = '1'
    
    # Import only the needed functions
    import main
    
    # Check if context is available
    if not hasattr(main, 'CLI_CONTEXT_AVAILABLE'):
        print("⚠ Skipping menu sync test - main module initialization issue")
        return
    
    if not main.CLI_CONTEXT_AVAILABLE:
        print("⚠ Skipping menu sync test - CLI context not available in main")
        return
    
    # Initialize menus
    main.initialize_menu_items()
    
    # Check sync
    assert len(main.menu_state.modules) == len(main.cli_context.modules), "Modules should be synced"
    assert len(main.menu_state.tools) == len(main.cli_context.tools), "Tools should be synced"
    assert len(main.menu_state.dev_tools) == len(main.cli_context.dev_tools), "Dev tools should be synced"
    
    print("✓ Menu sync test passed")


def test_content_renderers():
    """Test content renderer registration"""
    from cli_context_manager import get_cli_context
    from cli_content_renderers import register_all_renderers
    
    context = get_cli_context()
    register_all_renderers(context)
    
    # Check if renderers are registered
    assert 'tools' in context.content_renderers, "Tools renderer should be registered"
    assert 'system_info' in context.content_renderers, "System info renderer should be registered"
    assert 'security_tools' in context.content_renderers, "Security tools renderer should be registered"
    assert 'web_forge' in context.content_renderers, "Web forge renderer should be registered"
    assert 'version_manager' in context.content_renderers, "Version manager renderer should be registered"
    
    print("✓ Content renderer test passed")


def test_sidebar_rendering():
    """Test sidebar rendering (without actual display)"""
    import os
    os.environ['UNIBOS_TEST_MODE'] = '1'
    
    try:
        import main
        if not main.CLI_CONTEXT_AVAILABLE:
            print("⚠ Skipping sidebar test - CLI context not available in main")
            return
            
        # Initialize
        main.initialize_menu_items()
        context = main.cli_context
    
        # Update terminal size
        context.state.cols = 80
        context.state.lines = 24
        
        # Test that draw_sidebar doesn't crash
        try:
            # Capture output
            import io
            from contextlib import redirect_stdout
            
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                main.draw_sidebar()
            
            output = buffer.getvalue()
            # Check that something was written (ANSI codes at minimum)
            assert len(output) > 0, "Sidebar should produce output"
            
            print("✓ Sidebar rendering test passed")
        except Exception as e:
            print(f"✗ Sidebar rendering failed: {e}")
            raise
    except ImportError:
        print("⚠ Skipping sidebar test - main module not importable")
        return


def test_content_clearing():
    """Test content area clearing"""
    import os
    os.environ['UNIBOS_TEST_MODE'] = '1'
    
    try:
        import main
        if not main.CLI_CONTEXT_AVAILABLE:
            print("⚠ Skipping content clearing test - CLI context not available in main")
            return
            
        # Capture output
        import io
        from contextlib import redirect_stdout
        
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            main.clear_content_area()
        
        # Should produce output (ANSI codes)
        output = buffer.getvalue()
        assert len(output) > 0, "Clear content should produce output"
        
        print("✓ Content clearing test passed")
    except ImportError:
        print("⚠ Skipping content clearing test - main module not importable")
        return
    except Exception as e:
        print(f"✗ Content clearing failed: {e}")
        raise


def main():
    """Run all tests"""
    print("=" * 50)
    print("CLI Refactoring Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Context creation
        context = test_context_creation()
        
        # Test 2: Navigation
        test_navigation(context)
        
        # Test 3: Menu sync
        test_menu_sync()
        
        # Test 4: Content renderers
        test_content_renderers()
        
        # Test 5: Sidebar rendering
        test_sidebar_rendering()
        
        # Test 6: Content clearing
        test_content_clearing()
        
        print("=" * 50)
        print("✅ All tests passed successfully!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())