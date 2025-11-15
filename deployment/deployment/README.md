# UNIBOS v533 Deployment Guide

## Rocksteady Production Deployment

### Quick Start

```bash
# Full deployment with all checks
./deploy/rocksteady_v533.sh

# Or specific actions
./deploy/rocksteady_v533.sh check         # Health check only
./deploy/rocksteady_v533.sh install-ocr   # Install OCR dependencies
```

### Features

✓ **Pre-Flight Checks**: Automatically detects deployment blockers
- Flutter build directories (1.6GB)
- Large log files (>10MB)
- Database backups
- Local venv directories

✓ **Smart File Sync**: Uses `.rsyncignore` to exclude:
- Python venv and caches
- Git repository
- Archive directories
- Database files
- Build artifacts
- Large media files

✓ **Dependency Management**: Automatically checks and installs:
- Core Python packages (Django, DRF, Celery, Channels)
- Uvicorn workers for ASGI
- OCR/ML libraries (optional)

✓ **Database Migrations**: Detects and applies pending migrations

✓ **Service Management**: Restarts gunicorn and nginx with verification

✓ **Health Checks**: Verifies HTTP endpoints and module accessibility

### Pre-Deployment Checklist

Before running deployment, ensure:

1. **SSH Access**: Can connect to rocksteady without password
   ```bash
   ssh rocksteady "echo 'Connection OK'"
   ```

2. **Clean Local Repository**: No large build artifacts
   ```bash
   # Remove Flutter build (if exists)
   rm -rf modules/birlikteyiz/mobile/build

   # Remove large logs
   find core/web -name "*.log" -size +10M -delete
   ```

3. **Database Backup**: Production database is backed up (if needed)
   ```bash
   ssh rocksteady "cd /home/ubuntu/unibos && ./tools/scripts/backup_database.sh"
   ```

### Deployment Actions

#### Full Deployment
```bash
./deploy/rocksteady_v533.sh deploy
```

Performs:
1. Local size check and bloat detection
2. File sync with smart exclusions
3. Dependency verification and installation
4. Database migrations
5. Service restart
6. Health checks

#### Health Check Only
```bash
./deploy/rocksteady_v533.sh check
```

Tests:
- HTTP endpoint (/)
- Module endpoints (/module/birlikteyiz/)

#### Install OCR Dependencies
```bash
./deploy/rocksteady_v533.sh install-ocr
```

Installs:
- System packages: tesseract-ocr, poppler-utils, libgl1, libglib2.0-0
- Python packages: paddleocr, torch, transformers, easyocr, surya-ocr

#### Sync Files Only
```bash
./deploy/rocksteady_v533.sh sync
```

Only transfers code, skips dependency checks and service restarts.

#### Database Migrations Only
```bash
./deploy/rocksteady_v533.sh migrate
```

Checks and applies pending Django migrations.

#### Restart Services Only
```bash
./deploy/rocksteady_v533.sh restart
```

Restarts gunicorn and nginx services.

### Common Issues

#### Issue: "Flutter build directory found: 1.5G"
**Solution**: Remove Flutter build artifacts before deployment
```bash
rm -rf modules/birlikteyiz/mobile/build
```

#### Issue: "Large log files found"
**Solution**: Clean or archive large logs
```bash
find core/web -name "*.log" -size +10M -delete
# Or archive them
mkdir -p archive/logs
mv core/web/logs/*.log archive/logs/
```

#### Issue: "Connection refused"
**Solution**: Check SSH configuration and rocksteady accessibility
```bash
# Test SSH
ssh rocksteady "echo 'OK'"

# Check if in ~/.ssh/config
grep -A 5 "Host rocksteady" ~/.ssh/config
```

#### Issue: "Gunicorn failed to start"
**Solution**: Check logs on remote server
```bash
ssh rocksteady "journalctl -u gunicorn -n 50 --no-pager"
```

### Manual Deployment Steps

If automated script fails, you can perform steps manually:

```bash
# 1. Sync files
rsync -avz --exclude-from=.rsyncignore . rocksteady:/home/ubuntu/unibos/

# 2. Install dependencies
ssh rocksteady "cd /home/ubuntu/unibos/core/web && source venv/bin/activate && pip install -r requirements.txt && pip install 'uvicorn[standard]'"

# 3. Run migrations
ssh rocksteady "cd /home/ubuntu/unibos/core/web && PYTHONPATH=/home/ubuntu/unibos/core/web:/home/ubuntu/unibos DJANGO_SETTINGS_MODULE=unibos_backend.settings.production ./venv/bin/python3 manage.py migrate"

# 4. Restart services
ssh rocksteady "sudo systemctl restart gunicorn && sudo systemctl restart nginx"

# 5. Check status
ssh rocksteady "curl -I http://localhost:8000/"
```

### File Size Guidelines

**Expected transfer sizes:**
- Core code only: ~50-100 MB
- With dependencies (in venv): Not transferred (built on remote)
- Total deployment: ~50-100 MB

**Warning thresholds:**
- Total > 500 MB: Check for bloat
- Single directory > 100 MB: Investigate
- Logs > 10 MB each: Archive or delete

### Architecture Notes

**v533 Structure:**
```
unibos/
├── core/              # Core platform
│   └── web/          # Django backend
│       ├── venv/     # Remote only
│       └── ...
├── modules/          # Feature modules
│   └── birlikteyiz/
│       ├── backend/  # Django app
│       └── mobile/   # Flutter app (build/ excluded)
├── data/             # Runtime data (excluded from transfer)
└── deploy/           # Deployment scripts
```

**Exclusions in `.rsyncignore`:**
- `venv/` - Built on remote
- `archive/` - Historical versions
- `data/` and `data_db/` - Runtime data
- `*.log` - Log files
- `build/` - Compiled artifacts
- `__pycache__/` - Python cache

### Rollback

If deployment fails, rollback on remote:

```bash
# If you have a backup
ssh rocksteady "cd /home/ubuntu && rm -rf unibos && mv unibos.backup unibos"

# Restart services
ssh rocksteady "sudo systemctl restart gunicorn nginx"
```

### Monitoring

Check deployment health:
```bash
# Service status
ssh rocksteady "systemctl status gunicorn nginx"

# Recent logs
ssh rocksteady "journalctl -u gunicorn -n 50 --no-pager"

# HTTP test
ssh rocksteady "curl -I http://localhost:8000/"
```

### Support

For issues:
1. Check logs: `ssh rocksteady "journalctl -u gunicorn -n 100"`
2. Verify services: `./deploy/rocksteady_v533.sh check`
3. Review this README for common issues
