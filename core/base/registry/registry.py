"""
UNIBOS Module Registry

Auto-discovery and management of UNIBOS modules.
Scans modules/ directory for module.json files and provides:
- Module discovery
- Dependency resolution
- Platform compatibility checking
- Dynamic INSTALLED_APPS generation
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class ModuleStatus(Enum):
    """Module status"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    AVAILABLE = "available"
    INCOMPATIBLE = "incompatible"
    ERROR = "error"


@dataclass
class ModuleInfo:
    """Module information from module.json"""
    # Basic info
    id: str
    name: str
    version: str
    description: str
    author: str
    icon: str = "📦"

    # Paths
    module_path: Path = None
    json_path: Path = None

    # Capabilities
    capabilities: Dict = field(default_factory=dict)

    # Dependencies
    dependencies: Dict = field(default_factory=dict)

    # Status
    status: ModuleStatus = ModuleStatus.AVAILABLE
    enabled: bool = False

    # Platform requirements
    platforms: List[str] = field(default_factory=list)

    # Raw metadata
    metadata: Dict = field(default_factory=dict)

    def has_backend(self) -> bool:
        """Check if module has backend component"""
        return self.capabilities.get('backend', False)

    def has_web(self) -> bool:
        """Check if module has web UI"""
        return self.capabilities.get('web', False)

    def has_mobile(self) -> bool:
        """Check if module has mobile app"""
        return self.capabilities.get('mobile', False)

    def has_cli(self) -> bool:
        """Check if module has CLI"""
        return self.capabilities.get('cli', False)

    def is_realtime(self) -> bool:
        """Check if module requires realtime (WebSocket)"""
        return self.capabilities.get('realtime', False)

    def get_django_app_label(self) -> str:
        """Get Django app label for INSTALLED_APPS"""
        return f"modules.{self.id}.backend"


class ModuleRegistry:
    """
    UNIBOS Module Registry

    Discovers and manages modules in the modules/ directory.
    """

    def __init__(self, modules_dir: Optional[Path] = None):
        """
        Initialize module registry

        Args:
            modules_dir: Path to modules directory (default: GIT_ROOT/modules/)
        """
        # Set modules directory
        if modules_dir is None:
            # Try to find git root (for pipx installed packages)
            import subprocess
            import os

            # First check UNIBOS_ROOT environment variable
            unibos_root = os.environ.get('UNIBOS_ROOT')
            if unibos_root:
                modules_dir = Path(unibos_root) / 'modules'
            else:
                # Try git root
                try:
                    result = subprocess.run(
                        ['git', 'rev-parse', '--show-toplevel'],
                        cwd=Path.cwd(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        git_root = Path(result.stdout.strip())
                        modules_dir = git_root / 'modules'
                    else:
                        # Fallback to relative path from __file__
                        project_root = Path(__file__).parent.parent.parent
                        modules_dir = project_root / 'modules'
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    # Git not available, use relative path
                    project_root = Path(__file__).parent.parent.parent
                    modules_dir = project_root / 'modules'

        self.modules_dir = Path(modules_dir)
        self.modules: Dict[str, ModuleInfo] = {}

        # Discover modules
        self._discover_modules()

    def _discover_modules(self):
        """Discover all modules by scanning module.json files"""
        if not self.modules_dir.exists():
            return

        for module_dir in self.modules_dir.iterdir():
            if not module_dir.is_dir():
                continue

            if module_dir.name.startswith('.') or module_dir.name.startswith('_'):
                continue

            json_file = module_dir / 'module.json'
            if not json_file.exists():
                continue

            # Load module info
            try:
                module_info = self._load_module_info(json_file, module_dir)
                self.modules[module_info.id] = module_info
            except Exception as e:
                print(f"Warning: Failed to load module {module_dir.name}: {e}")

    def _load_module_info(self, json_file: Path, module_dir: Path) -> ModuleInfo:
        """Load module info from module.json"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract basic info
        module_id = data.get('id', module_dir.name)
        name = data.get('name', module_id)
        version = data.get('version', '0.0.0')
        description = data.get('description', '')
        author = data.get('author', 'Unknown')
        icon = data.get('icon', '📦')

        # Extract capabilities
        capabilities = data.get('capabilities', {})

        # Extract dependencies
        dependencies = data.get('dependencies', {})

        # Platform requirements
        platforms = data.get('platforms', ['linux', 'macos', 'windows'])

        # Check if enabled (check for marker file)
        enabled_file = module_dir / '.enabled'
        enabled = enabled_file.exists()

        # Determine status
        status = ModuleStatus.ENABLED if enabled else ModuleStatus.AVAILABLE

        return ModuleInfo(
            id=module_id,
            name=name,
            version=version,
            description=description,
            author=author,
            icon=icon,
            module_path=module_dir,
            json_path=json_file,
            capabilities=capabilities,
            dependencies=dependencies,
            status=status,
            enabled=enabled,
            platforms=platforms,
            metadata=data,
        )

    def get_module(self, module_id: str) -> Optional[ModuleInfo]:
        """Get module by ID"""
        return self.modules.get(module_id)

    def get_all_modules(self) -> List[ModuleInfo]:
        """Get all discovered modules"""
        return list(self.modules.values())

    def get_enabled_modules(self) -> List[ModuleInfo]:
        """Get only enabled modules"""
        return [m for m in self.modules.values() if m.enabled]

    def get_available_modules(self) -> List[ModuleInfo]:
        """Get modules that can be enabled"""
        return [m for m in self.modules.values() if not m.enabled]

    def enable_module(self, module_id: str) -> bool:
        """
        Enable a module

        Args:
            module_id: Module ID to enable

        Returns:
            bool: True if successful
        """
        module = self.get_module(module_id)
        if not module:
            return False

        # Create .enabled marker file
        enabled_file = module.module_path / '.enabled'
        enabled_file.touch()

        # Update status
        module.enabled = True
        module.status = ModuleStatus.ENABLED

        return True

    def disable_module(self, module_id: str) -> bool:
        """
        Disable a module

        Args:
            module_id: Module ID to disable

        Returns:
            bool: True if successful
        """
        module = self.get_module(module_id)
        if not module:
            return False

        # Remove .enabled marker file
        enabled_file = module.module_path / '.enabled'
        if enabled_file.exists():
            enabled_file.unlink()

        # Update status
        module.enabled = False
        module.status = ModuleStatus.AVAILABLE

        return True

    def get_django_apps(self) -> List[str]:
        """
        Get list of Django apps for INSTALLED_APPS

        Returns only enabled modules with backend capability.
        """
        apps = []

        for module in self.get_enabled_modules():
            if module.has_backend():
                apps.append(module.get_django_app_label())

        return apps

    def check_dependencies(self, module_id: str) -> Dict[str, bool]:
        """
        Check if module dependencies are met

        Args:
            module_id: Module ID to check

        Returns:
            Dict mapping dependency names to whether they're satisfied
        """
        module = self.get_module(module_id)
        if not module:
            return {}

        results = {}

        # Check core module dependencies
        core_deps = module.dependencies.get('core_modules', [])
        for dep in core_deps:
            # TODO: Check if core module exists
            results[f"core:{dep}"] = True

        # Check module dependencies
        module_deps = module.dependencies.get('modules', [])
        for dep in module_deps:
            dep_module = self.get_module(dep)
            results[f"module:{dep}"] = dep_module is not None and dep_module.enabled

        # Check Python package dependencies
        python_deps = module.dependencies.get('python_packages', [])
        for dep in python_deps:
            # TODO: Check if package is installed
            results[f"python:{dep}"] = True

        return results

    def check_platform_compatibility(self, module_id: str, platform: str) -> bool:
        """
        Check if module is compatible with platform

        Args:
            module_id: Module ID
            platform: Platform name (linux, macos, windows, raspberry_pi)

        Returns:
            bool: True if compatible
        """
        module = self.get_module(module_id)
        if not module:
            return False

        if not module.platforms:
            return True  # No platform restrictions

        return platform in module.platforms

    def get_module_stats(self) -> Dict:
        """Get module statistics"""
        total = len(self.modules)
        enabled = len(self.get_enabled_modules())
        available = len(self.get_available_modules())

        # Count by capability
        backend = sum(1 for m in self.modules.values() if m.has_backend())
        web = sum(1 for m in self.modules.values() if m.has_web())
        mobile = sum(1 for m in self.modules.values() if m.has_mobile())
        cli = sum(1 for m in self.modules.values() if m.has_cli())
        realtime = sum(1 for m in self.modules.values() if m.is_realtime())

        return {
            'total': total,
            'enabled': enabled,
            'available': available,
            'by_capability': {
                'backend': backend,
                'web': web,
                'mobile': mobile,
                'cli': cli,
                'realtime': realtime,
            }
        }


# Singleton instance
_module_registry: Optional[ModuleRegistry] = None


def get_module_registry() -> ModuleRegistry:
    """Get singleton module registry"""
    global _module_registry

    if _module_registry is None:
        _module_registry = ModuleRegistry()

    return _module_registry
