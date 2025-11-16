#!/usr/bin/env python
"""
Create sample users for UNIBOS platform
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
django_path = Path(__file__).parent
project_root = django_path.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(django_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def create_users():
    """Create sample users for testing"""

    users_data = [
        {
            'username': 'berkhatirli',
            'email': 'berk@unibos.com',
            'password': 'unibos123',
            'is_superuser': True,
            'is_staff': True,
            'first_name': 'Berk',
            'last_name': 'Hatırlı'
        },
        {
            'username': 'admin',
            'email': 'admin@unibos.com',
            'password': 'admin123',
            'is_superuser': True,
            'is_staff': True,
            'first_name': 'Admin',
            'last_name': 'User'
        },
        {
            'username': 'testuser',
            'email': 'test@unibos.com',
            'password': 'test123',
            'is_superuser': False,
            'is_staff': False,
            'first_name': 'Test',
            'last_name': 'User'
        },
        {
            'username': 'demo',
            'email': 'demo@unibos.com',
            'password': 'demo123',
            'is_superuser': False,
            'is_staff': False,
            'first_name': 'Demo',
            'last_name': 'User'
        }
    ]

    # Check current User model
    print(f"Using User model: {User}")
    print(f"User table name: {User._meta.db_table}")

    # List existing users
    existing = User.objects.all()
    print(f"\nExisting users: {existing.count()}")
    for user in existing:
        print(f"  - {user.username} ({user.email})")

    # Create new users
    print("\nCreating sample users...")
    for user_data in users_data:
        username = user_data['username']
        email = user_data['email']
        password = user_data.pop('password')

        # Check if user exists
        if User.objects.filter(username=username).exists():
            print(f"  ✓ User '{username}' already exists")
            continue

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **{k: v for k, v in user_data.items() if k not in ['username', 'email']}
        )
        print(f"  ✅ Created user: {username} ({email})")

    # Show final count
    final_count = User.objects.count()
    print(f"\nTotal users in database: {final_count}")

    # Show superusers
    superusers = User.objects.filter(is_superuser=True)
    print(f"Superusers: {', '.join([u.username for u in superusers])}")

if __name__ == '__main__':
    try:
        create_users()
        print("\n✅ Sample users created successfully!")
    except Exception as e:
        print(f"\n❌ Error creating users: {e}")
        import traceback
        traceback.print_exc()