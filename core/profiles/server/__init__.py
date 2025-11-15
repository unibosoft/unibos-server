"""
UNIBOS Server CLI
CLI for production server (rocksteady)

This CLI is designed for the central UNIBOS server that:
- Manages production Django backend (PostgreSQL)
- Coordinates distributed nodes
- Provides central API endpoints
- Handles synchronization hub
- Monitors system health and performance
"""

from core.version import __version__

__all__ = ['__version__']
