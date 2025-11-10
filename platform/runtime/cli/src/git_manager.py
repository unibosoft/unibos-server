#!/usr/bin/env python3
"""
Enhanced Git Manager for UNIBOS
Complete git operations with repository management
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional

# Colors
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"

class GitManager:
    """Enhanced git manager with full repository management"""
    
    def __init__(self):
        self.base_path = Path("/Users/berkhatirli/Desktop/unibos")
        os.chdir(self.base_path)
        self.check_screenshots_on_start()
        
    def check_screenshots_on_start(self):
        """Check for screenshots when starting"""
        try:
            from screenshot_manager import screenshot_manager
            count, archived = screenshot_manager.check_and_archive_all()
            if count > 0:
                print(f"\n{Colors.YELLOW}📸 Archived {count} screenshots{Colors.RESET}")
                for path in archived:
                    print(f"   ✓ {path.name}")
                print()
        except:
            pass
    
    def run_git_command(self, args: List[str], check: bool = True) -> Tuple[int, str, str]:
        """Run git command and return (returncode, stdout, stderr)"""
        try:
            result = subprocess.run(
                ['git'] + args,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
        except Exception as e:
            return -1, "", str(e)
    
    def get_repo_info(self) -> dict:
        """Get detailed repository information"""
        info = {
            'initialized': False,
            'branch': 'N/A',
            'remote_name': 'N/A',
            'remote_url': 'N/A',
            'changes': 0,
            'staged': 0,
            'untracked': 0,
            'ahead': 0,
            'behind': 0
        }
        
        # Check if git repo
        code, _, _ = self.run_git_command(['status'], check=False)
        if code != 0:
            return info
        
        info['initialized'] = True
        
        # Current branch
        code, stdout, _ = self.run_git_command(['branch', '--show-current'], check=False)
        if code == 0:
            info['branch'] = stdout.strip() or 'detached'
        
        # Remote info
        code, stdout, _ = self.run_git_command(['remote', '-v'], check=False)
        if code == 0 and stdout:
            lines = stdout.strip().split('\n')
            for line in lines:
                if 'fetch' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        info['remote_name'] = parts[0]
                        info['remote_url'] = parts[1]
                        break
        
        # Changes count
        code, stdout, _ = self.run_git_command(['status', '--porcelain'], check=False)
        if code == 0:
            lines = [l for l in stdout.split('\n') if l.strip()]
            info['changes'] = len(lines)
            info['staged'] = len([l for l in lines if l[0] in 'MADRC'])
            info['untracked'] = len([l for l in lines if l.startswith('??')])
        
        # Ahead/behind
        if info['remote_name'] != 'N/A' and info['branch'] != 'N/A':
            code, stdout, _ = self.run_git_command(
                ['rev-list', '--left-right', '--count', 
                 f"{info['remote_name']}/{info['branch']}...HEAD"], 
                check=False
            )
            if code == 0 and stdout:
                parts = stdout.strip().split()
                if len(parts) == 2:
                    info['behind'] = int(parts[0])
                    info['ahead'] = int(parts[1])
        
        return info
    
    def show_git_menu(self):
        """Show enhanced git menu"""
        while True:
            os.system('clear')
            print(f"{Colors.CYAN}{Colors.BOLD}📦 Git Manager{Colors.RESET}")
            print(f"{Colors.DIM}{'='*60}{Colors.RESET}\n")
            
            # Get and display repo info
            info = self.get_repo_info()
            
            if not info['initialized']:
                print(f"{Colors.RED}⚠️  Not a git repository{Colors.RESET}")
                print(f"\n{Colors.CYAN}Options:{Colors.RESET}")
                print(f"  1. Initialize new repository")
                print(f"  q. Back to main")
                
                choice = input(f"\n{Colors.BLUE}Choice: {Colors.RESET}")
                if choice == '1':
                    self.init_repo()
                elif choice == 'q':
                    break
                continue
            
            # Display repo status
            print(f"{Colors.YELLOW}📂 Repository Info:{Colors.RESET}")
            print(f"  Branch: {Colors.GREEN}{info['branch']}{Colors.RESET}")
            print(f"  Remote: {Colors.BLUE}{info['remote_name']}{Colors.RESET} → {info['remote_url']}")
            
            # Status summary
            status_parts = []
            if info['changes'] > 0:
                status_parts.append(f"{Colors.YELLOW}{info['changes']} changes{Colors.RESET}")
            if info['staged'] > 0:
                status_parts.append(f"{Colors.GREEN}{info['staged']} staged{Colors.RESET}")
            if info['untracked'] > 0:
                status_parts.append(f"{Colors.RED}{info['untracked']} untracked{Colors.RESET}")
            
            if status_parts:
                print(f"  Status: {' | '.join(status_parts)}")
            else:
                print(f"  Status: {Colors.GREEN}Clean{Colors.RESET}")
            
            # Sync status
            if info['ahead'] > 0 or info['behind'] > 0:
                sync_parts = []
                if info['ahead'] > 0:
                    sync_parts.append(f"{Colors.GREEN}↑{info['ahead']}{Colors.RESET}")
                if info['behind'] > 0:
                    sync_parts.append(f"{Colors.RED}↓{info['behind']}{Colors.RESET}")
                print(f"  Sync: {' '.join(sync_parts)}")
            
            # Menu options
            print(f"\n{Colors.CYAN}📋 Basic Operations:{Colors.RESET}")
            print(f"  1. Status (detailed)")
            print(f"  2. Stage & Commit")
            print(f"  3. Push")
            print(f"  4. Pull")
            print(f"  5. Create dev version")
            
            print(f"\n{Colors.CYAN}🌿 Branch Operations:{Colors.RESET}")
            print(f"  6. List branches")
            print(f"  7. Create branch")
            print(f"  8. Switch branch")
            print(f"  9. Merge branch")
            
            print(f"\n{Colors.CYAN}🌐 Remote Operations:{Colors.RESET}")
            print(f"  10. Manage remotes")
            print(f"  11. Clone repository")
            
            print(f"\n{Colors.CYAN}📜 History:{Colors.RESET}")
            print(f"  12. View log")
            print(f"  13. Show diff")
            
            print(f"\n  {Colors.DIM}q. Back to main{Colors.RESET}")
            
            choice = input(f"\n{Colors.BLUE}Choice: {Colors.RESET}")
            
            if choice == 'q':
                break
            elif choice == '1':
                self.show_status()
            elif choice == '2':
                self.stage_and_commit()
            elif choice == '3':
                self.push()
            elif choice == '4':
                self.pull()
            elif choice == '5':
                self.create_dev_version()
            elif choice == '6':
                self.list_branches()
            elif choice == '7':
                self.create_branch()
            elif choice == '8':
                self.switch_branch()
            elif choice == '9':
                self.merge_branch()
            elif choice == '10':
                self.manage_remotes()
            elif choice == '11':
                self.clone_repo()
            elif choice == '12':
                self.show_log()
            elif choice == '13':
                self.show_diff()
            else:
                print(f"{Colors.RED}Invalid choice{Colors.RESET}")
                input("\nPress Enter...")
    
    def init_repo(self):
        """Initialize new repository"""
        print(f"\n{Colors.CYAN}Initializing Git Repository...{Colors.RESET}")
        
        code, stdout, stderr = self.run_git_command(['init'])
        if code == 0:
            print(f"{Colors.GREEN}✓ Repository initialized{Colors.RESET}")
            
            # Ask for remote
            print(f"\n{Colors.CYAN}Add remote repository? (y/n):{Colors.RESET} ", end='')
            if input().lower() == 'y':
                url = input("Remote URL (e.g., https://github.com/user/repo.git): ")
                if url:
                    code, _, _ = self.run_git_command(['remote', 'add', 'origin', url])
                    if code == 0:
                        print(f"{Colors.GREEN}✓ Remote added{Colors.RESET}")
        else:
            print(f"{Colors.RED}Failed: {stderr}{Colors.RESET}")
        
        input("\nPress Enter...")
    
    def show_status(self):
        """Show detailed status"""
        print(f"\n{Colors.CYAN}Git Status:{Colors.RESET}\n")
        code, stdout, _ = self.run_git_command(['status', '-v'])
        print(stdout)
        input("\nPress Enter...")
    
    def stage_and_commit(self):
        """Stage changes and commit"""
        # Show changes
        code, stdout, _ = self.run_git_command(['status', '--short'])
        if not stdout.strip():
            print(f"{Colors.YELLOW}No changes to commit{Colors.RESET}")
            input("\nPress Enter...")
            return
        
        print(f"\n{Colors.CYAN}Changes:{Colors.RESET}")
        print(stdout)
        
        print(f"\n{Colors.CYAN}Options:{Colors.RESET}")
        print("  1. Stage all and commit")
        print("  2. Stage specific files")
        print("  3. View diff first")
        print("  c. Cancel")
        
        choice = input(f"\n{Colors.BLUE}Choice: {Colors.RESET}")
        
        if choice == '1':
            # Stage all
            self.run_git_command(['add', '-A'])
            print(f"{Colors.GREEN}✓ All changes staged{Colors.RESET}")
            
            # Get commit message
            msg = input("\nCommit message: ").strip()
            if not msg:
                # VERSION.json'dan bilgi al
                try:
                    version_file = Path(__file__).parent / "VERSION.json"
                    if version_file.exists():
                        import json
                        with open(version_file, 'r', encoding='utf-8') as f:
                            version_data = json.load(f)
                        version = version_data.get('version', 'Unknown')
                        description = version_data.get('description', '')
                        if description:
                            msg = f"{version}: {description}"
                        else:
                            msg = f"{version} - Update"
                        print(f"{Colors.GRAY}Using auto-generated message: {msg}{Colors.RESET}")
                    else:
                        msg = f"Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                except:
                    msg = f"Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            code, _, _ = self.run_git_command(['commit', '-m', msg])
            if code == 0:
                print(f"{Colors.GREEN}✓ Committed{Colors.RESET}")
        
        elif choice == '2':
            # Interactive staging
            print("\nEnter file paths to stage (empty line to finish):")
            files = []
            while True:
                file = input("> ").strip()
                if not file:
                    break
                files.append(file)
            
            if files:
                code, _, _ = self.run_git_command(['add'] + files)
                if code == 0:
                    print(f"{Colors.GREEN}✓ Files staged{Colors.RESET}")
                    
                    msg = input("\nCommit message: ").strip()
                    if not msg:
                        # VERSION.json'dan bilgi al
                        try:
                            version_file = Path(__file__).parent / "VERSION.json"
                            if version_file.exists():
                                with open(version_file, 'r', encoding='utf-8') as f:
                                    version_data = json.load(f)
                                version = version_data.get('version', 'Unknown')
                                description = version_data.get('description', '')
                                if description:
                                    msg = f"{version}: {description}"
                                else:
                                    msg = f"{version} - Update"
                            else:
                                msg = f"Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        except:
                            msg = f"Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    
                    self.run_git_command(['commit', '-m', msg])
                    print(f"{Colors.GREEN}✓ Committed{Colors.RESET}")
        
        elif choice == '3':
            code, stdout, _ = self.run_git_command(['diff'])
            print(stdout)
            input("\nPress Enter to continue...")
            self.stage_and_commit()
            return
        
        input("\nPress Enter...")
    
    def push(self):
        """Push to remote with version branch strategy"""
        info = self.get_repo_info()
        
        if info['remote_name'] == 'N/A':
            print(f"{Colors.RED}No remote configured{Colors.RESET}")
            input("\nPress Enter...")
            return
        
        # Get current version
        try:
            version_file = self.base_path / 'src' / 'VERSION.json'
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                    current_version = version_data['version']
            else:
                print(f"{Colors.RED}VERSION.json not found{Colors.RESET}")
                input("\nPress Enter...")
                return
        except Exception as e:
            print(f"{Colors.RED}Error reading version: {e}{Colors.RESET}")
            input("\nPress Enter...")
            return
        
        current_branch = info['branch']
        
        print(f"\n{Colors.CYAN}🚀 Enhanced Push Strategy{Colors.RESET}")
        print(f"{Colors.YELLOW}Current version: {current_version}{Colors.RESET}")
        print(f"{Colors.YELLOW}Current branch: {current_branch}{Colors.RESET}")
        
        # Step 1: Push to current branch first
        print(f"\n{Colors.CYAN}Step 1: Pushing to {current_branch}...{Colors.RESET}")
        
        # Check if we have an upstream branch
        code, stdout, _ = self.run_git_command(['rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'], check=False)
        has_upstream = code == 0
        
        if not has_upstream:
            print(f"{Colors.YELLOW}Setting up upstream for {current_branch}...{Colors.RESET}")
            code, stdout, stderr = self.run_git_command(['push', '-u', info['remote_name'], current_branch], check=False)
        else:
            code, stdout, stderr = self.run_git_command(['push'], check=False)
        
        if code != 0:
            print(f"{Colors.RED}Push to {current_branch} failed: {stderr}{Colors.RESET}")
            input("\nPress Enter...")
            return
        
        print(f"{Colors.GREEN}✓ Pushed to {current_branch} successfully{Colors.RESET}")
        
        # Step 2: If we're not on main, merge to main and push
        if current_branch != 'main':
            print(f"\n{Colors.CYAN}Step 2: Merging to main...{Colors.RESET}")
            
            # Stash any uncommitted changes
            self.run_git_command(['stash'])
            
            # Switch to main
            code, _, stderr = self.run_git_command(['checkout', 'main'], check=False)
            if code != 0:
                print(f"{Colors.RED}Failed to switch to main: {stderr}{Colors.RESET}")
                self.run_git_command(['stash', 'pop'])
                input("\nPress Enter...")
                return
            
            # Pull latest main
            self.run_git_command(['pull', 'origin', 'main'])
            
            # Merge current branch
            code, _, stderr = self.run_git_command(['merge', current_branch, '--no-ff', '-m', f'Merge {current_branch} into main'], check=False)
            if code != 0:
                print(f"{Colors.RED}Merge failed: {stderr}{Colors.RESET}")
                self.run_git_command(['checkout', current_branch])
                self.run_git_command(['stash', 'pop'])
                input("\nPress Enter...")
                return
            
            # Push main
            code, _, stderr = self.run_git_command(['push', 'origin', 'main'], check=False)
            if code != 0:
                print(f"{Colors.RED}Push to main failed: {stderr}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}✓ Pushed to main successfully{Colors.RESET}")
            
            # Switch back to original branch
            self.run_git_command(['checkout', current_branch])
            self.run_git_command(['stash', 'pop'])
        
        # Step 3: Create/update version branch
        version_branch = current_version
        print(f"\n{Colors.CYAN}Step 3: Creating/updating version branch {version_branch}...{Colors.RESET}")
        
        # Check if version branch exists locally
        code, _, _ = self.run_git_command(['show-ref', '--verify', '--quiet', f'refs/heads/{version_branch}'], check=False)
        branch_exists = code == 0
        
        if branch_exists:
            # Switch to existing branch
            self.run_git_command(['checkout', version_branch])
            # Reset to current branch state
            self.run_git_command(['reset', '--hard', current_branch])
        else:
            # Create new branch
            code, _, stderr = self.run_git_command(['checkout', '-b', version_branch], check=False)
            if code != 0:
                print(f"{Colors.RED}Failed to create version branch: {stderr}{Colors.RESET}")
                input("\nPress Enter...")
                return
        
        # Push version branch
        code, _, stderr = self.run_git_command(['push', '-f', 'origin', version_branch], check=False)
        if code != 0:
            print(f"{Colors.RED}Push to version branch failed: {stderr}{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}✓ Pushed to {version_branch} successfully{Colors.RESET}")
        
        # Stay on version branch (as requested)
        print(f"\n{Colors.GREEN}✅ Push completed!{Colors.RESET}")
        print(f"{Colors.YELLOW}📍 Now on branch: {version_branch}{Colors.RESET}")
        print(f"\n{Colors.CYAN}Summary:{Colors.RESET}")
        print(f"  • {current_branch} → ✓ pushed")
        if current_branch != 'main':
            print(f"  • main → ✓ updated")
        print(f"  • {version_branch} → ✓ created/updated")
        
        input("\nPress Enter...")
    
    def pull(self):
        """Pull from remote"""
        print(f"\n{Colors.CYAN}Pulling from remote...{Colors.RESET}")
        
        code, stdout, stderr = self.run_git_command(['pull'], check=False)
        
        if code == 0:
            print(f"{Colors.GREEN}✓ Pulled successfully{Colors.RESET}")
            if stdout:
                print(stdout)
        else:
            print(f"{Colors.RED}Pull failed: {stderr}{Colors.RESET}")
        
        input("\nPress Enter...")
    
    def create_dev_version(self):
        """Create development version"""
        print(f"\n{Colors.CYAN}Creating development version...{Colors.RESET}")
        
        try:
            from development_version_manager import dev_version_manager
            
            purpose = input("Purpose (optional): ").strip()
            dev_path = dev_version_manager.create_development_version(
                purpose or "General development"
            )
            
            if dev_path:
                print(f"\n{Colors.GREEN}✓ Created: {dev_path.name}{Colors.RESET}")
                print(f"{Colors.YELLOW}Test with: ./launch_dev.sh{Colors.RESET}")
                
                # Ask to switch
                if input("\nSwitch to dev version? (y/n): ").lower() == 'y':
                    dev_version_manager.switch_to_dev_version(dev_path.name)
            else:
                print(f"{Colors.RED}Failed to create dev version{Colors.RESET}")
                
        except ImportError:
            print(f"{Colors.RED}Development version manager not available{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        
        input("\nPress Enter...")
    
    def list_branches(self):
        """List all branches"""
        print(f"\n{Colors.CYAN}Branches:{Colors.RESET}\n")
        
        code, stdout, _ = self.run_git_command(['branch', '-av'])
        print(stdout)
        
        input("\nPress Enter...")
    
    def create_branch(self):
        """Create new branch"""
        name = input("\nBranch name: ").strip()
        if not name:
            return
        
        code, _, stderr = self.run_git_command(['checkout', '-b', name], check=False)
        
        if code == 0:
            print(f"{Colors.GREEN}✓ Created and switched to branch: {name}{Colors.RESET}")
        else:
            print(f"{Colors.RED}Failed: {stderr}{Colors.RESET}")
        
        input("\nPress Enter...")
    
    def switch_branch(self):
        """Switch branch"""
        # List branches
        code, stdout, _ = self.run_git_command(['branch', '-a'])
        print(f"\n{Colors.CYAN}Available branches:{Colors.RESET}")
        print(stdout)
        
        name = input("\nBranch name: ").strip()
        if not name:
            return
        
        code, _, stderr = self.run_git_command(['checkout', name], check=False)
        
        if code == 0:
            print(f"{Colors.GREEN}✓ Switched to: {name}{Colors.RESET}")
        else:
            print(f"{Colors.RED}Failed: {stderr}{Colors.RESET}")
        
        input("\nPress Enter...")
    
    def merge_branch(self):
        """Merge branch"""
        info = self.get_repo_info()
        
        # List branches
        code, stdout, _ = self.run_git_command(['branch', '-a'])
        print(f"\n{Colors.CYAN}Available branches:{Colors.RESET}")
        print(stdout)
        print(f"\n{Colors.YELLOW}Current branch: {info['branch']}{Colors.RESET}")
        
        name = input("\nBranch to merge: ").strip()
        if not name:
            return
        
        code, stdout, stderr = self.run_git_command(['merge', name], check=False)
        
        if code == 0:
            print(f"{Colors.GREEN}✓ Merged successfully{Colors.RESET}")
            if stdout:
                print(stdout)
        else:
            print(f"{Colors.RED}Merge failed: {stderr}{Colors.RESET}")
        
        input("\nPress Enter...")
    
    def manage_remotes(self):
        """Manage remote repositories"""
        while True:
            os.system('clear')
            print(f"{Colors.CYAN}{Colors.BOLD}🌐 Remote Repository Management{Colors.RESET}")
            print(f"{Colors.DIM}{'='*60}{Colors.RESET}\n")
            
            # List remotes
            code, stdout, _ = self.run_git_command(['remote', '-v'])
            if stdout:
                print(f"{Colors.YELLOW}Current remotes:{Colors.RESET}")
                print(stdout)
            else:
                print(f"{Colors.YELLOW}No remotes configured{Colors.RESET}")
            
            print(f"\n{Colors.CYAN}Options:{Colors.RESET}")
            print("  1. Add remote")
            print("  2. Remove remote")
            print("  3. Change remote URL")
            print("  4. Rename remote")
            print("  b. Back")
            
            choice = input(f"\n{Colors.BLUE}Choice: {Colors.RESET}")
            
            if choice == 'b':
                break
            elif choice == '1':
                name = input("\nRemote name (e.g., origin): ").strip()
                url = input("Remote URL: ").strip()
                if name and url:
                    code, _, stderr = self.run_git_command(['remote', 'add', name, url], check=False)
                    if code == 0:
                        print(f"{Colors.GREEN}✓ Remote added{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}Failed: {stderr}{Colors.RESET}")
                    input("\nPress Enter...")
            
            elif choice == '2':
                name = input("\nRemote name to remove: ").strip()
                if name:
                    code, _, _ = self.run_git_command(['remote', 'remove', name])
                    if code == 0:
                        print(f"{Colors.GREEN}✓ Remote removed{Colors.RESET}")
                    input("\nPress Enter...")
            
            elif choice == '3':
                name = input("\nRemote name: ").strip()
                url = input("New URL: ").strip()
                if name and url:
                    code, _, _ = self.run_git_command(['remote', 'set-url', name, url])
                    if code == 0:
                        print(f"{Colors.GREEN}✓ URL updated{Colors.RESET}")
                    input("\nPress Enter...")
            
            elif choice == '4':
                old_name = input("\nCurrent name: ").strip()
                new_name = input("New name: ").strip()
                if old_name and new_name:
                    code, _, _ = self.run_git_command(['remote', 'rename', old_name, new_name])
                    if code == 0:
                        print(f"{Colors.GREEN}✓ Remote renamed{Colors.RESET}")
                    input("\nPress Enter...")
    
    def clone_repo(self):
        """Clone a repository"""
        print(f"\n{Colors.CYAN}Clone Repository{Colors.RESET}")
        print(f"{Colors.YELLOW}Warning: This will clone into a subdirectory{Colors.RESET}")
        
        url = input("\nRepository URL: ").strip()
        if not url:
            return
        
        # Optional: custom directory name
        dir_name = input("Directory name (optional): ").strip()
        
        args = ['clone', url]
        if dir_name:
            args.append(dir_name)
        
        print(f"\n{Colors.CYAN}Cloning...{Colors.RESET}")
        code, stdout, stderr = self.run_git_command(args, check=False)
        
        if code == 0:
            print(f"{Colors.GREEN}✓ Repository cloned{Colors.RESET}")
        else:
            print(f"{Colors.RED}Clone failed: {stderr}{Colors.RESET}")
        
        input("\nPress Enter...")
    
    def show_log(self):
        """Show commit log"""
        print(f"\n{Colors.CYAN}Commit History:{Colors.RESET}\n")
        
        # Show last 20 commits with graph
        code, stdout, _ = self.run_git_command(['log', '--oneline', '--graph', '-20'])
        print(stdout)
        
        input("\nPress Enter...")
    
    def show_diff(self):
        """Show differences"""
        print(f"\n{Colors.CYAN}Diff Options:{Colors.RESET}")
        print("  1. Working directory changes")
        print("  2. Staged changes")
        print("  3. Last commit")
        print("  c. Cancel")
        
        choice = input(f"\n{Colors.BLUE}Choice: {Colors.RESET}")
        
        if choice == '1':
            code, stdout, _ = self.run_git_command(['diff'])
        elif choice == '2':
            code, stdout, _ = self.run_git_command(['diff', '--cached'])
        elif choice == '3':
            code, stdout, _ = self.run_git_command(['diff', 'HEAD~1'])
        else:
            return
        
        if stdout:
            print(f"\n{stdout}")
        else:
            print(f"{Colors.YELLOW}No differences{Colors.RESET}")
        
        input("\nPress Enter...")

if __name__ == "__main__":
    manager = GitManager()
    manager.show_git_menu()