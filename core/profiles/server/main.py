#!/usr/bin/env python3
"""
UNIBOS Server CLI - Main Entry Point
Production server management and monitoring (rocksteady)
"""

import click
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.version import __version__


@click.group()
@click.version_option(version=__version__, prog_name='unibos-server')
@click.pass_context
def cli(ctx):
    """
    🖥️  unibos-server - production server management

    manages rocksteady production server:
    - service monitoring and health checks
    - node registry and coordination
    - database management
    - performance monitoring

    examples:
        unibos-server                  # interactive tui mode
        unibos-server health          # health check
        unibos-server nodes list      # list registered nodes
        unibos-server db backup       # backup database
    """
    ctx.ensure_object(dict)


# TODO: Add command groups (health, nodes, db, etc.)
# Will be implemented in later phases


def main():
    """
    Main entry point for the CLI

    Hybrid mode:
    - With arguments → Click commands
    - Without arguments → Interactive TUI mode
    """
    # Check if running in interactive mode (no arguments provided)
    if len(sys.argv) == 1:
        # No arguments - run interactive TUI mode
        try:
            from core.cli_server.interactive import run_interactive
            run_interactive()
        except KeyboardInterrupt:
            click.echo("\n\n👋 goodbye!")
            sys.exit(0)
        except Exception as e:
            click.echo(f"\n❌ error: {e}", err=True)
            sys.exit(1)
    else:
        # Arguments provided - run Click CLI
        try:
            cli(obj={})
        except KeyboardInterrupt:
            click.echo("\n\n👋 interrupted by user")
            sys.exit(130)
        except Exception as e:
            click.echo(f"\n❌ error: {e}", err=True)
            sys.exit(1)


if __name__ == '__main__':
    main()
