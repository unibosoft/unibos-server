#!/usr/bin/env python3
"""
Create berkhatirli user in PostgreSQL database
"""
import os
import sys
import django
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.clients.web.unibos_backend.settings.emergency')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def create_berkhatirli_user():
    """Create berkhatirli superuser"""

    # Check if user exists
    if User.objects.filter(username='berkhatirli').exists():
        print("User 'berkhatirli' already exists")
        user = User.objects.get(username='berkhatirli')
        # Update password
        user.set_password('unicorn')  # Default password
        user.save()
        print("Password updated for berkhatirli")
    else:
        # Create new superuser
        user = User.objects.create_superuser(
            username='berkhatirli',
            email='berk@unibos.com',
            password='unicorn',  # Default password
            first_name='Berk',
            last_name='Hatırlı'
        )

        # Set additional fields if they exist
        if hasattr(user, 'timezone'):
            user.timezone = 'Europe/Istanbul'
        if hasattr(user, 'language'):
            user.language = 'tr'
        if hasattr(user, 'theme'):
            user.theme = 'dark'

        user.save()
        print(f"Created superuser: berkhatirli")

    # List all users
    print("\nAll users in database:")
    for u in User.objects.all():
        print(f"  - {u.username} ({'superuser' if u.is_superuser else 'regular'})")

    return user

if __name__ == "__main__":
    try:
        user = create_berkhatirli_user()
        print("\n✅ Success! You can now login with:")
        print("   Username: berkhatirli")
        print("   Password: unicorn")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()