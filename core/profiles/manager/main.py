#!/usr/bin/env python3
"""
UNIBOS Manager CLI - Main Entry Point
Remote management CLI for UNIBOS instances
"""

import click
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.profiles.manager.commands.deploy import deploy_command
from core.profiles.manager.commands.status import status_command
from core.profiles.manager.commands.ssh import ssh_command
from core.version import __version__


@click.group()
@click.version_option(version=__version__, prog_name='unibos-manager')
@click.pass_context
def cli(ctx):
    """🎯 UNIBOS Manager CLI - Remote Management Tools

    Manager CLI for controlling UNIBOS instances remotely.
    Focused on deployment, monitoring, and remote operations.

    Examples:
        unibos-manager                  # Launch Manager TUI (default)
        unibos-manager status           # Check all instances
        unibos-manager deploy rocksteady # Deploy to production
        unibos-manager ssh rocksteady   # SSH to server
    """
    ctx.ensure_object(dict)


# Register command groups
cli.add_command(deploy_command, name='deploy')
cli.add_command(status_command, name='status')
cli.add_command(ssh_command, name='ssh')


@cli.command('tui')
def tui_command():
    """Launch Manager TUI (Text User Interface)"""
    try:
        from core.profiles.manager.tui import run_interactive
        run_interactive()
    except KeyboardInterrupt:
        click.echo("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


def main():
    """
    Main entry point for the Manager CLI

    Hybrid mode:
    - With arguments → Click commands
    - Without arguments → Interactive TUI mode
    """
    # Check if running in interactive mode (no arguments provided)
    if len(sys.argv) == 1:
        # No arguments - run interactive TUI mode
        try:
            from core.profiles.manager.tui import run_interactive
            run_interactive()
        except KeyboardInterrupt:
            click.echo("\n\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            click.echo(f"\n❌ Error: {e}", err=True)
            sys.exit(1)
    else:
        # Arguments provided - run Click CLI
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
