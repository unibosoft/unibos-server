"""
Production settings for UNIBOS
For deployment on Ubuntu/Oracle VM
"""

import os
from pathlib import Path

# Import base settings
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allow hosts
ALLOWED_HOSTS = [
    'rocksteady.local',
    'unibos.local',
    'localhost',
    '127.0.0.1',
    '158.178.201.117',
    'recaria.org',
    'www.recaria.org',
    '.recaria.org',
    '*'  # For testing, restrict in real production
]

# Database - Centralized PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'unibos_central'),
        'USER': os.environ.get('DB_USER', 'unibos_admin'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'unibos_password'),
        'HOST': os.environ.get('DB_HOST', 'rocksteady.local'),
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

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-production-key-change-this!')
SECURE_SSL_REDIRECT = False
# Changed to False for HTTP compatibility
SESSION_COOKIE_SECURE = False  # Was True - requires HTTPS
CSRF_COOKIE_SECURE = False     # Was True - requires HTTPS
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
X_FRAME_OPTIONS = 'DENY'

# Email Configuration for recaria.org
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.recaria.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'berk@recaria.org'
EMAIL_HOST_PASSWORD = 'Recaria2025Mail!'
DEFAULT_FROM_EMAIL = 'berk@recaria.org'
SERVER_EMAIL = 'berk@recaria.org'

# Import other settings from base
try:
    from ..settings import *
except:
    pass