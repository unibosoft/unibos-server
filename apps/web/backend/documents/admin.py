from django.contrib import admin

# Import gamification admin configurations
try:
    from modules.documents.backend.gamification_admin import *
except ImportError:
    pass  # Gamification models not yet migrated

# Register your models here.
