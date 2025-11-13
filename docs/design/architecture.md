# UNIBOS v533 - Final Architecture (REVISED)

**Date**: 2025-11-12
**Revision**: 2 (CLI + Data Structure)
**Status**: Ready for Implementation

## 🔧 Changes from Previous Version

1. **CLI Tool**: `unibos` command instead of `make`
2. **Data Structure**: Organized for core + modules

---

## 💻 UNIBOS CLI Tool

### Installation

```bash
# Development mode
cd /Users/berkhatirli/Desktop/unibos/
pip install -e .

# Now `unibos` command is available
unibos --help
```

### Commands

```bash
# Deployment
unibos deploy local              # Deploy to local production
unibos deploy rocksteady         # Deploy to VPS
unibos deploy raspberry <ip>    # Deploy to Raspberry Pi

# Building
unibos build local               # Build local package
unibos build rocksteady          # Build rocksteady package
unibos build raspberry           # Build raspberry package

# Database
unibos db migrate                # Run migrations
unibos db backup                 # Backup database
unibos db restore <backup>       # Restore from backup

# Development
unibos dev run                   # Run dev server
unibos dev shell                 # Django shell
unibos dev test                  # Run tests
unibos dev reset                 # Reset dev database

# Maintenance
unibos status                    # System health check
unibos logs [service]            # View logs
unibos restart [service]         # Restart services

# Version
unibos version                   # Show version info
unibos upgrade                   # Upgrade to latest
```

### Implementation

```python
# core/cli/main.py
import click

@click.group()
def cli():
    """UNIBOS - Universal Integrated Backend and Operating System"""
    pass

@cli.group()
def deploy():
    """Deployment commands"""
    pass

@deploy.command()
@click.argument('profile', type=click.Choice(['local', 'rocksteady', 'raspberry']))
@click.option('--target', help='Target host (for raspberry)')
def deploy_cmd(profile, target):
    """Deploy UNIBOS to target environment"""
    from core.deployment.deployer import Deployer

    deployer = Deployer()
    deployer.deploy(profile=profile, target=target)
    click.echo(f"✓ Deployed to {profile}")

@cli.group()
def dev():
    """Development commands"""
    pass

@dev.command()
def run():
    """Run development server"""
    import os
    os.system('cd core/web && python manage.py runserver')

@dev.command()
def test():
    """Run tests"""
    import pytest
    pytest.main(['tests/'])

# ... more commands

if __name__ == '__main__':
    cli()
```

```python
# setup.py (root)
from setuptools import setup, find_packages

setup(
    name='unibos',
    version='0.533.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'unibos=core.cli.main:cli',
        ],
    },
    install_requires=[
        'click>=8.0',
        'django>=4.2',
        # ... other deps
    ],
)
```

---

## 📁 Data Structure (Revised)

```
/Users/berkhatirli/Desktop/unibos/
│
└── data/                                  # 💾 ALL DATA
    ├── README.md                         # Data structure explained
    ├── .gitkeep
    │
    ├── core/                             # Core system data
    │   ├── postgres/                     # PostgreSQL
    │   │   ├── config/                   # (git tracked)
    │   │   │   ├── README.md
    │   │   │   ├── base.conf
    │   │   │   ├── master.conf
    │   │   │   └── replica.conf
    │   │   ├── init/                     # (git tracked)
    │   │   │   ├── README.md
    │   │   │   ├── 001_databases.sql
    │   │   │   ├── 002_extensions.sql
    │   │   │   ├── 003_roles.sql
    │   │   │   └── 004_initial_data.sql
    │   │   ├── replication/              # (git tracked)
    │   │   │   ├── README.md
    │   │   │   ├── setup_master.sh
    │   │   │   └── setup_replica.sh
    │   │   ├── backup/                   # (git tracked scripts only)
    │   │   │   ├── README.md
    │   │   │   └── scripts/
    │   │   │       ├── backup.sh
    │   │   │       ├── restore.sh
    │   │   │       └── verify.sh
    │   │   ├── migrations/               # (git tracked)
    │   │   │   └── [Django migrations]
    │   │   └── data/                     # (gitignored - runtime)
    │   │       ├── pg_data/              # PostgreSQL data files
    │   │       └── pg_wal/               # Write-ahead log
    │   │
    │   ├── redis/                        # Redis cache (gitignored)
    │   │   ├── dump.rdb
    │   │   └── appendonly.aof
    │   │
    │   ├── logs/                         # Logs (gitignored)
    │   │   ├── django/
    │   │   │   ├── debug.log
    │   │   │   └── error.log
    │   │   ├── celery/
    │   │   │   ├── worker.log
    │   │   │   └── beat.log
    │   │   ├── nginx/
    │   │   │   ├── access.log
    │   │   │   └── error.log
    │   │   └── system/
    │   │       └── unibos.log
    │   │
    │   └── cache/                        # Cache (gitignored)
    │       ├── filesystem/               # File-based cache
    │       └── sessions/                 # Session files
    │
    ├── modules/                          # Module-specific data (gitignored)
    │   ├── documents/
    │   │   ├── uploads/                  # Original uploaded files
    │   │   │   ├── invoices/
    │   │   │   ├── receipts/
    │   │   │   └── contracts/
    │   │   ├── processed/                # OCR processed
    │   │   │   ├── text/
    │   │   │   └── json/
    │   │   └── thumbnails/               # Generated thumbnails
    │   │
    │   ├── wimm/                         # Financial management
    │   │   ├── receipts/                 # Receipt images
    │   │   ├── invoices/                 # Invoice PDFs
    │   │   ├── reports/                  # Generated reports
    │   │   │   ├── monthly/
    │   │   │   └── yearly/
    │   │   └── exports/                  # Exported data
    │   │
    │   ├── recaria/                      # Recipe management
    │   │   ├── recipe_images/            # Recipe photos
    │   │   │   ├── main/
    │   │   │   └── steps/
    │   │   └── user_uploads/             # User contributed
    │   │
    │   ├── birlikteyiz/                  # Earthquake alerts
    │   │   ├── earthquake_cache/         # Cached EMSC data
    │   │   ├── maps/                     # Generated maps
    │   │   └── notification_queue/       # Pending notifications
    │   │
    │   ├── movies/                       # Media library
    │   │   ├── posters/                  # Movie posters
    │   │   ├── metadata/                 # Movie metadata
    │   │   └── cache/                    # API cache
    │   │
    │   ├── music/                        # Music player
    │   │   ├── covers/                   # Album covers
    │   │   ├── library/                  # Music files
    │   │   └── playlists/
    │   │
    │   ├── cctv/                         # Camera monitoring
    │   │   ├── recordings/               # Video recordings
    │   │   │   ├── motion/
    │   │   │   └── scheduled/
    │   │   ├── snapshots/                # Still images
    │   │   └── streams/                  # Stream cache
    │   │
    │   ├── restopos/                     # Restaurant POS
    │   │   ├── receipts/                 # Customer receipts
    │   │   ├── reports/                  # Sales reports
    │   │   └── invoices/                 # Supplier invoices
    │   │
    │   └── store/                        # E-commerce
    │       ├── products/
    │       │   ├── images/               # Product images
    │       │   └── documents/            # Product docs
    │       ├── orders/                   # Order files
    │       └── invoices/                 # Customer invoices
    │
    ├── shared/                           # Shared data (gitignored)
    │   ├── media/                        # Generic media
    │   │   ├── avatars/                  # User avatars
    │   │   ├── attachments/              # Generic attachments
    │   │   └── downloads/                # Downloaded files
    │   ├── static/                       # Collected static files
    │   │   └── [Django collectstatic output]
    │   └── temp/                         # Temporary files
    │       ├── uploads/                  # Upload temp
    │       └── processing/               # Processing temp
    │
    └── backups/                          # Backups (gitignored)
        ├── daily/                        # Daily backups
        │   └── unibos_YYYYMMDD.sql.gz
        ├── weekly/                       # Weekly backups
        │   └── unibos_YYYYMMDD_weekly.sql.gz
        └── manual/                       # Manual backups
            └── unibos_YYYYMMDD_HHmm.sql.gz
```

### .gitignore Updates

```gitignore
# Root data/ (entire directory ignored by default)
data/

# Exception: Keep configs and scripts
!data/core/postgres/config/
!data/core/postgres/config/**
!data/core/postgres/init/
!data/core/postgres/init/**
!data/core/postgres/replication/
!data/core/postgres/replication/**
!data/core/postgres/backup/scripts/
!data/core/postgres/backup/scripts/**
!data/core/postgres/migrations/
!data/core/postgres/migrations/**
!data/README.md
!data/.gitkeep

# Ignore core/data/ (old location, if exists)
core/data/
```

---

## 📊 Data Access Patterns

### Django Settings

```python
# core/web/unibos_backend/settings/base.py
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / 'data'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unibos_dev',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

# Media files (modules)
MEDIA_ROOT = DATA_DIR / 'modules'
MEDIA_URL = '/media/'

# Module-specific media roots
DOCUMENTS_ROOT = DATA_DIR / 'modules' / 'documents'
WIMM_ROOT = DATA_DIR / 'modules' / 'wimm'
RECARIA_ROOT = DATA_DIR / 'modules' / 'recaria'
# ... etc

# Static files
STATIC_ROOT = DATA_DIR / 'shared' / 'static'
STATIC_URL = '/static/'

# Logs
LOGGING = {
    'handlers': {
        'file': {
            'filename': DATA_DIR / 'core' / 'logs' / 'django' / 'debug.log',
        },
    },
}
```

### Module Access

```python
# modules/documents/models.py
from django.conf import settings
from pathlib import Path

class Document(models.Model):
    file = models.FileField()

    def get_upload_path(self, filename):
        """
        Returns: data/modules/documents/uploads/invoices/filename
        """
        return Path('documents') / 'uploads' / 'invoices' / filename

    def get_ocr_path(self):
        """
        Returns: data/modules/documents/processed/text/doc_id.txt
        """
        base = settings.DATA_DIR / 'modules' / 'documents' / 'processed'
        return base / 'text' / f'{self.id}.txt'
```

---

## 🚀 Deployment with CLI

### Local Development

```bash
# Run dev server
unibos dev run

# Data is in: /Desktop/unibos/data/
```

### Local Production Deployment

```bash
# Build
unibos build local

# Deploy
unibos deploy local

# Data is in: /Applications/unibos/data/
```

### Rocksteady Deployment

```bash
# Build
unibos build rocksteady

# Deploy
unibos deploy rocksteady

# Data is in: rocksteady:~/unibos/data/
```

### Raspberry Deployment

```bash
# Build
unibos build raspberry

# Deploy
unibos deploy raspberry 192.168.1.100

# Data is in: raspberry:~/unibos/data/
```

---

## 🔄 Data Migration Between Environments

### From Dev to Local Prod

```bash
# Export dev data
unibos db export --profile dev --output /tmp/dev_data.sql

# Import to local prod
unibos db import --profile local --input /tmp/dev_data.sql

# Sync media files
rsync -av \
  /Desktop/unibos/data/modules/ \
  /Applications/unibos/data/modules/
```

### From Local to Rocksteady

```bash
# Backup local
unibos db backup --profile local

# Transfer to rocksteady
scp /Applications/unibos/data/backups/latest.sql.gz \
  rocksteady:~/unibos/data/backups/

# Import on rocksteady
ssh rocksteady "unibos db restore ~/unibos/data/backups/latest.sql.gz"

# Sync media (selective)
rsync -av --exclude='temp/' \
  /Applications/unibos/data/modules/documents/ \
  rocksteady:~/unibos/data/modules/documents/
```

---

## 📋 Implementation Checklist

### Phase 1: CLI Tool
- [ ] Create `core/cli/main.py`
- [ ] Implement basic commands (deploy, build, dev)
- [ ] Create `setup.py` for installation
- [ ] Test `unibos` command

### Phase 2: Data Structure
- [ ] Create `/data/` structure
- [ ] Move configs to `data/core/postgres/`
- [ ] Update `.gitignore`
- [ ] Update Django settings for new paths

### Phase 3: Deployment System
- [ ] Implement `core/deployment/deployer.py`
- [ ] Implement `core/deployment/builder.py`
- [ ] Create deployment profiles
- [ ] Test local deployment

### Phase 4: Module Integration
- [ ] Update each module for new data paths
- [ ] Test file uploads
- [ ] Test media serving
- [ ] Verify all modules work

### Phase 5: Production
- [ ] Setup `/Applications/unibos/`
- [ ] Deploy to local production
- [ ] Test thoroughly
- [ ] Deploy to Rocksteady

---

## 🎯 CLI vs Make Comparison

### Make (Old)
```bash
make deploy-local
make build-rocksteady
make test
```

**Pros**: Simple, familiar
**Cons**: Not cross-platform, less flexible

### UNIBOS CLI (New)
```bash
unibos deploy local
unibos build rocksteady
unibos test
```

**Pros**:
- Cross-platform (works on Windows too)
- More professional
- Built-in help (`unibos --help`)
- Tab completion
- Python-integrated
- Easy to extend

**Cons**:
- Need to install (`pip install -e .`)

---

## ✅ Final Approval

**Questions**:

1. **CLI yaklaşımı uygun mu?** `unibos deploy local` vs `make deploy-local`

2. **Data structure düzgün mü?** `data/core/` + `data/modules/` + `data/shared/`

3. **Module data paths mantıklı mı?** Her module'ün data/modules/ altında kendi dizini

4. **Gitignore strategy doğru mu?** Sadece configs git'te, runtime data gitignore'da

Onaylarsan implementation'a başlayacağım!
