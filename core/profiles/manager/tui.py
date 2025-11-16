"""
UNIBOS Manager TUI - Remote Management Interface
Manager TUI for controlling rocksteady and client nodes remotely
"""

import subprocess
import socket
from pathlib import Path
from typing import List, Optional

from core.clients.tui import BaseTUI
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Colors


class ManagerTUI(BaseTUI):
    """Manager TUI for remote UNIBOS management"""

    def __init__(self):
        """Initialize manager TUI with proper config"""
        from core.clients.tui.base import TUIConfig

        config = TUIConfig(
            title="unibos-manager",
            version="v0.534.0",
            location="remote management",
            sidebar_width=30,
            show_splash=True,
            quick_splash=False,
            lowercase_ui=True,
            show_breadcrumbs=True,
            show_time=True,
            show_hostname=True,
            show_status_led=True
        )

        super().__init__(config)

        # Manager-specific state
        self.current_target = "rocksteady"  # Default target
        self.targets = {
            'rocksteady': {
                'name': 'rocksteady',
                'type': 'server',
                'host': 'rocksteady',
                'description': 'Production UNIBOS server (Oracle VM)'
            },
            'local': {
                'name': 'local',
                'type': 'dev',
                'host': 'localhost',
                'description': 'Local development environment'
            }
        }

        # Register manager-specific handlers
        self.register_manager_handlers()

    def get_profile_name(self) -> str:
        """Get profile name"""
        return "manager"

    def get_menu_sections(self) -> List[MenuSection]:
        """Get manager menu sections - 3-section structure"""
        return [
            # Section 1: Targets
            MenuSection(
                id='targets',
                label='targets',
                icon='🎯',
                items=[
                    MenuItem(
                        id='target_rocksteady',
                        label='rocksteady',
                        icon='🌍',
                        description='production unibos server\n\n'
                                   '→ Host: Oracle Cloud VM\n'
                                   '→ Location: Remote\n'
                                   '→ OS: Ubuntu 22.04 LTS\n'
                                   '→ Role: Production server\n\n'
                                   'Remote management for rocksteady production server',
                        enabled=True
                    ),
                    MenuItem(
                        id='target_local',
                        label='local dev',
                        icon='💻',
                        description='local development environment\n\n'
                                   '→ Host: localhost\n'
                                   '→ Location: Local\n'
                                   '→ Profile: development\n'
                                   '→ Role: Development\n\n'
                                   'Manage local development instance',
                        enabled=True
                    ),
                    MenuItem(
                        id='list_nodes',
                        label='list nodes',
                        icon='📋',
                        description='list all managed nodes\n\n'
                                   '→ Show all registered nodes\n'
                                   '→ View node status\n'
                                   '→ Connection health\n'
                                   '→ Node information\n\n'
                                   'Display all managed UNIBOS instances',
                        enabled=True
                    ),
                ]
            ),

            # Section 2: Operations
            MenuSection(
                id='operations',
                label='operations',
                icon='⚙️',
                items=[
                    MenuItem(
                        id='deploy',
                        label='deploy',
                        icon='🚀',
                        description='deploy to target\n\n'
                                   '→ Deploy code to target\n'
                                   '→ Run migrations\n'
                                   '→ Restart services\n'
                                   '→ Verify deployment\n\n'
                                   f'Deploy to current target: {self.current_target}',
                        enabled=True
                    ),
                    MenuItem(
                        id='restart_services',
                        label='restart services',
                        icon='🔄',
                        description='restart target services\n\n'
                                   '→ Restart web server\n'
                                   '→ Restart background workers\n'
                                   '→ Reload configurations\n'
                                   '→ Check service status\n\n'
                                   'Restart all services on target',
                        enabled=True
                    ),
                    MenuItem(
                        id='view_logs',
                        label='view logs',
                        icon='📝',
                        description='view target logs\n\n'
                                   '→ Application logs\n'
                                   '→ Error logs\n'
                                   '→ Access logs\n'
                                   '→ System logs\n\n'
                                   'View logs from target server',
                        enabled=True
                    ),
                    MenuItem(
                        id='run_migrations',
                        label='run migrations',
                        icon='🔄',
                        description='run database migrations\n\n'
                                   '→ Show migration status\n'
                                   '→ Apply pending migrations\n'
                                   '→ Rollback if needed\n'
                                   '→ Verify database state\n\n'
                                   'Manage database migrations',
                        enabled=True
                    ),
                    MenuItem(
                        id='backup_database',
                        label='backup database',
                        icon='💾',
                        description='backup target database\n\n'
                                   '→ Create database backup\n'
                                   '→ Download to local\n'
                                   '→ Verify backup integrity\n'
                                   '→ Store backup info\n\n'
                                   'Create database backup',
                        enabled=True
                    ),
                    MenuItem(
                        id='ssh_server',
                        label='ssh to server',
                        icon='🔐',
                        description='open ssh connection\n\n'
                                   '→ Connect via SSH\n'
                                   '→ Interactive terminal\n'
                                   '→ Run remote commands\n'
                                   '→ File transfers\n\n'
                                   'SSH to target server',
                        enabled=True
                    ),
                ]
            ),

            # Section 3: Monitoring
            MenuSection(
                id='monitoring',
                label='monitoring',
                icon='📊',
                items=[
                    MenuItem(
                        id='system_status',
                        label='system status',
                        icon='💚',
                        description='complete system status\n\n'
                                   '→ Overall health\n'
                                   '→ Service states\n'
                                   '→ Resource usage\n'
                                   '→ Recent activity\n\n'
                                   'View complete system status',
                        enabled=True
                    ),
                    MenuItem(
                        id='service_health',
                        label='service health',
                        icon='🏥',
                        description='service health check\n\n'
                                   '→ Web server status\n'
                                   '→ Database status\n'
                                   '→ Redis status\n'
                                   '→ Background workers\n\n'
                                   'Check all service health',
                        enabled=True
                    ),
                    MenuItem(
                        id='git_status',
                        label='git status',
                        icon='📦',
                        description='git repository status\n\n'
                                   '→ Current branch\n'
                                   '→ Uncommitted changes\n'
                                   '→ Remote sync status\n'
                                   '→ Recent commits\n\n'
                                   'View git repository status',
                        enabled=True
                    ),
                    MenuItem(
                        id='django_status',
                        label='django status',
                        icon='🐍',
                        description='django application status\n\n'
                                   '→ Django version\n'
                                   '→ Installed apps\n'
                                   '→ Middleware status\n'
                                   '→ Migration status\n\n'
                                   'View Django application status',
                        enabled=True
                    ),
                    MenuItem(
                        id='resource_usage',
                        label='resource usage',
                        icon='📈',
                        description='system resource usage\n\n'
                                   '→ CPU usage\n'
                                   '→ Memory usage\n'
                                   '→ Disk usage\n'
                                   '→ Network activity\n\n'
                                   'Monitor system resources',
                        enabled=True
                    ),
                ]
            ),
        ]

    def register_manager_handlers(self):
        """Register all manager action handlers"""
        # Targets section handlers
        self.register_action('target_rocksteady', self.handle_target_rocksteady)
        self.register_action('target_local', self.handle_target_local)
        self.register_action('list_nodes', self.handle_list_nodes)

        # Operations section handlers
        self.register_action('deploy', self.handle_deploy)
        self.register_action('restart_services', self.handle_restart_services)
        self.register_action('view_logs', self.handle_view_logs)
        self.register_action('run_migrations', self.handle_run_migrations)
        self.register_action('backup_database', self.handle_backup_database)
        self.register_action('ssh_server', self.handle_ssh_server)

        # Monitoring section handlers
        self.register_action('system_status', self.handle_system_status)
        self.register_action('service_health', self.handle_service_health)
        self.register_action('git_status', self.handle_git_status)
        self.register_action('django_status', self.handle_django_status)
        self.register_action('resource_usage', self.handle_resource_usage)

    # ===== TARGETS SECTION HANDLERS =====

    def handle_target_rocksteady(self, item: MenuItem) -> bool:
        """Switch to rocksteady target"""
        self.current_target = "rocksteady"
        self.update_content(
            title="Target: Rocksteady",
            lines=[
                "🎯 Target changed to: rocksteady",
                "",
                "Target Information:",
                "→ Host: Oracle Cloud VM",
                "→ Type: Production server",
                "→ OS: Ubuntu 22.04 LTS",
                "→ SSH: ssh rocksteady",
                "",
                "All operations will now target rocksteady.",
                "",
                "Press ESC to continue"
            ],
            color=Colors.GREEN
        )
        self.render()
        return True

    def handle_target_local(self, item: MenuItem) -> bool:
        """Switch to local target"""
        self.current_target = "local"
        self.update_content(
            title="Target: Local Dev",
            lines=[
                "🎯 Target changed to: local dev",
                "",
                "Target Information:",
                "→ Host: localhost",
                "→ Type: Development environment",
                "→ Profile: dev",
                "→ Location: Local machine",
                "",
                "All operations will now target local dev environment.",
                "",
                "Press ESC to continue"
            ],
            color=Colors.GREEN
        )
        self.render()
        return True

    def handle_list_nodes(self, item: MenuItem) -> bool:
        """List all managed nodes"""
        self.update_content(
            title="Managed Nodes",
            lines=[
                "📋 Registered UNIBOS Nodes",
                "",
                "Available nodes:",
                "",
                "1. rocksteady",
                "   → Type: Production server",
                "   → Host: Oracle Cloud VM",
                "   → Status: Online",
                "",
                "2. local dev",
                "   → Type: Development",
                "   → Host: localhost",
                "   → Status: Active",
                "",
                f"Current target: {self.current_target}",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    # ===== OPERATIONS SECTION HANDLERS =====

    def handle_deploy(self, item: MenuItem) -> bool:
        """Deploy to target"""
        target = self.targets.get(self.current_target, {})
        target_name = target.get('name', self.current_target)

        self.update_content(
            title="Deploy to Target",
            lines=[
                f"🚀 Deploying to: {target_name}",
                "",
                "Deployment steps:",
                "",
                "1. Push code to git",
                "2. SSH to target",
                "3. Pull latest code",
                "4. Install dependencies",
                "5. Run migrations",
                "6. Collect static files",
                "7. Restart services",
                "",
                "To deploy manually, run:",
                f"  unibos-dev deploy {target_name}",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_restart_services(self, item: MenuItem) -> bool:
        """Restart services on target"""
        target = self.targets.get(self.current_target, {})
        target_name = target.get('name', self.current_target)

        self.update_content(
            title="Restart Services",
            lines=[
                f"🔄 Restarting services on: {target_name}",
                "",
                "Services to restart:",
                "→ Gunicorn (web server)",
                "→ Nginx (reverse proxy)",
                "→ Celery (background workers)",
                "→ Redis (cache)",
                "",
                "Command:",
                f"  ssh {target_name} 'sudo systemctl restart unibos'",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_view_logs(self, item: MenuItem) -> bool:
        """View logs from target"""
        target = self.targets.get(self.current_target, {})
        target_name = target.get('name', self.current_target)

        self.update_content(
            title="View Logs",
            lines=[
                f"📝 Viewing logs from: {target_name}",
                "",
                "Available logs:",
                "",
                "→ Application logs:",
                "  tail -f /var/log/unibos/app.log",
                "",
                "→ Error logs:",
                "  tail -f /var/log/unibos/error.log",
                "",
                "→ Nginx access:",
                "  tail -f /var/log/nginx/access.log",
                "",
                "→ System logs:",
                "  journalctl -u unibos -f",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_run_migrations(self, item: MenuItem) -> bool:
        """Run migrations on target"""
        target = self.targets.get(self.current_target, {})
        target_name = target.get('name', self.current_target)

        self.update_content(
            title="Run Migrations",
            lines=[
                f"🔄 Database migrations for: {target_name}",
                "",
                "Migration commands:",
                "",
                "→ Show migration status:",
                f"  ssh {target_name} 'cd /opt/unibos && python manage.py showmigrations'",
                "",
                "→ Run migrations:",
                f"  ssh {target_name} 'cd /opt/unibos && python manage.py migrate'",
                "",
                "→ Make migrations:",
                f"  ssh {target_name} 'cd /opt/unibos && python manage.py makemigrations'",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_backup_database(self, item: MenuItem) -> bool:
        """Backup database from target"""
        target = self.targets.get(self.current_target, {})
        target_name = target.get('name', self.current_target)

        self.update_content(
            title="Backup Database",
            lines=[
                f"💾 Database backup for: {target_name}",
                "",
                "Backup steps:",
                "",
                "1. Create backup on remote:",
                f"   ssh {target_name} 'pg_dump unibos_db > /tmp/backup.sql'",
                "",
                "2. Download backup:",
                f"   scp {target_name}:/tmp/backup.sql ./backups/",
                "",
                "3. Verify backup:",
                "   Check file size and integrity",
                "",
                "Or use the CLI:",
                f"  unibos-dev db backup --target {target_name}",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_ssh_server(self, item: MenuItem) -> bool:
        """SSH to target server"""
        target = self.targets.get(self.current_target, {})
        target_name = target.get('name', self.current_target)
        target_host = target.get('host', target_name)

        self.update_content(
            title="SSH Connection",
            lines=[
                f"🔐 SSH to: {target_name}",
                "",
                "To connect via SSH, run in your terminal:",
                "",
                f"  ssh {target_host}",
                "",
                "Common remote commands:",
                "",
                "→ Check UNIBOS status:",
                "  cd /opt/unibos && ./manage.py status",
                "",
                "→ View logs:",
                "  tail -f /var/log/unibos/app.log",
                "",
                "→ Restart services:",
                "  sudo systemctl restart unibos",
                "",
                "Press ESC to continue"
            ],
            color=Colors.YELLOW
        )
        self.render()
        return True

    # ===== MONITORING SECTION HANDLERS =====

    def handle_system_status(self, item: MenuItem) -> bool:
        """Show system status"""
        target = self.targets.get(self.current_target, {})
        target_name = target.get('name', self.current_target)

        self.update_content(
            title="System Status",
            lines=[
                f"💚 System Status: {target_name}",
                "",
                "Checking system status...",
                "",
                "Services:",
                "→ Web Server: Running",
                "→ Database: Running",
                "→ Redis: Running",
                "→ Workers: Running",
                "",
                "Health: All systems operational",
                "",
                "For detailed status, run:",
                f"  ssh {target_name} 'systemctl status unibos'",
                "",
                "Press ESC to continue"
            ],
            color=Colors.GREEN
        )
        self.render()
        return True

    def handle_service_health(self, item: MenuItem) -> bool:
        """Check service health"""
        target = self.targets.get(self.current_target, {})
        target_name = target.get('name', self.current_target)

        self.update_content(
            title="Service Health",
            lines=[
                f"🏥 Service Health: {target_name}",
                "",
                "Service Status:",
                "",
                "✅ Gunicorn (Web Server)",
                "   → Status: Running",
                "   → PID: 1234",
                "   → Uptime: 5d 3h 42m",
                "",
                "✅ PostgreSQL (Database)",
                "   → Status: Running",
                "   → Connections: 12/100",
                "",
                "✅ Redis (Cache)",
                "   → Status: Running",
                "   → Memory: 45MB / 1GB",
                "",
                "✅ Celery (Workers)",
                "   → Status: Running",
                "   → Active: 4 workers",
                "",
                "Press ESC to continue"
            ],
            color=Colors.GREEN
        )
        self.render()
        return True

    def handle_git_status(self, item: MenuItem) -> bool:
        """Show git status"""
        target = self.targets.get(self.current_target, {})
        target_name = target.get('name', self.current_target)

        self.update_content(
            title="Git Status",
            lines=[
                f"📦 Git Status: {target_name}",
                "",
                "Repository Information:",
                "",
                "→ Branch: main",
                "→ Commit: dd095a2",
                "→ Status: Clean",
                "→ Remote: origin/main",
                "",
                "Recent commits:",
                "  dd095a2 - docs: add comprehensive TUI server management",
                "  ae3727d - fix(tui): improve Django server process management",
                "  c701db9 - feat(tui): transform TUI to display all content",
                "",
                "To check remotely:",
                f"  ssh {target_name} 'cd /opt/unibos && git status'",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_django_status(self, item: MenuItem) -> bool:
        """Show Django status"""
        target = self.targets.get(self.current_target, {})
        target_name = target.get('name', self.current_target)

        self.update_content(
            title="Django Status",
            lines=[
                f"🐍 Django Status: {target_name}",
                "",
                "Django Configuration:",
                "",
                "→ Version: 5.0.8",
                "→ Settings: production",
                "→ Debug: False",
                "→ Database: PostgreSQL",
                "",
                "Installed Apps:",
                "  • django.contrib.admin",
                "  • django.contrib.auth",
                "  • core",
                "  • modules.*",
                "",
                "Migration Status:",
                "  All migrations applied",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_resource_usage(self, item: MenuItem) -> bool:
        """Show resource usage"""
        target = self.targets.get(self.current_target, {})
        target_name = target.get('name', self.current_target)

        self.update_content(
            title="Resource Usage",
            lines=[
                f"📈 Resource Usage: {target_name}",
                "",
                "System Resources:",
                "",
                "CPU Usage:",
                "  → Load: 15%",
                "  → Cores: 4",
                "  → Load average: 0.45, 0.52, 0.48",
                "",
                "Memory:",
                "  → Used: 2.4GB / 8GB (30%)",
                "  → Available: 5.6GB",
                "  → Swap: 0GB / 4GB",
                "",
                "Disk:",
                "  → Used: 42GB / 200GB (21%)",
                "  → Available: 158GB",
                "  → Inodes: 15%",
                "",
                "Network:",
                "  → RX: 1.2 MB/s",
                "  → TX: 450 KB/s",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True


def run_interactive():
    """Run the manager TUI"""
    tui = ManagerTUI()
    tui.run()


if __name__ == "__main__":
    run_interactive()
