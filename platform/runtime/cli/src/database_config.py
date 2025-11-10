#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database configuration for UNIBOS
Unified configuration that imports from database module
"""

# Import everything from the main database config
from database.config import *
from database.db_manager import ENGINE, Session, DB_TYPE

# Re-export for backward compatibility
__all__ = [
    'DATABASE_CONFIG',
    'DATABASE_URL',
    'DJANGO_DATABASE',
    'ENGINE',
    'Session',
    'DB_TYPE',
    'get_database_url',
    'get_connection_params'
]

# Backward compatibility functions
def get_database_url():
    """Get database connection URL"""
    return DATABASE_URL

def get_connection_params():
    """Get database connection parameters"""
    if DB_TYPE == 'postgresql':
        return DATABASE_CONFIG
    else:
        from pathlib import Path
        db_path = Path.home() / '.unibos' / 'unibos.db'
        return {'database': str(db_path)}