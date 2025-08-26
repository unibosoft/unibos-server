#!/bin/bash
# Verify that rocksteady has the latest code

echo "🔍 Verifying code sync with rocksteady..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check connection
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes rocksteady echo "connected" >/dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to rocksteady${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Connected to rocksteady${NC}"
echo ""

# Compare key files
echo "Comparing key files..."
echo "========================"

# 1. Check VERSION.json
echo ""
echo "VERSION.json:"
LOCAL_VERSION=$(cat VERSION.json 2>/dev/null | grep version | cut -d'"' -f4)
REMOTE_VERSION=$(ssh rocksteady 'cat ~/unibos/VERSION.json 2>/dev/null | grep version | cut -d"\"" -f4')
if [ "$LOCAL_VERSION" = "$REMOTE_VERSION" ]; then
    echo -e "  Local:  ${GREEN}$LOCAL_VERSION${NC}"
    echo -e "  Remote: ${GREEN}$REMOTE_VERSION${NC} ✅"
else
    echo -e "  Local:  ${GREEN}$LOCAL_VERSION${NC}"
    echo -e "  Remote: ${RED}$REMOTE_VERSION${NC} ❌ MISMATCH!"
fi

# 2. Check public_server_menu_proper.py exists
echo ""
echo "Public Server Menu:"
if ssh rocksteady '[ -f ~/unibos/src/public_server_menu_proper.py ]'; then
    echo -e "  ${GREEN}✅ public_server_menu_proper.py exists${NC}"
    
    # Check file size
    LOCAL_SIZE=$(wc -c < src/public_server_menu_proper.py 2>/dev/null)
    REMOTE_SIZE=$(ssh rocksteady 'wc -c < ~/unibos/src/public_server_menu_proper.py 2>/dev/null')
    echo "  File size: Local=$LOCAL_SIZE bytes, Remote=$REMOTE_SIZE bytes"
    
    # Check if it has the new functions
    if ssh rocksteady 'grep -q "def full_deployment" ~/unibos/src/public_server_menu_proper.py'; then
        echo -e "  ${GREEN}✅ Has full_deployment function${NC}"
    else
        echo -e "  ${RED}❌ Missing full_deployment function${NC}"
    fi
else
    echo -e "  ${RED}❌ public_server_menu_proper.py NOT FOUND${NC}"
fi

# 3. Check main.py
echo ""
echo "Main CLI:"
LOCAL_MAIN_LINES=$(wc -l < src/main.py 2>/dev/null)
REMOTE_MAIN_LINES=$(ssh rocksteady 'wc -l < ~/unibos/src/main.py 2>/dev/null')
echo "  main.py lines: Local=$LOCAL_MAIN_LINES, Remote=$REMOTE_MAIN_LINES"

# 4. Check backend files
echo ""
echo "Backend:"
if ssh rocksteady '[ -f ~/unibos/backend/requirements_minimal.txt ]'; then
    echo -e "  ${GREEN}✅ requirements_minimal.txt exists${NC}"
else
    echo -e "  ${YELLOW}⚠️  requirements_minimal.txt missing (may use fallback)${NC}"
fi

# 5. Check deployment scripts
echo ""
echo "Deployment Scripts:"
for script in rocksteady_deploy.sh rocksteady_config.sh; do
    if ssh rocksteady "[ -f ~/unibos/$script ]"; then
        echo -e "  ${GREEN}✅ $script exists${NC}"
    else
        echo -e "  ${YELLOW}⚠️  $script missing${NC}"
    fi
done

# 6. Compare modification times
echo ""
echo "Last Modified Times:"
echo "===================="
LOCAL_MODIFIED=$(stat -f "%Sm" src/public_server_menu_proper.py 2>/dev/null || stat -c "%y" src/public_server_menu_proper.py 2>/dev/null)
REMOTE_MODIFIED=$(ssh rocksteady 'stat -c "%y" ~/unibos/src/public_server_menu_proper.py 2>/dev/null || echo "unknown"')
echo "  Local:  $LOCAL_MODIFIED"
echo "  Remote: $REMOTE_MODIFIED"

# 7. Check if rsync would transfer files
echo ""
echo "Files that need syncing:"
echo "========================"
NEED_SYNC=$(rsync -avzn --exclude={.git,venv,__pycache__,archive,quarantine,*.sql,*.log,db.sqlite3,.DS_Store} . rocksteady:~/unibos/ | grep -v "^$" | grep -v "sending incremental" | grep -v "sent" | grep -v "total size" | head -20)
if [ -z "$NEED_SYNC" ]; then
    echo -e "${GREEN}✅ All files are up to date${NC}"
else
    echo -e "${YELLOW}⚠️  These files need syncing:${NC}"
    echo "$NEED_SYNC"
fi

echo ""
echo "========================"
echo "Summary:"
if [ "$LOCAL_VERSION" = "$REMOTE_VERSION" ] && [ -z "$NEED_SYNC" ]; then
    echo -e "${GREEN}✅ Rocksteady is up to date with local code${NC}"
else
    echo -e "${RED}❌ Rocksteady needs to be synced${NC}"
    echo ""
    echo "To sync now, run:"
    echo -e "${BLUE}  rsync -avz --exclude={.git,venv,__pycache__,archive,quarantine,*.sql,*.log,db.sqlite3,.DS_Store} . rocksteady:~/unibos/${NC}"
fi