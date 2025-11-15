"""
UNIBOS Server CLI - Service Management Commands

Cross-platform service management using the platform abstraction layer.
"""
import click
from core.platform import get_service_manager, ServiceStatus


@click.group(name='service')
def service_group():
    """🔧 Manage system services"""
    pass


@service_group.command(name='start')
@click.argument('service_name')
def start_service(service_name):
    """Start a service

    Examples:
        unibos-server service start nginx
        unibos-server service start postgresql
    """
    click.echo(f"🔄 Starting {service_name}...")

    manager = get_service_manager()

    try:
        success = manager.start(service_name)

        if success:
            click.echo(f"✅ {service_name} started successfully")

            # Show status
            info = manager.status(service_name)
            if info.is_running():
                click.echo(f"   Status: {info.status.value}")
                if info.pid:
                    click.echo(f"   PID: {info.pid}")
        else:
            click.echo(f"❌ Failed to start {service_name}", err=True)
            click.echo(f"   Check service name and permissions", err=True)

    except NotImplementedError as e:
        click.echo(f"❌ {e}", err=True)
        click.echo(f"   Service manager: {manager.manager.value}", err=True)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@service_group.command(name='stop')
@click.argument('service_name')
def stop_service(service_name):
    """Stop a service

    Examples:
        unibos-server service stop nginx
        unibos-server service stop postgresql
    """
    click.echo(f"🛑 Stopping {service_name}...")

    manager = get_service_manager()

    try:
        success = manager.stop(service_name)

        if success:
            click.echo(f"✅ {service_name} stopped successfully")

            # Show status
            info = manager.status(service_name)
            click.echo(f"   Status: {info.status.value}")
        else:
            click.echo(f"❌ Failed to stop {service_name}", err=True)
            click.echo(f"   Check service name and permissions", err=True)

    except NotImplementedError as e:
        click.echo(f"❌ {e}", err=True)
        click.echo(f"   Service manager: {manager.manager.value}", err=True)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@service_group.command(name='restart')
@click.argument('service_name')
def restart_service(service_name):
    """Restart a service

    Examples:
        unibos-server service restart nginx
        unibos-server service restart postgresql
    """
    click.echo(f"🔄 Restarting {service_name}...")

    manager = get_service_manager()

    try:
        success = manager.restart(service_name)

        if success:
            click.echo(f"✅ {service_name} restarted successfully")

            # Show status
            info = manager.status(service_name)
            if info.is_running():
                click.echo(f"   Status: {info.status.value}")
                if info.pid:
                    click.echo(f"   PID: {info.pid}")
        else:
            click.echo(f"❌ Failed to restart {service_name}", err=True)
            click.echo(f"   Check service name and permissions", err=True)

    except NotImplementedError as e:
        click.echo(f"❌ {e}", err=True)
        click.echo(f"   Service manager: {manager.manager.value}", err=True)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@service_group.command(name='status')
@click.argument('service_name', required=False)
def status_service(service_name):
    """Show service status

    Examples:
        unibos-server service status nginx
        unibos-server service status        # All UNIBOS services
    """
    manager = get_service_manager()

    # If specific service requested
    if service_name:
        click.echo(f"📊 Status for {service_name}:\n")

        info = manager.status(service_name)

        # Status indicator
        if info.status == ServiceStatus.RUNNING:
            status_icon = "🟢"
        elif info.status == ServiceStatus.STOPPED:
            status_icon = "⚫"
        elif info.status == ServiceStatus.FAILED:
            status_icon = "🔴"
        else:
            status_icon = "⚪"

        click.echo(f"{status_icon} {info.name}")
        click.echo(f"   Status: {info.status.value}")
        click.echo(f"   Manager: {info.manager.value if info.manager else 'unknown'}")

        if info.pid:
            click.echo(f"   PID: {info.pid}")
        if info.uptime:
            click.echo(f"   Uptime: {info.uptime}")

    # Otherwise show all UNIBOS services
    else:
        click.echo("📊 UNIBOS Services Status:\n")

        # Common UNIBOS services to check
        services = ['nginx', 'postgresql', 'redis', 'celery']

        for svc in services:
            info = manager.status(svc)

            if info.status == ServiceStatus.RUNNING:
                status_icon = "🟢"
            elif info.status == ServiceStatus.STOPPED:
                status_icon = "⚫"
            elif info.status == ServiceStatus.FAILED:
                status_icon = "🔴"
            else:
                status_icon = "⚪"

            click.echo(f"{status_icon} {svc:15} {info.status.value}")

        click.echo(f"\n💡 Service Manager: {manager.manager.value}")
