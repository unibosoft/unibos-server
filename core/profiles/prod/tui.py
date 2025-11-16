"""
UNIBOS Client TUI - End User Interface
Client TUI for end users running on local machines and Raspberry Pi
"""

import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.clients.tui import BaseTUI
from core.clients.tui.components import MenuSection
from core.clients.cli.framework.ui import MenuItem, Colors


class ClientTUI(BaseTUI):
    """Client TUI for end user UNIBOS nodes"""

    def __init__(self):
        """Initialize client TUI with proper config"""
        from core.clients.tui.base import TUIConfig

        config = TUIConfig(
            title="unibos",
            version="v0.534.0",
            location="local node",
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

        # Register client-specific handlers
        self.register_client_handlers()

    def get_profile_name(self) -> str:
        """Get profile name"""
        return "client"

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
        except (json.JSONDecodeError, IOError):
            return None

    def discover_modules(self) -> List[MenuItem]:
        """
        Discover installed modules dynamically

        Returns:
            List of MenuItem objects for each discovered module
        """
        modules_dir = Path("/Users/berkhatirli/Desktop/unibos-dev/modules")
        modules = []

        if modules_dir.exists():
            for module_path in sorted(modules_dir.iterdir()):
                if module_path.is_dir() and not module_path.name.startswith('_'):
                    if (module_path / '.enabled').exists():
                        metadata = self.load_module_metadata(module_path)

                        if metadata:
                            module_name = metadata.get('name', module_path.name)
                            module_icon = metadata.get('icon', '📦')
                            module_desc = metadata.get('description', f'Launch {module_name} module')

                            display_name_data = metadata.get('display_name')
                            if isinstance(display_name_data, dict):
                                display_name = display_name_data.get('en', module_name)
                            else:
                                display_name = module_name

                            description = (
                                f'{module_desc}\n\n'
                                f'→ Module: {metadata.get("id", module_path.name)}\n'
                                f'→ Version: {metadata.get("version", "unknown")}\n\n'
                                f'Press Enter to launch'
                            )

                            label = display_name.lower()
                        else:
                            label = module_path.name
                            module_icon = '📦'
                            description = f'Launch {module_path.name} module\n\nPress Enter to launch'

                        modules.append(MenuItem(
                            id=f"module_{module_path.name}",
                            label=label,
                            icon=module_icon,
                            description=description,
                            enabled=True
                        ))

        if not modules:
            modules.append(MenuItem(
                id='no_modules',
                label='no modules found',
                icon='📦',
                description='No modules installed.\n\n'
                           'Install modules to access applications.',
                enabled=False
            ))

        return modules

    def get_menu_sections(self) -> List[MenuSection]:
        """Get client menu sections - 3-section structure"""
        return [
            # Section 1: Modules (User applications)
            MenuSection(
                id='modules',
                label='modules',
                icon='📦',
                items=self.discover_modules()
            ),

            # Section 2: System (Client system management)
            MenuSection(
                id='system',
                label='system',
                icon='⚙️',
                items=[
                    MenuItem(
                        id='system_settings',
                        label='system settings',
                        icon='🔧',
                        description='system configuration\n\n'
                                   '→ General settings\n'
                                   '→ User preferences\n'
                                   '→ Appearance\n'
                                   '→ Privacy settings\n\n'
                                   'Configure system settings',
                        enabled=True
                    ),
                    MenuItem(
                        id='network_settings',
                        label='network settings',
                        icon='📡',
                        description='wifi and connectivity\n\n'
                                   '→ WiFi configuration\n'
                                   '→ Network status\n'
                                   '→ Connection info\n'
                                   '→ Peer discovery\n\n'
                                   'Manage network settings',
                        enabled=True
                    ),
                    MenuItem(
                        id='update_system',
                        label='update system',
                        icon='🔄',
                        description='check for updates\n\n'
                                   '→ System updates\n'
                                   '→ Module updates\n'
                                   '→ Download updates\n'
                                   '→ Install updates\n\n'
                                   'Update system and modules',
                        enabled=True
                    ),
                    MenuItem(
                        id='backup_data',
                        label='backup data',
                        icon='💾',
                        description='backup user data\n\n'
                                   '→ Create backup\n'
                                   '→ Restore backup\n'
                                   '→ Backup schedule\n'
                                   '→ Backup location\n\n'
                                   'Backup and restore data',
                        enabled=True
                    ),
                    MenuItem(
                        id='storage_management',
                        label='storage management',
                        icon='💿',
                        description='disk space management\n\n'
                                   '→ Disk usage\n'
                                   '→ Clean cache\n'
                                   '→ Remove old files\n'
                                   '→ External storage\n\n'
                                   'Manage storage space',
                        enabled=True
                    ),
                ]
            ),

            # Section 3: Info (Client information)
            MenuSection(
                id='info',
                label='info',
                icon='ℹ️',
                items=[
                    MenuItem(
                        id='system_status',
                        label='system status',
                        icon='💚',
                        description='device information\n\n'
                                   '→ System health\n'
                                   '→ Resource usage\n'
                                   '→ Service status\n'
                                   '→ Hardware info\n\n'
                                   'View system status',
                        enabled=True
                    ),
                    MenuItem(
                        id='module_status',
                        label='module status',
                        icon='📊',
                        description='installed modules\n\n'
                                   '→ Module list\n'
                                   '→ Module versions\n'
                                   '→ Module status\n'
                                   '→ Dependencies\n\n'
                                   'View module information',
                        enabled=True
                    ),
                    MenuItem(
                        id='network_status',
                        label='network status',
                        icon='🌐',
                        description='connectivity information\n\n'
                                   '→ Network interfaces\n'
                                   '→ IP addresses\n'
                                   '→ Connected peers\n'
                                   '→ Server connection\n\n'
                                   'View network status',
                        enabled=True
                    ),
                    MenuItem(
                        id='help_support',
                        label='help & support',
                        icon='❓',
                        description='documentation and help\n\n'
                                   '→ User guide\n'
                                   '→ FAQ\n'
                                   '→ Troubleshooting\n'
                                   '→ Contact support\n\n'
                                   'Get help and support',
                        enabled=True
                    ),
                    MenuItem(
                        id='about',
                        label='about',
                        icon='📋',
                        description='version and credits\n\n'
                                   '→ UNIBOS version\n'
                                   '→ System info\n'
                                   '→ Credits\n'
                                   '→ License\n\n'
                                   'About UNIBOS',
                        enabled=True
                    ),
                ]
            ),
        ]

    def register_client_handlers(self):
        """Register all client action handlers"""
        # System section handlers
        self.register_action('system_settings', self.handle_system_settings)
        self.register_action('network_settings', self.handle_network_settings)
        self.register_action('update_system', self.handle_update_system)
        self.register_action('backup_data', self.handle_backup_data)
        self.register_action('storage_management', self.handle_storage_management)

        # Info section handlers
        self.register_action('system_status', self.handle_system_status)
        self.register_action('module_status', self.handle_module_status)
        self.register_action('network_status', self.handle_network_status)
        self.register_action('help_support', self.handle_help_support)
        self.register_action('about', self.handle_about)

    # ===== SYSTEM SECTION HANDLERS =====

    def handle_system_settings(self, item: MenuItem) -> bool:
        """System configuration"""
        self.update_content(
            title="System Settings",
            lines=[
                "🔧 System Configuration",
                "",
                "Settings Categories:",
                "",
                "→ General Settings",
                "  • Language preferences",
                "  • Time zone",
                "  • Date format",
                "  • Default applications",
                "",
                "→ User Preferences",
                "  • Profile settings",
                "  • Privacy options",
                "  • Notifications",
                "  • Accessibility",
                "",
                "→ Appearance",
                "  • Theme selection",
                "  • Color scheme",
                "  • Font size",
                "  • Display settings",
                "",
                "🚧 Settings UI coming soon!",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_network_settings(self, item: MenuItem) -> bool:
        """Network configuration"""
        self.update_content(
            title="Network Settings",
            lines=[
                "📡 Network Configuration",
                "",
                "Network Options:",
                "",
                "→ WiFi Settings",
                "  • Available networks",
                "  • Connect to WiFi",
                "  • Saved networks",
                "  • WiFi password",
                "",
                "→ Network Info",
                "  • IP address",
                "  • MAC address",
                "  • Gateway",
                "  • DNS servers",
                "",
                "→ Peer Discovery",
                "  • Scan for UNIBOS nodes",
                "  • Connected peers",
                "  • Mesh network status",
                "",
                "Current status:",
                "  Run: ip addr show",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_update_system(self, item: MenuItem) -> bool:
        """Check for updates"""
        self.update_content(
            title="System Update",
            lines=[
                "🔄 System Update",
                "",
                "Update Options:",
                "",
                "→ Check for Updates",
                "  • System updates",
                "  • Module updates",
                "  • Security patches",
                "",
                "→ Update Process",
                "  1. Check for updates",
                "  2. Download updates",
                "  3. Install updates",
                "  4. Restart if needed",
                "",
                "→ Current Version",
                "  • UNIBOS: v0.534.0",
                "  • Profile: client",
                "",
                "To update manually:",
                "  Run: unibos update",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_backup_data(self, item: MenuItem) -> bool:
        """Backup user data"""
        self.update_content(
            title="Data Backup",
            lines=[
                "💾 Backup & Restore",
                "",
                "Backup Options:",
                "",
                "→ Create Backup",
                "  • User data",
                "  • Module data",
                "  • Settings",
                "  • Database",
                "",
                "→ Restore Backup",
                "  • Select backup file",
                "  • Verify integrity",
                "  • Restore data",
                "",
                "→ Backup Schedule",
                "  • Automatic backups",
                "  • Backup frequency",
                "  • Retention policy",
                "",
                "→ Backup Location",
                "  • Local storage",
                "  • External drive",
                "  • Network location",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_storage_management(self, item: MenuItem) -> bool:
        """Manage storage"""
        self.update_content(
            title="Storage Management",
            lines=[
                "💿 Storage Management",
                "",
                "Storage Information:",
                "",
                "→ Disk Usage",
                "  Run: df -h",
                "",
                "→ Large Files",
                "  Find: du -h ~ | sort -hr | head -20",
                "",
                "→ Clean Cache",
                "  • Clear temporary files",
                "  • Remove old logs",
                "  • Clean package cache",
                "",
                "→ External Storage",
                "  • Mount USB drives",
                "  • SD card management",
                "  • Network shares",
                "",
                "Storage cleanup tips:",
                "  • Remove unused modules",
                "  • Clean old backups",
                "  • Archive old data",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    # ===== INFO SECTION HANDLERS =====

    def handle_system_status(self, item: MenuItem) -> bool:
        """Show system status"""
        self.update_content(
            title="System Status",
            lines=[
                "💚 System Status",
                "",
                "System Information:",
                "",
                "→ Health: Operational",
                "→ Profile: Client",
                "→ Version: v0.534.0",
                "",
                "Resources:",
                "  Run: top",
                "",
                "Services:",
                "  • Django: Check with systemctl",
                "  • Database: Check with systemctl",
                "",
                "Disk Space:",
                "  Run: df -h",
                "",
                "Memory:",
                "  Run: free -h",
                "",
                "Uptime:",
                "  Run: uptime",
                "",
                "Press ESC to continue"
            ],
            color=Colors.GREEN
        )
        self.render()
        return True

    def handle_module_status(self, item: MenuItem) -> bool:
        """Show module status"""
        modules_dir = Path("/Users/berkhatirli/Desktop/unibos-dev/modules")
        module_count = 0

        if modules_dir.exists():
            module_count = len([m for m in modules_dir.iterdir()
                               if m.is_dir() and (m / '.enabled').exists()])

        self.update_content(
            title="Module Status",
            lines=[
                "📊 Installed Modules",
                "",
                f"Total modules: {module_count}",
                "",
                "Module Information:",
                "",
                "→ View all modules:",
                "  Check the 'Modules' section in main menu",
                "",
                "→ Module directory:",
                f"  {modules_dir}",
                "",
                "→ Enable module:",
                "  Create .enabled file in module directory",
                "",
                "→ Module metadata:",
                "  Check module.json file",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_network_status(self, item: MenuItem) -> bool:
        """Show network status"""
        self.update_content(
            title="Network Status",
            lines=[
                "🌐 Network Information",
                "",
                "Network Interfaces:",
                "  Run: ip addr show",
                "",
                "WiFi Status:",
                "  Run: nmcli device wifi list",
                "",
                "Connection Info:",
                "  • Check IP address",
                "  • Check gateway",
                "  • Check DNS",
                "",
                "Peer Discovery:",
                "  • Scan for UNIBOS nodes",
                "  • View connected peers",
                "  • Mesh network status",
                "",
                "Server Connection:",
                "  • Connection to rocksteady",
                "  • Sync status",
                "  • Last sync time",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_help_support(self, item: MenuItem) -> bool:
        """Show help and support"""
        self.update_content(
            title="Help & Support",
            lines=[
                "❓ Help & Support",
                "",
                "Documentation:",
                "",
                "→ User Guide",
                "  • Getting started",
                "  • Module usage",
                "  • Troubleshooting",
                "  • Tips and tricks",
                "",
                "→ FAQ",
                "  • Common questions",
                "  • Known issues",
                "  • Best practices",
                "",
                "→ Support",
                "  • Contact: support@unibos.com",
                "  • Community forum",
                "  • GitHub issues",
                "",
                "→ Resources",
                "  • Documentation: https://docs.unibos.com",
                "  • Video tutorials",
                "  • Sample projects",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True

    def handle_about(self, item: MenuItem) -> bool:
        """Show about information"""
        import socket
        import platform

        hostname = socket.gethostname()
        system = platform.system()
        machine = platform.machine()

        self.update_content(
            title="About UNIBOS",
            lines=[
                "📋 UNIBOS - Universal Integrated Backend Operating System",
                "",
                "Version Information:",
                "",
                f"→ Version: v0.534.0",
                f"→ Profile: Client",
                f"→ Platform: {system} {machine}",
                f"→ Hostname: {hostname}",
                "",
                "About:",
                "",
                "UNIBOS is a modular, offline-first operating system",
                "designed for distributed computing and peer-to-peer",
                "collaboration.",
                "",
                "Features:",
                "  • Modular architecture",
                "  • Offline-first operation",
                "  • P2P mesh networking",
                "  • Multi-device sync",
                "",
                "Credits:",
                "  • Developer: Berk Hatirli",
                "  • License: MIT",
                "",
                "Press ESC to continue"
            ],
            color=Colors.CYAN
        )
        self.render()
        return True


def run_interactive():
    """Run the client TUI"""
    tui = ClientTUI()
    tui.run()


if __name__ == "__main__":
    run_interactive()
