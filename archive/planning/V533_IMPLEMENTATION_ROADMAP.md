# UNIBOS v533 - Implementation Roadmap

**Date**: 2025-11-12
**Status**: Ready for Implementation
**Architecture Doc**: [UNIBOS_v533_ARCHITECTURE.md](./UNIBOS_v533_ARCHITECTURE.md)

## Overview

This document provides a step-by-step roadmap for implementing the v533 architecture migration. The migration transforms UNIBOS from a 3-layer structure (apps/platform/modules) to a clean 2-layer structure (core/modules) with proper data management and CLI tooling.

## Architecture Documentation

- **Main Architecture**: [UNIBOS_v533_ARCHITECTURE.md](./UNIBOS_v533_ARCHITECTURE.md) - The authoritative v533 architecture
- **Planning Archive**: [archive/docs/v533_planning/](./archive/docs/v533_planning/) - Historical planning documents

## Pre-Migration Checklist

- [x] Architecture approved by user
- [x] Old planning docs archived
- [x] manage.py path fixed for new structure
- [x] Selective gitignore rules added
- [ ] Pre-migration backup created
- [ ] All current work committed

## Phase 1: Foundation (Week 1)

### 1.1 Create Data Structure

**Goal**: Establish the `/data/` directory at root with proper hierarchy

```bash
# Create data structure
mkdir -p data/{core,modules,shared,backups}
mkdir -p data/core/{postgres,redis,logs,cache}
mkdir -p data/core/postgres/{config,init,replication,backup/scripts,migrations,data}
mkdir -p data/core/logs/{django,celery,nginx,system}
mkdir -p data/shared/{media,static,temp}
mkdir -p data/backups/{daily,weekly,manual}

# Create module data directories
mkdir -p data/modules/{documents,wimm,recaria,birlikteyiz,movies,music,cctv,restopos,store}
mkdir -p data/modules/documents/{uploads,processed,thumbnails}
mkdir -p data/modules/wimm/{receipts,invoices,reports,exports}
mkdir -p data/modules/recaria/{recipe_images,user_uploads}
# ... (add all module directories)

# Create README
touch data/README.md
```

**Files to Create**:
- `data/README.md` - Explains data structure
- `data/core/postgres/config/*.conf` - PostgreSQL configs
- `data/core/postgres/init/*.sql` - Database init scripts

**Testing**:
- Verify directory structure matches architecture
- Ensure proper permissions

### 1.2 Create CLI Tool Structure

**Goal**: Implement `unibos` CLI command with Click

```bash
# Create CLI structure
mkdir -p core/cli
touch core/cli/__init__.py
touch core/cli/main.py
```

**Files to Create**:
- `core/cli/main.py` - Main CLI entry point with Click
- `core/cli/commands/` - Command modules (deploy, dev, db, etc.)
- `setup.py` - Python package setup for CLI installation

**CLI Commands to Implement**:
```python
# Deployment
unibos deploy local
unibos deploy rocksteady
unibos deploy raspberry <ip>

# Building
unibos build local
unibos build rocksteady
unibos build raspberry

# Database
unibos db migrate
unibos db backup
unibos db restore <backup>

# Development
unibos dev run
unibos dev shell
unibos dev test
unibos dev reset

# Maintenance
unibos status
unibos logs [service]
unibos restart [service]

# Version
unibos version
unibos upgrade
```

**Testing**:
- `pip install -e .` for development install
- `unibos --help` shows all commands
- Each command group works correctly

### 1.3 Create Deployment Infrastructure

**Goal**: Implement deployment system with profiles

```bash
# Create deployment structure
mkdir -p core/deployment/{deployer,builder,profiles}
touch core/deployment/__init__.py
touch core/deployment/deployer.py
touch core/deployment/builder.py
touch core/deployment/profiles/{local,rocksteady,raspberry}.py
```

**Files to Create**:
- `core/deployment/deployer.py` - Main deployment orchestrator
- `core/deployment/builder.py` - Build system for different targets
- `core/deployment/profiles/local.py` - Local production profile
- `core/deployment/profiles/rocksteady.py` - VPS profile
- `core/deployment/profiles/raspberry.py` - Raspberry Pi profile

**Deployment Profiles**:
```python
# local.py
DEPLOYMENT_TARGET = "/Users/berkhatirli/Applications/unibos/"
DATABASE_NAME = "unibos_local"
ENVIRONMENT = "production"

# rocksteady.py
DEPLOYMENT_TARGET = "rocksteady:~/unibos/"
DATABASE_NAME = "unibos_prod"
ENVIRONMENT = "production"

# raspberry.py
DEPLOYMENT_TARGET = "raspberry:~/unibos/"
DATABASE_NAME = "unibos_edge"
ENVIRONMENT = "edge"
```

**Testing**:
- Build process creates correct artifacts
- Deployment profiles load correctly
- Can simulate deployment (dry run)

## Phase 2: Core Restructuring (Week 2)

### 2.1 Reorganize Core Structure

**Goal**: Flatten core structure, remove unnecessary nesting

**Current Structure**:
```
core/
├── backend/  (Django web)
└── ... (future additions)
```

**New Structure**:
```
core/
├── web/               # Django web runtime (renamed from backend)
├── cli/               # CLI tool
├── deployment/        # Deployment system
├── platform/          # Platform infrastructure
│   ├── orchestration/ # Task distribution
│   ├── routing/       # Connection routing
│   └── offline/       # Offline mode
├── models/            # Shared domain models
├── p2p/               # P2P infrastructure
├── sdk/               # SDKs (dart, python)
├── services/          # Shared services
├── sync/              # Sync logic
├── system/            # System modules
└── tools/             # Development tools (moved from root)
```

**Steps**:
```bash
# Rename backend to web
git mv core/backend core/web

# Move tools to core
git mv tools core/tools

# Create new directories
mkdir -p core/platform/{orchestration,routing,offline}
mkdir -p core/sdk/{dart,python}

# Update all import paths
# (This will be done with find/replace scripts)
```

**Files to Update**:
- All import statements in Python files
- Django settings files
- WSGI/ASGI configuration
- Deployment scripts

**Testing**:
- All imports resolve correctly
- Django can start with new paths
- No broken references

### 2.2 Update Django Settings

**Goal**: Update settings to use new data paths

**File**: `core/web/unibos_backend/settings/base.py`

**Changes**:
```python
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # /unibos/
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

**Testing**:
- Django finds data directories
- Media uploads work correctly
- Static files serve properly
- Logs write to correct location

### 2.3 Update Module Data Paths

**Goal**: Update each module to use new data structure

**For each module**:
1. Update `models.py` file paths
2. Update upload handlers
3. Update media serving
4. Test file operations

**Example** - Documents module:
```python
# modules/documents/models.py
from django.conf import settings
from pathlib import Path

class Document(models.Model):
    file = models.FileField()

    def get_upload_path(self, filename):
        """Returns: data/modules/documents/uploads/invoices/filename"""
        return Path('documents') / 'uploads' / 'invoices' / filename

    def get_ocr_path(self):
        """Returns: data/modules/documents/processed/text/doc_id.txt"""
        base = settings.DATA_DIR / 'modules' / 'documents' / 'processed'
        return base / 'text' / f'{self.id}.txt'
```

**Modules to Update** (13 total):
1. documents
2. wimm
3. recaria
4. birlikteyiz
5. movies
6. music
7. cctv
8. restopos
9. store
10. solitaire
11. version_manager
12. administration
13. logging

**Testing**:
- File uploads work for each module
- Files saved to correct data/ subdirectory
- Media retrieval works
- No path errors

## Phase 3: Platform Infrastructure (Week 3)

### 3.1 Task Distribution System

**Goal**: Implement Rocksteady → Raspberry task distribution

```bash
mkdir -p core/platform/orchestration
touch core/platform/orchestration/{__init__.py,task_queue.py,task_distributor.py,task_scheduler.py,worker_registry.py,health_monitor.py}
```

**Components**:
- `task_queue.py` - Celery-based task queue
- `task_distributor.py` - Task distribution logic
- `task_scheduler.py` - Scheduling system
- `worker_registry.py` - Worker (Raspberry) registry
- `health_monitor.py` - Worker health checks

**Technology**: Celery + Redis (already in use)

**Testing**:
- Tasks can be queued
- Workers can receive tasks
- Health monitoring works
- Failover works

### 3.2 Connection Routing

**Goal**: Implement connection routing logic

```bash
mkdir -p core/platform/routing
touch core/platform/routing/{__init__.py,router.py,priority_table.py,load_balancer.py,health_checker.py}
mkdir -p core/platform/routing/policies
touch core/platform/routing/policies/{local_first.py,performance_based.py,cost_optimized.py}
```

**Components**:
- `router.py` - Main routing logic
- `priority_table.py` - Routing priorities
- `load_balancer.py` - Load balancing
- `health_checker.py` - Endpoint health checks

**Policies**:
- Local-first: Prefer local raspberry
- Performance-based: Route by latency
- Cost-optimized: Minimize bandwidth costs

**Testing**:
- Routes to correct endpoint
- Health checks work
- Failover works
- Load balancing distributes correctly

### 3.3 Offline Mode Strategy

**Goal**: Implement offline mode with sync queue

```bash
mkdir -p core/platform/offline
touch core/platform/offline/{__init__.py,offline_detector.py,sync_strategy.py,conflict_resolver.py,queue_manager.py}
mkdir -p core/platform/offline/storage
touch core/platform/offline/storage/{local_cache.py,delta_tracker.py}
```

**Components**:
- `offline_detector.py` - Detect offline state
- `sync_strategy.py` - Sync when online
- `conflict_resolver.py` - CRDT conflict resolution
- `queue_manager.py` - Offline operation queue

**Testing**:
- Offline detection works
- Operations queue correctly
- Sync works when online
- Conflicts resolve correctly

## Phase 4: Production Deployment (Week 4)

### 4.1 Local Production Setup

**Goal**: Deploy to `/Users/berkhatirli/Applications/unibos/`

**Steps**:
```bash
# Build
unibos build local

# Deploy
unibos deploy local

# Verify
unibos status
```

**Verification**:
- Application runs at /Applications/unibos/
- Data stored in /Applications/unibos/data/
- Database: unibos_local
- All modules work
- Media files accessible

### 4.2 Rocksteady Deployment

**Goal**: Deploy to VPS

**Steps**:
```bash
# Build
unibos build rocksteady

# Deploy
unibos deploy rocksteady

# Verify
ssh rocksteady "cd ~/unibos && unibos status"
```

**Verification**:
- Application accessible at unibos.berkhatirli.com
- Database: unibos_prod + unibos_common
- All services running (gunicorn, nginx, celery)
- Health checks pass

### 4.3 Raspberry Pi Deployment

**Goal**: Deploy to Raspberry Pi edge device

**Steps**:
```bash
# Build
unibos build raspberry

# Deploy
unibos deploy raspberry 192.168.1.100

# Verify
ssh raspberry "cd ~/unibos && unibos status"
```

**Verification**:
- PostgreSQL streaming replica active
- mDNS broadcasting (unibos.local)
- Can accept local connections
- Offline mode works

## Phase 5: Documentation & Testing (Week 5)

### 5.1 Documentation

**Documents to Create/Update**:
- [ ] Update README.md with v533 architecture
- [ ] Create deployment guide
- [ ] Create developer guide
- [ ] Document CLI commands
- [ ] Document data structure
- [ ] Update module integration guide

### 5.2 Testing

**Test Categories**:

1. **Unit Tests**: Core functionality
2. **Integration Tests**: Module interaction
3. **Deployment Tests**: All deployment targets
4. **Performance Tests**: Load and stress testing
5. **Security Tests**: Authentication, authorization, data protection

**Test Checklist**:
- [ ] All 13 modules function correctly
- [ ] File uploads/downloads work
- [ ] Database operations work
- [ ] CLI commands work
- [ ] Deployment succeeds
- [ ] Health monitoring works
- [ ] Offline mode works
- [ ] Sync works correctly

### 5.3 Migration Completion

**Final Steps**:
- [ ] All tests pass
- [ ] Documentation complete
- [ ] User acceptance testing
- [ ] Production deployment successful
- [ ] Monitoring configured
- [ ] Backup strategy active
- [ ] Create v533 release tag

## Rollback Strategy

### If Migration Fails

1. **Stop Services**:
   ```bash
   unibos restart --all
   ```

2. **Restore from Pre-Migration Backup**:
   ```bash
   unibos db restore /path/to/backup
   ```

3. **Revert Code**:
   ```bash
   git checkout v532
   ```

4. **Restart Services**:
   ```bash
   unibos restart --all
   ```

### Pre-Migration Backups

Create comprehensive backup before starting:
```bash
# Database
unibos db backup --profile dev

# Code
git tag -a v532_final -m "Last v532 before v533 migration"

# Data files
rsync -av data/ backups/v532_data_$(date +%Y%m%d)/
```

## Risk Management

### High Risk Items

1. **Data Loss**: Mitigated by backups before each phase
2. **Import Path Breakage**: Mitigated by comprehensive testing
3. **Module Incompatibility**: Mitigated by module-by-module testing
4. **Production Downtime**: Mitigated by testing on local prod first

### Mitigation Strategies

- Test each phase thoroughly before proceeding
- Keep v532 working in parallel during migration
- Use feature flags to enable/disable new features
- Monitor logs closely during migration
- Have rollback plan ready at each phase

## Timeline

**Estimated Duration**: 5 weeks (flexible based on issues)

- **Week 1**: Foundation (data structure, CLI, deployment infra)
- **Week 2**: Core restructuring (rename, reorganize, update paths)
- **Week 3**: Platform infrastructure (orchestration, routing, offline)
- **Week 4**: Production deployment (local, rocksteady, raspberry)
- **Week 5**: Documentation & testing (docs, tests, release)

## Success Criteria

Migration is considered successful when:

- [ ] All 13 modules work correctly
- [ ] CLI tool functional
- [ ] Data structure properly organized
- [ ] Deployment works to all targets
- [ ] No regressions from v532
- [ ] Documentation complete
- [ ] User approves migration

## Next Steps

1. Review this roadmap with user
2. Create pre-migration backup
3. Begin Phase 1: Foundation
4. Track progress using todo list
5. Update this document as needed

---

**Document Version**: 1.0
**Last Updated**: 2025-11-12
**Status**: Ready for implementation
