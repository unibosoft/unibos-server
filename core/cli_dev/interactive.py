"""
UNIBOS-DEV Interactive Mode
Interactive TUI mode for development CLI

Implements development-specific menu structure and actions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.cli.interactive import InteractiveMode
from core.cli.ui import MenuItem, Colors
from core.version import __version__


class UnibosDevInteractive(InteractiveMode):
    """
    Interactive mode for unibos-dev CLI

    Provides TUI interface for development operations:
    - Development server management
    - Git workflows and deployment
    - Database operations
    - Platform management
    """

    def __init__(self):
        super().__init__(
            title="UNIBOS Development",
            version=__version__
        )

    def get_sections(self):
        """
        Get menu sections for unibos-dev

        Returns:
            List of section dicts with menu items
        """
        return [
            {
                'id': 'dev',
                'label': 'Development',
                'icon': '🔧',
                'items': [
                    MenuItem(
                        id='dev_run',
                        label='Start Development Server',
                        icon='▶️',
                        description='Start Django development server with hot reload\n\nRuns: python manage.py runserver 0.0.0.0:8000'
                    ),
                    MenuItem(
                        id='dev_stop',
                        label='Stop Development Server',
                        icon='⏹️',
                        description='Stop running development server'
                    ),
                    MenuItem(
                        id='dev_status',
                        label='Show Status',
                        icon='📊',
                        description='Display system status, services, and module information'
                    ),
                    MenuItem(
                        id='dev_shell',
                        label='Django Shell',
                        icon='🐚',
                        description='Open Django interactive shell for debugging'
                    ),
                ]
            },
            {
                'id': 'git',
                'label': 'Git & Deploy',
                'icon': '🚀',
                'items': [
                    MenuItem(
                        id='git_status',
                        label='Git Status',
                        icon='📋',
                        description='Show current git repository status'
                    ),
                    MenuItem(
                        id='git_push_dev',
                        label='Push to Dev',
                        icon='⬆️',
                        description='Push to development repository (GitHub)'
                    ),
                    MenuItem(
                        id='git_sync_prod',
                        label='Sync to Prod Directory',
                        icon='🔄',
                        description='Sync code to local production directory'
                    ),
                    MenuItem(
                        id='deploy_rocksteady',
                        label='Deploy to Rocksteady',
                        icon='🎯',
                        description='Deploy to Rocksteady production server\n\nFull deployment with migrations, static files, and service restart'
                    ),
                ]
            },
            {
                'id': 'database',
                'label': 'Database',
                'icon': '🗄️',
                'items': [
                    MenuItem(
                        id='db_backup',
                        label='Create Backup',
                        icon='💾',
                        description='Create database backup to archive/database_backups/'
                    ),
                    MenuItem(
                        id='db_restore',
                        label='Restore Backup',
                        icon='📥',
                        description='Restore database from backup file'
                    ),
                    MenuItem(
                        id='db_migrate',
                        label='Run Migrations',
                        icon='🔄',
                        description='Apply pending database migrations'
                    ),
                    MenuItem(
                        id='db_makemigrations',
                        label='Make Migrations',
                        icon='📝',
                        description='Generate new migration files from model changes'
                    ),
                ]
            },
            {
                'id': 'platform',
                'label': 'Platform',
                'icon': '🌐',
                'items': [
                    MenuItem(
                        id='platform_modules',
                        label='List Modules',
                        icon='📦',
                        description='Show all registered modules and their status'
                    ),
                    MenuItem(
                        id='platform_config',
                        label='Show Configuration',
                        icon='⚙️',
                        description='Display current platform configuration'
                    ),
                    MenuItem(
                        id='platform_identity',
                        label='Node Identity',
                        icon='🔐',
                        description='Show node identity and persistence information'
                    ),
                ]
            }
        ]

    def handle_action(self, item: MenuItem) -> bool:
        """
        Handle menu item action

        Args:
            item: Selected menu item

        Returns:
            True to continue menu loop, False to exit
        """
        import subprocess
        import os
        from core.cli.ui import clear_screen, Colors

        clear_screen()
        print(f"{Colors.ORANGE}{Colors.BOLD}▶ {item.label}{Colors.RESET}\n")

        try:
            if item.id == 'dev_run':
                print(f"{Colors.DIM}Starting development server...{Colors.RESET}\n")
                subprocess.run(['unibos-dev', 'dev', 'run'], check=True)

            elif item.id == 'dev_stop':
                print(f"{Colors.DIM}Stopping development server...{Colors.RESET}\n")
                subprocess.run(['unibos-dev', 'dev', 'stop'], check=True)

            elif item.id == 'dev_status':
                subprocess.run(['unibos-dev', 'status'], check=True)

            elif item.id == 'dev_shell':
                print(f"{Colors.DIM}Opening Django shell...{Colors.RESET}\n")
                # Change to web directory and run shell
                web_dir = project_root / 'core' / 'web'
                os.chdir(web_dir)
                subprocess.run([
                    'python',
                    'manage.py',
                    'shell'
                ], check=True)

            elif item.id == 'git_status':
                subprocess.run(['git', 'status'], check=True)

            elif item.id == 'git_push_dev':
                subprocess.run(['unibos-dev', 'git', 'push-dev'], check=True)

            elif item.id == 'git_sync_prod':
                subprocess.run(['unibos-dev', 'git', 'sync-prod'], check=True)

            elif item.id == 'deploy_rocksteady':
                subprocess.run(['unibos-dev', 'deploy', 'rocksteady'], check=True)

            elif item.id == 'db_backup':
                subprocess.run(['unibos-dev', 'db', 'backup'], check=True)

            elif item.id == 'db_restore':
                print(f"{Colors.YELLOW}Enter backup file path:{Colors.RESET} ", end='')
                backup_file = input().strip()
                if backup_file:
                    subprocess.run(['unibos-dev', 'db', 'restore', backup_file], check=True)

            elif item.id == 'db_migrate':
                subprocess.run(['unibos-dev', 'db', 'migrate'], check=True)

            elif item.id == 'db_makemigrations':
                subprocess.run(['unibos-dev', 'db', 'makemigrations'], check=True)

            elif item.id == 'platform_modules':
                subprocess.run(['unibos-dev', 'platform', 'modules'], check=True)

            elif item.id == 'platform_config':
                subprocess.run(['unibos-dev', 'platform', 'config'], check=True)

            elif item.id == 'platform_identity':
                subprocess.run(['unibos-dev', 'platform', 'identity'], check=True)

            else:
                print(f"{Colors.YELLOW}⚠ Action not yet implemented: {item.id}{Colors.RESET}")

        except subprocess.CalledProcessError as e:
            print(f"\n{Colors.RED}❌ Command failed with exit code {e.returncode}{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠ Interrupted{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")

        # Pause before returning to menu
        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        input()

        return True  # Continue menu loop


def run_interactive():
    """Run unibos-dev in interactive mode"""
    interactive = UnibosDevInteractive()
    interactive.run(show_splash=True)
