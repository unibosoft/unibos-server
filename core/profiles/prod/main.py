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


@click.group(invoke_without_command=True)
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
        unibos launch <module>    # launch specific module
        unibos update             # update system
        unibos backup             # backup data
        unibos settings           # open settings
    """
    ctx.ensure_object(dict)

    # If no subcommand, run TUI
    if ctx.invoked_subcommand is None:
        try:
            from core.profiles.prod.tui import run_interactive
            run_interactive()
        except KeyboardInterrupt:
            click.echo("\n\ngoodbye!")
            sys.exit(0)
        except Exception as e:
            click.echo(f"\nerror: {e}", err=True)
            sys.exit(1)


@cli.command()
@click.argument('module_name', required=False)
def launch(module_name):
    """Launch a specific module"""
    if not module_name:
        click.echo("Usage: unibos launch <module_name>")
        click.echo("\nAvailable modules:")
        click.echo("  • together-we-stand")
        click.echo("  • recaria")
        click.echo("  • movies")
        click.echo("  • music")
        return

    click.echo(f"🚀 Launching module: {module_name}")
    click.echo(f"\nModule: {module_name}")
    click.echo("Status: Starting...")
    click.echo("\nTo launch manually:")
    click.echo(f"  cd modules/{module_name} && python manage.py runserver")


@cli.command()
def status():
    """Show node status"""
    click.echo("💚 UNIBOS Node Status")
    click.echo("\nNode Information:")
    click.echo("  • Profile: Client")
    click.echo("  • Version: v0.534.0")
    click.echo("  • Status: Operational")
    click.echo("\nSystem Resources:")
    click.echo("  Run: top")
    click.echo("\nServices:")
    click.echo("  Run: systemctl --user status")


@cli.command()
def update():
    """Update system and modules"""
    click.echo("🔄 System Update")
    click.echo("\nChecking for updates...")
    click.echo("\nUpdate process:")
    click.echo("  1. Check for updates")
    click.echo("  2. Download updates")
    click.echo("  3. Install updates")
    click.echo("  4. Restart services")


@cli.command()
def backup():
    """Backup user data"""
    click.echo("💾 Data Backup")
    click.echo("\nCreating backup...")
    click.echo("\nBackup includes:")
    click.echo("  • User data")
    click.echo("  • Module data")
    click.echo("  • Settings")
    click.echo("  • Database")


@cli.command()
def settings():
    """Open settings"""
    click.echo("🔧 System Settings")
    click.echo("\nSettings categories:")
    click.echo("  • General settings")
    click.echo("  • Network settings")
    click.echo("  • Module settings")
    click.echo("  • Privacy settings")
    click.echo("\nLaunch TUI for interactive settings:")
    click.echo("  unibos")


def main():
    """
    Main entry point for the CLI

    Hybrid mode:
    - With arguments -> Click commands
    - Without arguments -> Interactive TUI mode
    """
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
