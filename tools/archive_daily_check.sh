#!/bin/bash
# UNIBOS Archive Daily Health Check
# Verifies archive integrity and alerts on any issues

ARCHIVE_ROOT="/Users/berkhatirli/Desktop/unibos-dev/archive"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "🔍 UNIBOS Archive Daily Health Check"
echo "================================================"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Location: $ARCHIVE_ROOT"
echo ""

# Check 1: Archive directory exists
echo -n "1. Archive directory exists... "
if [ ! -d "$ARCHIVE_ROOT" ]; then
    echo -e "${RED}❌ CRITICAL: Archive directory missing!${NC}"
    exit 1
else
    echo -e "${GREEN}✓${NC}"
fi

# Check 2: Version archives directory exists
echo -n "2. Version archives directory... "
if [ ! -d "$ARCHIVE_ROOT/versions/old_pattern_v001_v533" ]; then
    echo -e "${RED}❌ CRITICAL: Version archives missing!${NC}"
    exit 1
else
    echo -e "${GREEN}✓${NC}"
fi

# Check 3: Count version directories
echo -n "3. Counting version archives... "
VERSION_COUNT=$(find "$ARCHIVE_ROOT/versions/old_pattern_v001_v533" -maxdepth 1 -type d -name "unibos_v*" 2>/dev/null | wc -l | xargs)
echo "$VERSION_COUNT found"

if [ $VERSION_COUNT -lt 100 ]; then
    echo -e "   ${RED}❌ CRITICAL: Too few versions! Expected 533+${NC}"
    exit 1
elif [ $VERSION_COUNT -lt 533 ]; then
    echo -e "   ${YELLOW}⚠️  WARNING: Expected ~533 versions${NC}"
fi

# Check 4: Git tracking status
echo -n "4. Checking git tracking... "
if git ls-files --error-unmatch "$ARCHIVE_ROOT" &>/dev/null; then
    GIT_TRACKED=$(git ls-files archive/ | wc -l | xargs)
    echo -e "${GREEN}✓${NC} ($GIT_TRACKED files tracked)"
else
    echo -e "${RED}❌ CRITICAL: Archive not tracked in git!${NC}"
    echo -e "   ${YELLOW}Archive is in .gitignore - NOT PROTECTED!${NC}"
fi

# Check 5: Recent modifications (suspicious)
echo -n "5. Checking for recent modifications... "
RECENT_MODS=$(find "$ARCHIVE_ROOT/versions" -type f -mtime -1 2>/dev/null | wc -l | xargs)
if [ $RECENT_MODS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  WARNING: $RECENT_MODS files modified in last 24h${NC}"
    echo "   Recently modified files:"
    find "$ARCHIVE_ROOT/versions" -type f -mtime -1 2>/dev/null | head -5 | sed 's/^/   /'
    if [ $RECENT_MODS -gt 5 ]; then
        echo "   ... and $(($RECENT_MODS - 5)) more"
    fi
else
    echo -e "${GREEN}✓${NC} (no recent changes)"
fi

# Check 6: Calculate total size
echo -n "6. Archive size... "
TOTAL_SIZE=$(du -sh "$ARCHIVE_ROOT" 2>/dev/null | cut -f1)
echo "$TOTAL_SIZE"

# Check 7: Verify critical subdirectories
echo -n "7. Critical subdirectories... "
CRITICAL_DIRS=("code" "data" "development" "docs" "planning" "versions")
MISSING_DIRS=()

for dir in "${CRITICAL_DIRS[@]}"; do
    if [ ! -d "$ARCHIVE_ROOT/$dir" ]; then
        MISSING_DIRS+=("$dir")
    fi
done

if [ ${#MISSING_DIRS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  WARNING: Missing directories${NC}"
    for dir in "${MISSING_DIRS[@]}"; do
        echo "   - $dir"
    done
else
    echo -e "${GREEN}✓${NC} (all present)"
fi

# Check 8: Verify VERSIONING_RULES.md exists
echo -n "8. Archive protection docs... "
if [ -f "$ARCHIVE_ROOT/../docs/ARCHIVE_PROTECTION_RULES.md" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠️  ARCHIVE_PROTECTION_RULES.md not found${NC}"
fi

# Summary
echo ""
echo "================================================"
echo "📊 Summary"
echo "================================================"
echo "Total Versions: $VERSION_COUNT"
echo "Total Size: $TOTAL_SIZE"
echo "Git Status: $([ -n "$GIT_TRACKED" ] && echo "Tracked ($GIT_TRACKED files)" || echo "NOT TRACKED ⚠️")"
echo "Recent Changes: $RECENT_MODS files"
echo ""

# Overall status
if [ $VERSION_COUNT -ge 500 ] && [ $RECENT_MODS -eq 0 ]; then
    echo -e "${GREEN}✅ Archive health: GOOD${NC}"
    exit 0
elif [ $VERSION_COUNT -lt 100 ]; then
    echo -e "${RED}❌ Archive health: CRITICAL${NC}"
    exit 1
else
    echo -e "${YELLOW}⚠️  Archive health: NEEDS ATTENTION${NC}"
    exit 0
fi
