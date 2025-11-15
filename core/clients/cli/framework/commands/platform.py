"""
UNIBOS Platform Information Command

Display platform and hardware information.
"""

import click
from core.platform import PlatformDetector


@click.command(name='platform')
@click.option('--json', 'as_json', is_flag=True, help='Output as JSON')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information')
def platform_command(as_json, verbose):
    """🖥️  Show platform and hardware information"""

    try:
        info = PlatformDetector.detect()

        if as_json:
            import json
            click.echo(json.dumps(info.to_dict(), indent=2))
            return

        # Header
        click.echo(click.style('🖥️  Platform Information', fg='cyan', bold=True))
        click.echo()

        # System
        click.echo(click.style('System:', fg='yellow', bold=True))
        click.echo(f"  OS: {info.os_name} {info.os_version}")
        click.echo(f"  Architecture: {info.architecture}")
        click.echo(f"  Device Type: {info.device_type}")
        click.echo(f"  Hostname: {info.hostname}")
        if info.local_ip:
            click.echo(f"  Local IP: {info.local_ip}")

        # Raspberry Pi Info
        if info.is_raspberry_pi:
            click.echo()
            click.echo(click.style('Raspberry Pi:', fg='magenta', bold=True))
            click.echo(f"  Model: {info.raspberry_pi_model or 'Unknown'}")
            click.echo(f"  GPIO: {'Available' if info.has_gpio else 'Not available'}")

        # Hardware
        click.echo()
        click.echo(click.style('Hardware:', fg='yellow', bold=True))
        click.echo(f"  CPU Cores: {info.cpu_count} physical, {info.cpu_count_logical} logical")
        if verbose:
            click.echo(f"  CPU Frequency: {info.cpu_freq_mhz:.0f} MHz")
        click.echo(f"  RAM: {info.ram_available_gb:.1f} GB / {info.ram_total_gb:.1f} GB available")
        click.echo(f"  Disk: {info.disk_free_gb:.1f} GB / {info.disk_total_gb:.1f} GB free")

        # Capabilities
        click.echo()
        click.echo(click.style('Capabilities:', fg='yellow', bold=True))
        click.echo(f"  GPU: {'Yes' if info.has_gpu else 'No'}")
        click.echo(f"  Camera: {'Yes' if info.has_camera else 'No'}")
        if info.is_raspberry_pi:
            click.echo(f"  LoRa: {'Yes' if info.has_lora else 'No'}")

        # Suitability Check
        if verbose:
            click.echo()
            click.echo(click.style('Suitability:', fg='yellow', bold=True))
            click.echo(f"  Server: {'✓' if info.is_suitable_for_server() else '✗'}")
            click.echo(f"  Edge Device: {'✓' if info.is_suitable_for_edge() else '✗'}")

    except Exception as e:
        click.echo(click.style(f'✗ Error detecting platform: {e}', fg='red'))
        raise click.Abort()
