#!/usr/bin/env python3
"""
Test Preview Screens
====================
Test script to verify that module preview screens are working
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

def test_preview_renderers():
    """Test that all preview renderers are registered"""
    from cli_context_manager import get_cli_context
    from cli_content_renderers import register_all_renderers
    
    # Get context
    context = get_cli_context()
    
    # Register all renderers
    register_all_renderers(context)
    
    # Check that preview renderers are registered for main modules
    expected_modules = [
        'wimm', 'wims', 'currencies', 'kisisel', 
        'documents', 'cctv', 'recaria', 'birlikteyiz',
        'ai_builder', 'administration'
    ]
    
    print("Checking registered preview renderers:")
    print("=" * 50)
    
    for module_key in expected_modules:
        if module_key in context.content_renderers:
            renderer = context.content_renderers[module_key]
            print(f"✓ {module_key:<15} - {renderer.__class__.__name__}")
        else:
            print(f"✗ {module_key:<15} - NOT REGISTERED")
    
    print("=" * 50)
    
    # Test that we can get a renderer for the current selection
    print("\nTesting content rendering selection:")
    print("-" * 50)
    
    # Select first module
    context.state.selected_index = 0
    current_item = context.get_current_item()
    
    if current_item:
        print(f"Current item: {current_item.name} (key: {current_item.key})")
        
        if current_item.key in context.content_renderers:
            print(f"✓ Preview renderer available: {context.content_renderers[current_item.key].__class__.__name__}")
        else:
            print(f"⚠ Using default renderer")
    
    print("-" * 50)
    print("\n✅ Preview screen test complete!")


def test_renderer_output():
    """Test actual renderer output"""
    from cli_context_manager import get_cli_context
    from cli_content_renderers import register_all_renderers, WIMMPreviewRenderer
    import io
    import sys
    
    # Get context
    context = get_cli_context()
    register_all_renderers(context)
    
    print("\nTesting renderer output (sample):")
    print("=" * 50)
    
    # Create a WIMM renderer
    renderer = WIMMPreviewRenderer()
    
    # Capture output
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        # Render to a virtual area
        renderer.clear = lambda x, y, w, h: None  # Disable clearing for test
        renderer.render(context, 1, 1, 60, 25)
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Check if output contains expected content
        if "WIMM" in output and "expense tracking" in output:
            print("✓ WIMM renderer produces expected output")
        else:
            print("✗ WIMM renderer output unexpected")
            
        # Show a sample of the output (cleaned of ANSI codes)
        import re
        clean_output = re.sub(r'\033\[[^m]*m', '', output)
        clean_output = re.sub(r'\033\[\d+;\d+H', '\n', clean_output)
        lines = [line for line in clean_output.split('\n') if line.strip()][:5]
        
        print("\nSample output (first 5 lines):")
        for line in lines:
            print(f"  {line}")
            
    except Exception as e:
        sys.stdout = old_stdout
        print(f"Error testing renderer: {e}")
    
    print("=" * 50)


if __name__ == "__main__":
    print("Module Preview Screen Test")
    print("==========================\n")
    
    test_preview_renderers()
    test_renderer_output()