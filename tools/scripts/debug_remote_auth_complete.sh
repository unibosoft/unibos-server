#!/bin/bash
# Complete remote authentication debug and fix script

echo "=========================================="
echo "🔍 UNIBOS Remote Authentication Debug"
echo "=========================================="

# 1. Check what's actually in the remote database
echo -e "\n📊 Step 1: Checking remote database users..."
ssh rocksteady << 'EOF'
echo "Current users in database:"
PGPASSWORD=unibos_password psql -h localhost -U unibos_user -d unibos_central << SQL
SELECT username, email, is_active, is_staff, is_superuser, last_login 
FROM auth_user 
ORDER BY id DESC LIMIT 5;

-- Check password format
SELECT username, substring(password, 1, 20) as password_prefix 
FROM auth_user 
WHERE username='berkhatirli';
SQL
EOF

# 2. Test authentication directly on remote
echo -e "\n🔐 Step 2: Testing authentication on remote..."
ssh rocksteady << 'EOF'
cd ~/unibos/platform/runtime/web/backend

# Test with Django shell
./venv/bin/python << PYTHON
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.production')
django.setup()

from django.contrib.auth import authenticate, get_user_model
User = get_user_model()

print("\n=== Authentication Test ===")
# Test with both passwords
passwords = ['Bodrum2015*', 'unibos123']
for pwd in passwords:
    user = authenticate(username='berkhatirli', password=pwd)
    if user:
        print(f"✅ Authentication successful with password: {pwd}")
        break
    else:
        print(f"❌ Failed with password: {pwd}")

# Check user directly
try:
    user = User.objects.get(username='berkhatirli')
    print(f"\n✓ User exists: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Active: {user.is_active}")
    print(f"  Superuser: {user.is_superuser}")
    print(f"  Password hash starts with: {user.password[:30]}")
except User.DoesNotExist:
    print("❌ User 'berkhatirli' not found!")
PYTHON
EOF

# 3. Check Django settings on remote
echo -e "\n⚙️ Step 3: Checking Django settings..."
ssh rocksteady << 'EOF'
cd ~/unibos/platform/runtime/web/backend

./venv/bin/python << PYTHON
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.production')
django.setup()

from django.conf import settings

print("\n=== Django Settings ===")
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS[:3]}...")
print(f"SESSION_COOKIE_SECURE: {getattr(settings, 'SESSION_COOKIE_SECURE', 'Not set')}")
print(f"CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', 'Not set')}")
print(f"SESSION_ENGINE: {settings.SESSION_ENGINE}")
print(f"DATABASES: {settings.DATABASES['default']['ENGINE']}")

# Check authentication backends
print(f"\nAuthentication Backends:")
for backend in settings.AUTHENTICATION_BACKENDS:
    print(f"  - {backend}")
PYTHON
EOF

# 4. Force reset berkhatirli password on remote
echo -e "\n🔄 Step 4: Force resetting berkhatirli password on remote..."
ssh rocksteady << 'EOF'
cd ~/unibos/platform/runtime/web/backend

./venv/bin/python << PYTHON
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.production')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    user = User.objects.get(username='berkhatirli')
    user.set_password('Bodrum2015*')
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print("✅ Password reset to: Bodrum2015*")
    
    # Test immediately
    from django.contrib.auth import authenticate
    test = authenticate(username='berkhatirli', password='Bodrum2015*')
    if test:
        print("✅ Authentication test passed!")
    else:
        print("❌ Authentication test failed after reset!")
        
except Exception as e:
    print(f"❌ Error: {e}")
PYTHON
EOF

# 5. Check Redis and clear sessions
echo -e "\n🔴 Step 5: Checking Redis and clearing sessions..."
ssh rocksteady << 'EOF'
# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is running"
    # Clear all sessions to force re-login
    redis-cli FLUSHDB
    echo "✓ All sessions cleared"
else
    echo "✗ Redis not running - starting..."
    sudo systemctl start redis-server || sudo service redis-server start
    sleep 2
    if redis-cli ping > /dev/null 2>&1; then
        echo "✓ Redis started"
        redis-cli FLUSHDB
        echo "✓ Sessions cleared"
    fi
fi
EOF

# 6. Fix settings file
echo -e "\n🔧 Step 6: Fixing production settings..."
ssh rocksteady << 'EOF'
cd ~/unibos/platform/runtime/web/backend

# Backup current settings
cp unibos_platform/runtime/web/backend/settings/production.py unibos_platform/runtime/web/backend/settings/production.py.backup

# Create new production settings
cat > unibos_platform/runtime/web/backend/settings/production.py << 'SETTINGS'
"""
Production settings for UNIBOS - Fixed for HTTP
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DEBUG = False

ALLOWED_HOSTS = ['*']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'unibos_central'),
        'USER': os.environ.get('DB_USER', 'unibos_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'unibos_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 600,
        'ATOMIC_REQUESTS': True,
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/opt/unibos/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/opt/unibos/media'

# Security - HTTP compatible
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-production-key-change-this!')
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False  # Critical for HTTP
CSRF_COOKIE_SECURE = False     # Critical for HTTP
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False    # Must be False for AJAX
SESSION_COOKIE_SAMESITE = 'Lax'
X_FRAME_OPTIONS = 'DENY'

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 hours

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'http://rocksteady.local',
    'http://localhost:8000',
    'http://158.178.201.117',
    'http://158.178.201.117:8000',
    'http://recaria.org',
    'https://recaria.org',
]

# Import base settings
try:
    from .base import *
except ImportError:
    # Essential apps if base.py missing
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'corsheaders',
        'apps.core',
        'apps.authentication',
        'apps.users',
        'apps.web_ui',
    ]
    
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    
    ROOT_URLCONF = 'unibos_backend.urls'
    AUTH_USER_MODEL = 'users.User'
    
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / 'templates'],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'apps.web_ui.context_processors.sidebar_context',
                    'apps.web_ui.context_processors.global_context',
                ],
            },
        },
    ]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
SETTINGS

echo "✓ Production settings updated"
EOF

# 7. Restart Django
echo -e "\n🔄 Step 7: Restarting Django..."
ssh rocksteady << 'EOF'
# Kill old processes
pkill -f "manage.py runserver"
sleep 2

# Start Django
cd ~/unibos/platform/runtime/web/backend
nohup ./venv/bin/python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &
echo "✓ Django restarted"

# Wait and check
sleep 5
if pgrep -f "manage.py runserver" > /dev/null; then
    echo "✓ Django is running"
else
    echo "✗ Django failed to start"
    echo "Last 10 lines of server.log:"
    tail -10 server.log
fi
EOF

# 8. Final authentication test
echo -e "\n✅ Step 8: Final authentication test..."
echo "Testing via API..."
RESPONSE=$(ssh rocksteady 'curl -s -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"berkhatirli\",\"password\":\"Bodrum2015*\"}" 2>&1')

if echo "$RESPONSE" | grep -q "token"; then
    echo "✅ API Authentication successful!"
else
    echo "❌ API Authentication failed"
    echo "Response: $RESPONSE"
fi

# Test login page
echo -e "\nTesting login page..."
HTTP_STATUS=$(ssh rocksteady 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/login/')
echo "Login page HTTP status: $HTTP_STATUS"

echo "
=========================================="
echo "📝 Summary:"
echo "- Username: berkhatirli"
echo "- Password: Bodrum2015*"
echo "- URL: https://recaria.org"
echo ""
echo "If login still fails, check:"
echo "1. Clear browser cache/cookies"
echo "2. Try incognito/private mode"
echo "3. Check browser console for errors"
echo "=========================================="