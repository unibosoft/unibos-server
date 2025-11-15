"""
UNIBOS Stop Command

Stop UNIBOS services.
"""

import click
import subprocess
from pathlib import Path


def get_django_path():
    """Get Django project path"""
    # Navigate from CLI to Django
    cli_path = Path(__file__).parent.parent.parent.parent
    django_path = cli_path / 'web'
    return django_path


@click.command(name='stop')
@click.option('--force', '-f', is_flag=True, help='Force stop (kill processes)')
def stop_command(force):
    """🛑 Stop UNIBOS services"""

    click.echo(click.style('🛑 Stopping UNIBOS Services', fg='yellow', bold=True))
    click.echo()

    stopped = []
    failed = []

    # Stop Django dev server
    click.echo('  Stopping Django...')
    result = subprocess.run(
        ['pgrep', '-f', 'manage.py runserver'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode == 0:
        pids = result.stdout.decode().strip().split('\n')
        for pid in pids:
            if pid:
                try:
                    if force:
                        subprocess.run(['kill', '-9', pid], check=True)
                    else:
                        subprocess.run(['kill', pid], check=True)
                    stopped.append(f'Django (PID {pid})')
                except subprocess.CalledProcessError:
                    failed.append(f'Django (PID {pid})')
    else:
        click.echo(f"    {click.style('ℹ', fg='blue')} Django not running")

    # Stop Celery worker
    click.echo('  Stopping Celery worker...')
    result = subprocess.run(
        ['pgrep', '-f', 'celery.*worker'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode == 0:
        pids = result.stdout.decode().strip().split('\n')
        for pid in pids:
            if pid:
                try:
                    if force:
                        subprocess.run(['kill', '-9', pid], check=True)
                    else:
                        subprocess.run(['kill', pid], check=True)
                    stopped.append(f'Celery worker (PID {pid})')
                except subprocess.CalledProcessError:
                    failed.append(f'Celery worker (PID {pid})')
    else:
        click.echo(f"    {click.style('ℹ', fg='blue')} Celery worker not running")

    # Stop Celery beat
    click.echo('  Stopping Celery beat...')
    result = subprocess.run(
        ['pgrep', '-f', 'celery.*beat'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode == 0:
        pids = result.stdout.decode().strip().split('\n')
        for pid in pids:
            if pid:
                try:
                    if force:
                        subprocess.run(['kill', '-9', pid], check=True)
                    else:
                        subprocess.run(['kill', pid], check=True)
                    stopped.append(f'Celery beat (PID {pid})')
                except subprocess.CalledProcessError:
                    failed.append(f'Celery beat (PID {pid})')
    else:
        click.echo(f"    {click.style('ℹ', fg='blue')} Celery beat not running")

    # Summary
    click.echo()
    if stopped:
        click.echo(click.style('✓ Stopped services:', fg='green'))
        for service in stopped:
            click.echo(f"  • {service}")

    if failed:
        click.echo(click.style('✗ Failed to stop:', fg='red'))
        for service in failed:
            click.echo(f"  • {service}")

    if not stopped and not failed:
        click.echo(click.style('ℹ No services were running', fg='blue'))
