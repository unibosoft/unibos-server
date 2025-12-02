"""
UNIBOS CLI - Status & Health Commands
System health checks and status information
"""

import click
import subprocess
import sys
from pathlib import Path


@click.command(name='status')
@click.option('--detailed', is_flag=True, help='Show detailed status')
def status_command(detailed):
    """📊 Show system status and health"""
    click.echo(click.style('📊 unibos system status', fg='cyan', bold=True))
    click.echo()

    root_dir = Path(__file__).parent.parent.parent.parent.parent  # Up 5 levels to project root

    # Version info
    try:
        import json
        version_file = root_dir / 'VERSION.json'
        if version_file.exists():
            with open(version_file) as f:
                version_info = json.load(f)
                # Handle version as dict or string
                version = version_info.get('version', 'unknown')
                if isinstance(version, dict):
                    version = f"{version.get('major', 0)}.{version.get('minor', 0)}.{version.get('patch', 0)}"
                click.echo(f"version: {click.style(version, fg='yellow')}")
                if detailed:
                    click.echo(f"build: {version_info.get('build', 'unknown')}")
                    click.echo(f"date: {version_info.get('build_date', 'unknown')}")
    except Exception:
        click.echo("version: unknown")

    click.echo()

    # Directory structure
    dirs_to_check = [
        ('core', root_dir / 'core'),
        ('modules', root_dir / 'modules'),
        ('data', root_dir / 'data'),
        ('deployment', root_dir / 'deployment'),
    ]

    click.echo(click.style('📁 directory structure:', fg='cyan'))
    for name, path in dirs_to_check:
        status = '✓' if path.exists() else '✗'
        color = 'green' if path.exists() else 'red'
        click.echo(f"  {click.style(status, fg=color)} {name}: {path}")

    click.echo()

    # Django status
    django_path = root_dir / 'core' / 'clients' / 'web' / 'manage.py'
    if django_path.exists():
        click.echo(click.style('🌐 django:', fg='cyan'))
        click.echo(f"  {click.style('✓', fg='green')} django installed")

        if detailed:
            # Try to get Django version
            try:
                result = subprocess.run(
                    [sys.executable, str(django_path), '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    click.echo(f"  version: {result.stdout.strip()}")
            except Exception:
                pass
    else:
        click.echo(f"  {click.style('✗', fg='red')} django not found")

    click.echo()

    # Database
    click.echo(click.style('🗄️  database:', fg='cyan'))
    data_db = root_dir / 'data_db'
    if data_db.exists():
        click.echo(f"  {click.style('✓', fg='green')} database directory exists")
    else:
        click.echo(f"  {click.style('⚠', fg='yellow')} database directory not found (may use postgresql)")

    # Check for PostgreSQL
    try:
        result = subprocess.run(
            ['psql', '--version'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            version = result.stdout.strip().lower()
            click.echo(f"  {click.style('✓', fg='green')} postgresql available: {version}")
    except Exception:
        pass

    if detailed:
        click.echo()
        click.echo(click.style('💡 tip:', fg='yellow'))
        click.echo('  run "unibos-dev deploy check" for deployment health check')
        click.echo('  run "unibos-dev dev run" to start development server')
        click.echo('  run "unibos-dev --help" for all available commands')
