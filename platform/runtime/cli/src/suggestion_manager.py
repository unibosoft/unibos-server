#!/usr/bin/env python3
"""
💡 UNIBOS Suggestion Manager - Legacy Compatibility Module
This module provides backward compatibility by importing from development_manager
"""

# Import everything from development_manager
from development_manager import *

# Additional info for users
import warnings

def _show_deprecation_notice():
    """Show deprecation notice on first import"""
    warnings.warn(
        "suggestion_manager.py is deprecated. Please use development_manager.py instead.",
        DeprecationWarning,
        stacklevel=2
    )

# Show notice only in development mode
import os
if os.environ.get('UNIBOS_ENV') == 'development':
    _show_deprecation_notice()

# Module info
__doc__ = """
This module has been replaced by development_manager.py

The new development_manager provides:
- All suggestion management features
- Enhanced test automation with TEST_SPECIALIST agent
- Better database support (SQLite and PostgreSQL)
- Improved development session tracking
- Unified development workflow management

For new code, please import from development_manager:
    from development_manager import development_manager, UnifiedDevelopmentManager
"""