#!/bin/bash
# Rocksteady Server Monitor Script
# This script collects system information from rocksteady

SERVER="rocksteady"

echo "=== ROCKSTEADY MONITOR ==="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Test SSH connection
echo -n "SSH Connection: "
if ssh -o ConnectTimeout=2 -o BatchMode=yes $SERVER "echo 'OK'" &>/dev/null; then
    echo "✓ Connected"
    CONNECTION=true
else
    echo "✗ Failed"
    CONNECTION=false
    exit 1
fi

if [ "$CONNECTION" = true ]; then
    echo ""
    echo "=== SYSTEM INFO ==="
    ssh $SERVER "hostname"
    ssh $SERVER "uname -a | cut -d' ' -f1-3"
    ssh $SERVER "uptime -p"
    
    echo ""
    echo "=== RESOURCES ==="
    ssh $SERVER "free -h | grep Mem"
    ssh $SERVER "df -h / | tail -1"
    
    echo ""
    echo "=== SERVICES ==="
    
    # Check Django
    echo -n "Django Backend: "
    if ssh $SERVER "pgrep -f 'manage.py runserver' > /dev/null"; then
        echo "✓ Running"
        ssh $SERVER "ps aux | grep 'manage.py runserver' | grep -v grep | head -1"
    else
        echo "✗ Stopped"
    fi
    
    # Check PostgreSQL
    echo -n "PostgreSQL: "
    if ssh $SERVER "pg_isready -q 2>/dev/null"; then
        echo "✓ Running"
    else
        echo "? Unknown"
    fi
    
    # Check UNIBOS directory
    echo ""
    echo "=== DEPLOYMENT ==="
    echo -n "UNIBOS Path: "
    if ssh $SERVER "[ -d ~/unibos ] && echo 'exists'"; then
        echo "~/unibos ✓"
        # Get last modification time
        ssh $SERVER "stat -c 'Last Update: %y' ~/unibos/manage.py 2>/dev/null | cut -d'.' -f1"
        # Count Python files
        FILE_COUNT=$(ssh $SERVER "find ~/unibos -name '*.py' 2>/dev/null | wc -l")
        echo "Python Files: $FILE_COUNT"
    else
        echo "~/unibos ✗ Not found"
    fi
    
    # Check ports
    echo ""
    echo "=== NETWORK ==="
    echo "Open Ports:"
    ssh $SERVER "ss -tlnp 2>/dev/null | grep LISTEN | grep -E ':8000|:5432|:22' | awk '{print \$4}' | sed 's/.*:/Port /' | sort -u"
fi