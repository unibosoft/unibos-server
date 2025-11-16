"""
UNIBOS-SERVER TUI - Production Server Management
Server TUI for rocksteady.fun production server operations
"""

import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.clients.tui import BaseTUI
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Colors


class ServerTUI(BaseTUI):
    """Production server TUI for rocksteady management"""

    def __init__(self):
        """Initialize server TUI with proper config"""
        from core.clients.tui.base import TUIConfig

        config = TUIConfig(
            title="unibos-server",
            version="v0.534.0",
            location="rocksteady.fun",
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

        # Register server-specific handlers
        self.register_server_handlers()

    def get_profile_name(self) -> str:
        """Get profile name"""
        return "server"

    def get_menu_sections(self) -> List[MenuSection]:
        """Get server menu sections - 3-section structure"""
        return [
            # Section 1: Services (Server services management)
            MenuSection(
                id='services',
                label='services',
                icon='⚙️',
                items=[
                    MenuItem(
                        id='django_service',
                        label='django application',
                        icon='🐍',
                        description='django web application\n\n'
                                   '→ Start/stop Django app\n'
                                   '→ Check service status\n'
                                   '→ View application logs\n'
                                   '→ Restart gunicorn\n\n'
                                   'Manage Django application service',
                        enabled=True
                    ),
                    MenuItem(
                        id='postgresql_service',
                        label='postgresql database',
                        icon='🗄️',
                        description='postgresql database service\n\n'
                                   '→ Database service status\n'
                                   '→ Connection monitoring\n'
                                   '→ Performance tuning\n'
                                   '→ Vacuum operations\n\n'
                                   'Manage PostgreSQL database',
                        enabled=True
                    ),
                    MenuItem(
                        id='nginx_service',
                        label='nginx web server',
                        icon='🌐',
                        description='nginx reverse proxy\n\n'
                                   '→ Web server status\n'
                                   '→ Configuration reload\n'
                                   '→ SSL certificates\n'
                                   '→ Access logs\n\n'
                                   'Manage Nginx web server',
                        enabled=True
                    ),
                    MenuItem(
                        id='systemd_services',
                        label='systemd services',
                        icon='🔧',
                        description='system services overview\n\n'
                                   '→ All service status\n'
                                   '→ Enable/disable services\n'
                                   '→ Service dependencies\n'
                                   '→ System logs\n\n'
                                   'Manage systemd services',
                        enabled=True
                    ),
                    MenuItem(
                        id='background_workers',
                        label='background workers',
                        icon='👷',
                        description='celery background tasks\n\n'
                                   '→ Worker status\n'
                                   '→ Task queue monitoring\n'
                                   '→ Restart workers\n'
                                   '→ View worker logs\n\n'
                                   'Manage background workers',
                        enabled=True
                    ),
                ]
            ),

            # Section 2: Operations (Server operations)
            MenuSection(
                id='operations',
                label='operations',
                icon='🛠️',
                items=[
                    MenuItem(
                        id='view_logs',
                        label='view logs',
                        icon='📝',
                        description='application and system logs\n\n'
                                   '→ Django application logs\n'
                                   '→ Nginx access/error logs\n'
                                   '→ PostgreSQL logs\n'
                                   '→ System journal logs\n\n'
                                   'View server logs',
                        enabled=True
                    ),
                    MenuItem(
                        id='restart_all',
                        label='restart all',
                        icon='🔄',
                        description='full server restart\n\n'
                                   '→ Restart all services\n'
                                   '→ Graceful shutdown\n'
                                   '→ Service verification\n'
                                   '→ Health check\n\n'
                                   'Restart all server services',
                        enabled=True
                    ),
                    MenuItem(
                        id='database_backup',
                        label='database backup',
                        icon='💾',
                        description='backup database\n\n'
                                   '→ Create PostgreSQL dump\n'
                                   '→ Verify backup integrity\n'
                                   '→ Store backup file\n'
                                   '→ Backup rotation\n\n'
                                   'Create database backup',
                        enabled=True
                    ),
                    MenuItem(
                        id='update_system',
                        label='update system',
                        icon='🚀',
                        description='pull code, migrate, restart\n\n'
                                   '→ Pull latest code from git\n'
                                   '→ Install dependencies\n'
                                   '→ Run migrations\n'
                                   '→ Collect static files\n'
                                   '→ Restart services\n\n'
                                   'Full system update',
                        enabled=True
                    ),
                    MenuItem(
                        id='maintenance_mode',
                        label='maintenance mode',
                        icon='🚧',
                        description='enable/disable maintenance\n\n'
                                   '→ Toggle maintenance mode\n'
                                   '→ Custom maintenance page\n'
                                   '→ Service shutdown\n'
                                   '→ Scheduled maintenance\n\n'
                                   'Maintenance mode control',
                        enabled=True
                    ),
                ]
            ),

            # Section 3: Monitoring (Server monitoring)
            MenuSection(
                id='monitoring',
                label='monitoring',
                icon='📊',
                items=[
                    MenuItem(
                        id='system_status',
                        label='system status',
                        icon='💚',
                        description='cpu, memory, disk, uptime\n\n'
                                   '→ CPU usage and load\n'
                                   '→ Memory consumption\n'
                                   '→ Disk space usage\n'
                                   '→ System uptime\n\n'
                                   'Complete system status',
                        enabled=True
                    ),
                    MenuItem(
                        id='service_health',
                        label='service health',
                        icon='🏥',
                        description='all services status\n\n'
                                   '→ Django health check\n'
                                   '→ Database connections\n'
                                   '→ Redis status\n'
                                   '→ Service uptime\n\n'
                                   'Check all service health',
                        enabled=True
                    ),
                    MenuItem(
                        id='active_users',
                        label='active users',
                        icon='👥',
                        description='connected users\n\n'
                                   '→ Current active sessions\n'
                                   '→ SSH connections\n'
                                   '→ Web sessions\n'
                                   '→ User activity\n\n'
                                   'Monitor active users',
                        enabled=True
                    ),
                    MenuItem(
                        id='database_stats',
                        label='database stats',
                        icon='📈',
                        description='db size, connections\n\n'
                                   '→ Database size\n'
                                   '→ Active connections\n'
                                   '→ Query performance\n'
                                   '→ Table statistics\n\n'
                                   'Database statistics',
                        enabled=True
                    ),
                    MenuItem(
                        id='error_logs',
                        label='error logs',
                        icon='❌',
                        description='recent errors\n\n'
                                   '→ Application errors\n'
                                   '→ System errors\n'
                                   '→ Database errors\n'
                                   '→ Error analysis\n\n'
                                   'View recent errors',
                        enabled=True
                    ),
                ]
            ),
        ]

    def register_server_handlers(self):
        """Register all server action handlers"""
        # Services section handlers
        self.register_action('django_service', self.handle_django_service)
        self.register_action('postgresql_service', self.handle_postgresql_service)
        self.register_action('nginx_service', self.handle_nginx_service)
        self.register_action('systemd_services', self.handle_systemd_services)
        self.register_action('background_workers', self.handle_background_workers)

        # Operations section handlers
        self.register_action('view_logs', self.handle_view_logs)
        self.register_action('restart_all', self.handle_restart_all)
        self.register_action('database_backup', self.handle_database_backup)
        self.register_action('update_system', self.handle_update_system)
        self.register_action('maintenance_mode', self.handle_maintenance_mode)

        # Monitoring section handlers
        self.register_action('system_status', self.handle_system_status)
        self.register_action('service_health', self.handle_service_health)
        self.register_action('active_users', self.handle_active_users)
        self.register_action('database_stats', self.handle_database_stats)
        self.register_action('error_logs', self.handle_error_logs)

    # ===== SERVICES SECTION HANDLERS =====

    def handle_django_service(self, item: MenuItem) -> bool:
        """Manage Django application service"""
        self.update_content(
            title="Django Application Service",
            lines=[
                "🐍 Django Application Management",
                "",
                "Service Control:",
                "",
                "→ Check status:",
                "  sudo systemctl status gunicorn",
                "",
                "→ Restart Django:",
                "  sudo systemctl restart gunicorn",
                "",
                "→ View logs:",
                "  sudo journalctl -u gunicorn -f",
                "",
                "→ Reload application:",
                "  sudo systemctl reload gunicorn",
                "",
                "Configuration:",
                "  /etc/systemd/system/gunicorn.service",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_postgresql_service(self, item: MenuItem) -> bool:
        """Manage PostgreSQL database service"""
        self.update_content(
            title="PostgreSQL Database Service",
            lines=[
                "🗄️ PostgreSQL Database Management",
                "",
                "Service Control:",
                "",
                "→ Check status:",
                "  sudo systemctl status postgresql",
                "",
                "→ Restart database:",
                "  sudo systemctl restart postgresql",
                "",
                "→ View connections:",
                "  sudo -u postgres psql -c 'SELECT count(*) FROM pg_stat_activity;'",
                "",
                "→ Database shell:",
                "  sudo -u postgres psql unibos_db",
                "",
                "Performance:",
                "  sudo -u postgres psql -c 'VACUUM ANALYZE;'",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_nginx_service(self, item: MenuItem) -> bool:
        """Manage Nginx web server"""
        self.update_content(
            title="Nginx Web Server",
            lines=[
                "🌐 Nginx Web Server Management",
                "",
                "Service Control:",
                "",
                "→ Check status:",
                "  sudo systemctl status nginx",
                "",
                "→ Restart Nginx:",
                "  sudo systemctl restart nginx",
                "",
                "→ Reload configuration:",
                "  sudo nginx -s reload",
                "",
                "→ Test configuration:",
                "  sudo nginx -t",
                "",
                "→ View access logs:",
                "  tail -f /var/log/nginx/access.log",
                "",
                "→ View error logs:",
                "  tail -f /var/log/nginx/error.log",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_systemd_services(self, item: MenuItem) -> bool:
        """View all systemd services"""
        self.update_content(
            title="Systemd Services",
            lines=[
                "🔧 System Services Overview",
                "",
                "UNIBOS Services:",
                "",
                "→ List all services:",
                "  systemctl list-units --type=service",
                "",
                "→ UNIBOS services:",
                "  systemctl list-units 'unibos*' 'gunicorn*' 'celery*'",
                "",
                "→ Failed services:",
                "  systemctl --failed",
                "",
                "→ Service status:",
                "  systemctl status <service-name>",
                "",
                "→ Enable service:",
                "  sudo systemctl enable <service-name>",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_background_workers(self, item: MenuItem) -> bool:
        """Manage Celery background workers"""
        self.update_content(
            title="Background Workers",
            lines=[
                "👷 Celery Background Workers",
                "",
                "Worker Control:",
                "",
                "→ Check worker status:",
                "  sudo systemctl status celery",
                "",
                "→ Restart workers:",
                "  sudo systemctl restart celery",
                "",
                "→ View worker logs:",
                "  sudo journalctl -u celery -f",
                "",
                "→ Inspect active tasks:",
                "  celery -A core inspect active",
                "",
                "→ Queue statistics:",
                "  celery -A core inspect stats",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    # ===== OPERATIONS SECTION HANDLERS =====

    def handle_view_logs(self, item: MenuItem) -> bool:
        """View server logs"""
        self.update_content(
            title="View Logs",
            lines=[
                "📝 Server Logs",
                "",
                "Available Logs:",
                "",
                "→ Django application:",
                "  tail -f /var/log/unibos/django.log",
                "",
                "→ Nginx access:",
                "  tail -f /var/log/nginx/access.log",
                "",
                "→ Nginx errors:",
                "  tail -f /var/log/nginx/error.log",
                "",
                "→ System journal:",
                "  sudo journalctl -f",
                "",
                "→ Service logs:",
                "  sudo journalctl -u gunicorn -f",
                "  sudo journalctl -u celery -f",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_restart_all(self, item: MenuItem) -> bool:
        """Restart all services"""
        self.update_content(
            title="Restart All Services",
            lines=[
                "🔄 Full Server Restart",
                "",
                "This will restart all UNIBOS services:",
                "",
                "1. Stop background workers",
                "2. Stop Django application",
                "3. Reload Nginx",
                "4. Start Django application",
                "5. Start background workers",
                "",
                "Commands:",
                "",
                "  sudo systemctl restart gunicorn",
                "  sudo systemctl restart celery",
                "  sudo systemctl reload nginx",
                "",
                "Or use combined command:",
                "  sudo systemctl restart gunicorn celery && sudo systemctl reload nginx",
                "",
                "Press ESC to continue"
            ],
            color=Colors.YELLOW
        )
        self.render()
        return True

    def handle_database_backup(self, item: MenuItem) -> bool:
        """Create database backup"""
        self.update_content(
            title="Database Backup",
            lines=[
                "💾 PostgreSQL Database Backup",
                "",
                "Backup Commands:",
                "",
                "→ Create backup:",
                "  sudo -u postgres pg_dump unibos_db > backup_$(date +%Y%m%d_%H%M%S).sql",
                "",
                "→ Create compressed backup:",
                "  sudo -u postgres pg_dump unibos_db | gzip > backup.sql.gz",
                "",
                "→ Backup with schema:",
                "  sudo -u postgres pg_dump -Fc unibos_db > backup.dump",
                "",
                "→ List backups:",
                "  ls -lh /var/backups/unibos/",
                "",
                "→ Restore from backup:",
                "  sudo -u postgres psql unibos_db < backup.sql",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_update_system(self, item: MenuItem) -> bool:
        """Update system - pull, migrate, restart"""
        self.update_content(
            title="System Update",
            lines=[
                "🚀 Full System Update",
                "",
                "Update Procedure:",
                "",
                "1. Pull latest code:",
                "   cd /opt/unibos && git pull",
                "",
                "2. Install dependencies:",
                "   pip install -r requirements.txt",
                "",
                "3. Run migrations:",
                "   python manage.py migrate",
                "",
                "4. Collect static files:",
                "   python manage.py collectstatic --noinput",
                "",
                "5. Restart services:",
                "   sudo systemctl restart gunicorn celery",
                "",
                "6. Verify deployment:",
                "   curl http://localhost/health",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_maintenance_mode(self, item: MenuItem) -> bool:
        """Toggle maintenance mode"""
        self.update_content(
            title="Maintenance Mode",
            lines=[
                "🚧 Maintenance Mode Control",
                "",
                "Enable Maintenance:",
                "",
                "→ Create maintenance file:",
                "  touch /opt/unibos/.maintenance",
                "",
                "→ Stop services:",
                "  sudo systemctl stop gunicorn celery",
                "",
                "→ Show maintenance page (Nginx):",
                "  # Configure Nginx to show maintenance page",
                "",
                "Disable Maintenance:",
                "",
                "→ Remove maintenance file:",
                "  rm /opt/unibos/.maintenance",
                "",
                "→ Start services:",
                "  sudo systemctl start gunicorn celery",
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
        self.update_content(
            title="System Status",
            lines=[
                "💚 System Status - Rocksteady",
                "",
                "System Resources:",
                "",
                "→ CPU usage:",
                "  top -bn1 | grep 'Cpu(s)'",
                "",
                "→ Memory usage:",
                "  free -h",
                "",
                "→ Disk usage:",
                "  df -h",
                "",
                "→ System uptime:",
                "  uptime",
                "",
                "→ Load average:",
                "  cat /proc/loadavg",
                "",
                "→ Process count:",
                "  ps aux | wc -l",
                "",
                "Press ESC to continue"
            ],
            color=Colors.GREEN
        )
        self.render()
        return True

    def handle_service_health(self, item: MenuItem) -> bool:
        """Check service health"""
        self.update_content(
            title="Service Health",
            lines=[
                "🏥 Service Health Check",
                "",
                "Check All Services:",
                "",
                "→ Django:",
                "  systemctl is-active gunicorn",
                "  curl http://localhost:8000/health",
                "",
                "→ PostgreSQL:",
                "  systemctl is-active postgresql",
                "  sudo -u postgres psql -c 'SELECT 1;'",
                "",
                "→ Redis:",
                "  systemctl is-active redis",
                "  redis-cli ping",
                "",
                "→ Nginx:",
                "  systemctl is-active nginx",
                "  curl -I http://localhost",
                "",
                "Press ESC to continue"
            ],
            color=Colors.GREEN
        )
        self.render()
        return True

    def handle_active_users(self, item: MenuItem) -> bool:
        """Show active users"""
        self.update_content(
            title="Active Users",
            lines=[
                "👥 Active Users and Sessions",
                "",
                "User Monitoring:",
                "",
                "→ Logged in users:",
                "  who",
                "",
                "→ User sessions:",
                "  w",
                "",
                "→ Last logins:",
                "  last -10",
                "",
                "→ SSH connections:",
                "  netstat -tnpa | grep 'ESTABLISHED.*sshd'",
                "",
                "→ Active web sessions:",
                "  # Check Django session table",
                "  sudo -u postgres psql -c 'SELECT count(*) FROM django_session;'",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_database_stats(self, item: MenuItem) -> bool:
        """Show database statistics"""
        self.update_content(
            title="Database Statistics",
            lines=[
                "📈 Database Statistics",
                "",
                "PostgreSQL Stats:",
                "",
                "→ Database size:",
                "  sudo -u postgres psql -c \"SELECT pg_size_pretty(pg_database_size('unibos_db'));\"",
                "",
                "→ Active connections:",
                "  sudo -u postgres psql -c 'SELECT count(*) FROM pg_stat_activity;'",
                "",
                "→ Table sizes:",
                "  sudo -u postgres psql -c \"SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) FROM pg_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;\"",
                "",
                "→ Query performance:",
                "  sudo -u postgres psql -c 'SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;'",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_error_logs(self, item: MenuItem) -> bool:
        """View recent error logs"""
        self.update_content(
            title="Error Logs",
            lines=[
                "❌ Recent Error Logs",
                "",
                "Error Log Files:",
                "",
                "→ Django errors:",
                "  tail -50 /var/log/unibos/django.log | grep ERROR",
                "",
                "→ Nginx errors:",
                "  tail -50 /var/log/nginx/error.log",
                "",
                "→ System errors:",
                "  sudo journalctl -p err -n 50",
                "",
                "→ Service failures:",
                "  systemctl --failed",
                "",
                "→ Application exceptions:",
                "  sudo journalctl -u gunicorn | grep Exception | tail -20",
                "",
                "Press ESC to continue"
            ],
            color=Colors.RED
        )
        self.render()
        return True


def run_interactive():
    """Run the server TUI"""
    tui = ServerTUI()
    tui.run()


if __name__ == "__main__":
    run_interactive()
