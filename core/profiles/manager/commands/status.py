"""
Status Command for Manager Profile

Check status of remote UNIBOS instances.
"""

import click
import subprocess
import socket


@click.command('status')
@click.argument('target', type=click.Choice(['rocksteady', 'local', 'all'], case_sensitive=False), default='all')
def status_command(target):
    """
    Check status of UNIBOS instances

    Examples:
        unibos-dev manager status
        unibos-dev manager status rocksteady
        unibos-dev manager status local
    """
    click.echo("📊 Checking UNIBOS instance status...")
    click.echo()

    if target == 'all':
        check_rocksteady_status()
        click.echo()
        check_local_status()
    elif target == 'rocksteady':
        check_rocksteady_status()
    elif target == 'local':
        check_local_status()
    else:
        click.echo(f"❌ Unknown target: {target}", err=True)
        return 1

    return 0


def check_rocksteady_status():
    """Check rocksteady server status"""
    click.echo("🌍 Rocksteady (Production Server)")
    click.echo("─" * 50)

    # Check SSH connectivity
    click.echo("🔐 SSH Connectivity:")
    try:
        result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=5', 'rocksteady', 'echo "connected"'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            click.echo("  ✅ SSH connection successful")
        else:
            click.echo("  ❌ SSH connection failed")
            return
    except subprocess.TimeoutExpired:
        click.echo("  ❌ SSH connection timeout")
        return
    except Exception as e:
        click.echo(f"  ❌ Error: {e}")
        return

    # Check git status
    click.echo()
    click.echo("📦 Git Repository:")
    try:
        result = subprocess.run(
            ['ssh', 'rocksteady', 'cd /opt/unibos && git branch --show-current'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            click.echo(f"  → Branch: {branch}")

            # Get commit hash
            result = subprocess.run(
                ['ssh', 'rocksteady', 'cd /opt/unibos && git rev-parse --short HEAD'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                commit = result.stdout.strip()
                click.echo(f"  → Commit: {commit}")
        else:
            click.echo("  ⚠️  Could not get git status")
    except Exception as e:
        click.echo(f"  ⚠️  Error: {e}")

    # Check service status
    click.echo()
    click.echo("🏥 Services:")
    try:
        result = subprocess.run(
            ['ssh', 'rocksteady', 'systemctl is-active unibos'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip() == 'active':
            click.echo("  ✅ UNIBOS service: Running")
        else:
            click.echo("  ❌ UNIBOS service: Stopped")
    except Exception as e:
        click.echo(f"  ⚠️  Error: {e}")

    # Check disk usage
    click.echo()
    click.echo("💾 Disk Usage:")
    try:
        result = subprocess.run(
            ['ssh', 'rocksteady', 'df -h /opt/unibos | tail -1'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split()
            if len(parts) >= 5:
                click.echo(f"  → Used: {parts[2]} / {parts[1]} ({parts[4]})")
        else:
            click.echo("  ⚠️  Could not get disk usage")
    except Exception as e:
        click.echo(f"  ⚠️  Error: {e}")


def check_local_status():
    """Check local development status"""
    click.echo("💻 Local Development")
    click.echo("─" * 50)

    # Check if running locally
    click.echo("🔍 Environment:")
    try:
        hostname = socket.gethostname()
        click.echo(f"  → Host: {hostname}")
    except Exception as e:
        click.echo(f"  ⚠️  Error: {e}")

    # Check git status
    click.echo()
    click.echo("📦 Git Repository:")
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            click.echo(f"  → Branch: {branch}")

            # Get commit hash
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                commit = result.stdout.strip()
                click.echo(f"  → Commit: {commit}")

            # Check for uncommitted changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                if result.stdout.strip():
                    click.echo("  ⚠️  Uncommitted changes present")
                else:
                    click.echo("  ✅ Working tree clean")
        else:
            click.echo("  ⚠️  Not a git repository")
    except Exception as e:
        click.echo(f"  ⚠️  Error: {e}")

    # Check Django server status
    click.echo()
    click.echo("🐍 Django Server:")
    import os
    from pathlib import Path

    # Check for PID file
    pid_file = Path('/tmp/unibos_dev_server.pid')
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            # Check if process is running
            try:
                os.kill(pid, 0)  # Signal 0 checks if process exists
                click.echo(f"  ✅ Running (PID: {pid})")
            except OSError:
                click.echo("  ❌ Not running (stale PID file)")
        except:
            click.echo("  ⚠️  Invalid PID file")
    else:
        click.echo("  ❌ Not running")

    # Check database connection
    click.echo()
    click.echo("🗄️  Database:")
    try:
        result = subprocess.run(
            ['psql', '-U', 'postgres', '-d', 'unibos_dev', '-c', 'SELECT 1;'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            click.echo("  ✅ PostgreSQL connected")
        else:
            click.echo("  ❌ PostgreSQL connection failed")
    except subprocess.TimeoutExpired:
        click.echo("  ❌ Database connection timeout")
    except FileNotFoundError:
        click.echo("  ⚠️  psql not found (PostgreSQL not installed?)")
    except Exception as e:
        click.echo(f"  ⚠️  Error: {e}")
