"""
SSH Command for Manager Profile

SSH connection management for remote UNIBOS instances.
"""

import click
import subprocess
import os


@click.command('ssh')
@click.argument('target', type=click.Choice(['rocksteady', 'local'], case_sensitive=False), default='rocksteady')
@click.option('--command', '-c', help='Execute command on remote host')
def ssh_command(target, command):
    """
    SSH to UNIBOS instances

    Examples:
        unibos-dev manager ssh rocksteady
        unibos-dev manager ssh rocksteady --command "systemctl status unibos"
    """
    if target == 'local':
        click.echo("⚠️  SSH to local is not necessary")
        click.echo("   You're already on the local machine!")
        return 1

    if target == 'rocksteady':
        ssh_to_rocksteady(command)
    else:
        click.echo(f"❌ Unknown target: {target}", err=True)
        return 1

    return 0


def ssh_to_rocksteady(command: str = None):
    """SSH to rocksteady server"""
    if command:
        # Execute command remotely
        click.echo(f"🔐 Executing on rocksteady: {command}")
        click.echo()

        ssh_cmd = ['ssh', 'rocksteady', command]
        try:
            result = subprocess.run(ssh_cmd)
            return result.returncode
        except KeyboardInterrupt:
            click.echo("\n\n⚠️  Command interrupted by user")
            return 130
        except Exception as e:
            click.echo(f"\n❌ Error: {e}", err=True)
            return 1
    else:
        # Interactive SSH session
        click.echo("🔐 Opening SSH connection to rocksteady...")
        click.echo()
        click.echo("────────────────────────────────────────────────")
        click.echo("  Production Server: Oracle Cloud VM")
        click.echo("  Location: /opt/unibos")
        click.echo("  Type 'exit' to close connection")
        click.echo("────────────────────────────────────────────────")
        click.echo()

        ssh_cmd = ['ssh', 'rocksteady']
        try:
            # Use os.system for interactive TTY
            return os.system(' '.join(ssh_cmd))
        except KeyboardInterrupt:
            click.echo("\n\n⚠️  SSH connection interrupted")
            return 130
        except Exception as e:
            click.echo(f"\n❌ Error: {e}", err=True)
            return 1
