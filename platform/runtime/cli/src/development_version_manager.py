#!/usr/bin/env python3
"""
Development Version Manager for UNIBOS
Manages development versions for safe code modifications
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unibos_logger import logger, LogCategory, LogLevel

class DevelopmentVersionManager:
    """Manages development versions for safe code modifications"""
    
    def __init__(self):
        self.base_path = Path("/Users/berkhatirli/Desktop/unibos")
        self.versions_path = self.base_path / "archive" / "versions"
        self.dev_versions_path = self.base_path / "dev_versions"
        self.version_file = self.base_path / "src" / "VERSION.json"
        self.current_version = self._get_current_version()
        
        # Create dev_versions directory if not exists
        self.dev_versions_path.mkdir(exist_ok=True)
        
    def _get_current_version(self) -> str:
        """Get current version from VERSION.json"""
        try:
            with open(self.version_file, 'r') as f:
                data = json.load(f)
                return data.get('version', 'unknown')
        except:
            return 'unknown'
    
    def create_development_version(self, purpose: str = "development") -> Optional[Path]:
        """Create a new development version from current codebase"""
        logger.info(f"Creating development version from {self.current_version}", 
                   category=LogCategory.SYSTEM)
        
        # Generate dev version name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        dev_version_name = f"{self.current_version}_dev_{timestamp}"
        dev_path = self.dev_versions_path / dev_version_name
        
        try:
            # Copy essential directories
            essential_dirs = ['src', 'projects', 'tests']
            essential_files = [
                'CLAUDE.md', 'CLAUDE_CORE.md', 'CLAUDE_RULES.md', 
                'CLAUDE_VERSION.md', 'CLAUDE_SUGGESTIONS.md',
                'README.md', 'unibos.sh', 'launch.sh'
            ]
            
            # Create dev version directory
            dev_path.mkdir(exist_ok=True)
            
            # Copy directories
            for dir_name in essential_dirs:
                src = self.base_path / dir_name
                if src.exists():
                    dst = dev_path / dir_name
                    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                        '__pycache__', '*.pyc', '.DS_Store', 'venv', '.git'
                    ))
                    logger.debug(f"Copied {dir_name} to dev version", 
                               category=LogCategory.SYSTEM)
            
            # Copy files
            for file_name in essential_files:
                src = self.base_path / file_name
                if src.exists():
                    dst = dev_path / file_name
                    shutil.copy2(src, dst)
            
            # Create dev version info
            dev_info = {
                "base_version": self.current_version,
                "dev_version": dev_version_name,
                "created": datetime.now().isoformat(),
                "purpose": purpose,
                "status": "in_development",
                "changes": []
            }
            
            with open(dev_path / "DEV_VERSION_INFO.json", 'w') as f:
                json.dump(dev_info, f, indent=2)
            
            # Update VERSION.json in dev version
            version_file = dev_path / "src" / "VERSION.json"
            if version_file.exists():
                with open(version_file, 'r') as f:
                    version_data = json.load(f)
                
                version_data['version'] = f"{self.current_version}_dev"
                version_data['is_development'] = True
                version_data['base_version'] = self.current_version
                
                with open(version_file, 'w') as f:
                    json.dump(version_data, f, indent=2)
            
            logger.success(f"Created development version: {dev_version_name}", 
                          category=LogCategory.SYSTEM)
            return dev_path
            
        except Exception as e:
            logger.error(f"Failed to create development version: {e}", 
                        category=LogCategory.SYSTEM)
            if dev_path.exists():
                shutil.rmtree(dev_path)
            return None
    
    def list_dev_versions(self) -> Dict[str, Any]:
        """List all development versions"""
        dev_versions = {}
        
        if not self.dev_versions_path.exists():
            return dev_versions
        
        for dev_dir in self.dev_versions_path.iterdir():
            if dev_dir.is_dir():
                info_file = dev_dir / "DEV_VERSION_INFO.json"
                if info_file.exists():
                    with open(info_file, 'r') as f:
                        info = json.load(f)
                        dev_versions[dev_dir.name] = info
        
        return dev_versions
    
    def switch_to_dev_version(self, dev_version_name: str) -> bool:
        """Switch to a development version (for testing)"""
        dev_path = self.dev_versions_path / dev_version_name
        
        if not dev_path.exists():
            logger.error(f"Development version not found: {dev_version_name}", 
                        category=LogCategory.SYSTEM)
            return False
        
        # Create a symlink or update launch script to use dev version
        launch_script = self.base_path / "launch_dev.sh"
        
        script_content = f"""#!/bin/bash
# Launch script for development version: {dev_version_name}

cd "{dev_path}"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Run the development version
python3 src/main.py

echo "Development version {dev_version_name} terminated."
"""
        
        with open(launch_script, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(launch_script, 0o755)
        
        logger.info(f"Created launch script for dev version: {dev_version_name}", 
                   category=LogCategory.SYSTEM)
        print(f"\nTo test the development version, run: ./launch_dev.sh")
        
        return True
    
    def merge_dev_version(self, dev_version_name: str, 
                         new_version: Optional[str] = None) -> bool:
        """Merge development version back to main codebase"""
        dev_path = self.dev_versions_path / dev_version_name
        
        if not dev_path.exists():
            logger.error(f"Development version not found: {dev_version_name}", 
                        category=LogCategory.SYSTEM)
            return False
        
        try:
            # First, archive current version
            from archive_version import archive_current_version
            archive_success = archive_current_version()
            
            if not archive_success:
                logger.error("Failed to archive current version", 
                           category=LogCategory.SYSTEM)
                return False
            
            # Copy dev version files back to main
            for item in dev_path.iterdir():
                if item.name in ['DEV_VERSION_INFO.json', '.git']:
                    continue
                
                dst = self.base_path / item.name
                
                if item.is_dir():
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(item, dst, ignore=shutil.ignore_patterns(
                        '__pycache__', '*.pyc', '.DS_Store'
                    ))
                else:
                    shutil.copy2(item, dst)
            
            # Update version if provided
            if new_version:
                version_file = self.base_path / "src" / "VERSION.json"
                with open(version_file, 'r') as f:
                    version_data = json.load(f)
                
                version_data['version'] = new_version
                version_data['is_development'] = False
                version_data.pop('base_version', None)
                version_data['merged_from'] = dev_version_name
                
                with open(version_file, 'w') as f:
                    json.dump(version_data, f, indent=2)
                
                # Update main.py version
                main_py = self.base_path / "src" / "main.py"
                if main_py.exists():
                    content = main_py.read_text()
                    # Update version references
                    old_version = self.current_version
                    content = content.replace(f'v{old_version.lstrip("v")}', 
                                            f'v{new_version.lstrip("v")}')
                    main_py.write_text(content)
            
            # Archive the dev version
            archive_path = self.dev_versions_path / "archived"
            archive_path.mkdir(exist_ok=True)
            shutil.move(str(dev_path), str(archive_path / dev_version_name))
            
            logger.success(f"Merged development version: {dev_version_name}", 
                          category=LogCategory.SYSTEM)
            return True
            
        except Exception as e:
            logger.error(f"Failed to merge development version: {e}", 
                        category=LogCategory.SYSTEM)
            return False
    
    def cleanup_old_dev_versions(self, keep_count: int = 5):
        """Clean up old development versions"""
        archived_path = self.dev_versions_path / "archived"
        if not archived_path.exists():
            return
        
        # Get all archived versions sorted by date
        archived_versions = []
        for dev_dir in archived_path.iterdir():
            if dev_dir.is_dir():
                info_file = dev_dir / "DEV_VERSION_INFO.json"
                if info_file.exists():
                    with open(info_file, 'r') as f:
                        info = json.load(f)
                        archived_versions.append({
                            'path': dev_dir,
                            'created': info.get('created', ''),
                            'name': dev_dir.name
                        })
        
        # Sort by creation date
        archived_versions.sort(key=lambda x: x['created'])
        
        # Remove old versions
        if len(archived_versions) > keep_count:
            for version in archived_versions[:-keep_count]:
                shutil.rmtree(version['path'])
                logger.info(f"Removed old dev version: {version['name']}", 
                           category=LogCategory.SYSTEM)

# Export for use in other modules
dev_version_manager = DevelopmentVersionManager()

if __name__ == "__main__":
    # Test the manager
    manager = DevelopmentVersionManager()
    
    # Create a development version
    dev_path = manager.create_development_version("Testing development version system")
    if dev_path:
        print(f"Created development version at: {dev_path}")
    
    # List development versions
    versions = manager.list_dev_versions()
    print(f"\nDevelopment versions: {len(versions)}")
    for name, info in versions.items():
        print(f"  - {name}: {info['status']} (created: {info['created'][:10]})")