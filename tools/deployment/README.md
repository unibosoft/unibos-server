# UNIBOS Deployment Tools

Deployment scripts and utilities for the UNIBOS platform.

## Deployment Scripts

Scripts for deploying UNIBOS to various environments.

### Production Deployment
- Deploy to rocksteady server
- Database migrations
- Static file collection
- Service restart

### Development Deployment
- Local development setup
- Development server configuration
- Test environment setup

## Usage

All deployment scripts should be run from the project root:

```bash
# Deploy to production
bash tools/deployment/deploy_prod.sh

# Deploy to staging
bash tools/deployment/deploy_staging.sh

# Setup development environment
bash tools/deployment/setup_dev.sh
```

## Deployment Workflow

1. **Pre-deployment Checks**
   - Version verification
   - Dependency check
   - Database backup

2. **Deployment**
   - Code deployment
   - Database migrations
   - Static file collection

3. **Post-deployment**
   - Service restart
   - Health checks
   - Monitoring setup

## Configuration

Deployment configurations are stored in:
- Environment variables (.env)
- Deployment config files
- Server-specific settings

## Rollback

In case of deployment failure:
1. Check deployment logs
2. Run rollback script if available
3. Restore database from backup if needed