# UNIBOS Manager Profile

The **manager** profile is the 4th profile in the UNIBOS architecture, designed for remote management of UNIBOS instances and deployments.

## Profile Purpose

The manager profile is for:
- Managing rocksteady (unibos-server) remotely
- Managing client nodes (unibos instances)
- Deployment operations
- Remote monitoring
- NOT for local development (that's dev profile)
- NO internal server functions (no Django)

## Architecture

```
core/profiles/
├── dev/           # Development profile
├── server/        # Server profile
├── prod/          # Production profile
└── manager/       # Manager profile (NEW)
    ├── __init__.py
    ├── main.py         # CLI entry point
    ├── tui.py          # Manager TUI class
    └── commands/       # CLI commands
        ├── __init__.py
        ├── deploy.py   # Deployment commands
        ├── status.py   # Status checking
        └── ssh.py      # SSH operations
```

## Usage

### CLI Commands

The manager profile is integrated into the main `unibos-dev` CLI:

```bash
# Show help
unibos-dev manager --help

# Check status of all instances
unibos-dev manager status

# Check specific instance
unibos-dev manager status rocksteady
unibos-dev manager status local

# Deploy to production
unibos-dev manager deploy rocksteady

# Deploy to local
unibos-dev manager deploy local

# SSH to server
unibos-dev manager ssh rocksteady

# Execute remote command
unibos-dev manager ssh rocksteady --command "systemctl status unibos"

# Launch Manager TUI
unibos-dev manager tui
```

### TUI Interface

Launch the interactive Manager TUI:

```bash
unibos-dev manager tui
```

The Manager TUI has 3 sections:

#### Section 1: Targets
- **rocksteady** - Production UNIBOS server (Oracle VM)
- **local dev** - Local development environment
- **list nodes** - Display all managed UNIBOS instances

#### Section 2: Operations
- **deploy** - Deploy to target
- **restart services** - Restart target services
- **view logs** - View target logs
- **run migrations** - Run database migrations
- **backup database** - Backup target database
- **ssh to server** - Open SSH connection

#### Section 3: Monitoring
- **system status** - Complete system status
- **service health** - Service health check
- **git status** - Git repository status
- **django status** - Django application status
- **resource usage** - System resource usage

## Target Management

The manager profile supports multiple targets:

### Rocksteady (Production)
- **Type**: Production server
- **Host**: Oracle Cloud VM
- **OS**: Ubuntu 22.04 LTS
- **SSH**: `ssh rocksteady`
- **Location**: `/opt/unibos`

### Local Dev
- **Type**: Development environment
- **Host**: localhost
- **Profile**: dev
- **Location**: Current working directory

## Deployment Workflow

When deploying to a target (e.g., rocksteady):

1. **Push code to git**
   - Ensures code is in version control

2. **SSH to target**
   - Connect to remote server

3. **Pull latest code**
   - Get latest changes from git

4. **Install dependencies**
   - Update Python packages

5. **Run migrations**
   - Apply database changes

6. **Collect static files**
   - Gather static assets

7. **Restart services**
   - Restart UNIBOS services

### Deployment Options

```bash
# Full deployment
unibos-dev manager deploy rocksteady

# Skip migrations
unibos-dev manager deploy rocksteady --skip-migrations

# Skip static files
unibos-dev manager deploy rocksteady --skip-static

# Don't restart services
unibos-dev manager deploy rocksteady --no-restart
```

## Status Checking

The manager profile provides comprehensive status checking:

```bash
# Check all instances
unibos-dev manager status

# Check specific instance
unibos-dev manager status rocksteady
```

Status includes:
- SSH connectivity
- Git repository status (branch, commit)
- Service status (running/stopped)
- Disk usage
- Database connectivity (local only)
- Django server status (local only)

## SSH Operations

### Interactive SSH

```bash
unibos-dev manager ssh rocksteady
```

Opens an interactive SSH session to the target server.

### Execute Remote Command

```bash
unibos-dev manager ssh rocksteady --command "ls -la /opt/unibos"
unibos-dev manager ssh rocksteady --command "systemctl status unibos"
unibos-dev manager ssh rocksteady --command "tail -f /var/log/unibos/app.log"
```

## Integration with Main CLI

The manager profile is integrated as a command group in the main `unibos-dev` CLI:

```python
# In core/profiles/dev/main.py
from core.profiles.manager.main import cli as manager_cli
cli.add_command(manager_cli, name='manager')
```

This allows seamless access to manager functions from the main CLI.

## Design Philosophy

### Remote-First
The manager profile is designed for **remote management**:
- All operations target remote instances
- SSH-based communication
- Remote monitoring and control
- No local Django dependencies

### Separation of Concerns
- **dev profile**: Local development, testing, debugging
- **server profile**: Server-side operations (rocksteady itself)
- **prod profile**: Production-specific operations
- **manager profile**: Remote management and deployment

### BaseTUI Architecture
The Manager TUI follows the same architecture as other profiles:
- Inherits from `BaseTUI`
- Uses `MenuSection` and `MenuItem` components
- Implements action handlers
- Consistent navigation and UX

## Common Operations

### Check All Systems
```bash
unibos-dev manager status
```

### Deploy Latest Code
```bash
# 1. Commit and push locally
git add .
git commit -m "Update feature"
git push

# 2. Deploy to production
unibos-dev manager deploy rocksteady
```

### View Remote Logs
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

## Future Enhancements

Planned features for the manager profile:

1. **Multi-node Management**
   - Manage multiple client nodes
   - Bulk operations across nodes
   - Node discovery and registration

2. **Advanced Monitoring**
   - Real-time metrics dashboard
   - Alert configuration
   - Performance tracking

3. **Automated Deployment**
   - CI/CD integration
   - Rollback capabilities
   - Blue-green deployments

4. **Configuration Management**
   - Remote configuration updates
   - Environment variable management
   - Secret management

5. **Backup Management**
   - Automated backups
   - Backup scheduling
   - Restore operations

## Troubleshooting

### SSH Connection Failed
```bash
# Test SSH connectivity
ssh rocksteady

# Check SSH config
cat ~/.ssh/config
```

### Deployment Failed
```bash
# Check remote git status
unibos-dev manager ssh rocksteady --command "cd /opt/unibos && git status"

# Check service logs
unibos-dev manager ssh rocksteady --command "journalctl -u unibos -n 50"
```

### Service Not Running
```bash
# Check service status
unibos-dev manager ssh rocksteady --command "systemctl status unibos"

# Start service
unibos-dev manager ssh rocksteady --command "sudo systemctl start unibos"
```

## Best Practices

1. **Always test locally first**
   - Test changes in dev profile
   - Verify functionality before deployment

2. **Use version control**
   - Commit all changes
   - Push before deploying

3. **Monitor deployments**
   - Watch logs during deployment
   - Verify service health after deployment

4. **Regular backups**
   - Backup database before major changes
   - Keep multiple backup copies

5. **Security**
   - Use SSH keys (not passwords)
   - Limit SSH access
   - Monitor access logs

## Summary

The manager profile completes the UNIBOS architecture by providing comprehensive remote management capabilities. It seamlessly integrates with the existing dev, server, and prod profiles while maintaining clear separation of concerns.

**Key Features:**
- Remote instance management
- Deployment automation
- Status monitoring
- SSH operations
- TUI interface
- Integrated with main CLI

**Use Cases:**
- Deploy to production
- Monitor remote instances
- Manage multiple nodes
- Remote troubleshooting
- Operational management
