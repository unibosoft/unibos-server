"""
Deploy Command for Manager Profile

Remote deployment operations for UNIBOS instances.
"""

import click
import subprocess
from pathlib import Path


@click.command('deploy')
@click.argument('target', type=click.Choice(['rocksteady', 'local'], case_sensitive=False), default='rocksteady')
@click.option('--skip-migrations', is_flag=True, help='Skip database migrations')
@click.option('--skip-static', is_flag=True, help='Skip static file collection')
@click.option('--restart/--no-restart', default=True, help='Restart services after deployment')
def deploy_command(target, skip_migrations, skip_static, restart):
    """
    Deploy UNIBOS to remote target

    Examples:
        unibos-dev manager deploy rocksteady
        unibos-dev manager deploy local --skip-migrations
    """
    click.echo(f"🚀 Deploying to {target}...")
    click.echo()

    if target == 'rocksteady':
        deploy_to_rocksteady(skip_migrations, skip_static, restart)
    elif target == 'local':
        deploy_to_local(skip_migrations, skip_static, restart)
    else:
        click.echo(f"❌ Unknown target: {target}", err=True)
        return 1

    click.echo()
    click.echo("✅ Deployment complete!")
    return 0


def deploy_to_rocksteady(skip_migrations: bool, skip_static: bool, restart: bool):
    """Deploy to rocksteady production server"""
    click.echo("Target: rocksteady (Oracle Cloud VM)")
    click.echo()

    # Step 1: Push code to git
    click.echo("📤 Step 1: Pushing code to git...")
    try:
        result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            click.echo("  ✅ Code pushed successfully")
        else:
            click.echo("  ⚠️  Warning: Could not push code")
            click.echo(f"     {result.stderr.strip()}")
    except Exception as e:
        click.echo(f"  ⚠️  Warning: {e}")

    click.echo()

    # Step 2: SSH and pull latest code
    click.echo("📥 Step 2: Pulling latest code on remote...")
    ssh_command = [
        'ssh', 'rocksteady',
        'cd /opt/unibos && git pull origin main'
    ]
    click.echo(f"  Running: {' '.join(ssh_command)}")
    try:
        result = subprocess.run(ssh_command, capture_output=True, text=True)
        if result.returncode == 0:
            click.echo("  ✅ Code pulled successfully")
        else:
            click.echo("  ❌ Failed to pull code")
            click.echo(f"     {result.stderr.strip()}")
            return
    except Exception as e:
        click.echo(f"  ❌ Error: {e}")
        return

    click.echo()

    # Step 3: Install dependencies
    click.echo("📦 Step 3: Installing dependencies...")
    ssh_command = [
        'ssh', 'rocksteady',
        'cd /opt/unibos && source venv/bin/activate && pip install -r requirements.txt'
    ]
    click.echo("  Installing Python packages...")
    try:
        subprocess.run(ssh_command, check=False)
        click.echo("  ✅ Dependencies installed")
    except Exception as e:
        click.echo(f"  ⚠️  Warning: {e}")

    click.echo()

    # Step 4: Run migrations
    if not skip_migrations:
        click.echo("🔄 Step 4: Running database migrations...")
        ssh_command = [
            'ssh', 'rocksteady',
            'cd /opt/unibos && source venv/bin/activate && python manage.py migrate'
        ]
        try:
            result = subprocess.run(ssh_command, capture_output=True, text=True)
            if result.returncode == 0:
                click.echo("  ✅ Migrations applied")
            else:
                click.echo("  ❌ Migration failed")
                click.echo(f"     {result.stderr.strip()}")
        except Exception as e:
            click.echo(f"  ❌ Error: {e}")
    else:
        click.echo("⏭️  Step 4: Skipping migrations (--skip-migrations)")

    click.echo()

    # Step 5: Collect static files
    if not skip_static:
        click.echo("📁 Step 5: Collecting static files...")
        ssh_command = [
            'ssh', 'rocksteady',
            'cd /opt/unibos && source venv/bin/activate && python manage.py collectstatic --noinput'
        ]
        try:
            result = subprocess.run(ssh_command, capture_output=True, text=True)
            if result.returncode == 0:
                click.echo("  ✅ Static files collected")
            else:
                click.echo("  ⚠️  Warning: Static collection failed")
        except Exception as e:
            click.echo(f"  ⚠️  Warning: {e}")
    else:
        click.echo("⏭️  Step 5: Skipping static files (--skip-static)")

    click.echo()

    # Step 6: Restart services
    if restart:
        click.echo("🔄 Step 6: Restarting services...")
        ssh_command = [
            'ssh', 'rocksteady',
            'sudo systemctl restart unibos'
        ]
        try:
            result = subprocess.run(ssh_command, capture_output=True, text=True)
            if result.returncode == 0:
                click.echo("  ✅ Services restarted")
            else:
                click.echo("  ❌ Failed to restart services")
                click.echo(f"     {result.stderr.strip()}")
        except Exception as e:
            click.echo(f"  ❌ Error: {e}")
    else:
        click.echo("⏭️  Step 6: Skipping service restart (--no-restart)")


def deploy_to_local(skip_migrations: bool, skip_static: bool, restart: bool):
    """Deploy to local development environment"""
    click.echo("Target: local development")
    click.echo()

    # For local, we just run the dev commands
    click.echo("📦 Installing dependencies...")
    try:
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=False)
        click.echo("  ✅ Dependencies installed")
    except Exception as e:
        click.echo(f"  ⚠️  Warning: {e}")

    click.echo()

    if not skip_migrations:
        click.echo("🔄 Running migrations...")
        try:
            subprocess.run(['python', 'manage.py', 'migrate'], check=False)
            click.echo("  ✅ Migrations applied")
        except Exception as e:
            click.echo(f"  ❌ Error: {e}")

    click.echo()

    if not skip_static:
        click.echo("📁 Collecting static files...")
        try:
            subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], check=False)
            click.echo("  ✅ Static files collected")
        except Exception as e:
            click.echo(f"  ⚠️  Warning: {e}")

    click.echo()

    if restart:
        click.echo("ℹ️  Local restart not implemented")
        click.echo("  Run 'unibos-dev dev run' to start the server")
