#!/bin/bash
# UNIBOS One-Line Deployment to Rocksteady
# Usage: ./deploy_to_rocksteady.sh

set -e

echo "🚀 Deploying UNIBOS to rocksteady..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${YELLOW}📦 Creating deployment package...${NC}"

# Create a temporary directory for clean deployment
TEMP_DIR=$(mktemp -d)
DEPLOY_NAME="unibos_deploy_$(date +%Y%m%d_%H%M%S)"

# Copy necessary files (excluding unnecessary ones)
rsync -av --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='.venv' \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='db.sqlite3' \
    --exclude='.DS_Store' \
    --exclude='archive/versions' \
    --exclude='data_db/backups' \
    --exclude='quarantine' \
    --exclude='*.sql' \
    "$SCRIPT_DIR/" "$TEMP_DIR/$DEPLOY_NAME/"

# Create deployment archive
cd "$TEMP_DIR"
tar czf "${DEPLOY_NAME}.tar.gz" "$DEPLOY_NAME"

echo -e "${YELLOW}📤 Uploading to rocksteady...${NC}"

# Upload to rocksteady
scp "${DEPLOY_NAME}.tar.gz" rocksteady:/tmp/

echo -e "${YELLOW}🔧 Deploying on rocksteady...${NC}"

# Deploy and run on rocksteady
ssh rocksteady << 'ENDSSH'
set -e

echo "📂 Extracting deployment package..."
cd /home/$(whoami)
rm -rf unibos_backup
if [ -d "unibos" ]; then
    mv unibos unibos_backup
fi

tar xzf /tmp/unibos_deploy_*.tar.gz
mv unibos_deploy_* unibos

cd unibos

echo "🔧 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo "📦 Installing CLI dependencies..."
cd src
pip install -q --upgrade pip
pip install -q -r requirements.txt 2>/dev/null || true

echo "📦 Installing backend dependencies..."
cd ../backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt 2>/dev/null || true

echo "🗄️ Setting up database..."
python manage.py migrate --noinput 2>/dev/null || true
python manage.py collectstatic --noinput 2>/dev/null || true

# Create superuser if not exists
python manage.py shell << PYTHON
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@unibos.local', 'unibos2025')
    print("✅ Admin user created: admin/unibos2025")
else:
    print("✅ Admin user already exists")
PYTHON

echo "🚀 Starting UNIBOS..."
cd ..

# Kill any existing unibos processes
pkill -f "python.*unibos" 2>/dev/null || true
pkill -f "python.*manage.py runserver" 2>/dev/null || true

# Make unibos.sh executable
chmod +x unibos.sh

# Start UNIBOS in background
nohup ./unibos.sh > /tmp/unibos.log 2>&1 &

echo "✅ UNIBOS deployed and started!"
echo "📋 Logs: tail -f /tmp/unibos.log"
echo "🌐 Access at: http://$(hostname -I | awk '{print $1}'):8000"

# Clean up
rm -f /tmp/unibos_deploy_*.tar.gz
ENDSSH

# Clean up local temp files
rm -rf "$TEMP_DIR"

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}🌐 UNIBOS is now running on rocksteady${NC}"
echo ""
echo "To check status:"
echo "  ssh rocksteady 'ps aux | grep unibos'"
echo ""
echo "To view logs:"
echo "  ssh rocksteady 'tail -f /tmp/unibos.log'"
echo ""
echo "To restart:"
echo "  ssh rocksteady 'cd ~/unibos && ./unibos.sh'"