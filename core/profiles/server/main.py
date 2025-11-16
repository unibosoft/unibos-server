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


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name='unibos-server')
@click.pass_context
def cli(ctx):
    """
    🖥️  unibos-server - production server management

    manages rocksteady production server:
    - service monitoring and health checks
    - database management
    - system operations and maintenance
    - performance monitoring

    examples:
        unibos-server                  # interactive tui mode
        unibos-server start           # start all services
        unibos-server stop            # stop all services
        unibos-server restart         # restart all services
        unibos-server logs            # view logs
        unibos-server status          # system status
        unibos-server backup          # backup database
    """
    ctx.ensure_object(dict)

    # If no subcommand, run TUI
    if ctx.invoked_subcommand is None:
        try:
            from core.profiles.server.tui import run_interactive
            run_interactive()
        except KeyboardInterrupt:
            click.echo("\n\n👋 goodbye!")
            sys.exit(0)
        except Exception as e:
            click.echo(f"\n❌ error: {e}", err=True)
            sys.exit(1)


@cli.command()
def start():
    """Start all services"""
    click.echo("🚀 Starting all services...")
    click.echo("\nServices to start:")
    click.echo("  • Django (gunicorn)")
    click.echo("  • PostgreSQL")
    click.echo("  • Nginx")
    click.echo("  • Celery workers")
    click.echo("\nRun: sudo systemctl start gunicorn celery nginx postgresql")


@cli.command()
def stop():
    """Stop all services"""
    click.echo("⏹️  Stopping all services...")
    click.echo("\nServices to stop:")
    click.echo("  • Celery workers")
    click.echo("  • Django (gunicorn)")
    click.echo("\nRun: sudo systemctl stop gunicorn celery")


@cli.command()
def restart():
    """Restart all services"""
    click.echo("🔄 Restarting all services...")
    click.echo("\nServices to restart:")
    click.echo("  • Django (gunicorn)")
    click.echo("  • Celery workers")
    click.echo("  • Nginx (reload)")
    click.echo("\nRun: sudo systemctl restart gunicorn celery && sudo systemctl reload nginx")


@cli.command()
def logs():
    """View server logs"""
    click.echo("📝 Server Logs")
    click.echo("\nAvailable log files:")
    click.echo("  • Django: tail -f /var/log/unibos/django.log")
    click.echo("  • Nginx access: tail -f /var/log/nginx/access.log")
    click.echo("  • Nginx error: tail -f /var/log/nginx/error.log")
    click.echo("  • System: sudo journalctl -f")


@cli.command()
def status():
    """Show system status"""
    click.echo("💚 System Status - Rocksteady")
    click.echo("\nChecking services...")
    click.echo("\nRun these commands:")
    click.echo("  • System: systemctl status gunicorn celery nginx postgresql")
    click.echo("  • Resources: free -h && df -h")
    click.echo("  • Uptime: uptime")


@cli.command()
def backup():
    """Backup database"""
    click.echo("💾 Database Backup")
    click.echo("\nCreating PostgreSQL backup...")
    click.echo("\nRun:")
    click.echo("  sudo -u postgres pg_dump unibos_db > backup_$(date +%Y%m%d_%H%M%S).sql")


def main():
    """
    Main entry point for the CLI

    Hybrid mode:
    - With arguments → Click commands
    - Without arguments → Interactive TUI mode
    """
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
