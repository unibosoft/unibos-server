"""
UNIBOS-DEV TUI - v527 Structure
Development TUI with 3-section layout: modules, tools, dev tools
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.clients.tui import BaseTUI
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Colors


class UnibosDevTUI(BaseTUI):
    """Development TUI with v527 structure"""

    def __init__(self):
        """Initialize dev TUI with proper config"""
        from core.clients.tui.base import TUIConfig

        config = TUIConfig(
            title="unibos-dev",
            version="v0.534.0",
            location="dev environment",
            sidebar_width=30,
            show_splash=True,
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

    def get_profile_name(self) -> str:
        """Get profile name"""
        return "development"

    def load_module_metadata(self, module_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load module metadata from module.json file

        Args:
            module_path: Path to the module directory

        Returns:
            Dictionary containing module metadata, or None if not found/invalid
        """
        module_json_path = module_path / 'module.json'

        if not module_json_path.exists():
            return None

        try:
            with open(module_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            # Log error but continue - module can still be discovered
            return None

    def discover_modules(self) -> List[MenuItem]:
        """
        Discover installed modules dynamically

        Modules are identified by:
        - .enabled file (indicates module is enabled)
        - backend/ directory (contains Django app)
        - module.json file (optional, contains metadata)

        Returns:
            List of MenuItem objects for each discovered module
        """
        modules_dir = Path("/Users/berkhatirli/Desktop/unibos-dev/modules")
        modules = []

        if modules_dir.exists():
            for module_path in sorted(modules_dir.iterdir()):
                if module_path.is_dir() and not module_path.name.startswith('_'):
                    # Check if module has .enabled file to be valid
                    if (module_path / '.enabled').exists():
                        # Try to load module metadata from module.json
                        metadata = self.load_module_metadata(module_path)

                        # Extract metadata or use defaults
                        if metadata:
                            module_name = metadata.get('name', module_path.name)
                            module_icon = metadata.get('icon', '📦')
                            module_desc = metadata.get('description', f'Launch {module_name} module')
                            module_version = metadata.get('version', 'unknown')

                            # Get display name (use English if available)
                            display_name_data = metadata.get('display_name')
                            if isinstance(display_name_data, dict):
                                display_name = display_name_data.get('en', module_name)
                            else:
                                display_name = module_name

                            # Build feature list
                            features = metadata.get('features', [])
                            feature_list = ''
                            if isinstance(features, list) and features:
                                feature_list = '\n'.join([f'  • {f}' for f in features[:5]])  # Limit to 5 features
                                if len(features) > 5:
                                    feature_list += f'\n  • ... and {len(features) - 5} more'

                            # Build description
                            description_parts = [
                                f'{module_desc}\n',
                                f'→ Module ID: {metadata.get("id", module_path.name)}',
                                f'→ Version: {module_version}',
                                f'→ Author: {metadata.get("author", "Unknown")}\n',
                            ]

                            if feature_list:
                                description_parts.append('Key Features:')
                                description_parts.append(feature_list)
                                description_parts.append('')

                            description_parts.append('Press Enter to launch module')

                            description = '\n'.join(description_parts)
                            label = display_name.lower()
                        else:
                            # Fallback to basic info if no metadata
                            label = module_path.name
                            module_icon = '📦'
                            description = (
                                f'Launch {module_path.name} module\n\n'
                                f'→ Module directory: {module_path}\n'
                                f'→ Status: Enabled\n'
                                f'→ No metadata file found\n\n'
                                f'Press Enter to launch module'
                            )

                        modules.append(MenuItem(
                            id=f"module_{module_path.name}",
                            label=label,
                            icon=module_icon,
                            description=description,
                            enabled=True
                        ))

        # If no modules found, add placeholder
        if not modules:
            modules.append(MenuItem(
                id='no_modules',
                label='no modules found',
                icon='📦',
                description='No enabled modules are currently installed.\n\n'
                           'Modules should be placed in:\n'
                           '/modules/\n\n'
                           'Each module must have:\n'
                           '  • .enabled file (marks module as enabled)\n'
                           '  • backend/ directory (Django app)\n'
                           '  • module.json file (optional metadata)',
                enabled=False
            ))

        return modules

    def get_menu_sections(self) -> List[MenuSection]:
        """Get development menu sections - v527 structure"""
        return [
            # Section 1: Modules (dynamically discovered)
            MenuSection(
                id='modules',
                label='modules',
                icon='📦',
                items=self.discover_modules()
            ),

            # Section 2: Tools (7 items)
            MenuSection(
                id='tools',
                label='tools',
                icon='🔧',
                items=[
                    MenuItem(
                        id='system_scrolls',
                        label='system scrolls',
                        icon='📜',
                        description='forge status & info\n\n'
                                   '→ System information\n'
                                   '→ Version details\n'
                                   '→ Service status\n'
                                   '→ Resource usage\n\n'
                                   'Complete system overview',
                        enabled=True
                    ),
                    MenuItem(
                        id='castle_guard',
                        label='castle guard',
                        icon='🛡️',
                        description='fortress security\n\n'
                                   '→ Security status\n'
                                   '→ Access controls\n'
                                   '→ Authentication logs\n'
                                   '→ Firewall settings\n\n'
                                   'Security management interface',
                        enabled=True
                    ),
                    MenuItem(
                        id='forge_smithy',
                        label='forge smithy',
                        icon='🔨',
                        description='setup forge tools\n\n'
                                   '→ Install dependencies\n'
                                   '→ Configure environment\n'
                                   '→ Setup database\n'
                                   '→ Initialize services\n\n'
                                   'Complete system setup wizard',
                        enabled=True
                    ),
                    MenuItem(
                        id='anvil_repair',
                        label='anvil repair',
                        icon='⚒️',
                        description='mend & fix issues\n\n'
                                   '→ Diagnostic tools\n'
                                   '→ Repair utilities\n'
                                   '→ Log analysis\n'
                                   '→ Recovery options\n\n'
                                   'System repair and maintenance',
                        enabled=True
                    ),
                    MenuItem(
                        id='code_forge',
                        label='code forge',
                        icon='⚙️',
                        description='version chronicles\n\n'
                                   '→ Git operations\n'
                                   '→ Version control\n'
                                   '→ Commit history\n'
                                   '→ Branch management\n\n'
                                   'Source code management',
                        enabled=True
                    ),
                    MenuItem(
                        id='web_ui',
                        label='web ui',
                        icon='🌐',
                        description='web interface manager\n\n'
                                   '→ Start Django server\n'
                                   '→ Stop Django server\n'
                                   '→ View server logs\n'
                                   '→ Server configuration\n\n'
                                   'Web interface control',
                        enabled=True
                    ),
                    MenuItem(
                        id='administration',
                        label='administration',
                        icon='👑',
                        description='system administration\n\n'
                                   '→ User management\n'
                                   '→ Permissions\n'
                                   '→ System settings\n'
                                   '→ Configuration\n\n'
                                   'Administrative tools',
                        enabled=True
                    ),
                ]
            ),

            # Section 3: Dev Tools (5 items)
            MenuSection(
                id='dev_tools',
                label='dev tools',
                icon='🛠️',
                items=[
                    MenuItem(
                        id='ai_builder',
                        label='ai builder',
                        icon='🤖',
                        description='ai-powered development\n\n'
                                   '→ Code generation\n'
                                   '→ AI assistance\n'
                                   '→ Smart refactoring\n'
                                   '→ Documentation generation\n\n'
                                   'AI development tools',
                        enabled=True
                    ),
                    MenuItem(
                        id='database_setup',
                        label='database setup',
                        icon='🗄️',
                        description='postgresql installer\n\n'
                                   '→ Install PostgreSQL\n'
                                   '→ Create database\n'
                                   '→ Run migrations\n'
                                   '→ Configure access\n\n'
                                   'Database installation wizard',
                        enabled=True
                    ),
                    MenuItem(
                        id='public_server',
                        label='public server',
                        icon='🌍',
                        description='deploy to ubuntu/oracle vm\n\n'
                                   '→ Deploy to rocksteady\n'
                                   '→ SSH to server\n'
                                   '→ Server management\n'
                                   '→ Production deployment\n\n'
                                   'Public server deployment',
                        enabled=True
                    ),
                    MenuItem(
                        id='sd_card',
                        label='sd card',
                        icon='💾',
                        description='sd operations\n\n'
                                   '→ Format SD card\n'
                                   '→ Create bootable image\n'
                                   '→ Backup/restore\n'
                                   '→ Partition management\n\n'
                                   'SD card utilities',
                        enabled=True
                    ),
                    MenuItem(
                        id='version_manager',
                        label='version manager',
                        icon='📋',
                        description='archive & git tools\n\n'
                                   '→ Create version archives\n'
                                   '→ Browse archive history\n'
                                   '→ Restore versions\n'
                                   '→ Git integration\n\n'
                                   'Version control and archiving',
                        enabled=True
                    ),
                ]
            ),
        ]

    def register_dev_handlers(self):
        """Register all development action handlers"""
        # Tools section handlers
        self.register_action('system_scrolls', self.handle_system_scrolls)
        self.register_action('castle_guard', self.handle_castle_guard)
        self.register_action('forge_smithy', self.handle_forge_smithy)
        self.register_action('anvil_repair', self.handle_anvil_repair)
        self.register_action('code_forge', self.handle_code_forge)
        self.register_action('web_ui', self.handle_web_ui)
        self.register_action('administration', self.handle_administration)

        # Dev tools section handlers
        self.register_action('ai_builder', self.handle_ai_builder)
        self.register_action('database_setup', self.handle_database_setup)
        self.register_action('public_server', self.handle_public_server)
        self.register_action('sd_card', self.handle_sd_card)
        self.register_action('version_manager', self.handle_version_manager)

    # ===== TOOLS SECTION HANDLERS =====

    def handle_system_scrolls(self, item: MenuItem) -> bool:
        """Show system status and information"""
        self.update_content(
            title="System Scrolls",
            lines=["⏳ Gathering system information...", ""],
            color=Colors.CYAN
        )
        self.render()

        try:
            # Execute status command
            result = self.execute_command(['unibos-dev', 'status'])

            # Show results
            self.show_command_output(result)

        except Exception as e:
            self.update_content(
                title="System Scrolls - Error",
                lines=[
                    "❌ Failed to load system information",
                    "",
                    f"Error: {str(e)}",
                    "",
                    "Try running: unibos-dev status"
                ],
                color=Colors.RED
            )
            self.render()

        return True

    def handle_castle_guard(self, item: MenuItem) -> bool:
        """Security management"""
        self.update_content(
            title="Castle Guard - Security Tools",
            lines=[
                "🛡️ Security Management",
                "",
                "Available security tools:",
                "",
                "→ Firewall Status",
                "→ SSH Configuration",
                "→ SSL Certificates",
                "→ Access Logs",
                "→ Failed Login Attempts",
                "",
                "🚧 This feature is under development.",
                "",
                "Security tools will include:",
                "  • System firewall management",
                "  • SSH key management",
                "  • SSL/TLS certificate monitoring",
                "  • Security audit logging",
                "  • Intrusion detection",
                "",
                "Press ESC to return to menu"
            ],
            color=Colors.YELLOW
        )
        self.render()
        return True

    def handle_forge_smithy(self, item: MenuItem) -> bool:
        """System setup wizard"""
        self.update_content(
            title="Forge Smithy - Setup Wizard",
            lines=[
                "🔨 System Setup Wizard",
                "",
                "This wizard helps you set up UNIBOS from scratch.",
                "",
                "Setup steps:",
                "",
                "1. Environment Check",
                "   → Python version",
                "   → Required packages",
                "   → System dependencies",
                "",
                "2. Database Setup",
                "   → PostgreSQL installation",
                "   → Database creation",
                "   → Run migrations",
                "",
                "3. Configuration",
                "   → Environment variables",
                "   → Settings files",
                "   → Secret keys",
                "",
                "4. Services",
                "   → Redis setup",
                "   → Background workers",
                "   → Django server",
                "",
                "🚧 Full wizard coming soon!",
                "",
                "For now, use:",
                "  • Database Setup (in Dev Tools)",
                "  • unibos-dev status (for checks)",
                "",
                "Press ESC to return to menu"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_anvil_repair(self, item: MenuItem) -> bool:
        """System repair and maintenance"""
        self.update_content(
            title="Anvil Repair - Diagnostics & Repair",
            lines=[
                "⚒️ System Diagnostics & Repair Tools",
                "",
                "Diagnostic Tools:",
                "",
                "→ Check System Health",
                "→ Verify Database Integrity",
                "→ Test Network Connectivity",
                "→ Validate File Permissions",
                "→ Analyze Log Files",
                "",
                "Repair Tools:",
                "",
                "→ Fix Database Issues",
                "→ Repair Corrupted Files",
                "→ Reset Configurations",
                "→ Clear Cache",
                "→ Rebuild Indexes",
                "",
                "🚧 This feature is under development.",
                "",
                "Available now:",
                "  • unibos-dev status (health check)",
                "  • Django management commands",
                "  • Database migrations",
                "",
                "Press ESC to return to menu"
            ],
            color=Colors.YELLOW
        )
        self.render()
        return True

    def handle_code_forge(self, item: MenuItem) -> bool:
        """Git and version control"""
        self.update_content(
            title="Code Forge - Git Operations",
            lines=["📊 Loading git status...", ""],
            color=Colors.CYAN
        )
        self.render()

        try:
            # Show git status
            result = self.execute_command(['unibos-dev', 'git', 'status'])

            # Build content with git commands
            lines = ["⚙️ Git Status", "", ""]

            # Add command output
            if result.returncode == 0:
                lines.extend(result.stdout.strip().split('\n'))
            else:
                lines.append("❌ Failed to get git status")
                if result.stderr:
                    lines.extend(result.stderr.strip().split('\n'))

            lines.extend([
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "Available Git Commands:",
                "",
                "  unibos-dev git status        - Show git status",
                "  unibos-dev git push-dev      - Push to dev repo",
                "  unibos-dev git sync-prod     - Sync to prod directory",
                "  unibos-dev git commit        - Create commit",
                "",
                "Run these commands from terminal for full git control.",
                "",
                "Press ESC to return to menu"
            ])

            self.update_content(
                title="Code Forge - Git Operations",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

        except Exception as e:
            self.update_content(
                title="Code Forge - Error",
                lines=[
                    "❌ Failed to execute git command",
                    "",
                    f"Error: {str(e)}",
                    "",
                    "Try running: unibos-dev git status"
                ],
                color=Colors.RED
            )
            self.render()

        return True

    def handle_web_ui(self, item: MenuItem) -> bool:
        """Web interface management - Interactive submenu"""
        return self._show_web_ui_submenu()

    def _show_web_ui_submenu(self) -> bool:
        """Show interactive Web UI submenu"""
        import time

        # Menu options
        options = [
            ("start", "🚀 Start Django Server", "Start the development server"),
            ("stop", "⏹️ Stop Django Server", "Stop the running server"),
            ("status", "📊 Server Status", "Check if server is running"),
            ("logs", "📝 View Server Logs", "Show recent server logs"),
            ("migrate", "🔄 Run Migrations", "Apply database migrations"),
            ("back", "← Back to Tools", "Return to main menu"),
        ]

        selected = 0

        while True:
            # Build menu display
            lines = [
                "🌐 Web UI Management",
                "",
                "Select an option:",
                ""
            ]

            for i, (key, label, desc) in enumerate(options):
                if i == selected:
                    lines.append(f"  → {label}")
                    lines.append(f"    {desc}")
                else:
                    lines.append(f"    {label}")
                lines.append("")

            lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "Navigation: ↑↓ to move, Enter to select, ESC to go back"
            ])

            self.update_content(
                title="Web UI Management",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

            # Get input
            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER':
                option_key = options[selected][0]

                if option_key == 'back':
                    return True
                elif option_key == 'start':
                    self._web_ui_start_server()
                elif option_key == 'stop':
                    self._web_ui_stop_server()
                elif option_key == 'status':
                    self._web_ui_show_status()
                elif option_key == 'logs':
                    self._web_ui_show_logs()
                elif option_key == 'migrate':
                    self._web_ui_run_migrations()

                # Wait for user to read output
                time.sleep(0.5)
            elif key == 'ESC':
                return True

        return True

    def _web_ui_start_server(self):
        """Start Django development server"""
        self.update_content(
            title="Starting Django Server",
            lines=["🚀 Starting development server...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'run'])
        self.show_command_output(result)

    def _web_ui_stop_server(self):
        """Stop Django development server"""
        self.update_content(
            title="Stopping Django Server",
            lines=["⏹️ Stopping development server...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'stop'])
        self.show_command_output(result)

    def _web_ui_show_status(self):
        """Show Django server status"""
        self.update_content(
            title="Django Server Status",
            lines=["📊 Checking server status...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'status'])
        self.show_command_output(result)

    def _web_ui_show_logs(self):
        """Show Django server logs"""
        self.update_content(
            title="Django Server Logs",
            lines=["📝 Loading server logs...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'logs'])
        self.show_command_output(result)

    def _web_ui_run_migrations(self):
        """Run Django migrations"""
        self.update_content(
            title="Running Migrations",
            lines=["🔄 Running database migrations...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'dev', 'migrate'])
        self.show_command_output(result)

    def handle_administration(self, item: MenuItem) -> bool:
        """System administration"""
        self.update_content(
            title="Administration - System Management",
            lines=[
                "👑 System Administration",
                "",
                "Administration Tools:",
                "",
                "→ User Management",
                "  • Create/delete users",
                "  • Manage permissions",
                "  • Reset passwords",
                "",
                "→ System Settings",
                "  • Environment configuration",
                "  • Feature flags",
                "  • API settings",
                "",
                "→ Module Management",
                "  • Enable/disable modules",
                "  • Module configuration",
                "  • Module permissions",
                "",
                "→ Monitoring",
                "  • System logs",
                "  • Performance metrics",
                "  • Error tracking",
                "",
                "🚧 This feature is under development.",
                "",
                "For now, use Django admin:",
                "  1. Start server: unibos-dev dev run",
                "  2. Visit: http://localhost:8000/admin",
                "",
                "Press ESC to return to menu"
            ],
            color=Colors.YELLOW
        )
        self.render()
        return True

    # ===== DEV TOOLS SECTION HANDLERS =====

    def handle_ai_builder(self, item: MenuItem) -> bool:
        """AI-powered development tools"""
        self.update_content(
            title="AI Builder - AI Development Tools",
            lines=[
                "🤖 AI-Powered Development",
                "",
                "The AI Builder provides intelligent code assistance and generation.",
                "",
                "Features:",
                "",
                "→ Code Generation",
                "  • Generate boilerplate code",
                "  • Create test cases",
                "  • Generate documentation",
                "",
                "→ AI Assistance",
                "  • Code completion",
                "  • Bug detection",
                "  • Code review suggestions",
                "",
                "→ Smart Refactoring",
                "  • Optimize code structure",
                "  • Improve performance",
                "  • Apply best practices",
                "",
                "→ Documentation",
                "  • Auto-generate docstrings",
                "  • Create README files",
                "  • API documentation",
                "",
                "🚧 This feature is under development.",
                "",
                "For now, you can use:",
                "  • Claude Code CLI (if installed)",
                "  • GitHub Copilot",
                "  • ChatGPT for code assistance",
                "",
                "Press ESC to return to menu"
            ],
            color=Colors.MAGENTA
        )
        self.render()
        return True

    def handle_database_setup(self, item: MenuItem) -> bool:
        """PostgreSQL installation wizard"""
        return self._show_database_setup_submenu()

    def _show_database_setup_submenu(self) -> bool:
        """Show interactive Database Setup submenu"""
        import time

        # Menu options
        options = [
            ("check", "🔍 Check Database Status", "Check if PostgreSQL is installed and running"),
            ("install", "📥 Install PostgreSQL", "Install PostgreSQL using Homebrew (macOS)"),
            ("create", "🗄️ Create Database", "Create UNIBOS database"),
            ("migrate", "🔄 Run Migrations", "Apply Django migrations"),
            ("backup", "💾 Backup Database", "Create database backup"),
            ("restore", "♻️ Restore Database", "Restore from backup"),
            ("back", "← Back to Dev Tools", "Return to main menu"),
        ]

        selected = 0

        while True:
            # Build menu display
            lines = [
                "🗄️ Database Setup Wizard",
                "",
                "PostgreSQL Database Management:",
                ""
            ]

            for i, (key, label, desc) in enumerate(options):
                if i == selected:
                    lines.append(f"  → {label}")
                    lines.append(f"    {desc}")
                else:
                    lines.append(f"    {label}")
                lines.append("")

            lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "Navigation: ↑↓ to move, Enter to select, ESC to go back"
            ])

            self.update_content(
                title="Database Setup Wizard",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

            # Get input
            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER':
                option_key = options[selected][0]

                if option_key == 'back':
                    return True
                elif option_key == 'check':
                    self._db_check_status()
                elif option_key == 'install':
                    self._db_install_postgresql()
                elif option_key == 'create':
                    self._db_create_database()
                elif option_key == 'migrate':
                    self._db_run_migrations()
                elif option_key == 'backup':
                    self._db_backup()
                elif option_key == 'restore':
                    self._db_restore()

                # Wait for user to read output
                time.sleep(0.5)
            elif key == 'ESC':
                return True

        return True

    def _db_check_status(self):
        """Check database status"""
        self.update_content(
            title="Database Status",
            lines=["🔍 Checking database status...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'status'])
        self.show_command_output(result)

    def _db_install_postgresql(self):
        """Install PostgreSQL"""
        self.update_content(
            title="Installing PostgreSQL",
            lines=[
                "📥 PostgreSQL Installation",
                "",
                "This will install PostgreSQL using Homebrew.",
                "",
                "Run this command in terminal:",
                "",
                "  brew install postgresql@14",
                "  brew services start postgresql@14",
                "",
                "Then create database:",
                "",
                "  createdb unibos_dev",
                "",
                "Press ESC to continue"
            ],
            color=Colors.YELLOW
        )
        self.render()

    def _db_create_database(self):
        """Create database"""
        self.update_content(
            title="Creating Database",
            lines=["🗄️ Creating UNIBOS database...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'create'])
        self.show_command_output(result)

    def _db_run_migrations(self):
        """Run migrations"""
        self.update_content(
            title="Running Migrations",
            lines=["🔄 Running database migrations...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'migrate'])
        self.show_command_output(result)

    def _db_backup(self):
        """Backup database"""
        self.update_content(
            title="Database Backup",
            lines=["💾 Creating database backup...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'backup'])
        self.show_command_output(result)

    def _db_restore(self):
        """Restore database"""
        self.update_content(
            title="Database Restore",
            lines=["♻️ Restoring database...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'db', 'restore'])
        self.show_command_output(result)

    def handle_public_server(self, item: MenuItem) -> bool:
        """Deploy to public server"""
        return self._show_public_server_submenu()

    def _show_public_server_submenu(self) -> bool:
        """Show interactive Public Server submenu"""
        import time

        # Menu options
        options = [
            ("status", "📊 Server Status", "Check rocksteady server status"),
            ("deploy", "🚀 Deploy to Rocksteady", "Deploy UNIBOS to production server"),
            ("ssh", "🔐 SSH to Server", "Open SSH connection to rocksteady"),
            ("logs", "📝 View Server Logs", "Show production server logs"),
            ("backup", "💾 Backup Server", "Create server backup"),
            ("back", "← Back to Dev Tools", "Return to main menu"),
        ]

        selected = 0

        while True:
            # Build menu display
            lines = [
                "🌍 Public Server Management",
                "",
                "Ubuntu/Oracle VM (rocksteady) Deployment:",
                ""
            ]

            for i, (key, label, desc) in enumerate(options):
                if i == selected:
                    lines.append(f"  → {label}")
                    lines.append(f"    {desc}")
                else:
                    lines.append(f"    {label}")
                lines.append("")

            lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "Navigation: ↑↓ to move, Enter to select, ESC to go back"
            ])

            self.update_content(
                title="Public Server Management",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

            # Get input
            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER':
                option_key = options[selected][0]

                if option_key == 'back':
                    return True
                elif option_key == 'status':
                    self._server_check_status()
                elif option_key == 'deploy':
                    self._server_deploy()
                elif option_key == 'ssh':
                    self._server_ssh()
                elif option_key == 'logs':
                    self._server_logs()
                elif option_key == 'backup':
                    self._server_backup()

                # Wait for user to read output
                time.sleep(0.5)
            elif key == 'ESC':
                return True

        return True

    def _server_check_status(self):
        """Check server status"""
        self.update_content(
            title="Server Status",
            lines=["📊 Checking rocksteady server status...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'deploy', 'status', 'rocksteady'])
        self.show_command_output(result)

    def _server_deploy(self):
        """Deploy to server"""
        self.update_content(
            title="Deploying to Rocksteady",
            lines=["🚀 Deploying UNIBOS to production server...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'deploy', 'rocksteady'])
        self.show_command_output(result)

    def _server_ssh(self):
        """SSH to server"""
        self.update_content(
            title="SSH Connection",
            lines=[
                "🔐 Opening SSH connection to rocksteady...",
                "",
                "Run this command in your terminal:",
                "",
                "  ssh rocksteady",
                "",
                "Or use the deploy command for full options.",
                "",
                "Press ESC to continue"
            ],
            color=Colors.YELLOW
        )
        self.render()

    def _server_logs(self):
        """View server logs"""
        self.update_content(
            title="Server Logs",
            lines=["📝 Fetching server logs...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'deploy', 'logs', 'rocksteady'])
        self.show_command_output(result)

    def _server_backup(self):
        """Backup server"""
        self.update_content(
            title="Server Backup",
            lines=["💾 Creating server backup...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'deploy', 'backup', 'rocksteady'])
        self.show_command_output(result)

    def handle_sd_card(self, item: MenuItem) -> bool:
        """SD card operations"""
        self.update_content(
            title="SD Card Operations",
            lines=[
                "💾 SD Card Utilities",
                "",
                "SD card management for Raspberry Pi and other devices.",
                "",
                "Available Operations:",
                "",
                "→ Format SD Card",
                "  • Format for Raspberry Pi",
                "  • Create boot partition",
                "  • Set up file system",
                "",
                "→ Create Bootable Image",
                "  • Flash Raspberry Pi OS",
                "  • Flash custom images",
                "  • Verify image integrity",
                "",
                "→ Backup/Restore",
                "  • Create SD card backup",
                "  • Restore from backup",
                "  • Clone SD cards",
                "",
                "→ Partition Management",
                "  • View partitions",
                "  • Resize partitions",
                "  • Create new partitions",
                "",
                "🚧 This feature is under development.",
                "",
                "For now, use:",
                "  • Raspberry Pi Imager (GUI tool)",
                "  • dd command (advanced users)",
                "  • balenaEtcher",
                "",
                "Press ESC to return to menu"
            ],
            color=Colors.YELLOW
        )
        self.render()
        return True

    def handle_version_manager(self, item: MenuItem) -> bool:
        """Version control and archiving"""
        return self._show_version_manager_submenu()

    def _show_version_manager_submenu(self) -> bool:
        """Show interactive Version Manager submenu"""
        import time
        from pathlib import Path

        # Check if archive directory exists
        archive_dir = Path("/Users/berkhatirli/Desktop/unibos-dev/archive/versions")
        archive_exists = archive_dir.exists()

        # Menu options
        options = [
            ("browse", "📋 Browse Archives", "View version archive history"),
            ("create", "📦 Create Archive", "Create new version archive"),
            ("analyze", "📊 Archive Analyzer", "Analyze archive statistics"),
            ("git_status", "🔀 Git Status", "Show git repository status"),
            ("git_sync", "🔄 Git Sync", "Sync with git repositories"),
            ("validate", "✅ Validate Versions", "Validate version integrity"),
            ("back", "← Back to Dev Tools", "Return to main menu"),
        ]

        selected = 0

        while True:
            # Build menu display
            lines = [
                "📋 Version Manager",
                "",
                "Archive & Git Management:",
                ""
            ]

            # Show archive status
            if archive_exists:
                archive_count = len(list(archive_dir.glob("*/VERSION.json")))
                lines.append(f"📁 Archives found: {archive_count}")
                lines.append("")
            else:
                lines.append("⚠️ Archive directory not found")
                lines.append("")

            for i, (key, label, desc) in enumerate(options):
                if i == selected:
                    lines.append(f"  → {label}")
                    lines.append(f"    {desc}")
                else:
                    lines.append(f"    {label}")
                lines.append("")

            lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "Navigation: ↑↓ to move, Enter to select, ESC to go back"
            ])

            self.update_content(
                title="Version Manager",
                lines=lines,
                color=Colors.CYAN
            )
            self.render()

            # Get input
            key = self.get_key()

            if key == 'UP':
                selected = (selected - 1) % len(options)
            elif key == 'DOWN':
                selected = (selected + 1) % len(options)
            elif key == 'ENTER':
                option_key = options[selected][0]

                if option_key == 'back':
                    return True
                elif option_key == 'browse':
                    self._version_browse_archives()
                elif option_key == 'create':
                    self._version_create_archive()
                elif option_key == 'analyze':
                    self._version_analyze()
                elif option_key == 'git_status':
                    self._version_git_status()
                elif option_key == 'git_sync':
                    self._version_git_sync()
                elif option_key == 'validate':
                    self._version_validate()

                # Wait for user to read output
                time.sleep(0.5)
            elif key == 'ESC':
                return True

        return True

    def _version_browse_archives(self):
        """Browse version archives"""
        from pathlib import Path
        import json

        archive_dir = Path("/Users/berkhatirli/Desktop/unibos-dev/archive/versions")

        if not archive_dir.exists():
            self.update_content(
                title="Browse Archives",
                lines=[
                    "⚠️ Archive directory not found",
                    "",
                    f"Expected location: {archive_dir}",
                    "",
                    "Press ESC to continue"
                ],
                color=Colors.YELLOW
            )
            self.render()
            return

        # Find all version archives
        archives = []
        for version_file in sorted(archive_dir.glob("*/VERSION.json"), reverse=True):
            try:
                with open(version_file) as f:
                    data = json.load(f)
                    archives.append({
                        'path': version_file.parent,
                        'version': data.get('version', 'unknown'),
                        'date': data.get('release_date', 'unknown'),
                        'description': data.get('description', '')
                    })
            except:
                pass

        # Build display
        lines = ["📋 Version Archive History", "", ""]

        if archives:
            lines.append(f"Total archives: {len(archives)}")
            lines.append("")
            lines.append("Recent versions:")
            lines.append("")

            for i, archive in enumerate(archives[:10]):  # Show last 10
                lines.append(f"  {i+1}. v{archive['version']} - {archive['date']}")
                if archive['description']:
                    lines.append(f"     {archive['description'][:60]}")
                lines.append("")

            if len(archives) > 10:
                lines.append(f"... and {len(archives) - 10} more")
                lines.append("")
        else:
            lines.append("No archives found")
            lines.append("")

        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "Press ESC to continue"
        ])

        self.update_content(
            title="Browse Archives",
            lines=lines,
            color=Colors.CYAN
        )
        self.render()

    def _version_create_archive(self):
        """Create new version archive"""
        self.update_content(
            title="Create Archive",
            lines=[
                "📦 Creating version archive...",
                "",
                "This will create a snapshot of the current codebase.",
                "",
                "Use the archive_daily_check.sh script:",
                "",
                "  ./tools/archive_daily_check.sh",
                "",
                "Or use git to create a version tag:",
                "",
                "  git tag v0.534.1",
                "  git push --tags",
                "",
                "Press ESC to continue"
            ],
            color=Colors.YELLOW
        )
        self.render()

    def _version_analyze(self):
        """Analyze archives"""
        self.update_content(
            title="Archive Analyzer",
            lines=[
                "📊 Analyzing version archives...",
                "",
                "Run the archive analyzer script:",
                "",
                "  ./tools/archive_daily_check.sh",
                "",
                "This will show:",
                "  • Archive statistics",
                "  • Size trends",
                "  • Anomaly detection",
                "  • Protection status",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()

    def _version_git_status(self):
        """Show git status"""
        self.update_content(
            title="Git Status",
            lines=["🔀 Loading git status...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'git', 'status'])
        self.show_command_output(result)

    def _version_git_sync(self):
        """Sync with git"""
        self.update_content(
            title="Git Sync",
            lines=["🔄 Syncing with git repositories...", ""],
            color=Colors.CYAN
        )
        self.render()

        result = self.execute_command(['unibos-dev', 'git', 'sync-prod'])
        self.show_command_output(result)

    def _version_validate(self):
        """Validate versions"""
        self.update_content(
            title="Validate Versions",
            lines=[
                "✅ Version Validation",
                "",
                "This checks:",
                "  • Version number sequence",
                "  • Archive integrity",
                "  • Git tag consistency",
                "  • File completeness",
                "",
                "🚧 Full validation coming soon!",
                "",
                "Press ESC to continue"
            ],
            color=Colors.YELLOW
        )
        self.render()


def run_interactive():
    """Run the dev TUI"""
    tui = UnibosDevTUI()
    tui.run()


if __name__ == "__main__":
    run_interactive()
