# Manager Profile - Quick Start

Quick reference for the UNIBOS Manager profile.

## Installation

The manager profile is built-in. No installation needed.

## Quick Commands

### Launch Manager TUI
```bash
unibos-dev manager tui
```

### Check System Status
```bash
# All systems
unibos-dev manager status

# Production only
unibos-dev manager status rocksteady

# Local only
unibos-dev manager status local
```

### Deploy to Production
```bash
unibos-dev manager deploy rocksteady
```

### SSH to Server
```bash
# Interactive
unibos-dev manager ssh rocksteady

# Execute command
unibos-dev manager ssh rocksteady --command "systemctl status unibos"
```

## TUI Quick Reference

### Launch TUI
```bash
unibos-dev manager tui
```

### Navigation
| Key | Action |
|-----|--------|
| ↑/↓ | Navigate items |
| ←/→ | Navigate sections |
| TAB | Switch sections |
| Enter | Select item |
| ESC | Back/Cancel |
| Q | Quit |

### TUI Sections

**1. Targets** (3 items)
- rocksteady - Production server
- local dev - Local environment
- list nodes - Show all nodes

**2. Operations** (6 items)
- deploy - Deploy to target
- restart services - Restart services
- view logs - View logs
- run migrations - Run migrations
- backup database - Backup DB
- ssh to server - SSH connection

**3. Monitoring** (5 items)
- system status - System overview
- service health - Health check
- git status - Git info
- django status - Django info
- resource usage - Resources

## Common Tasks

### Deploy New Code
```bash
# 1. Commit locally
git add .
git commit -m "Update"
git push

# 2. Deploy
unibos-dev manager deploy rocksteady
```

### Check If Services Running
```bash
unibos-dev manager status rocksteady
```

### View Production Logs
```bash
unibos-dev manager ssh rocksteady --command "tail -f /var/log/unibos/app.log"
```

### Restart Services
```bash
unibos-dev manager ssh rocksteady --command "sudo systemctl restart unibos"
```

### Backup Database
```bash
unibos-dev manager ssh rocksteady --command "pg_dump unibos_db > /tmp/backup.sql"
```

## Deployment Options

```bash
# Full deployment
unibos-dev manager deploy rocksteady

# Skip migrations
unibos-dev manager deploy rocksteady --skip-migrations

# Skip static files
unibos-dev manager deploy rocksteady --skip-static

# Don't restart
unibos-dev manager deploy rocksteady --no-restart
```

## Help Commands

```bash
# Main help
unibos-dev manager --help

# Deploy help
unibos-dev manager deploy --help

# Status help
unibos-dev manager status --help

# SSH help
unibos-dev manager ssh --help
```

## Targets

### Rocksteady (Production)
- Host: Oracle Cloud VM
- SSH: `ssh rocksteady`
- Path: `/opt/unibos`

### Local Dev
- Host: localhost
- Path: Current directory

## Tips

1. **Always check status first**
   ```bash
   unibos-dev manager status
   ```

2. **Test locally before deploying**
   ```bash
   unibos-dev dev run  # Test locally first
   ```

3. **Monitor during deployment**
   ```bash
   # In another terminal, watch logs
   unibos-dev manager ssh rocksteady --command "tail -f /var/log/unibos/app.log"
   ```

4. **Backup before major changes**
   ```bash
   unibos-dev manager ssh rocksteady --command "pg_dump unibos_db > /tmp/backup.sql"
   ```

## Troubleshooting

### Can't connect to rocksteady
```bash
# Test SSH
ssh rocksteady

# Check config
cat ~/.ssh/config
```

### Deployment failed
```bash
# Check remote status
unibos-dev manager ssh rocksteady --command "cd /opt/unibos && git status"

# Check logs
unibos-dev manager ssh rocksteady --command "journalctl -u unibos -n 50"
```

### Service not running
```bash
# Check status
unibos-dev manager ssh rocksteady --command "systemctl status unibos"

# Start service
unibos-dev manager ssh rocksteady --command "sudo systemctl start unibos"
```

## More Information

- Full documentation: `core/profiles/manager/README.md`
- Implementation details: `docs/MANAGER_PROFILE.md`
- Test suite: `tools/test/test_manager_tui.py`

## Support

For issues or questions:
1. Check documentation in `core/profiles/manager/README.md`
2. Run tests: `python3 tools/test/test_manager_tui.py`
3. Check status: `unibos-dev manager status`
