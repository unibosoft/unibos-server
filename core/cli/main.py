#!/usr/bin/env python3
"""
UNIBOS CLI - Main Entry Point
Universal Integrated Backend and Operating System
"""

import click
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.cli.ui.splash import show_splash_screen, show_compact_header
from core.cli.commands.deploy import deploy_group
from core.cli.commands.dev import dev_group
from core.cli.commands.db import db_group
from core.cli.commands.status import status_command


@click.group()
@click.version_option(version='533+', prog_name='unibos')
@click.option('--no-splash', is_flag=True, help='Skip splash screen')
@click.pass_context
def cli(ctx, no_splash):
    """🪐 UNIBOS - Universal Integrated Backend and Operating System

    Modern CLI for managing UNIBOS infrastructure, development,
    and deployment operations.

    Examples:
        unibos status              # Show system status
        unibos dev run             # Start development server
        unibos deploy rocksteady   # Deploy to production
        unibos db backup           # Create database backup
    """
    # Store context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['no_splash'] = no_splash

    # Show splash only for main command (no subcommand)
    if ctx.invoked_subcommand is None and not no_splash:
        show_splash_screen(quick=False)
        click.echo()
        click.echo("💡 Run 'unibos --help' to see available commands")
    elif ctx.invoked_subcommand and not no_splash:
        # Show compact header for subcommands
        show_compact_header()


# Register command groups
cli.add_command(deploy_group)
cli.add_command(dev_group)
cli.add_command(db_group)
cli.add_command(status_command)


def main():
    """Main entry point for the CLI"""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\n\n👋 Interrupted by user")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
