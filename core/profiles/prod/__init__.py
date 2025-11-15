"""
UNIBOS Node CLI
CLI for standalone nodes (raspberry pi, local mac)

This CLI is designed for standalone UNIBOS nodes that:
- Run independently with local PostgreSQL database
- Support offline-first operation with sync queue
- Enable P2P mesh networking with peer discovery
- Sync with central server when online (optional)
- Manage local modules and services
"""

from core.version import __version__

__all__ = ['__version__']
