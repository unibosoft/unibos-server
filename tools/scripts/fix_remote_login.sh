#!/bin/bash
# Fix remote login issues on rocksteady

echo "🔧 Fixing remote authentication on rocksteady..."

# 1. Check current users in remote database
echo ""
echo "📊 Checking users in remote database..."
ssh rocksteady << 'EOF'
PGPASSWORD=unibos_password psql -h localhost -U unibos_user -d unibos_central -c "
SELECT username, is_active, is_superuser, last_login 
FROM auth_user 
ORDER BY date_joined DESC 
LIMIT 10;
"
EOF

# 2. Create berkhatirli user directly on remote if not exists
echo ""
echo "👤 Ensuring berkhatirli user exists..."
ssh rocksteady << 'EOF'
cd ~/unibos/backend

# Create user via Django shell
./venv/bin/python << PYTHON
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.production')
django.setup()

from django.contrib.auth.models import User

try:
    user = User.objects.get(username='berkhatirli')
    print(f"✓ User berkhatirli already exists (active: {user.is_active})")
    # Update password just in case
    user.set_password('unibos123')
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print("✓ Password reset to: unibos123")
except User.DoesNotExist:
    user = User.objects.create_superuser(
        username='berkhatirli',
        email='berk@unibos.com',
        password='unibos123'
    )
    print("✓ Created superuser berkhatirli with password: unibos123")
PYTHON
EOF

# 3. Check Redis status
echo ""
echo "🔴 Checking Redis status..."
ssh rocksteady << 'EOF'
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is running"
else
    echo "✗ Redis is not running - starting it..."
    sudo systemctl start redis-server || sudo service redis-server start
    sleep 2
    if redis-cli ping > /dev/null 2>&1; then
        echo "✓ Redis started successfully"
    else
        echo "✗ Failed to start Redis - sessions won't work!"
    fi
fi
EOF

# 4. Check Django settings
echo ""
echo "⚙️ Checking Django settings..."
ssh rocksteady << 'EOF'
cd ~/unibos/backend

# Check if production.py has correct session settings
if grep -q "SESSION_COOKIE_SECURE = False" unibos_apps/web/backend/settings/production.py; then
    echo "✓ Session cookies configured for HTTP"
else
    echo "✗ Fixing session cookie settings..."
    cat >> unibos_apps/web/backend/settings/production.py << 'SETTINGS'

# HTTP Session Settings
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SAMESITE = 'Lax'
SETTINGS
    echo "✓ Session settings fixed"
fi
EOF

# 5. Restart Django
echo ""
echo "🔄 Restarting Django..."
ssh rocksteady << 'EOF'
# Kill old processes
pkill -f "manage.py runserver"
sleep 2

# Start Django
cd ~/unibos/backend
nohup ./venv/bin/python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &
echo "✓ Django restarted with PID: $!"

# Wait for startup
sleep 5

# Check if running
if pgrep -f "manage.py runserver" > /dev/null; then
    echo "✓ Django is running"
else
    echo "✗ Django failed to start - check server.log"
fi
EOF

# 6. Test authentication
echo ""
echo "🔑 Testing authentication..."
RESPONSE=$(ssh rocksteady 'curl -s -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"berkhatirli\",\"password\":\"unibos123\"}" 2>&1')

if echo "$RESPONSE" | grep -q "token"; then
    echo "✅ Authentication successful!"
    echo "Response: $(echo $RESPONSE | head -c 100)..."
else
    echo "❌ Authentication failed!"
    echo "Response: $RESPONSE"
    
    echo ""
    echo "📝 Checking Django logs..."
    ssh rocksteady 'tail -20 ~/unibos/apps/web/backend/server.log'
fi

echo ""
echo "======================================"
echo "Summary:"
echo "- Username: berkhatirli"
echo "- Password: unibos123"
echo "- URL: https://recaria.org"
echo "======================================"