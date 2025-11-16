"""
UNIBOS-DEV Enhanced TUI
Development TUI with full v527 features and shared infrastructure
"""

import subprocess
from pathlib import Path
from typing import List

from core.clients.tui import BaseTUI
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Colors, clear_screen


class UnibosDevTUI(BaseTUI):
    """Enhanced TUI for unibos-dev with complete functionality"""

    def get_profile_name(self) -> str:
        """Get profile name"""
        return "development"

    def get_menu_sections(self) -> List[MenuSection]:
        """Get development menu sections"""
        return [
            # Development Tools Section
            MenuSection(
                id='dev',
                label='development',
                icon='🔧',
                items=[
                    MenuItem(
                        id='dev_run',
                        label='start server',
                        icon='▶️',
                        description='Start Django development server\n\n'
                                   '→ Runs on http://127.0.0.1:8000\n'
                                   '→ Auto-reload enabled\n'
                                   '→ Debug mode active\n\n'
                                   'Command: python manage.py runserver',
                        enabled=True
                    ),
                    MenuItem(
                        id='dev_stop',
                        label='stop server',
                        icon='⏹️',
                        description='Stop running development server\n\n'
                                   '→ Kills all Django runserver processes\n'
                                   '→ Frees up port 8000\n\n'
                                   'Command: pkill -f "manage.py runserver"',
                        enabled=True
                    ),
                    MenuItem(
                        id='dev_shell',
                        label='django shell',
                        icon='🐚',
                        description='Open Django interactive shell\n\n'
                                   '→ Full Django environment loaded\n'
                                   '→ Access to all models and settings\n'
                                   '→ IPython enhanced if available\n\n'
                                   'Command: python manage.py shell',
                        enabled=True
                    ),
                    MenuItem(
                        id='dev_test',
                        label='run tests',
                        icon='🧪',
                        description='Run Django test suite\n\n'
                                   '→ Runs all app tests\n'
                                   '→ Shows coverage if available\n'
                                   '→ Uses test database\n\n'
                                   'Command: python manage.py test',
                        enabled=True
                    ),
                    MenuItem(
                        id='dev_logs',
                        label='view logs',
                        icon='📋',
                        description='View development logs\n\n'
                                   '→ Shows last 50 lines by default\n'
                                   '→ Can follow in real-time\n'
                                   '→ Includes Django debug logs\n\n'
                                   'Log file: data/core/logs/django/debug.log',
                        enabled=True
                    ),
                ]
            ),

            # Git & Deployment Section
            MenuSection(
                id='git',
                label='git & deploy',
                icon='🚀',
                items=[
                    MenuItem(
                        id='git_status',
                        label='git status',
                        icon='📊',
                        description='Show git repository status\n\n'
                                   '→ Current branch\n'
                                   '→ Modified files\n'
                                   '→ Staged changes\n'
                                   '→ Unpushed commits\n\n'
                                   'Command: git status',
                        enabled=True
                    ),
                    MenuItem(
                        id='git_pull',
                        label='pull changes',
                        icon='⬇️',
                        description='Pull latest changes from remote\n\n'
                                   '→ Fetches from origin\n'
                                   '→ Merges into current branch\n'
                                   '→ Shows conflicts if any\n\n'
                                   'Command: git pull',
                        enabled=True
                    ),
                    MenuItem(
                        id='git_commit',
                        label='commit changes',
                        icon='💾',
                        description='Commit current changes\n\n'
                                   '→ Stages all changes\n'
                                   '→ Prompts for commit message\n'
                                   '→ Creates local commit\n\n'
                                   'Commands: git add -A && git commit',
                        enabled=True
                    ),
                    MenuItem(
                        id='git_push_all',
                        label='push to all repos',
                        icon='🌐',
                        description='Push to all 3 repositories\n\n'
                                   '→ Dev repository (GitHub)\n'
                                   '→ Server repository (GitHub)\n'
                                   '→ Prod repository (GitHub)\n\n'
                                   'Automatically switches .gitignore',
                        enabled=True
                    ),
                    MenuItem(
                        id='deploy_rocksteady',
                        label='deploy to server',
                        icon='🎯',
                        description='Deploy to rocksteady server\n\n'
                                   '→ SSH to rocksteady.fun\n'
                                   '→ Pull latest changes\n'
                                   '→ Run migrations\n'
                                   '→ Collect static files\n'
                                   '→ Restart services\n\n'
                                   'Full production deployment',
                        enabled=True
                    ),
                ]
            ),

            # Database Section
            MenuSection(
                id='database',
                label='database',
                icon='🗄️',
                items=[
                    MenuItem(
                        id='db_migrate',
                        label='run migrations',
                        icon='🔄',
                        description='Apply pending database migrations\n\n'
                                   '→ Shows pending migrations\n'
                                   '→ Applies in order\n'
                                   '→ Updates schema\n\n'
                                   'Command: python manage.py migrate',
                        enabled=True
                    ),
                    MenuItem(
                        id='db_makemigrations',
                        label='make migrations',
                        icon='📝',
                        description='Create new migration files\n\n'
                                   '→ Detects model changes\n'
                                   '→ Generates migration files\n'
                                   '→ Shows SQL preview\n\n'
                                   'Command: python manage.py makemigrations',
                        enabled=True
                    ),
                    MenuItem(
                        id='db_backup',
                        label='backup database',
                        icon='💾',
                        description='Create database backup\n\n'
                                   '→ Full database dump\n'
                                   '→ Timestamped filename\n'
                                   '→ Compressed format\n\n'
                                   'Location: archive/database_backups/',
                        enabled=True
                    ),
                    MenuItem(
                        id='db_restore',
                        label='restore backup',
                        icon='📥',
                        description='Restore from backup\n\n'
                                   '→ Lists available backups\n'
                                   '→ Confirms before restore\n'
                                   '→ Full data replacement\n\n'
                                   'Warning: Destructive operation',
                        enabled=True
                    ),
                    MenuItem(
                        id='db_shell',
                        label='database shell',
                        icon='🐚',
                        description='Open database shell\n\n'
                                   '→ Direct SQL access\n'
                                   '→ PostgreSQL psql client\n'
                                   '→ Full query capabilities\n\n'
                                   'Command: python manage.py dbshell',
                        enabled=True
                    ),
                ]
            ),

            # Platform Section
            MenuSection(
                id='platform',
                label='platform',
                icon='🌐',
                items=[
                    MenuItem(
                        id='platform_status',
                        label='system status',
                        icon='📊',
                        description='Show complete system status\n\n'
                                   '→ Version information\n'
                                   '→ Directory structure\n'
                                   '→ Service status\n'
                                   '→ Database connectivity\n'
                                   '→ Module registry\n\n'
                                   'Full health check',
                        enabled=True
                    ),
                    MenuItem(
                        id='platform_modules',
                        label='manage modules',
                        icon='📦',
                        description='Module management interface\n\n'
                                   '→ List all modules\n'
                                   '→ Enable/disable modules\n'
                                   '→ View module details\n'
                                   '→ Check dependencies\n\n'
                                   'Module registry control',
                        enabled=True
                    ),
                    MenuItem(
                        id='platform_config',
                        label='configuration',
                        icon='⚙️',
                        description='Platform configuration\n\n'
                                   '→ Environment settings\n'
                                   '→ Django settings\n'
                                   '→ Service configs\n'
                                   '→ Path configurations\n\n'
                                   'View and edit configs',
                        enabled=True
                    ),
                    MenuItem(
                        id='platform_identity',
                        label='node identity',
                        icon='🔐',
                        description='Node identity information\n\n'
                                   '→ Node UUID\n'
                                   '→ Node type (dev/server/prod)\n'
                                   '→ Registration status\n'
                                   '→ Network identity\n\n'
                                   'Persistent node identity',
                        enabled=True
                    ),
                ]
            ),
        ]

    def __init__(self):
        """Initialize dev TUI with proper config"""
        from core.clients.tui.base import TUIConfig

        config = TUIConfig(
            title="unibos-dev",
            version="v0.534.0",
            location="dev environment",
            sidebar_width=30,
            show_splash=True,  # Re-enabled splash screen
            quick_splash=False,
            lowercase_ui=True,  # v527 style
            show_breadcrumbs=True,
            show_time=True,
            show_hostname=True,
            show_status_led=True
        )

        super().__init__(config)

        # Register dev-specific handlers
        self.register_dev_handlers()

    def register_dev_handlers(self):
        """Register all development action handlers"""
        # Development actions
        self.register_action('dev_run', self.handle_dev_run)
        self.register_action('dev_stop', self.handle_dev_stop)
        self.register_action('dev_shell', self.handle_dev_shell)
        self.register_action('dev_test', self.handle_dev_test)
        self.register_action('dev_logs', self.handle_dev_logs)

        # Git actions
        self.register_action('git_status', self.handle_git_status)
        self.register_action('git_pull', self.handle_git_pull)
        self.register_action('git_commit', self.handle_git_commit)
        self.register_action('git_push_all', self.handle_git_push_all)
        self.register_action('deploy_rocksteady', self.handle_deploy_rocksteady)

        # Database actions
        self.register_action('db_migrate', self.handle_db_migrate)
        self.register_action('db_makemigrations', self.handle_db_makemigrations)
        self.register_action('db_backup', self.handle_db_backup)
        self.register_action('db_restore', self.handle_db_restore)
        self.register_action('db_shell', self.handle_db_shell)

        # Platform actions
        self.register_action('platform_status', self.handle_platform_status)
        self.register_action('platform_modules', self.handle_platform_modules)
        self.register_action('platform_config', self.handle_platform_config)
        self.register_action('platform_identity', self.handle_platform_identity)

    # Development handlers
    def handle_dev_run(self, item):
        """Start development server"""
        result = self.execute_command(['unibos-dev', 'dev', 'run'])
        self.show_command_output(result)
        return True

    def handle_dev_stop(self, item):
        """Stop development server"""
        result = self.execute_command(['unibos-dev', 'dev', 'stop'])
        self.show_command_output(result)
        return True

    def handle_dev_shell(self, item):
        """Open Django shell"""
        # Use subprocess.call for interactive shell
        subprocess.call(['unibos-dev', 'dev', 'shell'])
        return True

    def handle_dev_test(self, item):
        """Run tests"""
        result = self.execute_command(['unibos-dev', 'dev', 'test'])
        self.show_command_output(result)
        return True

    def handle_dev_logs(self, item):
        """View logs"""
        result = self.execute_command(['unibos-dev', 'dev', 'logs'])
        self.show_command_output(result)
        return True

    # Git handlers
    def handle_git_status(self, item):
        """Show git status"""
        result = self.execute_command(['git', 'status'])
        self.show_command_output(result)
        return True

    def handle_git_pull(self, item):
        """Pull from remote"""
        result = self.execute_command(['git', 'pull'])
        self.show_command_output(result)
        return True

    def handle_git_commit(self, item):
        """Commit changes"""
        # Get commit message
        clear_screen()
        print(f"{Colors.YELLOW}Enter commit message:{Colors.RESET} ", end='')
        message = input().strip()

        if message:
            # Stage all changes
            self.execute_command(['git', 'add', '-A'])
            # Commit
            result = self.execute_command(['git', 'commit', '-m', message])
            self.show_command_output(result)
        else:
            self.show_error("Commit message required")

        return True

    def handle_git_push_all(self, item):
        """Push to all repositories"""
        clear_screen()
        print(f"{Colors.YELLOW}Enter commit message:{Colors.RESET} ", end='')
        message = input().strip()

        if message:
            result = self.execute_command(['unibos-dev', 'git', 'push-all', message])
            self.show_command_output(result)
        else:
            self.show_error("Commit message required")

        return True

    def handle_deploy_rocksteady(self, item):
        """Deploy to rocksteady"""
        if self.confirm("Deploy to rocksteady server?"):
            result = self.execute_command(['unibos-dev', 'deploy', 'rocksteady'])
            self.show_command_output(result)
        return True

    # Database handlers
    def handle_db_migrate(self, item):
        """Run migrations"""
        result = self.execute_command(['unibos-dev', 'db', 'migrate'])
        self.show_command_output(result)
        return True

    def handle_db_makemigrations(self, item):
        """Make migrations"""
        result = self.execute_command(['unibos-dev', 'db', 'makemigrations'])
        self.show_command_output(result)
        return True

    def handle_db_backup(self, item):
        """Backup database"""
        result = self.execute_command(['unibos-dev', 'db', 'backup'])
        self.show_command_output(result)
        return True

    def handle_db_restore(self, item):
        """Restore database"""
        clear_screen()
        print(f"{Colors.YELLOW}Enter backup file path:{Colors.RESET} ", end='')
        backup_file = input().strip()

        if backup_file:
            if self.confirm(f"Restore from {backup_file}?"):
                result = self.execute_command(['unibos-dev', 'db', 'restore', backup_file])
                self.show_command_output(result)
        else:
            self.show_error("Backup file required")

        return True

    def handle_db_shell(self, item):
        """Open database shell"""
        subprocess.call(['unibos-dev', 'db', 'shell'])
        return True

    # Platform handlers
    def handle_platform_status(self, item):
        """Show platform status"""
        result = self.execute_command(['unibos-dev', 'status', '--detailed'])
        self.show_command_output(result)
        return True

    def handle_platform_modules(self, item):
        """Manage modules"""
        result = self.execute_command(['unibos-dev', 'platform', '-v'])
        self.show_command_output(result)
        return True

    def handle_platform_config(self, item):
        """Show configuration"""
        result = self.execute_command(['unibos-dev', 'platform', '-v', '--json'])
        self.show_command_output(result)
        return True

    def handle_platform_identity(self, item):
        """Show node identity"""
        clear_screen()
        print(f"{Colors.CYAN}Node Identity Information:{Colors.RESET}\n")

        try:
            from core.base.identity import get_instance_identity
            instance = get_instance_identity()
            identity = instance.get_identity()

            print(f"  Node UUID: {Colors.BOLD}{identity.uuid}{Colors.RESET}")
            print(f"  Node Type: {identity.node_type.value}")
            print(f"  Hostname: {identity.hostname}")
            print(f"  Platform: {identity.platform}")
            print(f"  Created: {identity.created_at}")
            print(f"  Last Seen: {identity.last_seen}")

            if identity.registered_to:
                print(f"  Registered To: {identity.registered_to}")
        except Exception as e:
            print(f"{Colors.RED}Error loading identity: {e}{Colors.RESET}")

        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()
        return True

    # Helper methods
    def show_command_output(self, result):
        """Show command output with formatting"""
        clear_screen()

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(f"{Colors.RED}{result.stderr}{Colors.RESET}")

        if result.returncode != 0:
            print(f"\n{Colors.RED}Command failed with exit code {result.returncode}{Colors.RESET}")

        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()

    def confirm(self, message):
        """Get user confirmation"""
        response = input(f"{Colors.YELLOW}{message} (y/n):{Colors.RESET} ").strip().lower()
        return response in ['y', 'yes']


def run_interactive():
    """Run the enhanced dev TUI"""
    tui = UnibosDevTUI()
    tui.run()


if __name__ == "__main__":
    run_interactive()