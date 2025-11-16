#!/usr/bin/env python3
"""
Test Django server startup through TUI
"""
import subprocess
import time
import os

# Clean up any existing processes
print("Cleaning up existing Django processes...")
subprocess.run(['pkill', '-f', 'manage.py runserver'], capture_output=True)

# Remove PID file if exists
pid_file = '/tmp/unibos_tui_django_server.pid'
if os.path.exists(pid_file):
    os.remove(pid_file)
    print(f"Removed PID file: {pid_file}")

time.sleep(1)

print("\nTrying to start Django server through unibos-dev TUI...")
print("This simulates what happens when you select 'Start Development Server' in TUI")

# Test the TUI server startup
print("\n1. First checking if port 8000 is free...")
result = subprocess.run(['lsof', '-i', ':8000'], capture_output=True)
if result.returncode == 0:
    print("   Port 8000 is already in use!")
    print(result.stdout.decode())
else:
    print("   Port 8000 is free ✓")

print("\n2. Starting Django server via unibos-dev command...")
print("   Command: unibos-dev dev run")

# Start the server
proc = subprocess.Popen(
    ['unibos-dev', 'dev', 'run'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Give it time to start
print("   Waiting for server to start...")
time.sleep(5)

# Check if it's running
if proc.poll() is None:
    print("\n✅ Server started successfully!")
    print("   Server is running on http://127.0.0.1:8000")
    print("\n   To stop the server, press Ctrl+C or run: pkill -f 'manage.py runserver'")

    # Show first few lines of output
    print("\n   Server output:")
    for _ in range(10):
        line = proc.stdout.readline()
        if line:
            print(f"   {line.rstrip()}")
        line = proc.stderr.readline()
        if line:
            print(f"   ERROR: {line.rstrip()}")

    # Keep running
    print("\n   Server is running. Press Ctrl+C to stop...")
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n   Stopping server...")
        proc.terminate()
        proc.wait()
else:
    print("\n❌ Server failed to start!")
    stdout, stderr = proc.communicate()
    if stdout:
        print("   Output:", stdout)
    if stderr:
        print("   Error:", stderr)