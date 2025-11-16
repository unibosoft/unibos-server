# UNIBOS ARCHIVE PROTECTION RULES

**Created:** November 16, 2025
**Critical Priority:** MAXIMUM
**Status:** MANDATORY - STRICTLY ENFORCED

---

## ⚠️ CRITICAL WARNING

**THE ARCHIVE DIRECTORY CONTAINS IRREPLACEABLE HISTORICAL DATA**

Any loss of archive data is **UNACCEPTABLE** and considered a **CRITICAL INCIDENT**.

Archive data includes:
- 533+ version snapshots (v001-v533)
- Historical code evolution
- Development decisions and context
- CLAUDE_RULES documentation across versions
- Critical deployment configurations
- Database backups and schemas
- Production deployment history

---

## 1. ARCHIVE STRUCTURE

### Current Organization

```
/Users/berkhatirli/Desktop/unibos-dev/archive/
├── code/                           # Archived code snippets and experiments
├── data/                           # Archived data files
├── deprecated/                     # Deprecated but preserved functionality
├── development/                    # Development artifacts and tools
│   └── deployment/
│       └── deployment_scripts/
├── docs/                          # Archived documentation
├── ignore_files_backup_20251115/  # Backup of ignored files
├── planning/                      # Project planning and design docs
└── versions/                      # VERSION ARCHIVES (CRITICAL!)
    └── old_pattern_v001_v533/     # All versions v001-v533
        ├── analyze_versions.sh
        ├── unibos_v001_20250625_0041/
        ├── unibos_v002_20250625_0100/
        ├── ...
        └── unibos_v533_YYYYMMDD_HHMM/
```

### Version Naming Convention

```
unibos_vXXX_YYYYMMDD_HHMM/
       │    │        │
       │    │        └─ Time (24h format)
       │    └────────── Date
       └─────────────── Version number (3 digits, zero-padded)
```

---

## ⚠️ CRITICAL ISSUE DETECTED

**CURRENT STATUS: ARCHIVE IS IN .gitignore**

```bash
# Current .gitignore contains:
archive/
archive_backup*/
screenshots_archive/
archive/database_backups/
```

**THIS IS EXTREMELY DANGEROUS!**

Archive versions (v001-v533) are currently NOT protected by git. If deleted, they CANNOT be recovered from git history.

**IMMEDIATE ACTION REQUIRED:**
1. Review which parts of archive should be in git
2. Consider: Should version snapshots be git-tracked or externally backed up?
3. If git-tracked: Remove `archive/` from .gitignore and commit
4. If external: Setup robust external backup system IMMEDIATELY

**Current Risk Level:** 🔴 CRITICAL

---

## 2. ABSOLUTE PROHIBITIONS

### 🚫 NEVER DO THESE:

1. **NEVER delete any directory in `/archive/`**
   - Not even "empty" directories
   - Not even "old" versions
   - Not even "duplicate" versions

2. **NEVER move files out of `/archive/` without backup**
   - Always create backup first
   - Document the move in git commit
   - Keep original until verified

3. **NEVER modify files in `/archive/versions/`**
   - Archives are read-only historical records
   - Use copies for analysis
   - Never "fix" or "update" archived versions

4. **NEVER run cleanup scripts on `/archive/`**
   - No automated cleanup
   - No "temp file" removal
   - No "duplicate" detection

5. **NEVER add `/archive/` to `.gitignore`**
   - Archive must be version controlled
   - Every version matters
   - Git is our safety net

6. **NEVER use `rm -rf` near `/archive/`**
   - Use explicit file paths
   - Always use `-i` (interactive) flag
   - Verify target before deletion

---

## 3. MANDATORY PROTECTIONS

### File System Protection

```bash
# Make archive directories immutable (macOS/Linux)
# DO NOT RUN YET - for future hardening
# chflags -R uchg /Users/berkhatirli/Desktop/unibos-dev/archive/versions/

# Alternative: Make read-only
chmod -R a-w /Users/berkhatirli/Desktop/unibos-dev/archive/versions/
```

### Git Protection

```bash
# Archive must ALWAYS be tracked
git check-ignore archive/
# Should return: (nothing) - archive is NOT ignored

# Verify archive is in git
git ls-files archive/ | head -10
# Should show: archive files are tracked
```

### Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# UNIBOS Archive Protection Hook

# Check if any archive files are being deleted
DELETED_ARCHIVES=$(git diff --cached --name-status | grep "^D.*archive/" || true)

if [ ! -z "$DELETED_ARCHIVES" ]; then
    echo "❌ ERROR: Attempt to delete archive files detected!"
    echo ""
    echo "The following archive files are marked for deletion:"
    echo "$DELETED_ARCHIVES"
    echo ""
    echo "Archive deletions are STRICTLY PROHIBITED."
    echo "If you absolutely must remove these files, you must:"
    echo "  1. Document the reason in ARCHIVE_DELETIONS.md"
    echo "  2. Create a backup first"
    echo "  3. Get explicit approval"
    echo "  4. Use: git commit --no-verify (at your own risk)"
    echo ""
    exit 1
fi

# Check for large archive modifications
MODIFIED_ARCHIVES=$(git diff --cached --name-only | grep "^archive/" || true)
if [ ! -z "$MODIFIED_ARCHIVES" ]; then
    echo "⚠️  WARNING: Archive files are being modified:"
    echo "$MODIFIED_ARCHIVES"
    echo ""
    echo "Archives should be read-only. Are you sure about this?"
    echo "Press ENTER to continue or Ctrl+C to abort..."
    read
fi

exit 0
```

### Backup Strategy

1. **Local Backups**
   ```bash
   # Daily backup to external location
   rsync -av --delete \
     /Users/berkhatirli/Desktop/unibos-dev/archive/ \
     /Volumes/Backup/unibos-archive-$(date +%Y%m%d)/
   ```

2. **Git Remote Backups**
   ```bash
   # Ensure archive is pushed to remote
   git push origin main

   # Tag important archive states
   git tag -a archive-v533 -m "Archive state at v533"
   git push origin archive-v533
   ```

3. **Cloud Backups**
   - Consider using Git LFS for large archives
   - Multiple git remotes (GitHub, GitLab, Bitbucket)
   - Periodic exports to cloud storage

---

## 4. SAFE OPERATIONS

### ✅ Allowed Operations

1. **Reading Archive Files**
   ```bash
   # Safe - read-only access
   cat archive/versions/old_pattern_v001_v533/unibos_v533_*/VERSION.json
   ```

2. **Analyzing Archives**
   ```bash
   # Safe - creates temporary copies
   cp -r archive/versions/old_pattern_v001_v533/unibos_v533_* /tmp/analysis/
   ```

3. **Adding New Archives**
   ```bash
   # Safe - only adds, never removes
   cp -r /path/to/new/version archive/versions/unibos_v534_20251116_0800/
   git add archive/versions/unibos_v534_20251116_0800/
   git commit -m "Archive: Add v534 snapshot"
   ```

4. **Creating Archive Indexes**
   ```bash
   # Safe - creates metadata without modifying archives
   ls -lh archive/versions/old_pattern_v001_v533/ > archive/versions/INDEX.txt
   ```

### Archive Access Pattern

```python
# Python example for safe archive access
from pathlib import Path
import shutil

ARCHIVE_ROOT = Path("/Users/berkhatirli/Desktop/unibos-dev/archive")
ARCHIVE_VERSIONS = ARCHIVE_ROOT / "versions" / "old_pattern_v001_v533"

# SAFE: Read-only access
def get_version_info(version_num):
    version_dir = ARCHIVE_VERSIONS / f"unibos_v{version_num:03d}_*"
    versions = list(ARCHIVE_VERSIONS.glob(f"unibos_v{version_num:03d}_*"))
    if versions:
        version_path = versions[0]
        version_file = version_path / "VERSION.json"
        if version_file.exists():
            return version_file.read_text()
    return None

# SAFE: Create working copy
def copy_version_for_analysis(version_num, dest_dir):
    versions = list(ARCHIVE_VERSIONS.glob(f"unibos_v{version_num:03d}_*"))
    if versions:
        src = versions[0]
        dest = Path(dest_dir) / src.name
        shutil.copytree(src, dest)  # Copy, don't move!
        return dest
    return None

# UNSAFE: Never modify originals
# ❌ def update_version(version_num): ...  # NO!
```

---

## 5. RECOVERY PROCEDURES

### If Archive Data is Lost

1. **IMMEDIATE ACTIONS**
   ```bash
   # Stop all operations
   # Do NOT commit anything
   # Do NOT run cleanup

   # Check git status
   git status

   # Check if files are staged for deletion
   git diff --cached --name-status | grep "^D.*archive/"

   # If files are staged, unstage them
   git reset HEAD archive/

   # Restore from git if deleted
   git checkout -- archive/
   ```

2. **Recovery from Git History**
   ```bash
   # Find last good commit
   git log --oneline --all -- archive/ | head -20

   # Restore from specific commit
   git checkout <commit-hash> -- archive/

   # Create recovery branch
   git checkout -b archive-recovery-$(date +%Y%m%d)
   git add archive/
   git commit -m "RECOVERY: Restore lost archive data"
   ```

3. **Recovery from Backups**
   ```bash
   # From local backup
   rsync -av /Volumes/Backup/unibos-archive-20251116/ \
     /Users/berkhatirli/Desktop/unibos-dev/archive/

   # Verify integrity
   diff -r archive/ /Volumes/Backup/unibos-archive-20251116/
   ```

4. **Report Incident**
   - Document what was lost
   - How it was recovered
   - Update this document with lessons learned
   - Add additional protections if needed

---

## 6. VERIFICATION PROCEDURES

### Daily Checks

```bash
#!/bin/bash
# archive_daily_check.sh

ARCHIVE_ROOT="/Users/berkhatirli/Desktop/unibos-dev/archive"

echo "🔍 Archive Daily Health Check - $(date)"
echo "================================================"

# Check archive exists
if [ ! -d "$ARCHIVE_ROOT" ]; then
    echo "❌ CRITICAL: Archive directory missing!"
    exit 1
fi

# Count version directories
VERSION_COUNT=$(find "$ARCHIVE_ROOT/versions/old_pattern_v001_v533" -maxdepth 1 -type d -name "unibos_v*" | wc -l)
echo "📦 Version Archives: $VERSION_COUNT"

if [ $VERSION_COUNT -lt 533 ]; then
    echo "⚠️  WARNING: Expected ~533 versions, found $VERSION_COUNT"
fi

# Check for git tracking
GIT_TRACKED=$(git ls-files archive/ | wc -l)
echo "📝 Files tracked in git: $GIT_TRACKED"

if [ $GIT_TRACKED -eq 0 ]; then
    echo "❌ CRITICAL: Archive not in git!"
    exit 1
fi

# Check for recent modifications
RECENT_MODS=$(find "$ARCHIVE_ROOT/versions" -type f -mtime -1 | wc -l)
if [ $RECENT_MODS -gt 0 ]; then
    echo "⚠️  WARNING: $RECENT_MODS archive files modified in last 24h"
    find "$ARCHIVE_ROOT/versions" -type f -mtime -1
fi

# Calculate total size
TOTAL_SIZE=$(du -sh "$ARCHIVE_ROOT" | cut -f1)
echo "💾 Total Archive Size: $TOTAL_SIZE"

echo "================================================"
echo "✅ Daily check complete"
```

### Weekly Verification

```bash
# Create checksum manifest
find archive/ -type f -exec md5 {} \; > archive/CHECKSUMS.txt
git add archive/CHECKSUMS.txt
git commit -m "Archive: Update weekly checksums"

# Verify no unexpected changes
git diff HEAD~1 archive/CHECKSUMS.txt
```

---

## 7. DOCUMENTATION REQUIREMENTS

### When Adding Archives

Every archive addition must include:

1. **Git Commit Message Format**
   ```
   Archive: Add v<version> - <brief description>

   - Version: v<version>
   - Date: YYYY-MM-DD HH:MM
   - Build: YYYYMMDD_HHMM
   - Size: XX MB
   - Changes: <what's new in this version>
   - Reason: <why this version was archived>

   Archive Structure:
   - Core files: <count>
   - Module files: <count>
   - Total size: XX MB
   ```

2. **Archive Metadata File**
   Create `archive/versions/unibos_vXXX_*/ARCHIVE_INFO.md`:
   ```markdown
   # Archive Information: v<version>

   ## Version Details
   - Version: v<version>
   - Build: YYYYMMDD_HHMM
   - Date: YYYY-MM-DD HH:MM
   - Author: <name>
   - Location: <where it was created>

   ## Archive Contents
   - Source files: <list major directories>
   - Documentation: <what docs are included>
   - Database: <if SQL dumps included>
   - Configuration: <key config files>

   ## Why Archived
   <Explanation of why this version was preserved>

   ## Known Issues
   <Any known issues in this version>

   ## Important Notes
   <Any special notes about this archive>
   ```

---

## 8. INTEGRATION WITH EXISTING RULES

### Relationship to VERSIONING_RULES.md

- Archive rules are COMPLEMENTARY to versioning rules
- VERSIONING_RULES.md defines how to CREATE versions
- ARCHIVE_PROTECTION_RULES.md defines how to PRESERVE versions

### Integration Points

```markdown
# In VERSIONING_RULES.md - add section:

## Archive Integration

After creating a new version:
1. Follow VERSION.json update procedure
2. Create archive snapshot
3. Follow ARCHIVE_PROTECTION_RULES.md
4. Verify archive integrity
5. Commit with proper archive metadata

See: docs/ARCHIVE_PROTECTION_RULES.md
```

---

## 9. AUTOMATION SAFEGUARDS

### Scripts Must Check Archive

```bash
#!/bin/bash
# Example: Any script that touches files

ARCHIVE_ROOT="/Users/berkhatirli/Desktop/unibos-dev/archive"

# Check if path touches archive
if [[ "$TARGET_PATH" == *"$ARCHIVE_ROOT"* ]]; then
    echo "❌ ERROR: This script is attempting to modify archive!"
    echo "Target: $TARGET_PATH"
    echo "Archive modifications require manual review."
    exit 1
fi
```

### CI/CD Protections

```yaml
# .github/workflows/archive-protection.yml
name: Archive Protection

on: [push, pull_request]

jobs:
  protect-archive:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check Archive Deletions
        run: |
          DELETED=$(git diff --name-status HEAD~1 HEAD | grep "^D.*archive/" || true)
          if [ ! -z "$DELETED" ]; then
            echo "❌ Archive deletion detected!"
            echo "$DELETED"
            exit 1
          fi

      - name: Check Archive Modifications
        run: |
          MODIFIED=$(git diff --name-only HEAD~1 HEAD | grep "^archive/versions/" || true)
          if [ ! -z "$MODIFIED" ]; then
            echo "⚠️  Archive modification detected (should be rare):"
            echo "$MODIFIED"
          fi
```

---

## 10. EDUCATION & AWARENESS

### For All Developers

**BEFORE touching ANYTHING in `/archive/`:**

1. ✋ **STOP** - Think twice
2. 📖 **READ** - This document completely
3. 🤔 **ASK** - Is this really necessary?
4. 💾 **BACKUP** - Create backup first
5. 📝 **DOCUMENT** - Record what and why
6. ✅ **VERIFY** - Check nothing was lost

### Common Mistakes to Avoid

❌ **"I'll just clean up these old files..."**
✅ Archives are NOT "old files" - they're historical records

❌ **"This directory looks empty..."**
✅ Even "empty" directories may have historical significance

❌ **"I'll reorganize the archive for better structure..."**
✅ Archive structure is frozen - create NEW organization elsewhere

❌ **"Let me fix this bug in the archived version..."**
✅ Archives are read-only - fix in current code, not history

❌ **"I'll remove duplicates to save space..."**
✅ "Duplicates" may be intentional snapshots at different times

---

## 11. EMERGENCY CONTACTS

### If Archive is Compromised

1. **Immediately notify:**
   - Project lead: Berk Hatırlı
   - Create incident report in git
   - Document extent of damage

2. **Do NOT:**
   - Continue working
   - Commit changes
   - Run any more scripts
   - "Try to fix it" without assessment

3. **Preserve evidence:**
   ```bash
   # Create incident snapshot
   git status > incident-$(date +%Y%m%d-%H%M%S).txt
   git log --oneline -20 >> incident-$(date +%Y%m%d-%H%M%S).txt
   git diff >> incident-$(date +%Y%m%d-%H%M%S).txt
   ```

---

## 12. FUTURE ENHANCEMENTS

### Planned Improvements

- [ ] Implement archive encryption
- [ ] Setup automated off-site backups
- [ ] Create archive integrity monitoring
- [ ] Build archive search/query tools
- [ ] Implement archive compression (carefully!)
- [ ] Create archive access audit log
- [ ] Setup automated checksum verification

### Research Items

- [ ] Git LFS for large archive files
- [ ] Deduplicated storage for archives
- [ ] Read-only file system for archive mount
- [ ] Blockchain-style integrity verification

---

## CONCLUSION

**THE ARCHIVE IS SACRED**

Every version snapshot represents:
- Hours of development work
- Critical decision points
- Working configurations
- Irreplaceable historical context

**When in doubt, DO NOT delete, modify, or move archive files.**

**It is ALWAYS better to ask first.**

---

**Document Version:** 1.0
**Last Updated:** November 16, 2025
**Next Review:** Weekly
**Status:** ACTIVE - MANDATORY COMPLIANCE
