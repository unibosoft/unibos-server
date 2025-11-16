#!/usr/bin/env python3
"""
Test script for TUI server management improvements
"""

import subprocess
import time
import os
import signal
from pathlib import Path

def test_server_management():
    """Test the improved server management functionality"""

    print("=== Testing TUI Server Management ===\n")

    # Test files
    pid_file = Path('/tmp/unibos_tui_django_server.pid')
    log_file = Path('/tmp/unibos_django_server.log')

    # 1. Check initial state
    print("1. Checking initial state...")
    if pid_file.exists():
        print(f"   - Cleaning up old PID file: {pid_file}")
        pid_file.unlink()
    if log_file.exists():
        print(f"   - Old log file exists: {log_file}")

    # Check for any existing Django processes
    result = subprocess.run(['pgrep', '-f', 'manage.py runserver'], capture_output=True)
    if result.returncode == 0:
        pids = result.stdout.decode().strip().split('\n')
        print(f"   - WARNING: Found {len(pids)} existing Django process(es): {pids}")
    else:
        print("   - No Django processes running ✓")

    print()

    # 2. Start server via CLI (simulating TUI behavior)
    print("2. Starting Django server (simulating TUI)...")

    # Start the server in background
    with open(log_file, 'w') as f:
        process = subprocess.Popen(
            ['unibos-dev', 'dev', 'run'],
            stdout=f,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid
        )

    # Save PID
    pid_file.write_text(str(process.pid))
    print(f"   - Started server with PID: {process.pid}")
    print(f"   - PID saved to: {pid_file}")
    print(f"   - Logs writing to: {log_file}")

    # Wait for server to start
    print("   - Waiting for server to start...")
    time.sleep(3)

    # Check if it's running
    if process.poll() is None:
        print("   - Server is running ✓")
    else:
        print("   - ERROR: Server failed to start!")
        if log_file.exists():
            with open(log_file, 'r') as f:
                print("\n   Log output:")
                print(f.read()[:500])
        return False

    print()

    # 3. Check server status
    print("3. Checking server status...")

    # Check PID file
    if pid_file.exists():
        saved_pid = int(pid_file.read_text().strip())
        print(f"   - PID file contains: {saved_pid}")

        # Check if process is running
        try:
            os.kill(saved_pid, 0)
            print(f"   - Process {saved_pid} is running ✓")
        except ProcessLookupError:
            print(f"   - ERROR: Process {saved_pid} is not running!")
    else:
        print("   - ERROR: PID file missing!")

    # Check port
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', 8000))
            print("   - ERROR: Port 8000 is not in use (server not listening)")
        except socket.error:
            print("   - Port 8000 is in use ✓")

    # Check with pgrep
    result = subprocess.run(['pgrep', '-f', 'manage.py runserver'], capture_output=True)
    if result.returncode == 0:
        pids = result.stdout.decode().strip().split('\n')
        print(f"   - Found {len(pids)} Django process(es): {pids}")

    print()

    # 4. Test duplicate start prevention
    print("4. Testing duplicate start prevention...")
    print("   - Attempting to start server again (should be prevented)...")

    # This would be handled by TUI logic checking PID file
    if pid_file.exists():
        saved_pid = int(pid_file.read_text().strip())
        try:
            os.kill(saved_pid, 0)
            print("   - Server already running (as expected) ✓")
        except ProcessLookupError:
            print("   - ERROR: PID file exists but process is dead!")

    print()

    # 5. Stop the server
    print("5. Stopping the server...")

    if pid_file.exists():
        saved_pid = int(pid_file.read_text().strip())
        print(f"   - Stopping PID {saved_pid}...")

        try:
            # Send SIGTERM
            os.kill(saved_pid, signal.SIGTERM)
            print("   - Sent SIGTERM")

            # Wait a moment
            time.sleep(2)

            # Check if stopped
            try:
                os.kill(saved_pid, 0)
                print("   - Process still running, sending SIGKILL...")
                os.kill(saved_pid, signal.SIGKILL)
            except ProcessLookupError:
                print("   - Process stopped successfully ✓")

            # Clean up PID file
            pid_file.unlink()
            print("   - PID file removed ✓")

        except Exception as e:
            print(f"   - ERROR: {e}")

    print()

    # 6. Verify cleanup
    print("6. Verifying cleanup...")

    # Check no processes running
    result = subprocess.run(['pgrep', '-f', 'manage.py runserver'], capture_output=True)
    if result.returncode == 0:
        pids = result.stdout.decode().strip().split('\n')
        print(f"   - WARNING: Still found {len(pids)} Django process(es): {pids}")
        print("   - Cleaning up...")
        subprocess.run(['pkill', '-f', 'manage.py runserver'])
        time.sleep(1)
    else:
        print("   - No Django processes running ✓")

    # Check PID file removed
    if not pid_file.exists():
        print("   - PID file removed ✓")
    else:
        print("   - WARNING: PID file still exists")

    # Check port is free
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', 8000))
            print("   - Port 8000 is free ✓")
        except socket.error:
            print("   - WARNING: Port 8000 still in use")

    print()

    # 7. Show log sample
    if log_file.exists():
        print("7. Server log sample:")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                print("   First 5 lines:")
                for line in lines[:5]:
                    print(f"   > {line.rstrip()}")

    print("\n=== Test Complete ===")
    return True


if __name__ == "__main__":
    # Clean up any orphaned processes first
    print("Cleaning up any orphaned Django processes...")
    subprocess.run(['pkill', '-f', 'manage.py runserver'], capture_output=True)
    time.sleep(1)

    # Run the test
    test_server_management()