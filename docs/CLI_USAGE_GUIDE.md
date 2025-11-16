# UNIBOS CLI Usage Guide

## Overview

The UNIBOS CLI provides a simplified, intuitive interface for managing UNIBOS development and production environments. This guide covers the new simplified CLI structure implemented in v0.534.0+.

## Key Improvements

1. **Direct Command Access**: Common dev commands are now available directly without the `dev` prefix
2. **Standalone Manager CLI**: `unibos-manager` is now a standalone command
3. **Backwards Compatibility**: All old command paths still work
4. **Smart Defaults**: Running commands without arguments launches interactive TUI

## Available Commands

### Core Commands (4 CLIs)

```bash
unibos           # Production CLI (for production systems)
unibos-dev       # Development CLI (main developer tool)
unibos-server    # Server CLI (for rocksteady/production server)
unibos-manager   # Manager CLI (remote management)
```

---

## unibos-dev CLI

### Interactive Mode (TUI)

```bash
unibos-dev       # Launch interactive TUI (no arguments)
```

### Direct Commands (NEW - Simplified)

Common development commands are now available directly:

```bash
# Development Server
unibos-dev run                    # Start Django dev server
unibos-dev run --port 8080        # Custom port
unibos-dev stop                   # Stop dev server

# Django Shell & Database
unibos-dev shell                  # Open Django shell
unibos-dev migrate                # Run migrations
unibos-dev makemigrations         # Create migrations
unibos-dev makemigrations myapp   # For specific app

# Testing & Logs
unibos-dev test                   # Run all tests
unibos-dev test myapp             # Test specific app
unibos-dev logs                   # View logs (last 50 lines)
unibos-dev logs -n 100            # Last 100 lines
unibos-dev logs -f                # Follow logs

# System Status
unibos-dev status                 # Show system status
unibos-dev status --detailed      # Detailed status
unibos-dev platform               # Platform info
```

### Backwards Compatible Commands

Old command paths still work for backwards compatibility:

```bash
# All of these still work:
unibos-dev dev run
unibos-dev dev shell
unibos-dev dev migrate
unibos-dev dev test
# ... etc
```

### Other Command Groups

```bash
# Deployment
unibos-dev deploy rocksteady      # Deploy to production
unibos-dev deploy check           # Check deployment config

# Database Management
unibos-dev db backup              # Backup database
unibos-dev db restore backup.sql  # Restore database
unibos-dev db reset               # Reset database

# Git Operations
unibos-dev git push-dev           # Push to dev repo
unibos-dev git sync-prod          # Sync to prod directory
unibos-dev git status             # Enhanced git status
```

---

## unibos-manager CLI (NEW Standalone)

The manager CLI is now available as a standalone command!

### Interactive Mode (TUI)

```bash
unibos-manager   # Launch Manager TUI (default)
```

### Direct Commands

```bash
# Status Checks
unibos-manager status             # Check all instances
unibos-manager status --detailed  # Detailed status

# Deployment
unibos-manager deploy rocksteady  # Deploy to production
unibos-manager deploy --dry-run rocksteady  # Dry run

# SSH Access
unibos-manager ssh rocksteady     # SSH to server
unibos-manager ssh rocksteady --command "ls -la"  # Run command
```

### Also Available via unibos-dev

The manager commands are still accessible via `unibos-dev manager` for backwards compatibility:

```bash
unibos-dev manager tui
unibos-dev manager status
unibos-dev manager deploy rocksteady
```

---

## Command Comparison

### Old vs New

#### Before (Complex)
```bash
unibos-dev dev tui              # Opens dev TUI
unibos-dev dev run              # Runs dev server
unibos-dev manager tui          # Opens manager TUI
unibos-dev manager status       # Checks status
```

#### After (Simplified)
```bash
unibos-dev                      # Opens dev TUI
unibos-dev run                  # Runs dev server
unibos-manager                  # Opens manager TUI
unibos-manager status           # Checks status
```

Both old and new styles work!

---

## Common Workflows

### Development Workflow

```bash
# Start working
unibos-dev                      # Launch TUI to see overview

# Run development server
unibos-dev run                  # Start server
unibos-dev logs -f              # Watch logs (new terminal)

# Make database changes
unibos-dev makemigrations       # Create migrations
unibos-dev migrate              # Apply migrations

# Test changes
unibos-dev test                 # Run tests

# Check status
unibos-dev status --detailed    # Detailed system check
```

### Deployment Workflow

```bash
# Check remote status
unibos-manager status           # Check all instances

# Deploy to production
unibos-manager deploy rocksteady

# Verify deployment
unibos-manager ssh rocksteady --command "systemctl status unibos"

# Monitor
unibos-manager status --detailed
```

### Database Management

```bash
# Backup before changes
unibos-dev db backup

# Make schema changes
unibos-dev makemigrations
unibos-dev migrate

# If something goes wrong
unibos-dev db restore backup_20250116.sql
```

---

## Tips & Best Practices

### 1. Use Tab Completion

Most shells support tab completion. After installing, you can tab-complete commands:

```bash
unibos-dev <TAB>       # Shows all available commands
unibos-manager de<TAB> # Completes to 'deploy'
```

### 2. Check Help for Options

Every command has detailed help:

```bash
unibos-dev --help
unibos-dev run --help
unibos-manager deploy --help
```

### 3. Use Shortcuts for Common Tasks

New shortcuts save typing:

```bash
unibos-dev run         # Instead of: unibos-dev dev run
unibos-dev shell       # Instead of: unibos-dev dev shell
unibos-manager         # Instead of: unibos-dev manager tui
```

### 4. TUI for Overview, CLI for Automation

- Use **TUI** (no arguments) for interactive exploration and overview
- Use **CLI** (with arguments) for scripts and automation

### 5. Keep Backwards Compatibility in Scripts

If you have existing scripts using the old paths, they'll continue to work:

```bash
# This still works fine in your scripts:
unibos-dev dev run
unibos-dev dev test
```

---

## Installation & Updates

### Install/Reinstall

```bash
# Using pipx (recommended)
pipx install -e /path/to/unibos-dev

# After code changes
pipx uninstall unibos
pipx install -e /path/to/unibos-dev
```

### Verify Installation

```bash
# Check all CLIs are available
which unibos-dev
which unibos-manager
which unibos-server
which unibos

# Check versions
unibos-dev --version
unibos-manager --version
```

---

## Troubleshooting

### Command Not Found

```bash
# Reinstall with pipx
pipx uninstall unibos
pipx install -e /path/to/unibos-dev
```

### Old Commands Not Working

All old command paths should still work. If they don't:

1. Check you're on version v0.534.0+: `unibos-dev --version`
2. Reinstall: `pipx reinstall unibos`
3. Clear shell cache: `hash -r` or restart terminal

### TUI Not Launching

If `unibos-dev` or `unibos-manager` without arguments doesn't launch TUI:

1. Check for Python errors in the output
2. Verify dependencies: `pipx runpip unibos list`
3. Check logs in `data/core/logs/`

---

## Migration Guide

### For Developers

If you have scripts or documentation using old paths:

**Option 1: Keep Old Paths (Recommended for now)**
- All old paths work, no changes needed
- Example: `unibos-dev dev run` still works

**Option 2: Update to New Shortcuts**
- Update `unibos-dev dev run` → `unibos-dev run`
- Update `unibos-dev manager tui` → `unibos-manager`
- More concise and modern

### For Documentation

Update examples to show new simplified syntax:

```bash
# OLD
unibos-dev dev run
unibos-dev manager status

# NEW (show this in docs)
unibos-dev run
unibos-manager status
```

---

## Summary

### New Features
- Direct command access: `unibos-dev run` instead of `unibos-dev dev run`
- Standalone manager: `unibos-manager` instead of `unibos-dev manager`
- Smart defaults: No arguments = TUI
- Full backwards compatibility

### All Available CLIs
- `unibos-dev` - Main developer CLI
- `unibos-manager` - Remote management CLI
- `unibos-server` - Production server CLI
- `unibos` - Production system CLI

### Quick Reference
```bash
# Interactive TUIs
unibos-dev          # Dev TUI
unibos-manager      # Manager TUI

# Common Commands
unibos-dev run      # Dev server
unibos-dev shell    # Django shell
unibos-dev status   # System status

# Manager Commands
unibos-manager status           # Check instances
unibos-manager deploy rocksteady # Deploy
unibos-manager ssh rocksteady   # SSH to server
```

---

**Version**: v0.534.0+
**Last Updated**: 2025-01-16
**Maintained by**: UNIBOS Core Team
