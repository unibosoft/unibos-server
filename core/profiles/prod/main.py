#!/usr/bin/env python3
"""
UNIBOS Node CLI - Main Entry Point
Standalone node management (raspberry pi, local mac)
"""

import click
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.version import __version__


@click.group()
@click.version_option(version=__version__, prog_name='unibos')
@click.pass_context
def cli(ctx):
    """
    unibos - standalone node management

    manages local unibos nodes (raspberry pi, mac):
    - offline-first operation with local database
    - p2p mesh networking and peer discovery
    - module management and local services
    - optional sync with central server

    examples:
        unibos                    # interactive tui mode
        unibos status             # node status
        unibos identity           # show node identity
        unibos modules list       # list installed modules
        unibos p2p discover       # discover peer nodes
    """
    ctx.ensure_object(dict)


# TODO: Add command groups (status, identity, modules, p2p, sync, etc.)
# Will be implemented in later phases


def main():
    """
    Main entry point for the CLI

    Hybrid mode:
    - With arguments -> Click commands
    - Without arguments -> Interactive TUI mode
    """
    # Check if running in interactive mode (no arguments provided)
    if len(sys.argv) == 1:
        # No arguments - run interactive TUI mode
        try:
            from core.cli_node.interactive import run_interactive
            run_interactive()
        except KeyboardInterrupt:
            click.echo("\n\ngoodbye!")
            sys.exit(0)
        except Exception as e:
            click.echo(f"\nerror: {e}", err=True)
            sys.exit(1)
    else:
        # Arguments provided - run Click CLI
        try:
            cli(obj={})
        except KeyboardInterrupt:
            click.echo("\n\ninterrupted by user")
            sys.exit(130)
        except Exception as e:
            click.echo(f"\nerror: {e}", err=True)
            sys.exit(1)


if __name__ == '__main__':
    main()
