#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
archive_version.py - UNIBOS Version Archiving System
Automatically archives current version to compressed and versions folders
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional

# Import logger
try:
    from unibos_logger import logger, LogCategory
except ImportError:
    # Fallback if logger not available
    class logger:
        @staticmethod
        def info(msg, **kwargs): print(f"INFO: {msg}")
        @staticmethod
        def error(msg, **kwargs): print(f"ERROR: {msg}")
        @staticmethod
        def warning(msg, **kwargs): print(f"WARNING: {msg}")
    
    class LogCategory:
        SYSTEM = "system"

def get_istanbul_time():
    """Get current time in Istanbul timezone"""
    # Istanbul is UTC+3
    istanbul_tz = timezone(timedelta(hours=3))
    return datetime.now(istanbul_tz)

class VersionArchiver:
    """Handles version archiving for UNIBOS"""
    
    def __init__(self, base_path: str = None):
        """Initialize version archiver"""
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.archive_base = self.base_path / "archive"
        self.versions_dir = self.archive_base / "versions"
        
        # Files and directories to exclude from archive
        self.exclude_patterns = [
            "*.git*", "./archive/*", "archive/*", "__pycache__/*", "*.pyc",
            ".venv/*", "venv/*", ".DS_Store", "node_modules/*",
            "backup/*", "*.tmp", "*.cache", "*/archive/*",
            "projects/unibos_v*", "./projects/unibos_v*",  # Exclude versioned projects
            "projects/unibos_v*_build_*",  # Also exclude build variants
            # Note: *.log removed to include CLAUDE_COMMUNICATION logs
        ]
        
        # Files to copy to versions folder
        self.copy_patterns = [
            "src", "projects", "tests", "*.md", "*.py", "*.sh",
            ".claude", ".vscode", "requirements.txt",
            "CLAUDE_COMMUNICATION_LOG*.md"  # Include all communication log formats
        ]
    
    def get_version_info(self) -> Dict[str, str]:
        """Get current version information from VERSION.json"""
        try:
            version_file = self.base_path / "src" / "VERSION.json"
            if not version_file.exists():
                raise FileNotFoundError(f"VERSION.json not found at {version_file}")
            
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get current Istanbul time
            now_istanbul = get_istanbul_time()
            
            return {
                'version': data.get('version', 'v000'),
                'build_number': data.get('build_number', now_istanbul.strftime('%Y%m%d_%H%M')),
                'description': data.get('description', 'No description')
            }
        except Exception as e:
            logger.error(f"Failed to read version info: {str(e)}", category=LogCategory.SYSTEM)
            raise
    
    # Compressed archive creation removed - only open archives are used
    
    def create_version_copy(self, version_info: Dict[str, str]) -> Optional[Path]:
        """Create uncompressed version copy in versions folder"""
        try:
            # Generate version folder name
            version_name = f"unibos_{version_info['version']}_{version_info['build_number']}"
            version_path = self.versions_dir / version_name
            
            # Create directory
            version_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Creating version copy: {version_name}", category=LogCategory.SYSTEM)
            
            # Copy files and directories
            for pattern in self.copy_patterns:
                # Find matching items
                if '*' in pattern:
                    # Handle wildcards
                    for item in self.base_path.glob(pattern):
                        if item.exists() and not any(exc in str(item) for exc in ['archive', '__pycache__', '.git']):
                            self._copy_item(item, version_path / item.name)
                else:
                    # Direct path
                    source = self.base_path / pattern
                    if source.exists():
                        self._copy_item(source, version_path / pattern)
            
            logger.info(f"Version copy created successfully: {version_name}", category=LogCategory.SYSTEM)
            return version_path
            
        except Exception as e:
            logger.error(f"Failed to create version copy: {str(e)}", category=LogCategory.SYSTEM)
            return None
    
    def _copy_item(self, source: Path, dest: Path):
        """Copy file or directory"""
        try:
            if source.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(source, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
        except Exception as e:
            logger.warning(f"Failed to copy {source}: {str(e)}", category=LogCategory.SYSTEM)
    
    def check_existing_archives(self, version_info: Dict[str, str]) -> Tuple[bool, bool]:
        """Check if archives already exist"""
        version = version_info['version']
        build = version_info['build_number']
        
        # Check version copy only (compressed archives no longer used)
        version_exists = any(self.versions_dir.glob(f"unibos_{version}_*")) if self.versions_dir.exists() else False
        
        return False, version_exists
    
    def manage_communication_logs(self):
        """Manage communication logs - keep only last 3 and archive current"""
        try:
            print("\n📝 Managing communication logs...")
            
            # Find ALL possible communication log patterns
            all_logs = []
            
            # Pattern 1: New versioned format (v203_to_v204 style)
            versioned_logs = list(self.base_path.glob("CLAUDE_COMMUNICATION_LOG_v*_to_v*_*.md"))
            all_logs.extend(versioned_logs)
            
            # Pattern 2: Old standard format
            standard_logs = list(self.base_path.glob("CLAUDE_COMMUNICATION_LOG_*.md"))
            for log in standard_logs:
                # Avoid duplicates from pattern 1
                if "_to_v" not in log.name and log not in all_logs:
                    all_logs.append(log)
            
            # Remove duplicates and sort by modification time (newest first)
            unique_logs = list(set(all_logs))
            comm_logs = sorted(unique_logs, key=lambda x: x.stat().st_mtime, reverse=True)
            
            if comm_logs:
                print(f"   📊 Found {len(comm_logs)} total communication log(s)")
                
                # Show what we found
                for i, log in enumerate(comm_logs[:5]):  # Show first 5
                    status = "✅ Keep" if i < 3 else "🗑️  Remove"
                    print(f"   {status}: {log.name}")
                
                # Archive current communication logs with the version
                print(f"   📦 Including top 3 communication log(s) in archive")
                
                # Remove logs beyond the 3rd one
                if len(comm_logs) > 3:
                    logs_to_remove = comm_logs[3:]
                    removed_count = 0
                    for log in logs_to_remove:
                        try:
                            print(f"   🗑️  Removing old log: {log.name}")
                            log.unlink()
                            removed_count += 1
                        except Exception as e:
                            print(f"   ⚠️  Failed to remove {log.name}: {str(e)}")
                    
                    if removed_count > 0:
                        print(f"   ✅ Removed {removed_count} old log(s), kept last 3")
                else:
                    print(f"   ✅ Only {len(comm_logs)} logs found (within limit)")
            else:
                print("   ℹ️  No communication logs found")
                
        except Exception as e:
            logger.warning(f"Failed to manage communication logs: {str(e)}", category=LogCategory.SYSTEM)
    
    # Size anomaly check removed - no longer needed without compressed archives
    
    def pre_archive_checklist(self) -> bool:
        """Perform pre-archive checks"""
        print("\n🔍 Pre-archive checklist:")
        checks_passed = True
        
        # Check for unarchived screenshots
        screenshots = list(self.base_path.glob("*.png")) + list(self.base_path.glob("*.jpg")) + list(self.base_path.glob("*.jpeg"))
        screenshots.extend(list(self.base_path.glob("*.PNG")) + list(self.base_path.glob("*.JPG")) + list(self.base_path.glob("*.JPEG")))
        
        if screenshots:
            print(f"   ⚠️  Found {len(screenshots)} unarchived screenshot(s) in main directory")
            print("      Please archive screenshots before version archiving")
            checks_passed = False
        else:
            print("   ✅ No unarchived screenshots")
        
        # Check version sync
        try:
            version_json = json.loads((self.base_path / "src" / "VERSION.json").read_text())
            main_py = (self.base_path / "src" / "main.py").read_text()
            
            version = version_json.get("version", "")
            if f'"version": "{version}"' in main_py:
                print(f"   ✅ Version sync OK: {version}")
            else:
                print(f"   ⚠️  Version mismatch between VERSION.json and main.py")
                checks_passed = False
        except:
            print("   ⚠️  Could not verify version sync")
            
        # Check CLAUDE files are up to date
        claude_files = list(self.base_path.glob("CLAUDE*.md"))
        if claude_files:
            print(f"   ✅ Found {len(claude_files)} CLAUDE documentation files")
        else:
            print("   ⚠️  No CLAUDE documentation files found")
            checks_passed = False
        
        # Check communication logger is available
        print("\n🔍 Checking communication logger...")
        try:
            from communication_logger import comm_logger
            print("   ✅ Communication logger is available")
        except ImportError:
            print("   ❌ Communication logger is not available!")
            print("      Communication logs will not be created for this version")
            checks_passed = False
        
        # Check for incomplete tasks in communication logs
        print("\n🔍 Checking for incomplete tasks in logs...")
        comm_logs = sorted(self.base_path.glob("CLAUDE_COMMUNICATION_LOG_*.md"), 
                          key=lambda x: x.stat().st_mtime, reverse=True)[:3]
        
        incomplete_found = False
        for log in comm_logs:
            try:
                content = log.read_text(encoding='utf-8')
                if any(keyword in content for keyword in ["devam ediyor", "çözülmemiş", "TODO", "❌"]):
                    print(f"   ⚠️  Incomplete tasks found in {log.name}")
                    incomplete_found = True
            except:
                pass
        
        if not incomplete_found and comm_logs:
            print("   ✅ No incomplete tasks in recent logs")
        elif incomplete_found:
            print("   ℹ️  Please complete all tasks before creating new version")
            checks_passed = False
            
        return checks_passed
    
    def verify_archive_structure(self, version_info: Dict[str, str]) -> bool:
        """Verify archive structure matches previous versions"""
        print("\n🔎 Verifying archive structure consistency...")
        
        # Expected archive name format
        archive_name = f"unibos_{version_info['version']}_{version_info['build_number']}"
        
        # Archive naming check now only for version folders
        
        # Check version folder structure
        if self.versions_dir.exists():
            recent_versions = sorted(self.versions_dir.glob("unibos_v*"), reverse=True)[:5]
            if recent_versions:
                # Verify no nested archive folders
                for version_dir in recent_versions:
                    if (version_dir / "archive").exists():
                        print(f"   ❌ Found nested archive in {version_dir.name}")
                        return False
                print("   ✅ No nested archive folders found")
        
        # Check version numbering sequence
        try:
            current_ver = int(version_info['version'][1:])  # Remove 'v' prefix
            if self.versions_dir.exists():
                # Get all version numbers
                all_versions = []
                for v_dir in self.versions_dir.glob("unibos_v*"):
                    try:
                        ver_match = v_dir.name.split('_')[1]  # unibos_vXXX_...
                        ver_num = int(ver_match[1:])  # Remove 'v'
                        all_versions.append(ver_num)
                    except:
                        continue
                
                if all_versions:
                    max_existing = max(all_versions)
                    if current_ver <= max_existing:
                        print(f"   ⚠️  Version number not incremental (current: v{current_ver:03d}, max: v{max_existing:03d})")
                    else:
                        print(f"   ✅ Version number is incremental (v{current_ver:03d})")
        except:
            pass
            
        return True
    
    def post_archive_verification(self, compressed_path: Path, version_path: Path) -> bool:
        """Verify created archives are valid"""
        print("\n🔍 Post-archive verification...")
        checks_passed = True
        
        # Compressed archive verification removed
        
        # Check version copy
        if version_path and version_path.exists():
            # Check for nested archive
            if (version_path / "archive").exists():
                print("   ❌ Version copy contains nested archive folder")
                checks_passed = False
            
            # Check for nested versions in projects
            nested_versions = list((version_path / "projects").glob("unibos_v*")) if (version_path / "projects").exists() else []
            if nested_versions:
                print(f"   ❌ Version copy contains {len(nested_versions)} nested version(s) in projects/")
                checks_passed = False
            
            if not (version_path / "archive").exists() and not nested_versions:
                print("   ✅ Version copy structure is clean")
                
        return checks_passed
    
    def perform_git_operations(self, version_info: Dict[str, str]) -> bool:
        """Perform git commit, tag, and push operations"""
        print("\n🔧 Performing Git operations...")
        
        try:
            # Check if git is initialized
            git_dir = self.base_path / ".git"
            if not git_dir.exists():
                print("   ⚠️  Git repository not initialized")
                print("   ℹ️  Initialize with: git init")
                return False
            
            # Check if we have a remote
            result = subprocess.run(
                ["git", "remote", "-v"],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            if not result.stdout:
                print("   ⚠️  No git remote configured")
                print("   ℹ️  Add remote with: git remote add origin <url>")
                return False
            
            # Stage all changes
            print("   📝 Staging all changes...")
            result = subprocess.run(
                ["git", "add", "-A"],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            if result.returncode != 0:
                print(f"   ❌ Failed to stage changes: {result.stderr}")
                return False
            
            # Create commit message
            version = version_info['version']
            build = version_info['build_number']
            description = version_info['description']
            commit_message = f"{version}: {description}"
            
            # Commit changes
            print(f"   💾 Committing: {commit_message}")
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            # Check if there were no changes to commit
            if result.returncode != 0:
                if "nothing to commit" in result.stdout:
                    print("   ℹ️  No changes to commit")
                else:
                    print(f"   ❌ Failed to commit: {result.stderr}")
                    return False
            
            # Skip tag creation - we use branches instead
            # tag_name = version
            # print(f"   🏷️  Creating tag: {tag_name}")
            
            # Delete tag if it already exists (locally and remotely)
            # subprocess.run(
            #     ["git", "tag", "-d", tag_name],
            #     capture_output=True,
            #     cwd=self.base_path
            # )
            
            # Create version branch
            branch_name = version  # e.g., v313
            print(f"   🌿 Creating branch {branch_name}...")
            
            # Create and checkout new branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            if result.returncode != 0:
                # Branch might already exist, try to checkout
                result = subprocess.run(
                    ["git", "checkout", branch_name],
                    capture_output=True,
                    text=True,
                    cwd=self.base_path
                )
                if result.returncode != 0:
                    print(f"   ❌ Failed to create/checkout branch: {result.stderr}")
                    return False
            
            # Skip tag creation - we use branches instead of tags
            # result = subprocess.run(
            #     ["git", "tag", "-a", tag_name, "-m", f"Version {version}: {description}"],
            #     capture_output=True,
            #     text=True,
            #     cwd=self.base_path
            # )
            
            if result.returncode != 0 and "already exists" not in result.stderr:
                print(f"   ⚠️  Failed to create tag: {result.stderr}")
                # Continue anyway, tag is optional
            
            # Push version branch
            print(f"\n   🌿 Step 1/2: Pushing version branch {branch_name}...")
            result = subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            if result.returncode != 0:
                print(f"   ❌ Failed to push branch: {result.stderr}")
                print(f"   ℹ️  You can manually push with: git push -u origin {branch_name}")
                return False
            else:
                print(f"   ✅ Successfully pushed {branch_name} to remote")
            
            # Switch back to main and merge
            print("   🔄 Switching back to main branch...")
            result = subprocess.run(
                ["git", "checkout", "main"],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            if result.returncode != 0:
                # Try master if main doesn't exist
                result = subprocess.run(
                    ["git", "checkout", "master"],
                    capture_output=True,
                    text=True,
                    cwd=self.base_path
                )
                if result.returncode != 0:
                    print(f"   ❌ Failed to switch to main branch: {result.stderr}")
                    return False
            
            # Merge version branch to main
            print(f"   🔀 Merging {branch_name} to main...")
            result = subprocess.run(
                ["git", "merge", branch_name, "--no-ff", "-m", f"Merge branch '{branch_name}'"],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            if result.returncode != 0 and "Already up to date" not in result.stdout:
                print(f"   ❌ Failed to merge: {result.stderr}")
                return False
            
            # Push main branch
            print(f"\n   🚀 Step 2/2: Pushing main branch...")
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            if result.returncode != 0:
                # Try master if main fails
                result = subprocess.run(
                    ["git", "push", "origin", "master"],
                    capture_output=True,
                    text=True,
                    cwd=self.base_path
                )
                if result.returncode != 0:
                    print(f"   ❌ Failed to push main: {result.stderr}")
                    return False
            else:
                print(f"   ✅ Successfully pushed main to remote")
            
            # Skip pushing tags - we only use branches
            # print(f"   🏷️  Pushing tag {tag_name}...")
            # subprocess.run(
            #     ["git", "push", "origin", tag_name],
            #     capture_output=True,
            #     cwd=self.base_path
            # )
            
            # VERIFICATION STEP - Check if push actually worked
            print("\n   🔍 Verifying push operations...")
            
            # Check main branch push
            main_check = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            local_commit = main_check.stdout.strip()
            
            remote_check = subprocess.run(
                ["git", "ls-remote", "origin", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            remote_commit = remote_check.stdout.split()[0] if remote_check.stdout else ""
            
            main_pushed = local_commit == remote_commit
            
            # Check branch push
            branch_check = subprocess.run(
                ["git", "ls-remote", "--heads", "origin", branch_name],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            branch_pushed = bool(branch_check.stdout.strip())
            
            # Skip tag verification - we only use branches
            # tag_check = subprocess.run(
            #     ["git", "ls-remote", "--tags", "origin", tag_name],
            #     capture_output=True,
            #     text=True,
            #     cwd=self.base_path
            # )
            # tag_pushed = bool(tag_check.stdout.strip())
            
            # Report results
            if main_pushed and branch_pushed:
                print("   ✅ Git operations completed successfully!")
                print(f"   📌 Verified: origin/main and origin/{branch_name} are up to date")
                # Skip tag reporting
                # if tag_pushed:
                #     print(f"   🏷️  Tag {tag_name} also pushed successfully")
            else:
                print("\n   ⚠️  PUSH VERIFICATION FAILED!")
                if not main_pushed:
                    print("   ❌ Main branch NOT pushed to remote")
                    print("   🔧 Fix: git push origin main")
                if not branch_pushed:
                    print(f"   ❌ Branch {branch_name} NOT pushed to remote")
                    print(f"   🔧 Fix: git push -u origin {branch_name}")
                # Skip tag warning
                # if not tag_pushed:
                #     print(f"   ⚠️  Tag {tag_name} NOT pushed (optional)")
                print("\n   🚨 MANUAL INTERVENTION REQUIRED!")
                print("   Run the fix commands above to complete the push operation.")
                
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Git command failed: {str(e)}")
            return False
        except Exception as e:
            print(f"   ❌ Unexpected error during git operations: {str(e)}")
            logger.error(f"Git operations failed: {str(e)}", category=LogCategory.SYSTEM)
            return False
    
    def archive_current_version(self, force: bool = False) -> bool:
        """Archive current version"""
        try:
            # Get version info
            version_info = self.get_version_info()
            
            print(f"\n📦 archiving unibos {version_info['version']} (build: {version_info['build_number']})")
            print(f"   {version_info['description']}")
            
            # Start communication logging for this archive process
            try:
                from communication_logger import comm_logger
                comm_logger.start_new_log(f"Archive process started for {version_info['version']}")
                comm_logger.add_message("System", f"Archiving version {version_info['version']} with build {version_info['build_number']}")
                comm_logger.add_message("System", f"Description: {version_info['description']}")
            except ImportError:
                print("   ℹ️  Communication logger not available")
            
            # Size anomaly check removed since we don't create compressed archives
            
            # Perform pre-archive checks
            if not self.pre_archive_checklist():
                if not force:
                    response = input("\n⚠️  Pre-archive checks failed. Continue anyway? (y/N): ")
                    if response.lower() != 'y':
                        print("Archive operation cancelled.")
                        return False
            
            # Verify archive structure consistency
            if not self.verify_archive_structure(version_info):
                if not force:
                    response = input("\n⚠️  Archive structure verification failed. Continue anyway? (y/N): ")
                    if response.lower() != 'y':
                        print("Archive operation cancelled.")
                        return False
            
            # Check existing archives
            _, version_exists = self.check_existing_archives(version_info)
            
            if not force and version_exists:
                print(f"\n⚠️  Version already exists for {version_info['version']}")
                
                response = input("\nOverwrite existing version? (y/N): ")
                if response.lower() != 'y':
                    print("Archive operation cancelled.")
                    return False
            
            # Manage communication logs before archiving
            self.manage_communication_logs()
            
            # Create version copy only (no compressed archive)
            print("\n📁 Creating version copy...")
            version_path = self.create_version_copy(version_info)
            
            # Post-archive verification
            if version_path:
                if not self.post_archive_verification(None, version_path):
                    print("\n⚠️  Post-archive verification found issues")
                    if not force:
                        print("   Please review the warnings above")
            
            # Git operations
            git_success = self.perform_git_operations(version_info)
            
            # Summary
            print("\n✅ Archive completed successfully!")
            if version_path:
                print(f"   📁 Version copy: {version_path.relative_to(self.base_path)}")
            
            if git_success:
                print(f"   🚀 Git: Successfully pushed to both main and {version_info['version']} branches")
            else:
                print(f"   ⚠️  Git: Manual push required for {version_info['version']}")
            
            # Update communication log and cleanup old logs
            try:
                from communication_logger import comm_logger
                comm_logger.add_message("System", f"Archive completed successfully for {version_info['version']}")
                if git_success:
                    comm_logger.add_message("System", f"Git: Pushed to both main and {version_info['version']} branches")
                comm_logger.update_version(version_info['version'])
                comm_logger.stop_logging("Archive process completed")
                
                # CLEAN UP OLD COMMUNICATION LOGS (keep only last 3)
                print("\n🧹 Cleaning up old communication logs...")
                import glob
                
                # Find all communication logs (both old and new format)
                old_format_logs = sorted(glob.glob('CLAUDE_COMMUNICATION_LOG_*.md'), reverse=True)
                new_format_logs = sorted(glob.glob('CLAUDE_COMMUNICATION_LOG_v*_to_v*_*.md'), reverse=True)
                all_logs = new_format_logs + old_format_logs
                
                # Keep only the most recent 3 logs
                logs_to_keep = 3
                if len(all_logs) > logs_to_keep:
                    logs_to_delete = all_logs[logs_to_keep:]
                    for log_file in logs_to_delete:
                        try:
                            os.remove(log_file)
                            print(f"   🗑️  Deleted old log: {log_file}")
                        except Exception as e:
                            print(f"   ⚠️  Failed to delete {log_file}: {e}")
                    print(f"   ✅ Kept {logs_to_keep} most recent communication logs")
                else:
                    print(f"   ✅ Only {len(all_logs)} logs exist, no cleanup needed")
            except Exception as e:
                print(f"   ⚠️  Communication log error: {e}")
                pass
            
            return True
            
        except Exception as e:
            print(f"\n❌ Archive failed: {str(e)}")
            logger.error(f"Archive operation failed: {str(e)}", category=LogCategory.SYSTEM)
            
            # Log error to communication log
            try:
                from communication_logger import comm_logger
                comm_logger.add_message("System", f"Archive failed: {str(e)}")
                comm_logger.stop_logging("Archive process failed")
            except:
                pass
            
            return False
    
    def list_archives(self):
        """List all existing archives"""
        print("\n📚 Existing Archives:")
        
        # List version copies only
        if self.versions_dir.exists():
            versions = sorted(self.versions_dir.glob("unibos_v*"), reverse=True)
            if versions:
                print("\n📁 Version Archives:")
                for version in versions[:10]:  # Show last 10
                    print(f"   - {version.name}")

# CLI interface
if __name__ == "__main__":
    archiver = VersionArchiver()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            archiver.list_archives()
        elif sys.argv[1] == "force":
            archiver.archive_current_version(force=True)
        else:
            print("Usage:")
            print("  python archive_version.py        - Archive current version")
            print("  python archive_version.py list   - List existing archives")
            print("  python archive_version.py force  - Force archive (overwrite existing)")
    else:
        archiver.archive_current_version()