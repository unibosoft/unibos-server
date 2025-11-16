# UNIBOS 4-Tier Architecture

Complete documentation for the UNIBOS 4-tier CLI/TUI architecture.

## Overview

UNIBOS now provides 4 distinct profiles, each with its own CLI and TUI:

1. **unibos-dev** - Development environment
2. **unibos-manager** - Remote management
3. **unibos-server** - Production server (rocksteady.fun)
4. **unibos** - Client/end user nodes

All 4 profiles follow the same pattern:
- No arguments = Opens TUI (interactive mode)
- With arguments = Runs CLI commands

## Architecture Pattern

```
Profile Structure:
core/profiles/{profile}/
├── __init__.py
├── main.py          # CLI entry point (hybrid mode)
├── tui.py           # TUI implementation (BaseTUI)
└── commands/        # CLI command implementations

Console Scripts (pyproject.toml):
- unibos-dev       → core.profiles.dev.main:main
- unibos-manager   → core.profiles.manager.main:main
- unibos-server    → core.profiles.server.main:main
- unibos           → core.profiles.prod.main:main
```

## 1. unibos-dev (Development)

**Purpose**: Local development environment for UNIBOS developers

**Location**: Runs on developer machines (Mac, Linux)

### TUI Structure (3 sections)

#### Section 1: Modules
Dynamically discovered from `/modules` directory:
- together we stand
- recaria
- movies
- music
- documents
- currencies
- personal inflation
- restopos
- solitaire
- store
- WIMM
- WIMS
- CCTV

#### Section 2: Tools
- system scrolls - System status and info
- castle guard - Security management
- forge smithy - Setup wizard
- anvil repair - Diagnostics and repair
- code forge - Git operations
- web ui - Django server management
- administration - Admin tools

#### Section 3: Dev Tools
- ai builder - AI development tools
- database setup - PostgreSQL wizard
- public server - Deploy to rocksteady
- sd card - SD card operations
- version manager - Archives and git

### CLI Commands

```bash
# TUI Mode
unibos-dev                     # Launch interactive TUI

# CLI Mode
unibos-dev status              # System status
unibos-dev run                 # Start Django server (shortcut)
unibos-dev shell               # Django shell (shortcut)
unibos-dev dev run             # Start development server
unibos-dev dev stop            # Stop development server
unibos-dev deploy rocksteady   # Deploy to production
unibos-dev db backup           # Database backup
unibos-dev git status          # Git status
unibos-dev git push-dev        # Push to dev repo
```

## 2. unibos-manager (Manager)

**Purpose**: Remote management of UNIBOS servers and clients

**Location**: Runs on developer machines for remote control

### TUI Structure (3 sections)

#### Section 1: Targets
- rocksteady - Production server
- local dev - Local development
- list nodes - Show all managed nodes

#### Section 2: Operations
- deploy - Deploy to target
- restart services - Restart all services
- view logs - View remote logs
- run migrations - Database migrations
- backup database - Create backup
- ssh to server - Open SSH connection

#### Section 3: Monitoring
- system status - Complete system status
- service health - All services health
- git status - Repository status
- django status - Django app status
- resource usage - CPU, memory, disk

### CLI Commands

```bash
# TUI Mode
unibos-manager                 # Launch interactive TUI

# CLI Mode (future)
unibos-manager deploy          # Deploy to current target
unibos-manager status          # Remote status
unibos-manager logs            # Remote logs
```

## 3. unibos-server (Production Server)

**Purpose**: Production server management on rocksteady.fun

**Location**: Runs on rocksteady.fun (Oracle Cloud VM, Ubuntu)

### TUI Structure (3 sections)

#### Section 1: Services
- django application - Start/stop/restart Django
- postgresql database - Database service control
- nginx web server - Web server management
- systemd services - All system services
- background workers - Celery/background tasks

#### Section 2: Operations
- view logs - Application and system logs
- restart all - Full server restart
- database backup - Backup database
- update system - Pull code, migrate, restart
- maintenance mode - Enable/disable maintenance

#### Section 3: Monitoring
- system status - CPU, memory, disk, uptime
- service health - All services status
- active users - Connected users
- database stats - DB size, connections
- error logs - Recent errors

### CLI Commands

```bash
# TUI Mode
unibos-server                  # Launch interactive TUI

# CLI Mode
unibos-server start            # Start all services
unibos-server stop             # Stop all services
unibos-server restart          # Restart all services
unibos-server logs             # View server logs
unibos-server status           # System status
unibos-server backup           # Backup database
```

### Typical Server Commands

```bash
# Service Management
sudo systemctl start gunicorn
sudo systemctl stop celery
sudo systemctl restart nginx
sudo systemctl status postgresql

# Logs
tail -f /var/log/unibos/django.log
tail -f /var/log/nginx/access.log
sudo journalctl -u gunicorn -f

# Database
sudo -u postgres pg_dump unibos_db > backup.sql
sudo -u postgres psql unibos_db

# System Update
cd /opt/unibos && git pull
python manage.py migrate
sudo systemctl restart gunicorn celery
```

## 4. unibos (Client/End User)

**Purpose**: End user interface for UNIBOS nodes

**Location**: Runs on user machines (Raspberry Pi, local computers)

### TUI Structure (3 sections)

#### Section 1: Modules
All installed user applications (same as dev but for end users):
- together we stand
- recaria
- movies
- music
- documents
- currencies
- personal inflation
- restopos
- solitaire
- store
- WIMM
- WIMS
- CCTV

#### Section 2: System
- system settings - Configuration
- network settings - WiFi, connectivity
- update system - Check for updates
- backup data - Backup user data
- storage management - Disk space

#### Section 3: Info
- system status - Device info
- module status - Installed modules
- network status - Connectivity
- help & support - Documentation
- about - Version info

### CLI Commands

```bash
# TUI Mode
unibos                         # Launch interactive TUI

# CLI Mode
unibos status                  # System status
unibos launch <module>         # Launch specific module
unibos launch recaria          # Launch recaria module
unibos update                  # Update system
unibos backup                  # Backup data
unibos settings                # Open settings
```

## Implementation Details

### BaseTUI Architecture

All TUIs inherit from `BaseTUI` which provides:

- **3-section layout**: Header, sidebar, content, footer
- **Keyboard navigation**: Arrow keys, Enter, ESC, Q
- **MenuSection/MenuItem structure**: Clean menu organization
- **Action handler registry**: Extensible handler system
- **Double buffering**: Flicker-free rendering
- **ANSI color support**: 256-color terminal support

### TUI Class Template

```python
from core.clients.tui import BaseTUI
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Colors

class ProfileTUI(BaseTUI):
    def __init__(self):
        config = TUIConfig(
            title="profile-name",
            version="v0.534.0",
            location="description",
            lowercase_ui=True
        )
        super().__init__(config)
        self.register_profile_handlers()

    def get_profile_name(self) -> str:
        return "profile"

    def get_menu_sections(self) -> List[MenuSection]:
        return [
            MenuSection(id='section1', label='label', icon='🎯', items=[...]),
            MenuSection(id='section2', label='label', icon='⚙️', items=[...]),
            MenuSection(id='section3', label='label', icon='📊', items=[...]),
        ]

    def register_profile_handlers(self):
        self.register_action('action_id', self.handle_action)

    def handle_action(self, item: MenuItem) -> bool:
        self.update_content(title="Title", lines=[...], color=Colors.CYAN)
        self.render()
        return True
```

### CLI Entry Point Template

```python
import click

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """CLI description"""
    if ctx.invoked_subcommand is None:
        from core.profiles.profile.tui import run_interactive
        run_interactive()

@cli.command()
def command():
    """Command description"""
    click.echo("Output")

def main():
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\n\nGoodbye!")
        sys.exit(0)
```

## Usage Examples

### Development Workflow

```bash
# Developer machine
unibos-dev                     # Open dev TUI
unibos-dev status              # Check system
unibos-dev run                 # Start Django
unibos-dev git status          # Check git
unibos-dev deploy rocksteady   # Deploy to production
```

### Server Management

```bash
# On rocksteady server
unibos-server                  # Open server TUI
unibos-server status           # Check services
unibos-server restart          # Restart services
unibos-server backup           # Backup database
```

### Remote Management

```bash
# Manager from developer machine
unibos-manager                 # Open manager TUI
# Select target: rocksteady
# Deploy, restart, view logs, etc.
```

### End User

```bash
# On Raspberry Pi or user computer
unibos                         # Open client TUI
unibos launch recaria          # Launch module
unibos status                  # Check status
unibos update                  # Update system
```

## Testing

Run the comprehensive test suite:

```bash
./tools/test/test_all_clis.sh
```

This tests:
- All 4 CLIs (help, version)
- CLI commands for each profile
- Proper exit codes
- Output formatting

Expected output: 21/21 tests passing

## File Locations

```
Core Profiles:
- core/profiles/dev/tui.py        # Development TUI
- core/profiles/manager/tui.py    # Manager TUI
- core/profiles/server/tui.py     # Server TUI
- core/profiles/prod/tui.py       # Client TUI

CLI Entry Points:
- core/profiles/dev/main.py       # unibos-dev
- core/profiles/manager/main.py   # unibos-manager
- core/profiles/server/main.py    # unibos-server
- core/profiles/prod/main.py      # unibos

Console Scripts:
- pyproject.toml                  # All 4 scripts defined

Tests:
- tools/test/test_all_clis.sh     # Comprehensive test suite
```

## Design Principles

1. **Consistency**: All 4 CLIs follow the same pattern
2. **Hybrid Mode**: TUI by default, CLI with arguments
3. **3-Section Layout**: Consistent menu structure
4. **BaseTUI Inheritance**: Shared UI framework
5. **Profile-Specific**: Each profile has unique handlers
6. **Extensible**: Easy to add new actions and sections

## Future Enhancements

1. **Server CLI**: Full command implementations
2. **Client P2P**: Peer discovery and mesh networking
3. **Manager SSH**: Direct SSH integration
4. **Module Launcher**: Launch modules from TUI
5. **Live Monitoring**: Real-time status updates
6. **Remote Execution**: Execute commands on remote targets

## Summary

The 4-tier architecture provides:

- **unibos-dev**: Developer tools and workflows
- **unibos-manager**: Remote management interface
- **unibos-server**: Production server operations
- **unibos**: End user client interface

Each profile has its own TUI and CLI, all following the same simple pattern:
- No args = TUI mode
- With args = CLI mode

This creates a consistent, intuitive interface across all deployment scenarios.
