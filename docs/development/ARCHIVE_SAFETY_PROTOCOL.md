# Archive Safety Protocol

**Document Type:** Safety Protocol
**Criticality:** 🔴 MAXIMUM - Data Loss Prevention
**Last Updated:** 2025-11-13
**Review Frequency:** Before any archive-related operation

---

## 🚨 CRITICAL RULE: ARCHIVE VERSIONS ARE SACRED

**The Golden Rule:**
> `archive/versions/` directory is **READ-ONLY**. Never modify, delete, or move existing version archives.

### Why This Matters
- Each version is a complete snapshot of UNIBOS at a specific point in time
- Versions are **irreplaceable** historical records
- Loss of versions = loss of ability to rollback/debug/compare
- Some versions may be the only record of critical decisions or implementations

---

## 📂 Archive Directory Structure

```
archive/
├── versions/              🔴 SACRED - READ ONLY
│   ├── unibos_v526_*/    ❌ NEVER TOUCH
│   ├── unibos_v527_*/    ❌ NEVER TOUCH
│   ├── unibos_v528_*/    ❌ NEVER TOUCH
│   ├── unibos_v530_*/    ❌ NEVER TOUCH
│   ├── unibos_v531_*/    ❌ NEVER TOUCH
│   ├── unibos_v532_*/    ❌ NEVER TOUCH
│   └── unibos_v533_*/    ❌ NEVER TOUCH
├── planning/              ✅ Safe to organize
│   ├── completed/        ✅ Safe to add/organize
│   │   └── 2025-11-13_* ✅ Completed tasks
│   ├── FUTURE_ROADMAP_v533.md ✅ Safe to edit
│   └── V533_IMPLEMENTATION_ROADMAP.md ✅ Archive (read-only recommended)
├── database_backups/     ✅ Safe (managed by backup scripts)
└── docs/                 ✅ Safe (historical documentation)
```

---

## ✅ SAFE Operations

### What You CAN Do

#### 1. Read Archive Versions (Always Safe)
```bash
# View archive contents
ls -lh archive/versions/

# Check specific version
ls -la archive/versions/unibos_v533_20251110_1400/

# Read files from archives
cat archive/versions/unibos_v533_20251110_1400/README.md

# Compare versions
diff -r archive/versions/unibos_v532_*/ archive/versions/unibos_v533_*/

# Check sizes (for analysis)
du -sh archive/versions/*
```

#### 2. Organize Planning Directory (Safe)
```bash
# Move completed tasks
mv completed_task.md archive/planning/completed/

# Create new planning docs
touch archive/planning/FUTURE_PLAN.md

# Update planning docs
vim archive/planning/FUTURE_ROADMAP_v533.md
```

#### 3. Work with .archiveignore (Safe - Future Archives Only)
```bash
# Edit .archiveignore (affects FUTURE archives only)
vim .archiveignore

# Test exclusion patterns (dry-run, no changes)
rsync --dry-run -av --exclude-from=.archiveignore . test_archive/

# Verify patterns work
grep -v '^#' .archiveignore | grep -v '^$'
```

#### 4. Create NEW Archives (Safe - Using Scripts)
```bash
# Using versioning script (RECOMMENDED)
./tools/scripts/unibos_version.sh
# Choose option 5: Archive Only

# Manual (if needed)
ARCHIVE_NAME="unibos_v534_$(date +%Y%m%d_%H%M)"
rsync -av --exclude-from=.archiveignore . "archive/versions/$ARCHIVE_NAME/"
```

---

## ❌ FORBIDDEN Operations

### What You MUST NEVER Do

#### 1. Never Modify Existing Archives
```bash
# ❌ FORBIDDEN - Deleting version
rm -rf archive/versions/unibos_v530_*/

# ❌ FORBIDDEN - Modifying version
vim archive/versions/unibos_v530_*/some_file.py

# ❌ FORBIDDEN - Moving version
mv archive/versions/unibos_v530_*/ /tmp/

# ❌ FORBIDDEN - Renaming version
mv archive/versions/unibos_v530_*/ archive/versions/unibos_v530_renamed/

# ❌ FORBIDDEN - Cleanup inside version
rm archive/versions/unibos_v530_*/modules/birlikteyiz/mobile/build/
```

#### 2. Never Run Cleanup Scripts on Existing Archives
```bash
# ❌ FORBIDDEN - Cleaning archive
find archive/versions/unibos_v530_*/ -name "build" -type d -exec rm -rf {} \;

# ❌ FORBIDDEN - Removing logs from archive
find archive/versions/ -name "*.log" -delete

# ❌ FORBIDDEN - Compressing archive (changes contents)
tar -czf archive/versions/unibos_v530_compressed.tar.gz archive/versions/unibos_v530_*/
rm -rf archive/versions/unibos_v530_*/
```

#### 3. Never Use Destructive Git Operations on Archives
```bash
# ❌ FORBIDDEN - Git clean in archive
git clean -fdx archive/versions/unibos_v530_*/

# ❌ FORBIDDEN - Resetting archive
git checkout -- archive/versions/unibos_v530_*/

# ❌ FORBIDDEN - Removing from git history
git filter-branch --tree-filter 'rm -rf archive/versions/unibos_v530_*' HEAD
```

---

## 🔍 Archive Optimization - SAFE Approach

### The ONLY Safe Way to Optimize Archives

**Principle:** Optimize FUTURE archives, not existing ones.

#### Step 1: Analyze Current Archives (Read-Only)
```bash
# Check current archive sizes
du -sh archive/versions/*

# Find large files/directories
find archive/versions/unibos_v533_*/ -type f -size +10M

# Identify what should be excluded
find archive/versions/unibos_v533_*/ -name "build" -type d
find archive/versions/unibos_v533_*/ -name "venv" -type d
find archive/versions/unibos_v533_*/ -name "*.log" -type f
```

**Example Analysis:**
```
archive/versions/unibos_v530_20251107_1152/  1.7GB
  └── modules/birlikteyiz/mobile/build/      1.6GB  ← Should exclude
archive/versions/unibos_v531_20251109_1403/  858MB  (build already removed)
```

#### Step 2: Update .archiveignore (Affects Future Only)
```bash
# Edit .archiveignore
vim .archiveignore

# Add exclusion patterns
echo "modules/*/mobile/build/" >> .archiveignore
echo "core/web/venv/" >> .archiveignore
echo "*.log" >> .archiveignore
```

#### Step 3: Test Exclusions (Dry-Run)
```bash
# Create test directory
mkdir -p /tmp/archive_test
cp -r . /tmp/archive_test/source/

# Test rsync with exclusions (DRY RUN)
rsync --dry-run -av --exclude-from=.archiveignore \
  /tmp/archive_test/source/ \
  /tmp/archive_test/archive/

# Verify exclusions worked
du -sh /tmp/archive_test/archive/
```

#### Step 4: Document Findings
Update `docs/development/VERSIONING_RULES.md` with findings:
- What patterns were found
- Why they should be excluded
- Expected size savings for future archives

#### Step 5: Leave Existing Archives Alone
**CRITICAL:** Do NOT touch existing archives in `archive/versions/`.

**Rationale:**
- Disk space is cheap
- Historical accuracy is priceless
- Existing archives may be referenced in commits, docs, or scripts
- Better to have bloated archive than risk data loss

---

## 📋 .archiveignore Best Practices

### Current Patterns (Verified Safe)
```bash
# Build artifacts
modules/*/mobile/build/
modules/*/mobile/.dart_tool/
modules/*/mobile/.flutter-plugins
modules/*/mobile/.flutter-plugins-dependencies

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
core/web/venv/
venv/
ENV/
env/

# Logs
*.log
core/web/logs/
logs/

# Databases (should be backed up separately)
*.sqlite3
*.db
data_db/
db.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Temporary
*.tmp
*.temp
tmp/
temp/

# Node
node_modules/
npm-debug.log*

# Git
.git/

# Large media (should be in data/)
*.mp4
*.mkv
*.avi
*.mov
```

### Verification Checklist
Before adding new pattern:
- [ ] Pattern is specific enough (not too broad)
- [ ] Pattern won't exclude important config/code
- [ ] Pattern tested with dry-run
- [ ] Pattern documented with comment
- [ ] Rationale added to VERSIONING_RULES.md

---

## 🚨 Emergency Procedures

### If Archive Was Accidentally Modified

#### Scenario 1: Small Change (File Edited)
**If you accidentally edited a file in an archive:**

1. **DON'T PANIC** - Git likely has the original
2. Check git status:
   ```bash
   git status archive/versions/
   ```
3. If modified, restore from git:
   ```bash
   git checkout -- archive/versions/unibos_v530_*/modified_file.py
   ```
4. Verify restoration:
   ```bash
   git diff archive/versions/unibos_v530_*/
   ```

#### Scenario 2: Large Change (Directory Deleted)
**If you accidentally deleted a directory in an archive:**

1. **STOP IMMEDIATELY** - Don't commit, don't continue
2. Check git status:
   ```bash
   git status archive/versions/
   ```
3. Restore from git:
   ```bash
   git checkout -- archive/versions/unibos_v530_*/
   ```
4. If already committed but not pushed:
   ```bash
   git reset --hard HEAD~1
   ```
5. If pushed (LAST RESORT):
   ```bash
   # Contact senior developer
   # May need git reflog, revert, or force-push with caution
   ```

#### Scenario 3: Archive Completely Deleted
**If entire archive version was deleted:**

1. **CRITICAL** - Stop all operations
2. Check if in git:
   ```bash
   git status
   ```
3. If not committed, restore:
   ```bash
   git checkout -- archive/versions/unibos_v530_*/
   ```
4. If committed:
   ```bash
   git log --all --full-history -- archive/versions/unibos_v530_*/
   git checkout <commit-hash> -- archive/versions/unibos_v530_*/
   ```
5. If all else fails:
   - Check server backups
   - Check other development machines
   - Check .git/objects for orphaned blobs

---

## ✅ Pre-Operation Checklist

**Before ANY operation involving archives:**

- [ ] I am NOT modifying existing `archive/versions/*` directories
- [ ] If creating new archive, using `tools/scripts/unibos_version.sh`
- [ ] If editing `.archiveignore`, tested with dry-run first
- [ ] If analyzing archives, using read-only commands only
- [ ] I have read and understood this safety protocol
- [ ] I have a backup plan if something goes wrong
- [ ] I know how to restore from git if needed

---

## 📊 Monitoring & Verification

### Regular Checks (Monthly)
```bash
# Check archive integrity (file count)
find archive/versions/ -type f | wc -l

# Check no uncommitted changes in archives
git status archive/versions/

# Verify .archiveignore hasn't changed unexpectedly
git diff .archiveignore

# Check archive sizes haven't decreased (would indicate deletion)
du -sh archive/versions/* > /tmp/archive_sizes.txt
# Compare with previous month's sizes
```

### Automated Verification (Future)
```bash
# TODO: Create tools/scripts/verify_archive_integrity.sh
# - Check all versions present
# - Verify no modifications (git status)
# - Compare file counts with baseline
# - Alert if any issues detected
```

---

## 📚 Related Documents

- [VERSIONING_RULES.md](./VERSIONING_RULES.md) - Versioning system rules
- [VERSIONING_WORKFLOW.md](./VERSIONING_WORKFLOW.md) - Workflow guide
- [FUTURE_ROADMAP_v533.md](../../archive/planning/FUTURE_ROADMAP_v533.md) - Future plans

---

## 📝 Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2025-11-13 | Initial creation | Formalize archive safety protocol |

---

**Remember:** When in doubt, DON'T touch archive/versions/. Ask first.

**Emergency Contact:** If you're about to do something risky with archives, create an issue or ask for review first.

---

**Last Updated:** 2025-11-13
**Next Review:** 2025-12-13 (Monthly)
**Status:** Active Protocol
