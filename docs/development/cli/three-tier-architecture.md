# UNIBOS Three-Tier CLI Architecture

**Created:** 2025-11-15
**Status:** Implemented
**Version:** v533+

## Overview

UNIBOS uses a three-tier CLI architecture to separate concerns and enhance security:

1. **unibos** - Production CLI (end users)
2. **unibos-dev** - Developer CLI (development workflow)
3. **unibos-server** - Server CLI (production server management)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      UNIBOS CLI Ecosystem                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   unibos     │  │  unibos-dev  │  │unibos-server │     │
│  │ (Production) │  │ (Developer)  │  │  (Server)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│        │                  │                  │              │
│        ├─ status          ├─ status          ├─ health      │
│        ├─ start           ├─ dev run         ├─ stats       │
│        ├─ logs            ├─ deploy          ├─ logs        │
│        └─ (future)        ├─ git             └─ (future)    │
│                           ├─ db                              │
│                           └─ version                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## CLI Comparison

| Feature | unibos | unibos-dev | unibos-server |
|---------|--------|------------|---------------|
| **Target Users** | End users | Developers | Server admins |
| **Deployment** | Local desktop, Raspberry Pi | Developer machine only | Rocksteady only |
| **Git Commands** | ❌ No | ✅ Yes | ❌ No |
| **Dev Server** | ❌ No | ✅ Yes | ❌ No |
| **Deployment** | ❌ No | ✅ Yes | ❌ No |
| **System Stats** | Basic | ❌ No | ✅ Detailed |
| **Service Management** | Basic | ❌ No | ✅ Advanced |
| **Security Level** | User-safe | Developer-only | Server-only |

## 1. Production CLI (unibos)

**Entry Point:** `core/cli/main.py`
**Setup:** `setup.py`
**Target:** End users (local desktop, Raspberry Pi)

### Commands

```bash
unibos status          # System status check
unibos start           # Start UNIBOS services
unibos logs            # View logs
unibos logs -f         # Follow logs
```

### Features

- ✅ Simple, user-friendly
- ✅ Basic system monitoring
- ✅ Service start/stop
- ✅ Log viewing
- ❌ No git/deployment commands (security)
- ❌ No development tools

### Dependencies

```python
install_requires=[
    'click>=8.0.0',
    'psutil>=5.9.0',     # Platform detection, monitoring
    'zeroconf>=0.80.0',  # mDNS discovery (Phase 3)
]
```

### Installation

```bash
# From repository
cd /path/to/unibos
pipx install .

# Verify
unibos --version
```

---

## 2. Developer CLI (unibos-dev)

**Entry Point:** `core/cli_dev/main.py`
**Setup:** `setup-dev.py`
**Target:** Developers only

### Commands

```bash
# Status & Info
unibos-dev status              # Detailed system status

# Development
unibos-dev dev run             # Django dev server
unibos-dev dev shell           # Django shell
unibos-dev dev test            # Run tests
unibos-dev dev migrate         # Run migrations
unibos-dev dev makemigrations  # Create migrations
unibos-dev dev logs            # View/follow logs

# Database
unibos-dev db backup           # Backup database
unibos-dev db backup --verify  # Backup + verify
unibos-dev db restore <file>   # Restore from backup
unibos-dev db migrate          # Run migrations
unibos-dev db status           # Show migration status

# Deployment
unibos-dev deploy rocksteady   # Deploy to production
unibos-dev deploy local        # Deploy to local prod
unibos-dev deploy raspberry <ip>  # Deploy to Pi
unibos-dev deploy check        # Health check

# Git Workflow
unibos-dev git push-dev        # Push to dev repo
unibos-dev git push-prod       # Push to prod repo (filtered!)
unibos-dev git sync-prod       # Sync to local prod directory
```

### Features

- ✅ Full development workflow
- ✅ Git operations (push-dev, push-prod)
- ✅ Deployment to all targets
- ✅ Database management
- ✅ Version management
- ⚠️  **Security:** Never deploy to production!

### Dependencies

```python
install_requires=[
    'click>=8.0.0',
]
```

### Installation

```bash
# Developer machine only
cd ~/Desktop/unibos-dev
mv setup.py setup-prod.py
mv setup-dev.py setup.py
pipx install -e . -f
mv setup.py setup-dev.py
mv setup-prod.py setup.py

# Verify
unibos-dev --version
```

---

## 3. Server CLI (unibos-server)

**Entry Point:** `core/cli_server/main.py`
**Setup:** `setup-server.py`
**Target:** Rocksteady production server

### Commands

```bash
unibos-server health   # Comprehensive health check
unibos-server stats    # Performance statistics
```

### Planned Commands

```bash
# Service Management
unibos-server service start [django|celery|redis|nginx|all]
unibos-server service stop [service]
unibos-server service restart [service]
unibos-server service status

# Logs
unibos-server logs django [--follow] [--lines N]
unibos-server logs celery
unibos-server logs nginx
unibos-server logs all

# Node Management (P2P)
unibos-server nodes list        # Connected nodes
unibos-server nodes status <uuid>
unibos-server nodes disconnect <uuid>

# Maintenance
unibos-server maintenance on    # Enable maintenance mode
unibos-server maintenance off
unibos-server clean cache
unibos-server clean logs --older-than 30d

# Updates
unibos-server update check
unibos-server update apply      # Git pull + migrate + restart
unibos-server rollback          # Rollback to previous version
```

### Features

- ✅ Production server monitoring
- ✅ Service health checks
- ✅ Performance statistics (CPU, RAM, disk, network)
- ✅ psutil integration
- 🔄 Service management (planned)
- 🔄 Node management (planned)

### Health Check Services

- Django (pgrep manage.py)
- Gunicorn (pgrep gunicorn)
- Celery Worker (pgrep celery worker)
- Celery Beat (pgrep celery beat)
- PostgreSQL (pg_isready)
- Redis (redis-cli ping)
- Nginx (pgrep nginx)

### Dependencies

```python
install_requires=[
    'click>=8.0.0',
    'psutil>=5.9.0',  # System monitoring
]
```

### Installation

```bash
# On rocksteady server
cd /var/www/unibos
mv setup.py setup-prod.py
mv setup-server.py setup.py
pipx install . -f
mv setup.py setup-server.py
mv setup-prod.py setup.py

# Verify
unibos-server --version
```

---

## Security Model

### Production Exclusions

**`.prodignore` and `.rsyncignore`:**

```
# Developer CLI (security critical)
core/cli_dev/
setup-dev.py

# Server CLI (only for rocksteady)
core/cli_server/
setup-server.py
```

**Why:**
- `unibos-dev` has git/deployment commands → **security risk** in production
- `unibos-server` is server-specific → **not needed** on user machines
- Only `core/cli/` (production CLI) syncs to production

### Deployment Filtering

```
Developer Machine        Production Server
┌─────────────────┐     ┌─────────────────┐
│ core/cli/       │ ──► │ core/cli/       │ ✓
│ core/cli_dev/   │ ─X─ │                 │
│ core/cli_server/│ ─X─ │                 │
│ setup.py        │ ──► │ setup.py        │ ✓
│ setup-dev.py    │ ─X─ │                 │
│ setup-server.py │ ─X─ │                 │
└─────────────────┘     └─────────────────┘
```

---

## Directory Structure

```
unibos-dev/
├── core/
│   ├── cli/              # Production CLI
│   │   ├── __init__.py
│   │   ├── main.py       # Entry: unibos
│   │   ├── commands/
│   │   │   ├── status.py
│   │   │   ├── start.py
│   │   │   └── logs.py
│   │   └── ui/
│   │       └── splash.py
│   │
│   ├── cli_dev/          # Developer CLI
│   │   ├── __init__.py
│   │   ├── main.py       # Entry: unibos-dev
│   │   ├── commands/
│   │   │   ├── status.py
│   │   │   ├── deploy.py
│   │   │   ├── dev.py
│   │   │   ├── db.py
│   │   │   └── git.py
│   │   └── ui/
│   │       ├── splash.py
│   │       ├── colors.py
│   │       └── layout.py
│   │
│   └── cli_server/       # Server CLI
│       ├── __init__.py
│       ├── main.py       # Entry: unibos-server
│       ├── commands/
│       │   ├── health.py
│       │   └── stats.py
│       └── ui/
│           └── splash.py
│
├── setup.py              # Production CLI
├── setup-dev.py          # Developer CLI
└── setup-server.py       # Server CLI
```

---

## Development Workflow

### 1. Developer Workflow

```bash
# Use unibos-dev for everything
unibos-dev dev run          # Start dev server
unibos-dev dev makemigrations
unibos-dev dev migrate
unibos-dev git push-dev     # Push to dev repo
unibos-dev deploy rocksteady  # Deploy to production
```

### 2. End User Workflow

```bash
# Use unibos for basic operations
unibos status               # Check system
unibos start                # Start services
unibos logs -f              # Monitor logs
```

### 3. Server Admin Workflow

```bash
# Use unibos-server on rocksteady
unibos-server health        # Check all services
unibos-server stats         # Performance metrics
unibos-server logs django -f  # Monitor Django
```

---

## Implementation Timeline

### ✅ Phase 1.1 (Completed - 2025-11-15)

- [x] Create three CLI directories
- [x] Implement basic commands for each CLI
- [x] Create setup files (setup.py, setup-dev.py, setup-server.py)
- [x] Update .prodignore and .rsyncignore
- [x] Test all three CLIs
- [x] Documentation

### 🔄 Phase 1.2 (Next)

- [ ] Platform detection (core/platform/detector.py)
- [ ] Integrate psutil into all CLIs
- [ ] CLI command: `unibos platform info`

### 📋 Phase 2 (Future)

- [ ] Complete server CLI commands (service, logs, maintenance)
- [ ] Module management commands
- [ ] Node management commands (P2P)

---

## Testing

### Production CLI

```bash
~/.local/bin/unibos --version
~/.local/bin/unibos status
~/.local/bin/unibos start
```

### Developer CLI

```bash
~/.local/bin/unibos-dev --version
~/.local/bin/unibos-dev status
~/.local/bin/unibos-dev dev run --port 8000
```

### Server CLI

```bash
~/.local/bin/unibos-server --version
~/.local/bin/unibos-server health
~/.local/bin/unibos-server stats
```

---

## Troubleshooting

### CLI Not Found

```bash
# Ensure ~/.local/bin is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Or use pipx ensurepath
pipx ensurepath
```

### Wrong CLI Installed

```bash
# Uninstall
pipx uninstall unibos
pipx uninstall unibos-dev
pipx uninstall unibos-server

# Reinstall correct one
cd /path/to/unibos
pipx install .  # for production CLI
```

### Module Not Found Error

```bash
# Ensure directory names use underscores (not hyphens)
core/cli_dev/     # ✓ Correct
core/cli-dev/     # ✗ Wrong (Python can't import)
```

---

## References

- [TODO.md](../../../TODO.md) - Phase 1.1 tasks
- [Architecture Analysis](../../../archive/planning/v533_architecture_analysis_2025-11-15.md)
- [setup.py](../../../setup.py)
- [setup-dev.py](../../../setup-dev.py)
- [setup-server.py](../../../setup-server.py)

---

**Last Updated:** 2025-11-15
**Next Review:** After Phase 1.2 completion
