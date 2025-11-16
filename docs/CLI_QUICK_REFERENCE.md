# UNIBOS CLI Quick Reference

Quick reference for all 4 UNIBOS CLI profiles.

## Basic Pattern

```bash
# TUI Mode (no arguments)
unibos-dev              # Opens development TUI
unibos-manager          # Opens manager TUI
unibos-server           # Opens server TUI
unibos                  # Opens client TUI

# CLI Mode (with arguments)
unibos-dev <command>    # Runs development command
unibos-manager <command># Runs manager command
unibos-server <command> # Runs server command
unibos <command>        # Runs client command
```

## unibos-dev (Development)

### Quick Commands
```bash
unibos-dev                     # Launch TUI
unibos-dev --help              # Show help
unibos-dev --version           # Show version

# Common Commands
unibos-dev status              # System status
unibos-dev run                 # Start Django server
unibos-dev stop                # Stop Django server
unibos-dev shell               # Django shell
unibos-dev test                # Run tests
unibos-dev migrate             # Run migrations

# Dev Commands (full path)
unibos-dev dev run             # Start dev server
unibos-dev dev stop            # Stop dev server
unibos-dev dev status          # Server status
unibos-dev dev logs            # View logs
unibos-dev dev migrate         # Run migrations

# Git Commands
unibos-dev git status          # Git status
unibos-dev git push-dev        # Push to dev repo
unibos-dev git sync-prod       # Sync to prod

# Database Commands
unibos-dev db status           # Database status
unibos-dev db create           # Create database
unibos-dev db migrate          # Run migrations
unibos-dev db backup           # Backup database

# Deployment Commands
unibos-dev deploy rocksteady   # Deploy to production
unibos-dev deploy status       # Deployment status
```

### TUI Sections
1. **Modules** - All installed modules (dynamic)
2. **Tools** - System tools (7 items)
3. **Dev Tools** - Development tools (5 items)

## unibos-manager (Manager)

### Quick Commands
```bash
unibos-manager                 # Launch TUI
unibos-manager --help          # Show help
unibos-manager --version       # Show version
```

### TUI Sections
1. **Targets** - rocksteady, local dev, list nodes
2. **Operations** - deploy, restart, logs, migrations, backup, ssh
3. **Monitoring** - system, service, git, django, resources

### Usage Pattern
1. Launch `unibos-manager`
2. Select target (rocksteady or local)
3. Perform operations on selected target
4. View monitoring data

## unibos-server (Server)

### Quick Commands
```bash
unibos-server                  # Launch TUI
unibos-server --help           # Show help
unibos-server --version        # Show version

# Service Commands
unibos-server start            # Start all services
unibos-server stop             # Stop all services
unibos-server restart          # Restart all services

# Operations
unibos-server logs             # View logs
unibos-server status           # System status
unibos-server backup           # Backup database
```

### TUI Sections
1. **Services** - django, postgresql, nginx, systemd, workers
2. **Operations** - logs, restart, backup, update, maintenance
3. **Monitoring** - system, health, users, database, errors

### Typical Server Operations
```bash
# On rocksteady.fun server:
ssh rocksteady
unibos-server                  # Launch TUI
unibos-server status           # Quick status check
unibos-server restart          # Restart services
unibos-server backup           # Create backup
```

## unibos (Client)

### Quick Commands
```bash
unibos                         # Launch TUI
unibos --help                  # Show help
unibos --version               # Show version

# Client Commands
unibos status                  # Node status
unibos launch <module>         # Launch module
unibos update                  # Update system
unibos backup                  # Backup data
unibos settings                # Open settings
```

### Module Launch
```bash
unibos launch                  # Show available modules
unibos launch recaria          # Launch recaria
unibos launch movies           # Launch movies
unibos launch music            # Launch music
```

### TUI Sections
1. **Modules** - All installed applications (dynamic)
2. **System** - settings, network, update, backup, storage
3. **Info** - status, modules, network, help, about

### Typical User Operations
```bash
# On Raspberry Pi or user computer:
unibos                         # Launch TUI
unibos launch recaria          # Launch app
unibos status                  # Check status
unibos update                  # Update system
```

## Common Patterns

### Help and Version
```bash
# All CLIs support:
<cli> --help                   # Show help
<cli> --version                # Show version
```

### TUI Navigation
```
↑ ↓           # Navigate menu items
← →           # Switch between sections
Enter         # Select item / Execute action
ESC           # Go back / Exit submenu
Q             # Quit application
?             # Show help (in TUI)
```

### TUI Sections Pattern
All TUIs have exactly 3 sections:
1. **Primary** - Main functionality
2. **Secondary** - Operations/Tools
3. **Tertiary** - Info/Monitoring

## Environment-Specific Usage

### Development (Mac/Linux)
```bash
unibos-dev                     # Main interface
unibos-manager                 # Remote management
```

### Production Server (rocksteady.fun)
```bash
unibos-server                  # Server management
```

### Client Nodes (Raspberry Pi, etc.)
```bash
unibos                         # User interface
```

## Testing

```bash
# Test all CLIs
./tools/test/test_all_clis.sh

# Expected: 21/21 tests passing
```

## Troubleshooting

### CLI Not Found
```bash
# Reinstall package
pip install -e .

# Or in development mode
pip install --editable .
```

### Permission Issues
```bash
# Make scripts executable
chmod +x core/profiles/*/main.py
```

### Import Errors
```bash
# Ensure proper Python path
export PYTHONPATH=/path/to/unibos-dev:$PYTHONPATH
```

## Quick Start Examples

### Developer Workflow
```bash
# Day 1: Setup
unibos-dev                     # Launch dev TUI
# Select: database setup → create database
# Select: web ui → start server

# Day 2: Development
unibos-dev                     # Check status
unibos-dev run                 # Quick server start
unibos-dev git status          # Check changes

# Day 3: Deployment
unibos-dev deploy rocksteady   # Deploy to production
unibos-manager                 # Monitor deployment
```

### Server Administrator
```bash
# Daily operations
unibos-server status           # Quick status
unibos-server                  # Full TUI for detailed work

# Maintenance
unibos-server backup           # Create backup
unibos-server restart          # Restart services

# Troubleshooting
unibos-server logs             # View logs
unibos-server                  # TUI for detailed checks
```

### End User
```bash
# Launch application
unibos                         # Browse modules
# Or quick launch:
unibos launch recaria          # Direct launch

# Maintenance
unibos update                  # Check for updates
unibos backup                  # Backup data
```

## Summary

| CLI | Purpose | Location | Main Use |
|-----|---------|----------|----------|
| unibos-dev | Development | Developer Mac/Linux | Development & deployment |
| unibos-manager | Remote mgmt | Developer machine | Manage remote servers |
| unibos-server | Server ops | rocksteady.fun | Server administration |
| unibos | Client | User machines | Application launcher |

All follow the same pattern:
- **No args**: Interactive TUI
- **With args**: CLI commands
- **3 sections**: Consistent structure
- **ESC/Q**: Exit at any time
