#!/bin/bash
# Start UNIBOS server on rocksteady

echo "🚀 Starting UNIBOS server on rocksteady..."

# Check connection
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes rocksteady echo "connected" >/dev/null 2>&1; then
    echo "❌ Cannot connect to rocksteady"
    echo "Please load your SSH key first:"
    echo "  ssh-add ~/.ssh/rocksteady-2025"
    exit 1
fi

echo "✅ Connected to rocksteady"

# Stop any existing server
echo "Stopping old server..."
ssh rocksteady 'pkill -f "manage.py runserver" 2>/dev/null || true'

# Start the server
echo "Starting new server..."
ssh rocksteady << 'EOF'
cd ~/unibos/backend

# Check if venv exists
if [ ! -d venv ]; then
    echo "❌ Virtual environment not found. Run full deployment first."
    exit 1
fi

# Start server in background
echo "Starting Django server on port 8000..."
nohup ./venv/bin/python manage.py runserver 0.0.0.0:8000 > logs/server.log 2>&1 &

# Wait and check if it started
sleep 3
if pgrep -f "manage.py runserver" > /dev/null; then
    echo "✅ Server started successfully!"
    echo "Access at: http://rocksteady:8000"
    echo "Logs at: ~/unibos/apps/web/backend/logs/server.log"
else
    echo "❌ Server failed to start"
    echo "Check logs: ssh rocksteady 'tail -n 50 ~/unibos/apps/web/backend/logs/server.log'"
fi
EOF

echo "Done!"