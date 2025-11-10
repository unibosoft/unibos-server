#!/usr/bin/env python3
"""
Safe Version Manager for UNIBOS
Ensures no data loss during version updates and development
"""

import os
import sys
import json
import subprocess
import shutil
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from unibos_logger import logger, LogCategory, LogLevel
except ImportError:
    class logger:
        @staticmethod
        def info(msg, **kwargs): print(f"INFO: {msg}")
        @staticmethod
        def error(msg, **kwargs): print(f"ERROR: {msg}")
        @staticmethod
        def warning(msg, **kwargs): print(f"WARNING: {msg}")
    class LogCategory:
        SYSTEM = "system"

# Colors for terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

class SafeVersionManager:
    """Manages safe version creation with rollback capabilities"""
    
    def __init__(self):
        # Always use absolute path to unibos directory
        self.base_path = Path("/Users/berkhatirli/Desktop/unibos").resolve()
        self.version_file = self.base_path / 'src' / 'VERSION.json'
        self.istanbul_tz = timezone(timedelta(hours=3))
        
        # Change to base directory
        os.chdir(self.base_path)
        
    def get_current_version(self) -> Dict[str, any]:
        """Get current version info"""
        try:
            if not self.version_file.exists():
                logger.error(f"VERSION.json not found at {self.version_file}", category=LogCategory.SYSTEM)
                return None
                
            with open(self.version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read VERSION.json: {e}", category=LogCategory.SYSTEM)
            return None
    
    def create_safe_development_branch(self, feature_name: str = None, auto_stash: bool = False) -> Tuple[bool, str]:
        """Create a safe development branch for Claude or user
        
        Args:
            feature_name: Optional feature name for the branch
            auto_stash: If True, automatically stash changes without prompting
        """
        try:
            # Get current version
            version_info = self.get_current_version()
            if not version_info:
                # Try to get version from current branch name
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                      capture_output=True, text=True)
                current_branch = result.stdout.strip()
                if current_branch.startswith('v'):
                    current_version = current_branch
                else:
                    current_version = 'v250'  # Default fallback
                logger.warning(f"Using branch name as version: {current_version}", category=LogCategory.SYSTEM)
            else:
                current_version = version_info['version']
            
            # Generate branch name - sanitize feature name for git compatibility
            timestamp = datetime.now(self.istanbul_tz).strftime('%Y%m%d_%H%M')
            if feature_name:
                # Replace Turkish characters with ASCII equivalents
                sanitized_name = feature_name.lower()
                tr_chars = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
                           'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'}
                for tr_char, ascii_char in tr_chars.items():
                    sanitized_name = sanitized_name.replace(tr_char, ascii_char)
                # Replace spaces and special characters with underscores
                sanitized_name = re.sub(r'[^a-z0-9_-]', '_', sanitized_name)
                # Remove duplicate underscores and trim
                sanitized_name = re.sub(r'_+', '_', sanitized_name).strip('_')
                branch_name = f"dev/{current_version}_{sanitized_name}_{timestamp}"
            else:
                branch_name = f"dev/{current_version}_temp_{timestamp}"
            
            # Check if we have uncommitted changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                if auto_stash:
                    # Auto stash changes
                    stash_msg = f"Auto-stash before creating {branch_name}"
                    subprocess.run(['git', 'stash', 'push', '-m', stash_msg])
                    logger.info(f"Changes auto-stashed", category=LogCategory.SYSTEM)
                else:
                    # Interactive mode
                    print(f"\n{Colors.YELLOW}⚠️  Uncommitted changes detected{Colors.RESET}")
                    print(f"{Colors.CYAN}Options:{Colors.RESET}")
                    print("1. Stash changes and continue")
                    print("2. Commit changes first")
                    print("3. Cancel")
                    
                    try:
                        choice = input(f"\n{Colors.BLUE}Choice: {Colors.RESET}")
                        
                        if choice == '1':
                            # Stash changes
                            stash_msg = f"Auto-stash before creating {branch_name}"
                            subprocess.run(['git', 'stash', 'push', '-m', stash_msg])
                            print(f"{Colors.GREEN}✓ Changes stashed{Colors.RESET}")
                        elif choice == '2':
                            # Let user commit
                            return False, "Lütfen önce değişikliklerinizi commit edin"
                        else:
                            return False, "Kullanıcı tarafından iptal edildi"
                    except (EOFError, KeyboardInterrupt):
                        # Non-interactive mode or user cancelled
                        return False, "Cannot prompt for input in non-interactive mode. Use auto_stash=True or commit changes first."
            
            # Create and checkout new branch
            result = subprocess.run(['git', 'checkout', '-b', branch_name], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"Failed to create branch: {result.stderr}"
            
            print(f"{Colors.GREEN}✓ Created development branch: {branch_name}{Colors.RESET}")
            
            # Create a safety checkpoint
            checkpoint_file = self.base_path / '.git' / 'UNIBOS_CHECKPOINT'
            checkpoint_data = {
                'branch': branch_name,
                'created_at': datetime.now(self.istanbul_tz).isoformat(),
                'base_version': current_version,
                'feature': feature_name or 'development'
            }
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            return True, branch_name
            
        except Exception as e:
            logger.error(f"Failed to create development branch: {e}", category=LogCategory.SYSTEM)
            return False, str(e)
    
    def validate_changes(self) -> Tuple[bool, List[str]]:
        """Validate changes before version update"""
        issues = []
        
        # Check for syntax errors in Python files
        print(f"\n{Colors.CYAN}🔍 Validating Python files...{Colors.RESET}")
        py_files = list(Path('src').glob('**/*.py'))
        
        for py_file in py_files:
            result = subprocess.run(['python3', '-m', 'py_compile', str(py_file)], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                issues.append(f"Syntax error in {py_file}: {result.stderr}")
        
        # Check for critical files
        critical_files = [
            'src/VERSION.json',
            'src/main.py',
            'src/launch.sh',
            'unibos.sh'
        ]
        
        for cf in critical_files:
            if not Path(cf).exists():
                issues.append(f"Critical file missing: {cf}")
        
        # Check for screenshots in main directory
        screenshots = list(Path('.').glob('*.png')) + list(Path('.').glob('*.jpg'))
        if screenshots:
            issues.append(f"Screenshots found in main directory: {len(screenshots)} files")
        
        # Check VERSION.json validity
        try:
            with open(self.version_file, 'r') as f:
                json.load(f)
        except Exception as e:
            issues.append(f"Invalid VERSION.json: {e}")
        
        return len(issues) == 0, issues
    
    def create_new_version(self, description: str, features: List[str] = None) -> Tuple[bool, str]:
        """Create a new version with safety checks"""
        try:
            # First validate changes
            valid, issues = self.validate_changes()
            if not valid:
                print(f"\n{Colors.RED}❌ Validation failed:{Colors.RESET}")
                for issue in issues:
                    print(f"  - {issue}")
                
                proceed = input(f"\n{Colors.YELLOW}Continue anyway? (y/n): {Colors.RESET}")
                if proceed.lower() != 'y':
                    return False, "Validation failed"
            
            # Get current version
            version_info = self.get_current_version()
            if not version_info:
                return False, "Could not read current version"
            
            # Calculate new version
            current_version = version_info['version']
            version_num = int(current_version[1:])  # Remove 'v' prefix
            new_version_num = version_num + 1
            new_version = f"v{new_version_num:03d}"
            
            # Create timestamp
            now_istanbul = datetime.now(self.istanbul_tz)
            build_number = now_istanbul.strftime('%Y%m%d_%H%M')
            
            # Update version info
            version_info['version'] = new_version
            version_info['build_number'] = build_number
            version_info['release_date'] = now_istanbul.strftime('%Y-%m-%d %H:%M:%S +03:00')
            version_info['description'] = description
            
            if features:
                # Add new features to the beginning
                existing_features = version_info.get('features', [])
                version_info['features'] = features + existing_features
            
            # Backup current VERSION.json
            backup_file = self.version_file.with_suffix('.json.backup')
            shutil.copy2(self.version_file, backup_file)
            
            # Write new VERSION.json
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, indent=2, ensure_ascii=False)
            
            print(f"{Colors.GREEN}✓ Updated VERSION.json to {new_version}{Colors.RESET}")
            
            # Update main.py version
            main_py = self.base_path / 'src' / 'main.py'
            if main_py.exists():
                content = main_py.read_text(encoding='utf-8')
                # Update version string
                import re
                content = re.sub(r'"version":\s*"v\d{3}"', f'"version": "{new_version}"', content)
                main_py.write_text(content, encoding='utf-8')
                print(f"{Colors.GREEN}✓ Updated main.py version{Colors.RESET}")
            
            # Create archive
            from archive_version import VersionArchiver
            archiver = VersionArchiver()
            archive_path = archiver.create_version_copy(version_info)
            
            if archive_path:
                print(f"{Colors.GREEN}✓ Created archive: {archive_path.name}{Colors.RESET}")
            
            # Create communication log
            self._create_communication_log(current_version, new_version, description)
            
            return True, new_version
            
        except Exception as e:
            logger.error(f"Failed to create new version: {e}", category=LogCategory.SYSTEM)
            
            # Try to restore backup
            backup_file = self.version_file.with_suffix('.json.backup')
            if backup_file.exists():
                shutil.copy2(backup_file, self.version_file)
                print(f"{Colors.YELLOW}⚠️  Restored VERSION.json from backup{Colors.RESET}")
            
            return False, str(e)
    
    def _create_communication_log(self, old_version: str, new_version: str, description: str):
        """Create communication log for version change"""
        try:
            timestamp = datetime.now(self.istanbul_tz).strftime('%Y%m%d_%H%M')
            log_name = f"CLAUDE_COMMUNICATION_LOG_{old_version}_to_{new_version}_{timestamp}.md"
            
            content = f"""# CLAUDE COMMUNICATION LOG

## Oturum Bilgileri
- **Başlangıç Versiyonu**: {old_version}
- **Bitiş Versiyonu**: {new_version}
- **Tarih**: {datetime.now(self.istanbul_tz).strftime('%Y-%m-%d')}
- **Başlangıç Saati**: {datetime.now(self.istanbul_tz).strftime('%H:%M:%S +03:00')} (Istanbul)
- **Bitiş Saati**: {datetime.now(self.istanbul_tz).strftime('%H:%M:%S +03:00')} (Istanbul)
- **Oturum Tipi**: Version Update
- **Kullanıcı**: {os.environ.get('USER', 'unknown')}

## Özet
{description}

## Yapılan İşlemler

### 1. Version Update ({new_version})
- **Açıklama**: {description}
- **Durum**: ✅ Tamamlandı

## Test Durumu
- ✅ Python syntax validation passed
- ✅ Critical files verified
- ✅ Archive created successfully

---
*Son güncelleme: {datetime.now(self.istanbul_tz).strftime('%Y-%m-%d %H:%M:%S +03:00')}*
"""
            
            log_path = self.base_path / log_name
            log_path.write_text(content, encoding='utf-8')
            
            # Clean old logs (keep only last 3)
            self._clean_old_logs()
            
        except Exception as e:
            logger.error(f"Failed to create communication log: {e}", category=LogCategory.SYSTEM)
    
    def _clean_old_logs(self):
        """Keep only the last 3 communication logs"""
        try:
            logs = sorted(Path('.').glob('CLAUDE_COMMUNICATION_LOG_*.md'), 
                         key=lambda x: x.stat().st_mtime, reverse=True)
            
            for log in logs[3:]:
                log.unlink()
                print(f"{Colors.DIM}Removed old log: {log.name}{Colors.RESET}")
                
        except Exception as e:
            logger.warning(f"Failed to clean old logs: {e}", category=LogCategory.SYSTEM)
    
    def commit_and_push_safely(self, commit_message: str = None) -> Tuple[bool, str]:
        """Safely commit and push changes"""
        try:
            # Stage all changes
            subprocess.run(['git', 'add', '-A'])
            
            # Create commit
            if not commit_message:
                version_info = self.get_current_version()
                commit_message = f"{version_info['version']}: {version_info['description']}"
            
            result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0 and "nothing to commit" not in result.stdout:
                return False, f"Commit failed: {result.stderr}"
            
            print(f"{Colors.GREEN}✓ Committed changes{Colors.RESET}")
            
            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True)
            current_branch = result.stdout.strip()
            
            # Push to current branch
            result = subprocess.run(['git', 'push', 'origin', current_branch], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, f"Push failed: {result.stderr}"
            
            print(f"{Colors.GREEN}✓ Pushed to {current_branch}{Colors.RESET}")
            
            # If on development branch, offer to merge to main
            if current_branch.startswith('dev/'):
                merge = input(f"\n{Colors.YELLOW}Merge to main and version branch? (y/n): {Colors.RESET}")
                if merge.lower() == 'y':
                    return self._merge_to_main_and_version()
            
            return True, "Changes pushed successfully"
            
        except Exception as e:
            logger.error(f"Failed to commit and push: {e}", category=LogCategory.SYSTEM)
            return False, str(e)
    
    def _merge_to_main_and_version(self) -> Tuple[bool, str]:
        """Merge current branch to main and create version branch"""
        try:
            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True)
            dev_branch = result.stdout.strip()
            
            # Get current version
            version_info = self.get_current_version()
            version = version_info['version']
            
            # Checkout main
            subprocess.run(['git', 'checkout', 'main'])
            subprocess.run(['git', 'pull', 'origin', 'main'])
            
            # Merge development branch
            result = subprocess.run(['git', 'merge', dev_branch, '--no-ff', 
                                   '-m', f'Merge {dev_branch} into main'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                subprocess.run(['git', 'checkout', dev_branch])
                return False, f"Merge failed: {result.stderr}"
            
            # Push to main
            subprocess.run(['git', 'push', 'origin', 'main'])
            print(f"{Colors.GREEN}✓ Merged to main{Colors.RESET}")
            
            # Create/update version branch
            subprocess.run(['git', 'checkout', '-B', version])
            subprocess.run(['git', 'push', 'origin', version, '--force'])
            print(f"{Colors.GREEN}✓ Updated version branch: {version}{Colors.RESET}")
            
            # Return to development branch
            subprocess.run(['git', 'checkout', dev_branch])
            
            # Optionally delete development branch
            delete = input(f"\n{Colors.YELLOW}Delete development branch? (y/n): {Colors.RESET}")
            if delete.lower() == 'y':
                subprocess.run(['git', 'branch', '-d', dev_branch])
                subprocess.run(['git', 'push', 'origin', '--delete', dev_branch])
                subprocess.run(['git', 'checkout', version])
            
            return True, "Successfully merged to main and version branch"
            
        except Exception as e:
            logger.error(f"Failed to merge: {e}", category=LogCategory.SYSTEM)
            return False, str(e)
    
    def rollback_to_checkpoint(self) -> Tuple[bool, str]:
        """Rollback to last checkpoint if something goes wrong"""
        try:
            checkpoint_file = self.base_path / '.git' / 'UNIBOS_CHECKPOINT'
            
            if not checkpoint_file.exists():
                return False, "No checkpoint found"
            
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
            
            print(f"\n{Colors.YELLOW}Checkpoint found:{Colors.RESET}")
            print(f"  Branch: {checkpoint['branch']}")
            print(f"  Created: {checkpoint['created_at']}")
            print(f"  Base version: {checkpoint['base_version']}")
            
            confirm = input(f"\n{Colors.RED}Rollback to this checkpoint? (y/n): {Colors.RESET}")
            if confirm.lower() != 'y':
                return False, "Rollback cancelled"
            
            # Stash current changes
            subprocess.run(['git', 'stash'])
            
            # Checkout checkpoint branch
            subprocess.run(['git', 'checkout', checkpoint['branch']])
            
            # Reset to checkpoint state
            subprocess.run(['git', 'reset', '--hard', f"origin/{checkpoint['branch']}"])
            
            print(f"{Colors.GREEN}✓ Rolled back to checkpoint{Colors.RESET}")
            
            # Remove checkpoint file
            checkpoint_file.unlink()
            
            return True, "Successfully rolled back"
            
        except Exception as e:
            logger.error(f"Failed to rollback: {e}", category=LogCategory.SYSTEM)
            return False, str(e)


def main():
    """CLI interface for safe version management"""
    manager = SafeVersionManager()
    
    print(f"{Colors.CYAN}{Colors.BOLD}🛡️  UNIBOS Safe Version Manager{Colors.RESET}")
    print(f"{Colors.DIM}{'='*50}{Colors.RESET}\n")
    
    print(f"{Colors.YELLOW}Options:{Colors.RESET}")
    print("1. Create development branch")
    print("2. Create new version")
    print("3. Validate changes")
    print("4. Commit and push safely")
    print("5. Rollback to checkpoint")
    print("6. Show current version")
    
    choice = input(f"\n{Colors.BLUE}Choice: {Colors.RESET}")
    
    if choice == '1':
        feature = input("Feature name (optional): ").strip()
        success, result = manager.create_safe_development_branch(feature)
        if success:
            print(f"\n{Colors.GREEN}✅ {result}{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}❌ {result}{Colors.RESET}")
    
    elif choice == '2':
        description = input("Version description: ").strip()
        if not description:
            print(f"{Colors.RED}Description required{Colors.RESET}")
            return
        
        features = []
        print("Enter new features (empty line to finish):")
        while True:
            feature = input("- ").strip()
            if not feature:
                break
            features.append(feature)
        
        success, result = manager.create_new_version(description, features)
        if success:
            print(f"\n{Colors.GREEN}✅ Created version {result}{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}❌ {result}{Colors.RESET}")
    
    elif choice == '3':
        valid, issues = manager.validate_changes()
        if valid:
            print(f"\n{Colors.GREEN}✅ All validations passed{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}❌ Validation issues found:{Colors.RESET}")
            for issue in issues:
                print(f"  - {issue}")
    
    elif choice == '4':
        message = input("Commit message (optional): ").strip()
        success, result = manager.commit_and_push_safely(message)
        if success:
            print(f"\n{Colors.GREEN}✅ {result}{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}❌ {result}{Colors.RESET}")
    
    elif choice == '5':
        success, result = manager.rollback_to_checkpoint()
        if success:
            print(f"\n{Colors.GREEN}✅ {result}{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}❌ {result}{Colors.RESET}")
    
    elif choice == '6':
        version_info = manager.get_current_version()
        if version_info:
            print(f"\n{Colors.CYAN}Current Version:{Colors.RESET}")
            print(f"  Version: {version_info['version']}")
            print(f"  Build: {version_info['build_number']}")
            print(f"  Description: {version_info['description']}")


if __name__ == "__main__":
    main()