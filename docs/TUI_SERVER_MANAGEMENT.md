# TUI Django Server Management

## Overview

The UNIBOS-DEV TUI provides integrated Django development server management with proper process tracking and conflict resolution. This document describes the implementation and usage of the improved server management system.

## Key Features

### 1. PID-Based Process Tracking

The TUI uses a PID file (`/tmp/unibos_tui_django_server.pid`) to track servers it starts:

- **Start Server**: Creates PID file with the process ID
- **Check Status**: Reads PID file to verify if the process is still running
- **Stop Server**: Uses PID to gracefully stop the specific process
- **Cleanup**: Removes PID file when server stops

### 2. Intelligent Conflict Detection

Before starting a server, the TUI checks:

1. **TUI Server Check**: Is there already a TUI-started server running?
2. **Port Check**: Is port 8000 already in use?
3. **Process Check**: Are there other Django processes running?

This three-level check prevents conflicts while providing clear feedback.

### 3. Process Management

The TUI distinguishes between:

- **TUI-started servers**: Tracked via PID file, can be managed by TUI
- **External servers**: Started outside TUI, detected but not managed
- **Orphaned processes**: Stale processes that can be cleaned up

### 4. Graceful Shutdown

When stopping a server, the TUI:

1. Sends SIGTERM for graceful shutdown
2. Waits briefly for the process to terminate
3. Sends SIGKILL if still running
4. Cleans up the PID file
5. Optionally cleans up other Django processes

## Implementation Details

### Files and Paths

```python
# PID tracking file
server_pid_file = Path('/tmp/unibos_tui_django_server.pid')

# Server output log
server_log_file = Path('/tmp/unibos_django_server.log')
```

### Key Methods

#### `_check_server_running()`

Checks if a TUI-started server is running:

```python
def _check_server_running(self) -> tuple[bool, int]:
    """
    Returns: (is_running, pid)
    """
    if self.server_pid_file.exists():
        pid = int(self.server_pid_file.read_text())
        # Verify process is still alive and is Django
        if process_exists(pid) and is_django_process(pid):
            return True, pid
    return False, 0
```

#### `_check_port_in_use()`

Checks if a port is available:

```python
def _check_port_in_use(self, port: int = 8000) -> bool:
    """Check if port is in use"""
    with socket.socket() as s:
        try:
            s.bind(('127.0.0.1', port))
            return False  # Port is free
        except socket.error:
            return True   # Port is in use
```

#### `_find_django_processes()`

Finds all Django runserver processes:

```python
def _find_django_processes(self) -> list:
    """Find all Django runserver processes"""
    # Uses psutil if available, falls back to pgrep
    return [
        {'pid': pid, 'cmdline': cmdline}
        for each Django process found
    ]
```

## Usage Scenarios

### Scenario 1: Clean Start

User clicks "Start Server" with no servers running:

1. TUI checks PID file → not found
2. Checks port 8000 → available
3. Starts server with `unibos-dev dev run`
4. Saves PID to file
5. Shows success message with PID

### Scenario 2: TUI Server Already Running

User clicks "Start Server" with TUI server running:

1. TUI checks PID file → found and valid
2. Shows message: "TUI-started server is already running!"
3. Displays PID and suggests using Stop Server

### Scenario 3: External Server Blocking Port

User clicks "Start Server" with external Django running:

1. TUI checks PID file → not found
2. Checks port 8000 → in use
3. Finds Django processes via psutil/pgrep
4. Shows warning with options:
   - Stop the external server manually
   - Use Stop Server to kill all Django processes
   - Start on different port

### Scenario 4: Graceful Stop

User clicks "Stop Server":

1. TUI reads PID from file
2. Sends SIGTERM to process
3. Waits 1 second
4. Checks if stopped, sends SIGKILL if needed
5. Removes PID file
6. Reports success

### Scenario 5: Orphaned Process Cleanup

TUI finds PID file but process is dead:

1. Detects stale PID file
2. Removes PID file
3. Optionally cleans up other Django processes
4. Allows fresh start

## Testing

### Manual Testing

1. Start server through TUI
2. Verify it runs at http://127.0.0.1:8000
3. Stop server through TUI
4. Verify cleanup

### Test Scripts

Two test scripts are provided:

1. **test_tui_server.py**: Full integration test
   - Simulates TUI server lifecycle
   - Tests PID tracking
   - Verifies cleanup

2. **test_tui_interactive.py**: Direct function testing
   - Tests individual TUI methods
   - Checks file states
   - Validates process detection

### Running Tests

```bash
# Full integration test
python3 test_tui_server.py

# Function-level test
python3 test_tui_interactive.py
```

## Error Handling

The TUI handles various error conditions:

1. **Permission Denied**: Can't stop process owned by another user
2. **Port Already in Use**: Another service using port 8000
3. **Process Start Failure**: Django configuration errors
4. **Stale PID Files**: Cleaned up automatically
5. **Missing Dependencies**: Falls back to basic tools

## Benefits

1. **Reliable Process Management**: No more "already running" false positives
2. **Clear Ownership**: TUI knows which servers it started
3. **Clean Shutdown**: Proper signal handling
4. **Better Debugging**: Separate log files for TUI sessions
5. **User-Friendly**: Clear messages about what's happening

## Future Enhancements

Potential improvements:

1. **Multiple Port Support**: Allow starting on alternate ports
2. **Process Groups**: Track all child processes
3. **Auto-Recovery**: Restart failed servers automatically
4. **Remote Management**: Control servers on other machines
5. **Status Dashboard**: Real-time server metrics

## Troubleshooting

### "Server already running" but nothing on port 8000

```bash
# Check for orphaned processes
pgrep -f "manage.py runserver"

# Clean up
pkill -f "manage.py runserver"

# Remove stale PID file
rm -f /tmp/unibos_tui_django_server.pid
```

### Can't stop server

```bash
# Find all Django processes
ps aux | grep "manage.py runserver"

# Force kill specific PID
kill -9 <PID>

# Kill all Django servers
pkill -9 -f "manage.py runserver"
```

### Port 8000 in use by non-Django service

```bash
# Find what's using port 8000
lsof -i :8000

# Or use netstat
netstat -an | grep 8000
```

## Dependencies

- **psutil** (preferred): Process management library
- **pgrep/pkill** (fallback): Unix process tools
- **Python socket**: Port checking
- **os.kill**: Signal sending

The implementation gracefully falls back if psutil is not available.