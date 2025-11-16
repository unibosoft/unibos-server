# UNIBOS Dev TUI - Quick Reference Guide

## Starting the TUI

```bash
unibos-dev tui
```

## Navigation

| Key | Action |
|-----|--------|
| ↑ / ↓ | Navigate through menu items |
| ← / → | Switch between sections |
| TAB | Switch between sections (alternative) |
| Enter | Select/execute item |
| ESC | Go back / exit submenu |
| Q | Quit TUI |

## Menu Structure

### 📦 Modules
Dynamically discovered modules with .enabled file

### 🔧 Tools (7 items)

#### 1. 📜 System Scrolls
**What it does**: Shows comprehensive system information
**Action**: Runs `unibos-dev status`
**Output**: OS, CPU, memory, Python version, services

#### 2. 🛡️ Castle Guard
**What it does**: Security management overview
**Status**: Coming soon - Informational placeholder
**Shows**: Security tools roadmap

#### 3. 🔨 Forge Smithy
**What it does**: System setup wizard
**Status**: Coming soon - Informational placeholder
**Shows**: Setup process outline

#### 4. ⚒️ Anvil Repair
**What it does**: Diagnostics and repair tools
**Status**: Coming soon - Informational placeholder
**Shows**: Available diagnostic and repair options

#### 5. ⚙️ Code Forge
**What it does**: Git operations and version control
**Action**: Shows git status + available commands
**Commands**: status, push-dev, sync-prod, commit

#### 6. 🌐 Web UI
**What it does**: Django server management
**Type**: Interactive submenu
**Options**:
- Start Server
- Stop Server
- Server Status
- View Logs
- Run Migrations

#### 7. 👑 Administration
**What it does**: System administration
**Status**: Coming soon - Informational placeholder
**Shows**: Admin tools overview + Django admin access

### 🛠️ Dev Tools (5 items)

#### 1. 🤖 AI Builder
**What it does**: AI-powered development tools
**Status**: Coming soon - Informational placeholder
**Shows**: AI capabilities overview

#### 2. 🗄️ Database Setup
**What it does**: PostgreSQL installation and management
**Type**: Interactive submenu
**Options**:
- Check Status
- Install PostgreSQL
- Create Database
- Run Migrations
- Backup Database
- Restore Database

#### 3. 🌍 Public Server
**What it does**: Deploy to rocksteady server
**Type**: Interactive submenu
**Options**:
- Server Status
- Deploy to Rocksteady
- SSH to Server
- View Server Logs
- Backup Server

#### 4. 💾 SD Card
**What it does**: SD card operations
**Status**: Coming soon - Informational placeholder
**Shows**: SD utilities overview

#### 5. 📋 Version Manager
**What it does**: Archive and git management
**Type**: Interactive submenu
**Options**:
- Browse Archives (shows last 10 versions)
- Create Archive
- Archive Analyzer
- Git Status
- Git Sync
- Validate Versions

## Interactive Submenus

### How to Use
1. Navigate to item with submenu
2. Press Enter
3. Use ↑↓ to select option
4. Press Enter to execute
5. Press ESC to go back

### Available Submenus
- Web UI (6 options)
- Database Setup (7 options)
- Public Server (6 options)
- Version Manager (7 options)

## Common Tasks

### Start Django Server
1. Navigate to Tools → Web UI
2. Press Enter
3. Select "Start Django Server"
4. Press Enter

### Check System Status
1. Navigate to Tools → System Scrolls
2. Press Enter
3. View system information

### Run Database Migrations
1. Navigate to Dev Tools → Database Setup
2. Press Enter
3. Select "Run Migrations"
4. Press Enter

### Deploy to Production
1. Navigate to Dev Tools → Public Server
2. Press Enter
3. Select "Deploy to Rocksteady"
4. Press Enter

### Check Git Status
1. Navigate to Tools → Code Forge
2. Press Enter
3. View git status and available commands

### Browse Version Archives
1. Navigate to Dev Tools → Version Manager
2. Press Enter
3. Select "Browse Archives"
4. Press Enter
5. View last 10 versions

## Tips

- **Loading States**: Watch for "⏳" indicator during operations
- **Error Messages**: Red "❌" indicates errors with details
- **Coming Soon**: Yellow "🚧" indicates features under development
- **Success**: Green "✓" indicates successful operations
- **Navigation**: Use arrow keys for smooth navigation
- **Escape**: Always available to go back

## Troubleshooting

### Handler not responding
- Press ESC to return to menu
- Check terminal for error messages
- Ensure unibos-dev CLI is installed

### Command execution fails
- Check that required services are running
- Verify CLI commands work from terminal
- Review error messages for details

### TUI not starting
```bash
# Check if installed
which unibos-dev

# Verify TUI module
python3 -c "from core.profiles.dev.tui import UnibosDevTUI"

# Run with debug
unibos-dev tui --debug
```

## CLI Integration

All handlers integrate with `unibos-dev` CLI. You can run these commands directly in terminal:

```bash
# System
unibos-dev status
unibos-dev platform

# Development
unibos-dev dev run
unibos-dev dev stop
unibos-dev dev status
unibos-dev dev logs
unibos-dev dev migrate

# Database
unibos-dev db status
unibos-dev db create
unibos-dev db migrate
unibos-dev db backup
unibos-dev db restore

# Git
unibos-dev git status
unibos-dev git push-dev
unibos-dev git sync-prod

# Deployment
unibos-dev deploy status rocksteady
unibos-dev deploy rocksteady
unibos-dev deploy logs rocksteady
```

## Keyboard Shortcuts Summary

```
Navigation:
  ↑ ↓    - Move through items
  ← →    - Switch sections
  TAB    - Switch sections

Actions:
  ENTER  - Select/Execute
  ESC    - Go back
  Q      - Quit

In Submenus:
  ↑ ↓    - Select option
  ENTER  - Execute option
  ESC    - Return to menu
```

---

**Version**: v0.534.0
**Last Updated**: 2025-11-16
**Documentation**: See TUI_HANDLERS_IMPLEMENTATION.md for detailed technical documentation
