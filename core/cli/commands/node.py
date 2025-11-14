"""
UNIBOS Production CLI - Node Commands

Node identity and registration management.
"""
import click
import json
from core.instance import get_instance_identity, NodeType


@click.group(name='node')
def node_group():
    """🔷 Node identity and registration"""
    pass


@node_group.command(name='info')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def node_info(output_json):
    """Show this node's identity and capabilities

    Examples:
        unibos node info           # Human-readable output
        unibos node info --json    # JSON output
    """
    try:
        identity = get_instance_identity()
        node = identity.get_identity()

        if output_json:
            # JSON output
            click.echo(json.dumps(node.to_dict(), indent=2))
        else:
            # Human-readable output
            click.echo("\n🔷 Node Identity\n")

            # Basic info
            click.echo(f"UUID:        {node.uuid}")
            click.echo(f"Type:        {node.node_type.value}")
            click.echo(f"Hostname:    {node.hostname}")
            click.echo(f"Platform:    {node.platform}")

            # Timestamps
            click.echo(f"\nCreated:     {node.created_at}")
            click.echo(f"Last Seen:   {node.last_seen}")

            # Registration status
            if node.registered_to:
                click.echo(f"\n✅ Registered to: {node.registered_to}")
            else:
                click.echo(f"\n⚪ Not registered to any central server")

            # Capabilities
            caps = node.capabilities
            click.echo("\n🔧 Capabilities")
            click.echo(f"  RAM:          {caps.ram_gb} GB")
            click.echo(f"  Storage:      {caps.storage_gb} GB")

            # Hardware
            hw_caps = []
            if caps.has_gpu:
                hw_caps.append("GPU")
            if caps.has_camera:
                hw_caps.append("Camera")
            if caps.has_gpio:
                hw_caps.append("GPIO")
            if caps.has_lora:
                hw_caps.append("LoRa")

            if hw_caps:
                click.echo(f"  Hardware:     {', '.join(hw_caps)}")
            else:
                click.echo(f"  Hardware:     None detected")

            # Services
            services = []
            if caps.can_run_django:
                services.append("Django")
            if caps.can_run_celery:
                services.append("Celery")
            if caps.can_run_websocket:
                services.append("WebSocket")

            click.echo(f"  Services:     {', '.join(services)}")

            # Modules
            if caps.available_modules:
                click.echo(f"  Modules:      {', '.join(caps.available_modules)}")
            else:
                click.echo(f"  Modules:      None loaded")

            click.echo()

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@node_group.command(name='register')
@click.argument('central_url')
@click.option('--token', help='Registration token (if required)')
def node_register(central_url, token):
    """Register this node with a central server

    Examples:
        unibos node register https://rocksteady.example.com
        unibos node register https://central.com --token abc123
    """
    try:
        identity = get_instance_identity()

        click.echo(f"🔄 Registering with {central_url}...")

        # TODO: Send registration request to central server
        # For now, just save the registration info locally
        identity.register_with_central(central_url, token)

        click.echo(f"✅ Registered successfully")
        click.echo(f"   Node UUID: {identity.get_uuid()}")
        click.echo(f"   Central:   {central_url}")

        if token:
            click.echo(f"   Token:     {token[:8]}...")

    except Exception as e:
        click.echo(f"❌ Registration failed: {e}", err=True)
        raise click.Abort()


@node_group.command(name='peers')
def node_peers():
    """List known peer nodes

    Shows other UNIBOS nodes on the local network (via mDNS discovery).

    Examples:
        unibos node peers
    """
    # TODO: Implement mDNS discovery with zeroconf
    click.echo("🔍 Discovering peer nodes on local network...")
    click.echo("\n⚠️  Peer discovery not yet implemented")
    click.echo("   Coming in Phase 3: P2P Network Foundation\n")
