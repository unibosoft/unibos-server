# Manager Profile - Complete Implementation

This document describes the implementation of the **manager** profile, the 4th profile in the UNIBOS architecture.

## Overview

The manager profile has been successfully integrated into the UNIBOS architecture as a first-class profile alongside dev, server, and prod.

## Architecture

### Profile Structure

```
core/profiles/
├── dev/           # Development profile (existing)
│   ├── __init__.py
│   ├── main.py
│   ├── tui.py
│   └── commands/
├── server/        # Server profile (existing)
│   ├── __init__.py
│   ├── tui.py
│   └── commands/
├── prod/          # Production profile (existing)
│   ├── __init__.py
│   ├── tui.py
│   └── commands/
└── manager/       # Manager profile (NEW)
    ├── __init__.py
    ├── main.py         # CLI entry point
    ├── tui.py          # ManagerTUI class
    ├── README.md       # Documentation
    └── commands/       # CLI commands
        ├── __init__.py
        ├── deploy.py   # Deployment commands
        ├── status.py   # Status checking
        └── ssh.py      # SSH operations
```

## Implementation Details

### 1. ManagerTUI Class (`tui.py`)

The ManagerTUI class inherits from BaseTUI and implements:

**3-Section Menu Structure:**
1. **Targets** (3 items)
   - rocksteady - Production server
   - local dev - Local development
   - list nodes - Node management

2. **Operations** (6 items)
   - deploy - Deploy to target
   - restart services - Restart services
   - view logs - View logs
   - run migrations - Database migrations
   - backup database - Database backup
   - ssh to server - SSH connection

3. **Monitoring** (5 items)
   - system status - System overview
   - service health - Service health
   - git status - Git repository
   - django status - Django status
   - resource usage - Resource monitoring

**Key Features:**
- Target switching (rocksteady/local)
- Remote operation handlers
- Monitoring capabilities
- SSH integration
- Consistent UX with other profiles

### 2. CLI Commands

**Deploy Command** (`commands/deploy.py`)
```bash
unibos-dev manager deploy rocksteady
unibos-dev manager deploy local --skip-migrations
```

Handles:
- Code pushing to git
- Remote pull on target
- Dependency installation
- Database migrations
- Static file collection
- Service restart

**Status Command** (`commands/status.py`)
```bash
unibos-dev manager status
unibos-dev manager status rocksteady
unibos-dev manager status local
```

Checks:
- SSH connectivity
- Git repository status
- Service status
- Disk usage
- Database connectivity
- Django server status

**SSH Command** (`commands/ssh.py`)
```bash
unibos-dev manager ssh rocksteady
unibos-dev manager ssh rocksteady --command "ls -la"
```

Provides:
- Interactive SSH sessions
- Remote command execution
- Secure connections

### 3. Integration with Main CLI

The manager profile is integrated into the main `unibos-dev` CLI:

**In `core/profiles/dev/main.py`:**
```python
# Import manager profile CLI
from core.profiles.manager.main import cli as manager_cli

# Register as command group
cli.add_command(manager_cli, name='manager')
```

This allows:
```bash
unibos-dev manager --help
unibos-dev manager tui
unibos-dev manager status
unibos-dev manager deploy rocksteady
unibos-dev manager ssh rocksteady
```

## Usage Examples

### 1. Launch Manager TUI
```bash
unibos-dev manager tui
```

### 2. Check All Systems
```bash
unibos-dev manager status
```

### 3. Deploy to Production
```bash
# 1. Commit and push locally
git add .
git commit -m "Update feature"
git push

# 2. Deploy to rocksteady
unibos-dev manager deploy rocksteady
```

### 4. SSH to Server
```bash
# Interactive session
unibos-dev manager ssh rocksteady

# Execute command
unibos-dev manager ssh rocksteady --command "systemctl status unibos"
```

### 5. View Remote Logs
```bash
unibos-dev manager ssh rocksteady --command "tail -f /var/log/unibos/app.log"
```

## Testing

All tests pass successfully:

```bash
python3 tools/test/test_manager_tui.py
```

**Test Results:**
- ✅ Import Test
- ✅ Instantiation Test
- ✅ Menu Structure Test (3 sections, 14 items)
- ✅ Handler Registration Test (14 handlers)
- ✅ Profile Name Test

## Design Principles

### 1. Consistent Architecture
- Uses same BaseTUI as dev/server/prod
- Follows same component patterns
- Consistent navigation and UX

### 2. Remote-First Design
- All operations target remote instances
- SSH-based communication
- No local Django dependencies

### 3. Separation of Concerns
- **dev**: Local development
- **server**: Server operations (on rocksteady)
- **prod**: Production-specific
- **manager**: Remote management (from anywhere)

### 4. Integration over Replacement
- Integrates with existing CLI
- Complements other profiles
- Doesn't replace deployment tools

## File Manifest

All files created for the manager profile:

```
/Users/berkhatirli/Desktop/unibos-dev/core/profiles/manager/
├── __init__.py                    # Package initialization
├── main.py                        # CLI entry point
├── tui.py                         # ManagerTUI class
├── README.md                      # Profile documentation
└── commands/
    ├── __init__.py                # Commands package
    ├── deploy.py                  # Deployment command
    ├── status.py                  # Status command
    └── ssh.py                     # SSH command

/Users/berkhatirli/Desktop/unibos-dev/docs/
└── MANAGER_PROFILE.md             # This document

/Users/berkhatirli/Desktop/unibos-dev/tools/test/
└── test_manager_tui.py            # Test suite
```

**Modified files:**
```
/Users/berkhatirli/Desktop/unibos-dev/core/profiles/dev/main.py
  - Added manager CLI import
  - Registered manager command group
  - Updated help text
```

## Commands Reference

### CLI Commands

```bash
# Show help
unibos-dev manager --help

# Launch TUI
unibos-dev manager tui

# Status commands
unibos-dev manager status              # Check all instances
unibos-dev manager status rocksteady   # Check production
unibos-dev manager status local        # Check local dev

# Deployment
unibos-dev manager deploy rocksteady              # Full deployment
unibos-dev manager deploy rocksteady --skip-migrations
unibos-dev manager deploy rocksteady --skip-static
unibos-dev manager deploy rocksteady --no-restart

# SSH operations
unibos-dev manager ssh rocksteady                 # Interactive
unibos-dev manager ssh rocksteady --command "..."  # Execute command
```

### TUI Navigation

```
↑/↓         Navigate items
←/→         Navigate sections
TAB         Switch sections
Enter       Select item
ESC         Back/Cancel
Q           Quit
```

## Future Enhancements

Potential future additions:

1. **Multi-node Management**
   - Support for multiple client nodes
   - Bulk operations
   - Node discovery

2. **Advanced Monitoring**
   - Real-time metrics
   - Alert configuration
   - Performance dashboards

3. **Automation**
   - CI/CD integration
   - Automated deployments
   - Rollback capabilities

4. **Configuration Management**
   - Remote config updates
   - Environment variables
   - Secret management

5. **Backup Management**
   - Automated backups
   - Scheduling
   - Restore operations

## Summary

The manager profile is now fully integrated into the UNIBOS architecture:

**Completed:**
- ✅ Directory structure created
- ✅ ManagerTUI class implemented
- ✅ CLI commands implemented (deploy, status, ssh)
- ✅ Integration with main CLI
- ✅ Comprehensive documentation
- ✅ Test suite created
- ✅ All tests passing

**Usage:**
```bash
# Launch Manager TUI
unibos-dev manager tui

# Check systems
unibos-dev manager status

# Deploy to production
unibos-dev manager deploy rocksteady

# SSH to server
unibos-dev manager ssh rocksteady
```

The manager profile completes the 4-profile architecture:
1. **dev** - Local development
2. **server** - Server operations
3. **prod** - Production-specific
4. **manager** - Remote management ✨ NEW

---

**Implementation Date:** November 16, 2025
**Version:** v0.534.0
**Status:** Complete and tested
