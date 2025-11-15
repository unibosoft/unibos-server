"""
UNIBOS Production CLI - Module Commands

Module discovery, management, and information.
"""
import click
import json
from core.modules import get_module_registry


@click.group(name='module')
def module_group():
    """📦 Module management"""
    pass


@module_group.command(name='list')
@click.option('--enabled', is_flag=True, help='Show only enabled modules')
@click.option('--available', is_flag=True, help='Show only available (disabled) modules')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def module_list(enabled, available, output_json):
    """List all modules

    Examples:
        unibos module list              # All modules
        unibos module list --enabled    # Only enabled
        unibos module list --available  # Only available
        unibos module list --json       # JSON output
    """
    try:
        registry = get_module_registry()

        # Get modules based on filter
        if enabled:
            modules = registry.get_enabled_modules()
        elif available:
            modules = registry.get_available_modules()
        else:
            modules = registry.get_all_modules()

        if output_json:
            # JSON output
            data = []
            for m in modules:
                data.append({
                    'id': m.id,
                    'name': m.name,
                    'version': m.version,
                    'description': m.description,
                    'enabled': m.enabled,
                    'capabilities': m.capabilities,
                })
            click.echo(json.dumps(data, indent=2))
        else:
            # Human-readable output
            if not modules:
                click.echo("\n⚪ No modules found\n")
                return

            click.echo(f"\n📦 UNIBOS Modules ({len(modules)} total)\n")

            for m in modules:
                # Status indicator
                if m.enabled:
                    status_icon = "✅"
                else:
                    status_icon = "⚪"

                # Capabilities
                caps = []
                if m.has_backend():
                    caps.append("Backend")
                if m.has_web():
                    caps.append("Web")
                if m.has_mobile():
                    caps.append("Mobile")
                if m.has_cli():
                    caps.append("CLI")
                if m.is_realtime():
                    caps.append("Realtime")

                caps_str = ", ".join(caps) if caps else "None"

                click.echo(f"{status_icon} {m.icon}  {m.name} (v{m.version})")
                click.echo(f"   ID: {m.id}")
                click.echo(f"   {m.description}")
                click.echo(f"   Capabilities: {caps_str}")
                click.echo()

            # Show stats
            stats = registry.get_module_stats()
            click.echo(f"📊 Stats: {stats['enabled']} enabled, {stats['available']} available\n")

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@module_group.command(name='info')
@click.argument('module_id')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def module_info(module_id, output_json):
    """Show detailed module information

    Examples:
        unibos module info birlikteyiz
        unibos module info store --json
    """
    try:
        registry = get_module_registry()
        module = registry.get_module(module_id)

        if not module:
            click.echo(f"❌ Module '{module_id}' not found", err=True)
            raise click.Abort()

        if output_json:
            # JSON output
            click.echo(json.dumps(module.metadata, indent=2))
        else:
            # Human-readable output
            click.echo(f"\n{module.icon}  {module.name}")
            click.echo(f"{'=' * 60}\n")

            click.echo(f"ID:          {module.id}")
            click.echo(f"Version:     {module.version}")
            click.echo(f"Author:      {module.author}")
            click.echo(f"Status:      {'✅ Enabled' if module.enabled else '⚪ Disabled'}")

            click.echo(f"\nDescription:")
            click.echo(f"  {module.description}")

            # Capabilities
            click.echo(f"\n🔧 Capabilities:")
            if module.has_backend():
                click.echo(f"  ✓ Backend API")
            if module.has_web():
                click.echo(f"  ✓ Web UI")
            if module.has_mobile():
                click.echo(f"  ✓ Mobile App")
            if module.has_cli():
                click.echo(f"  ✓ CLI Commands")
            if module.is_realtime():
                click.echo(f"  ✓ Real-time (WebSocket)")

            # Dependencies
            deps = module.dependencies
            if deps:
                click.echo(f"\n📦 Dependencies:")

                core_deps = deps.get('core_modules', [])
                if core_deps:
                    click.echo(f"  Core: {', '.join(core_deps)}")

                module_deps = deps.get('modules', [])
                if module_deps:
                    click.echo(f"  Modules: {', '.join(module_deps)}")

                python_deps = deps.get('python_packages', [])
                if python_deps:
                    click.echo(f"  Python: {', '.join(python_deps[:5])}")
                    if len(python_deps) > 5:
                        click.echo(f"          ... and {len(python_deps) - 5} more")

            # Platform compatibility
            if module.platforms:
                click.echo(f"\n💻 Platforms: {', '.join(module.platforms)}")

            # Path
            click.echo(f"\n📁 Location: {module.module_path}")

            click.echo()

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@module_group.command(name='enable')
@click.argument('module_id')
def module_enable(module_id):
    """Enable a module

    Examples:
        unibos module enable store
        unibos module enable movies
    """
    try:
        registry = get_module_registry()
        module = registry.get_module(module_id)

        if not module:
            click.echo(f"❌ Module '{module_id}' not found", err=True)
            raise click.Abort()

        if module.enabled:
            click.echo(f"⚠️  Module '{module.name}' is already enabled")
            return

        click.echo(f"🔄 Enabling {module.icon}  {module.name}...")

        success = registry.enable_module(module_id)

        if success:
            click.echo(f"✅ Module '{module.name}' enabled")
            click.echo(f"   Restart Django to apply changes")
        else:
            click.echo(f"❌ Failed to enable module", err=True)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@module_group.command(name='disable')
@click.argument('module_id')
def module_disable(module_id):
    """Disable a module

    Examples:
        unibos module disable store
        unibos module disable movies
    """
    try:
        registry = get_module_registry()
        module = registry.get_module(module_id)

        if not module:
            click.echo(f"❌ Module '{module_id}' not found", err=True)
            raise click.Abort()

        if not module.enabled:
            click.echo(f"⚠️  Module '{module.name}' is already disabled")
            return

        click.echo(f"🔄 Disabling {module.icon}  {module.name}...")

        success = registry.disable_module(module_id)

        if success:
            click.echo(f"✅ Module '{module.name}' disabled")
            click.echo(f"   Restart Django to apply changes")
        else:
            click.echo(f"❌ Failed to disable module", err=True)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@module_group.command(name='stats')
def module_stats():
    """Show module statistics

    Examples:
        unibos module stats
    """
    try:
        registry = get_module_registry()
        stats = registry.get_module_stats()

        click.echo("\n📊 Module Statistics\n")

        click.echo(f"Total Modules:    {stats['total']}")
        click.echo(f"Enabled:          {stats['enabled']}")
        click.echo(f"Available:        {stats['available']}")

        click.echo(f"\nBy Capability:")
        caps = stats['by_capability']
        click.echo(f"  Backend:        {caps['backend']}")
        click.echo(f"  Web UI:         {caps['web']}")
        click.echo(f"  Mobile:         {caps['mobile']}")
        click.echo(f"  CLI:            {caps['cli']}")
        click.echo(f"  Real-time:      {caps['realtime']}")

        click.echo()

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()
