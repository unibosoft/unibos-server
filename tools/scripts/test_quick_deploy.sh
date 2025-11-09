#!/bin/bash
# Test Quick Deploy and Service Restart

echo "🧪 Testing Quick Deploy Service Restart"
echo "========================================"

# Get initial service start times
echo "📊 Initial service status:"
INITIAL_DAPHNE=$(ssh rocksteady "systemctl show daphne --property=ActiveEnterTimestamp" 2>/dev/null | cut -d= -f2)
INITIAL_NGINX=$(ssh rocksteady "systemctl show nginx --property=ActiveEnterTimestamp" 2>/dev/null | cut -d= -f2)

echo "  Daphne started: $INITIAL_DAPHNE"
echo "  Nginx started: $INITIAL_NGINX"
echo ""

# Create a test file to verify sync
echo "# Test comment added at $(date)" >> apps/cli/src/main.py

echo "📦 Running quick deploy..."
python3 << 'EOF'
import sys
sys.path.append('.')
from src.public_server_menu import PublicServerMenu
import subprocess

menu = PublicServerMenu()

# Simulate quick deploy steps
print("  1. Backing up remote settings...")
backup_cmd = "ssh rocksteady 'cd ~/unibos/apps/web/backend && cp -f unibos_apps/web/backend/settings/production.py /tmp/prod_bak.py 2>/dev/null; cp -f .env /tmp/env_bak 2>/dev/null'"
subprocess.run(backup_cmd, shell=True, capture_output=True)

print("  2. Syncing files...")
rsync_cmd = "rsync -avz --exclude-from=.rsyncignore . rocksteady:~/unibos/"
result = subprocess.run(rsync_cmd, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    print("  ✅ Files synced")
    
    print("  3. Restoring settings...")
    restore_cmd = "ssh rocksteady 'cd ~/unibos/apps/web/backend && [ -f /tmp/prod_bak.py ] && cp -f /tmp/prod_bak.py unibos_apps/web/backend/settings/production.py; [ -f /tmp/env_bak ] && cp -f /tmp/env_bak .env'"
    subprocess.run(restore_cmd, shell=True, capture_output=True)
    
    print("  4. Restarting services...")
    restart_cmd = "ssh rocksteady 'sudo systemctl restart daphne && sudo systemctl reload nginx'"
    result = subprocess.run(restart_cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print("  ✅ Services restarted")
    else:
        print("  ❌ Service restart failed")
        print(result.stderr)
else:
    print("  ❌ Sync failed")
EOF

# Remove test comment
sed -i '' '/# Test comment added at/d' apps/cli/src/main.py 2>/dev/null || sed -i '/# Test comment added at/d' apps/cli/src/main.py

echo ""
echo "⏳ Waiting for services to stabilize..."
sleep 3

# Check new service start times
echo ""
echo "📊 Final service status:"
FINAL_DAPHNE=$(ssh rocksteady "systemctl show daphne --property=ActiveEnterTimestamp" 2>/dev/null | cut -d= -f2)
FINAL_NGINX=$(ssh rocksteady "systemctl show nginx --property=ActiveEnterTimestamp" 2>/dev/null | cut -d= -f2)

echo "  Daphne started: $FINAL_DAPHNE"
echo "  Nginx started: $FINAL_NGINX"

echo ""
echo "🔍 Verification:"

if [ "$INITIAL_DAPHNE" != "$FINAL_DAPHNE" ]; then
    echo "  ✅ Daphne was restarted"
else
    echo "  ❌ Daphne was NOT restarted"
fi

if [ "$INITIAL_NGINX" != "$FINAL_NGINX" ]; then
    echo "  ✅ Nginx was restarted/reloaded"
else
    echo "  ⚠️  Nginx was not restarted (may have been reloaded)"
fi

# Test web accessibility
echo ""
echo "🌐 Testing web access:"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://recaria.org)

if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ]; then
    echo "  ✅ Website is accessible (HTTP $HTTP_STATUS)"
else
    echo "  ❌ Website returned HTTP $HTTP_STATUS"
fi

echo ""
echo "✅ Test complete!"