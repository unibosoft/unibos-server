#!/usr/bin/env python3
"""
Interactive test of TUI server management
This simulates what the TUI does internally
"""

import sys
import os
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos-dev')

from pathlib import Path
from core.profiles.dev.tui import UnibosDevTUI

def test_server_functions():
    """Test the TUI server management functions directly"""

    print("=== Testing TUI Server Management Functions ===\n")

    # Create TUI instance
    tui = UnibosDevTUI()

    # Test 1: Check server status
    print("1. Checking server status...")
    is_running, pid = tui._check_server_running()
    if is_running:
        print(f"   - TUI server is running with PID: {pid}")
    else:
        print("   - TUI server is not running")

    port_in_use = tui._check_port_in_use(8000)
    if port_in_use:
        print("   - Port 8000 is in use")
    else:
        print("   - Port 8000 is free")

    django_procs = tui._find_django_processes()
    if django_procs:
        print(f"   - Found {len(django_procs)} Django process(es):")
        for proc in django_procs:
            print(f"     • PID {proc['pid']}: {proc['cmdline'][:60]}...")
    else:
        print("   - No Django processes found")

    print()

    # Test 2: PID file status
    print("2. PID file status:")
    if tui.server_pid_file.exists():
        pid_content = tui.server_pid_file.read_text().strip()
        print(f"   - PID file exists: {tui.server_pid_file}")
        print(f"   - Contains PID: {pid_content}")

        # Verify if PID is valid
        try:
            import psutil
            proc = psutil.Process(int(pid_content))
            cmdline = ' '.join(proc.cmdline())
            print(f"   - Process is running: {cmdline[:60]}...")
        except (psutil.NoSuchProcess, ValueError):
            print("   - Process is NOT running (stale PID file)")
    else:
        print(f"   - No PID file at: {tui.server_pid_file}")

    print()

    # Test 3: Log file status
    print("3. Log file status:")
    if tui.server_log_file.exists():
        size = tui.server_log_file.stat().st_size
        print(f"   - Log file exists: {tui.server_log_file}")
        print(f"   - Size: {size} bytes")

        if size > 0:
            with open(tui.server_log_file, 'r') as f:
                lines = f.readlines()
                print(f"   - Contains {len(lines)} lines")
                if lines:
                    print(f"   - Last line: {lines[-1].rstrip()}")
    else:
        print(f"   - No log file at: {tui.server_log_file}")

    print("\n=== Test Complete ===")

    # Return summary
    return {
        'tui_server_running': is_running,
        'tui_server_pid': pid if is_running else None,
        'port_8000_in_use': port_in_use,
        'django_processes': len(django_procs),
        'pid_file_exists': tui.server_pid_file.exists(),
        'log_file_exists': tui.server_log_file.exists()
    }


if __name__ == "__main__":
    # First clean up any processes
    import subprocess
    print("Cleaning up any orphaned processes...\n")
    subprocess.run(['pkill', '-f', 'manage.py runserver'], capture_output=True)

    # Run the test
    summary = test_server_functions()

    print("\nSummary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
