#!/usr/bin/env python3
"""
🗄️ UNIBOS Database Configuration
PostgreSQL veritabanı bağlantı ayarları
"""

import os
from pathlib import Path
from typing import Optional

# Veritabanı bağlantı bilgileri
DATABASE_CONFIG = {
    'host': os.getenv('UNIBOS_DB_HOST', 'localhost'),
    'port': os.getenv('UNIBOS_DB_PORT', '5432'),
    'database': os.getenv('UNIBOS_DB_NAME', 'unibos'),
    'user': os.getenv('UNIBOS_DB_USER', 'unibos'),
    'password': os.getenv('UNIBOS_DB_PASSWORD', 'unibos123'),
}

# SQLAlchemy connection string
DATABASE_URL = (
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
)

# Django database settings (for future use)
DJANGO_DATABASE = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': DATABASE_CONFIG['database'],
    'USER': DATABASE_CONFIG['user'],
    'PASSWORD': DATABASE_CONFIG['password'],
    'HOST': DATABASE_CONFIG['host'],
    'PORT': DATABASE_CONFIG['port'],
}

# Alembic migration directory
MIGRATION_DIR = Path(__file__).parent / 'migrations'

# Create .env file if not exists
ENV_FILE = Path(__file__).parent.parent.parent / '.env'
if not ENV_FILE.exists():
    env_content = f"""# UNIBOS Database Configuration
UNIBOS_DB_HOST=localhost
UNIBOS_DB_PORT=5432
UNIBOS_DB_NAME=unibos
UNIBOS_DB_USER=unibos
UNIBOS_DB_PASSWORD=unibos123
"""
    ENV_FILE.write_text(env_content)
    print(f"Created .env file at: {ENV_FILE}")