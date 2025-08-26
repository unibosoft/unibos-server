#!/bin/bash
# UNIBOS One-Liner Deployment Commands

echo "🚀 UNIBOS One-Liner Deployment Options:"
echo ""
echo "1️⃣  Quick Deploy (uploads current directory and runs unibos.sh):"
echo ""
echo 'rsync -avz --exclude=".git" --exclude="__pycache__" --exclude="venv" --exclude="node_modules" --exclude="*.log" --exclude="archive/versions" . rocksteady:~/unibos/ && ssh rocksteady "cd ~/unibos && chmod +x unibos.sh && ./unibos.sh"'
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "2️⃣  Deploy with backup (backs up existing installation):"
echo ""
echo 'ssh rocksteady "[ -d ~/unibos ] && mv ~/unibos ~/unibos_backup_$(date +%Y%m%d_%H%M%S) || true" && rsync -avz --exclude=".git" --exclude="__pycache__" --exclude="venv" . rocksteady:~/unibos/ && ssh rocksteady "cd ~/unibos && ./unibos.sh"'
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "3️⃣  Ultra-compact one-liner (minimal output):"
echo ""
echo 'rsync -qaz --exclude={.git,__pycache__,venv,node_modules,*.log} . rocksteady:~/unibos/ && ssh rocksteady "cd ~/unibos && ./unibos.sh" 2>/dev/null'
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "4️⃣  Deploy only backend (Django):"
echo ""
echo 'rsync -avz backend/ rocksteady:~/unibos/backend/ && ssh rocksteady "cd ~/unibos/backend && source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate && pip install -q -r requirements.txt && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"'
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "5️⃣  Deploy only CLI:"
echo ""
echo 'rsync -avz src/ rocksteady:~/unibos/src/ && ssh rocksteady "cd ~/unibos/src && python3 main.py"'
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "6️⃣  Deploy and run in background (with nohup):"
echo ""
echo 'rsync -qaz --exclude={.git,__pycache__,venv} . rocksteady:~/unibos/ && ssh rocksteady "cd ~/unibos && nohup ./unibos.sh > /tmp/unibos.log 2>&1 &" && echo "✅ Deployed! Logs: ssh rocksteady tail -f /tmp/unibos.log"'
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "7️⃣  Deploy with systemd service (production):"
echo ""
echo 'rsync -avz . rocksteady:~/unibos/ && ssh rocksteady "cd ~/unibos && sudo cp backend/unibos.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl restart unibos && sudo systemctl status unibos"'
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "🔧 Helper Commands:"
echo ""
echo "Check if running:"
echo '  ssh rocksteady "ps aux | grep -E \"python.*(main|manage)\" | grep -v grep"'
echo ""
echo "Kill existing processes:"
echo '  ssh rocksteady "pkill -f \"python.*(main|manage)\""'
echo ""
echo "View logs:"
echo '  ssh rocksteady "tail -f /tmp/unibos.log"'
echo ""
echo "Quick restart:"
echo '  ssh rocksteady "cd ~/unibos && pkill -f unibos; ./unibos.sh"'
echo ""
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "📝 Copy and paste any command above to deploy!"