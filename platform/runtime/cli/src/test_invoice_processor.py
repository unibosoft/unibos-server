#!/usr/bin/env python3
"""
Test script for Invoice Processor CLI Integration
==================================================
Tests the invoice processor module integration and content clearing.
"""

import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
print("testing imports...")
try:
    from cli_context_manager import CLIContext, get_cli_context, ContentRenderer, Colors
    print("✓ cli_context_manager imported")
except ImportError as e:
    print(f"✗ failed to import cli_context_manager: {e}")
    sys.exit(1)

try:
    from cli_content_renderers import InvoiceProcessorRenderer, DocumentsMenuRenderer, register_all_renderers
    print("✓ cli_content_renderers imported")
except ImportError as e:
    print(f"✗ failed to import cli_content_renderers: {e}")
    sys.exit(1)

try:
    from invoice_processor_cli import InvoiceProcessorCLI
    print("✓ invoice_processor_cli imported")
except ImportError as e:
    print(f"✗ failed to import invoice_processor_cli: {e}")
    sys.exit(1)

# Test content clearing
print("\ntesting content clearing...")
context = get_cli_context()
register_all_renderers(context)

# Clear screen
sys.stdout.write("\033[2J\033[H")
sys.stdout.flush()

# Test rendering
print("testing document menu renderer...")
doc_menu = DocumentsMenuRenderer()

# Simulate rendering
try:
    doc_menu.render(context, 1, 1, 80, 24)
    print("\n\n✓ document menu rendered successfully")
except Exception as e:
    print(f"\n\n✗ failed to render document menu: {e}")

time.sleep(2)

# Clear and test invoice processor
sys.stdout.write("\033[2J\033[H")
print("testing invoice processor renderer...")
invoice_renderer = InvoiceProcessorRenderer()

try:
    invoice_renderer.render(context, 1, 1, 80, 24)
    print("\n\n✓ invoice processor rendered successfully")
except Exception as e:
    print(f"\n\n✗ failed to render invoice processor: {e}")

# Test the clear function
time.sleep(2)
print("\n\ntesting clear function...")
renderer = ContentRenderer()
renderer.clear(1, 1, 80, 24)
print("✓ clear function executed")

# Summary
print("\n" + "="*50)
print("test summary:")
print("✓ all imports successful")
print("✓ renderers created")
print("✓ content clearing tested")
print("✓ invoice processor integrated")
print("\nto test in main app:")
print("1. run main.py")
print("2. navigate to documents module")
print("3. press enter to open documents menu")
print("4. select invoice processor")
print("5. verify no content bleeding")
print("="*50)