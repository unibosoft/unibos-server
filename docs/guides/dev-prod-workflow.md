# Dev/Prod Workflow Guide

**Document Type:** Practical Guide
**Created:** 2025-11-13
**Status:** Active

---

## 📋 Overview

UNIBOS uses a dual-repository system for development and production:

- **Dev Repo:** `https://github.com/unibosoft/unibos_dev` - Full development history
- **Prod Repo:** `https://github.com/unibosoft/unibos` - Clean production builds

### Directory Structure

```
/Users/berkhatirli/Desktop/unibos-dev/           # Development workspace
├── data/                                         # Dev data (gitignored)
│   ├── core/                                    # PostgreSQL, Redis, logs
│   └── modules/                                 # Module file uploads
├── archive/                                      # Version history (dev-only)
├── TODO.md, RULES.md                            # Dev docs (excluded from prod)
└── [full source code]

/Users/berkhatirli/Applications/unibos/          # Local production instance
├── data/                                         # Prod data (separate!)
│   ├── core/                                    # Separate PostgreSQL, Redis
│   └── modules/                                 # Separate uploads
└── [production code only - no dev files]
```

---

## 🔑 Key Principles

### 1. Complete Separation

**Dev and Prod MUST be completely isolated:**

✅ **Separate Databases:**
- Dev: `unibos_dev` (PostgreSQL, user: `unibos_dev_user`)
- Prod: `unibos_db` (PostgreSQL, user: `unibos_db_user`)

✅ **Separate Redis:**
- Dev: Redis DB 0
- Prod: Redis DB 1

✅ **Separate Data:**
- Dev: `/Users/berkhatirli/Desktop/unibos-dev/data/`
- Prod: `/Users/berkhatirli/Applications/unibos/data/`

✅ **Separate .env:**
- Each has its own configuration
- Different SECRET_KEY
- Different database credentials

### 2. Filtered Production Builds

Production excludes development-only files (`.prodignore`):
- ❌ `archive/` - Version history
- ❌ `data/` - Runtime data
- ❌ `TODO.md`, `RULES.md` - Dev documentation
- ❌ `docs/rules/` - Dev-specific rules
- ❌ `.claude/` - Claude session data
- ❌ `build/`, `__pycache__/` - Build artifacts
- ❌ Screenshots, logs, backups

### 3. Git Workflow

**Two Remotes:**
- `origin` → `unibos_dev` (development)
- `prod` → `unibos` (production)

---

## 🚀 Quick Start

### Initial Setup

```bash
# 1. Setup git remotes
unibos git setup

# 2. Verify remotes
unibos git status

# 3. Create prod database (one-time)
createdb unibos_db
```

---

## 📝 Daily Workflow

### Development Work

```bash
# 1. Work in dev directory
cd /Users/berkhatirli/Desktop/unibos-dev/

# 2. Make changes, test locally
unibos dev run

# 3. Commit changes
git add .
git commit -m "feat: add new feature"

# 4. Push to dev repo
unibos git push-dev
# or manually:
git push origin v533_migration
```

### Testing in Local Production

```bash
# 1. Sync to local prod
unibos git sync-prod

# 2. Test in prod environment
cd /Users/berkhatirli/Applications/unibos/
source core/web/venv/bin/activate
python core/web/manage.py runserver 8001

# 3. Access at http://localhost:8001
```

### Deploying to Production Git

```bash
# 1. Make sure dev is committed
unibos git status

# 2. Dry-run to see what will be pushed
unibos git push-prod --dry-run

# 3. Push to prod repo
unibos git push-prod
# WARNING: This is destructive! Use with caution.
```

---

## 🛠️ CLI Commands Reference

### `unibos git status`

Show git status for both dev and prod:

```bash
unibos git status
```

**Output:**
- Current branch
- Configured remotes
- Working directory status
- Unpushed commits

### `unibos git setup`

Setup or update git remotes:

```bash
# Initial setup
unibos git setup

# Force update remotes
unibos git setup --force
```

### `unibos git push-dev`

Push to development repository:

```bash
# Push current branch
unibos git push-dev

# Push specific branch
unibos git push-dev --branch v533_migration

# Force push (use with caution!)
unibos git push-dev --force
```

**Safety Checks:**
- ✅ Verifies working directory is clean
- ✅ Confirms remote exists
- ⚠️ Warns before force push

### `unibos git sync-prod`

Sync code to local production directory:

```bash
# Sync to default path (/Users/berkhatirli/Applications/unibos)
unibos git sync-prod

# Sync to custom path
unibos git sync-prod --path /path/to/prod

# Dry-run (show what would be synced)
unibos git sync-prod --dry-run
```

**Features:**
- ✅ Filters files using `.prodignore`
- ✅ Deletes removed files (`--delete`)
- ✅ Shows sync summary (size, file count)
- ✅ Safe dry-run mode

### `unibos git push-prod`

Push filtered code to production repository:

```bash
# Dry-run (recommended first)
unibos git push-prod --dry-run

# Actual push (requires confirmation)
unibos git push-prod

# Force push (skip confirmation)
unibos git push-prod --force
```

**Process:**
1. Creates temporary branch
2. Removes excluded files (per `.prodignore`)
3. Commits filtered tree
4. Pushes to `prod` remote (main branch)
5. Cleans up temporary branch

**⚠️ WARNING:** This is a destructive operation for the prod repo!

---

## 📂 File Exclusion (`.prodignore`)

### What Gets Excluded

The `.prodignore` file defines what should NOT go to production:

```bash
# Development files
TODO.md
RULES.md
docs/rules/
docs/design/decisions/
.claude/

# Archives
archive/

# Data & runtime
data/
*.sqlite3
*.log

# Build artifacts
build/
__pycache__/
*.pyc

# Virtual environments
venv/

# Environment files
.env
.env.*
!.env.example

# Backups
*.backup
*.sql

# Git
.git/
```

### Modifying `.prodignore`

```bash
# 1. Edit file
vim .prodignore

# 2. Test with dry-run
unibos git sync-prod --dry-run

# 3. Verify exclusions work
# 4. Commit to dev repo
git add .prodignore
git commit -m "chore: update prod exclusions"
```

---

## 🔒 Database Separation

### Dev Database

```bash
# Location: PostgreSQL on localhost:5432
Database: unibos_dev
User: unibos_dev_user
Redis: DB 0

# .env
DATABASE_URL=postgresql://unibos_dev_user:unibos_password@localhost:5432/unibos_dev
REDIS_URL=redis://localhost:6379/0
```

### Prod Database

```bash
# Location: PostgreSQL on localhost:5432
Database: unibos_db
User: unibos_db_user
Redis: DB 1

# .env
DATABASE_URL=postgresql://unibos_db_user:unibos_password@localhost:5432/unibos_db
REDIS_URL=redis://localhost:6379/1
```

### Creating Prod Database

```bash
# One-time setup
createdb unibos_db

# Grant permissions
psql -d unibos_db -c "GRANT ALL PRIVILEGES ON DATABASE unibos_db TO unibos_db_user;"

# Run migrations
cd /Users/berkhatirli/Applications/unibos/core/web
source venv/bin/activate
python manage.py migrate
```

---

## 🚨 Safety Checklist

### Before Syncing to Prod

- [ ] All dev changes committed
- [ ] Dev tests passing
- [ ] `.prodignore` up to date
- [ ] Run `sync-prod --dry-run` first

### Before Pushing to Prod Git

- [ ] Local prod tested
- [ ] No sensitive data in commits
- [ ] Run `push-prod --dry-run` first
- [ ] Reviewed filtered file list
- [ ] Backup current prod state if needed

### Before Production Deployment (VPS)

- [ ] Prod git updated
- [ ] Local prod tested
- [ ] Database backup created
- [ ] Deployment plan reviewed
- [ ] Use `unibos deploy rocksteady`

---

## 📊 Verification Commands

### Check Data Separation

```bash
# Dev data location
ls -lh /Users/berkhatirli/Desktop/unibos-dev/data/

# Prod data location
ls -lh /Users/berkhatirli/Applications/unibos/data/

# Should be DIFFERENT!
```

### Check Database Separation

```bash
# Dev database
psql -l | grep unibos_dev

# Prod database
psql -l | grep unibos_db

# Should be TWO separate databases!
```

### Check Redis Separation

```bash
# Dev Redis (DB 0)
redis-cli -n 0 DBSIZE

# Prod Redis (DB 1)
redis-cli -n 1 DBSIZE
```

### Check Git Remotes

```bash
# Should show both origin and prod
git remote -v
```

---

## 🐛 Troubleshooting

### Problem: "Remote 'prod' not found"

```bash
# Solution: Setup git remotes
unibos git setup
```

### Problem: Prod and Dev sharing same database

```bash
# Check .env files
cat /Users/berkhatirli/Desktop/unibos-dev/core/web/.env | grep DATABASE_URL
cat /Users/berkhatirli/Applications/unibos/core/web/.env | grep DATABASE_URL

# Should be DIFFERENT!
# If same, update prod .env:
DATABASE_URL=postgresql://unibos_db_user:unibos_password@localhost:5432/unibos_db
```

### Problem: Prod has dev-only files

```bash
# Check what's in prod
ls -la /Users/berkhatirli/Applications/unibos/

# Should NOT have:
# - archive/
# - TODO.md
# - RULES.md
# - data/ (except empty structure)

# Re-sync with correct exclusions
unibos git sync-prod
```

### Problem: Changes not appearing in prod

```bash
# 1. Verify sync completed
unibos git sync-prod

# 2. Check timestamps
ls -lt /Users/berkhatirli/Applications/unibos/core/web/

# 3. Compare with dev
diff -r /Users/berkhatirli/Desktop/unibos-dev/core/web/ \
        /Users/berkhatirli/Applications/unibos/core/web/ \
        --exclude=venv --exclude=__pycache__
```

---

## 📚 Related Documentation

- [setup.md](./setup.md) - Initial project setup
- [development.md](./development.md) - Development workflow
- [deployment.md](./deployment.md) - Production deployment (VPS)
- [../rules/archive-safety.md](../rules/archive-safety.md) - Archive protection

---

## 📝 Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-11-13 | Initial creation | System |
| 2025-11-13 | Added CLI commands reference | System |
| 2025-11-13 | Added database separation details | System |

---

**Last Updated:** 2025-11-13
**Status:** Active
**Review Frequency:** After major workflow changes
