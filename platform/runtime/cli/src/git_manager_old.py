#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🪐 unibos - enhanced git manager with development branch support
complete git operations with development version integration
clean interface with proper content area management

author: berk hatırlı - bitez, bodrum, muğla, türkiye
version: v241
purpose: full git functionality with development branch and version management
"""

import os
import sys
import subprocess
import json
import platform
import re
from pathlib import Path
from datetime import datetime

# Optional imports for timezone support
try:
    import pytz
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False

# platform-specific imports for single key input
if platform.system() != 'Windows':
    try:
        import termios
        import tty
        TERMIOS_AVAILABLE = True
    except ImportError:
        TERMIOS_AVAILABLE = False
else:
    TERMIOS_AVAILABLE = False
    try:
        import msvcrt
    except ImportError:
        pass

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    ORANGE = "\033[38;5;208m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_GRAY = "\033[100m"
    BG_ORANGE = "\033[48;5;208m"

def get_single_key():
    """get single key input without pressing enter - handles arrow keys"""
    if platform.system() == 'Windows':
        if 'msvcrt' in sys.modules:
            key = msvcrt.getch()
            if key in [b'\x00', b'\xe0']:  # Special key prefix on Windows
                key = msvcrt.getch()  # Get the second byte
                if key == b'H': return 'UP'
                elif key == b'P': return 'DOWN'
                elif key == b'K': return 'LEFT'
                elif key == b'M': return 'RIGHT'
            return key.decode('utf-8', errors='ignore')
        else:
            return input().strip()[:1]
    else:
        if TERMIOS_AVAILABLE:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                if key == '\x1b':  # ESC sequence
                    key += sys.stdin.read(2)
                    if key == '\x1b[A': return 'UP'
                    elif key == '\x1b[B': return 'DOWN'
                    elif key == '\x1b[C': return 'RIGHT'
                    elif key == '\x1b[D': return 'LEFT'
                    return key[2] if len(key) > 2 else ''
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return key
        else:
            return input().strip()[:1]

class GitManager:
    """enhanced git operations manager with lowercase ui"""
    
    def __init__(self):
        # Always work in the main directory (parent of src/)
        src_dir = Path(__file__).parent
        self.main_dir = src_dir.parent  # This is the main unibosoft directory
        self.current_dir = self.main_dir
        
        # Change to main directory for all git operations
        self.original_dir = Path.cwd()
        os.chdir(self.main_dir)
        
        self.git_dir = self.current_dir / ".git"
        self.is_git_repo = self.git_dir.exists()
        self.git_available = self.check_git_installation()
        self.git_version = self.get_git_version()
        
        # Hardcoded repository URL
        self.repo_url = "https://github.com/unibosoft/unibos.git"
    
    def __del__(self):
        """restore original directory when done"""
        try:
            os.chdir(self.original_dir)
        except:
            pass
        
    def check_git_installation(self):
        """check if git is installed and available"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_git_version(self):
        """get git version information"""
        if not self.git_available:
            return "not installed"
        
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip().lower()
        except:
            return "unknown version"
    
    def refresh_repo_status(self):
        """refresh repository status"""
        self.git_dir = self.current_dir / ".git"
        self.is_git_repo = self.git_dir.exists()
    
    def show_main_menu(self, draw_ui_callback=None):
        """display main git management menu with arrow key navigation"""
        menu_items = [
            ("1", "repository status", self.show_status),
            ("2", "initialize repository", self.init_repository),
            ("3", "add files", self.add_files),
            ("4", "commit changes", self.commit_changes),
            ("5", "push to remote", self.push_to_remote),
            ("6", "pull from remote", self.pull_from_remote),
            ("7", "branch management", self.branch_management),
            ("8", "remote management", self.remote_management),
            ("9", "view commit history", self.view_history),
            ("0", "exit", None)
        ]
        
        current_index = 0
        
        while True:
            # Use callback to draw UI if provided, otherwise clear screen
            if draw_ui_callback:
                draw_ui_callback()
            else:
                os.system('clear' if platform.system() != 'Windows' else 'cls')
            
            # Calculate content area position
            content_x = 27 if draw_ui_callback else 0  # Correct position after sidebar
            content_y = 5 if draw_ui_callback else 2    # Leave space for header if UI is drawn
            
            # Helper function to print at position
            def print_at(x, y, text):
                if draw_ui_callback:
                    # Clear the line first to avoid overlap
                    sys.stdout.write(f"\033[{y};{x}H\033[K{text}")
                    sys.stdout.flush()
                else:
                    print(text)
            
            # Draw header in sidebar style
            if draw_ui_callback:
                sys.stdout.write(f"\033[{content_y};{content_x}H{Colors.BG_GRAY}{Colors.BOLD}{Colors.WHITE}📦 git manager{Colors.RESET}")
                sys.stdout.flush()
            else:
                print("📦 git manager")
                print("=" * 50)
            
            if not self.git_available:
                print_at(content_x, content_y + 3, "❌ git not installed")
                print_at(content_x, content_y + 4, "💡 please install git manually")
                print_at(content_x, content_y + 6, "📝 installation instructions:")
                print_at(content_x, content_y + 7, "- linux: sudo apt install git")
                print_at(content_x, content_y + 8, "- macos: brew install git")
                print_at(content_x, content_y + 9, "- windows: https://git-scm.com/download/windows")
                print_at(content_x, content_y + 11, "press enter to continue...")
                input()
                return
            
            print_at(content_x, content_y + 3, "✅ git available - full functionality")
            
            # refresh status
            self.refresh_repo_status()
            
            y_offset = content_y + 5
            if self.is_git_repo:
                print_at(content_x, y_offset, f"📁 repository: {self.current_dir.name}")
                y_offset += 1
                # Show brief status inline
                try:
                    result = subprocess.run(['git', 'branch', '--show-current'], 
                                          capture_output=True, text=True, check=True)
                    branch = result.stdout.strip()
                    if branch:
                        print_at(content_x, y_offset, f"🌿 branch: {branch}")
                        y_offset += 1
                except:
                    pass
            else:
                print_at(content_x, y_offset, "❌ not a git repository")
                y_offset += 1
            
            y_offset += 1
            
            # Display menu items in sidebar style
            for i, (key, label, _) in enumerate(menu_items):
                if draw_ui_callback:
                    if i == current_index:
                        # Selected item - blue background
                        sys.stdout.write(f"\033[{y_offset + i};{content_x}H{Colors.BG_BLUE}{Colors.WHITE} {label:<45} {Colors.RESET}")
                    else:
                        # Normal item - gray background  
                        sys.stdout.write(f"\033[{y_offset + i};{content_x}H{Colors.BG_GRAY}{Colors.WHITE} {label:<45} {Colors.RESET}")
                    sys.stdout.flush()
                else:
                    # Fallback for non-UI mode
                    if i == current_index:
                        print(f"→ {key}. {label}")
                    else:
                        print(f"  {key}. {label}")
            
            # Instructions at bottom
            instruction_y = y_offset + len(menu_items) + 1
            if draw_ui_callback:
                sys.stdout.write(f"\033[{instruction_y};{content_x}H{Colors.DIM}↑↓ navigate | enter select | esc back{Colors.RESET}")
                sys.stdout.flush()
            else:
                print("\n💡 use ↑/↓ arrows or numbers, enter to select, 0/esc to exit")
            
            # Get key input
            key = get_single_key()
            
            if key == 'UP' and current_index > 0:
                current_index -= 1
            elif key == 'DOWN' and current_index < len(menu_items) - 1:
                current_index += 1
            elif key == '\r' or key == '\n':  # Enter key
                _, _, action = menu_items[current_index]
                if action is None:  # Exit option
                    return
                else:
                    # Execute action with UI callback
                    self._execute_action_with_ui(action, draw_ui_callback)
            elif key in '0123456789':
                # Direct number selection
                for i, (menu_key, _, action) in enumerate(menu_items):
                    if key == menu_key:
                        current_index = i
                        if action is None:  # Exit option
                            return
                        else:
                            self._execute_action_with_ui(action, draw_ui_callback)
                        break
            elif key == '\x1b' or key == 'ESC':  # ESC key
                return
    
    def _execute_action_with_ui(self, action, draw_ui_callback):
        """Execute an action while maintaining UI if callback provided"""
        if draw_ui_callback:
            # Create a wrapper to redirect output to content area
            import io
            from contextlib import redirect_stdout
            
            # Capture the action output
            captured_output = io.StringIO()
            
            try:
                with redirect_stdout(captured_output):
                    action()
            except Exception as e:
                captured_output.write(f"\n❌ error: {e}\n")
            
            # Now display the captured output in content area
            draw_ui_callback()
            
            # Calculate content area
            content_x = 27
            content_y = 5
            
            # Clear content area first
            cols, _ = os.get_terminal_size()
            for y in range(content_y, content_y + 30):
                sys.stdout.write(f"\033[{y};{content_x}H" + " " * (cols - content_x - 5))
            
            # Display captured output line by line
            output_lines = captured_output.getvalue().split('\n')
            for i, line in enumerate(output_lines[:25]):  # Limit to 25 lines
                if line:  # Skip empty lines
                    sys.stdout.write(f"\033[{content_y + i};{content_x}H{line}")
            
            # Position cursor for input prompt
            sys.stdout.write(f"\033[{content_y + min(len(output_lines), 25) + 1};{content_x}Hpress enter to continue...")
            sys.stdout.flush()
            input()
        else:
            os.system('clear' if platform.system() != 'Windows' else 'cls')
            action()
            input("\npress enter to continue...")
    
    def show_repo_status(self):
        """show brief repository status"""
        try:
            # get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
            if current_branch:
                print(f"🌿 current branch: {current_branch}")
            else:
                print("🌿 branch: detached head")
            
            # get status summary
            result = subprocess.run(['git', 'status', '--short'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                print(f"📊 changes: {len(lines)} files")
            else:
                print("✨ working tree clean")
                
        except subprocess.CalledProcessError:
            print("⚠️ unable to get status")
    
    def show_status(self):
        """show detailed repository status"""
        print("\n📊 repository status")
        print("=" * 50)
        
        if not self.is_git_repo:
            print("❌ not a git repository")
            return
        
        try:
            # Show current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
            if current_branch:
                print(f"🌿 current branch: {current_branch}")
            
            # Show status with porcelain format for better parsing
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                staged = []
                modified = []
                untracked = []
                
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('A ') or line.startswith('M '):
                        staged.append(line[3:])
                    elif line.startswith(' M'):
                        modified.append(line[3:])
                    elif line.startswith('??'):
                        untracked.append(line[3:])
                
                if staged:
                    print(f"\n✅ staged changes ({len(staged)} files):")
                    for f in staged[:5]:
                        print(f"   + {f}")
                    if len(staged) > 5:
                        print(f"   ... and {len(staged) - 5} more")
                
                if modified:
                    print(f"\n📝 modified files ({len(modified)} files):")
                    for f in modified[:5]:
                        print(f"   ~ {f}")
                    if len(modified) > 5:
                        print(f"   ... and {len(modified) - 5} more")
                
                if untracked:
                    print(f"\n❓ untracked files ({len(untracked)} files):")
                    for f in untracked[:5]:
                        print(f"   ? {f}")
                    if len(untracked) > 5:
                        print(f"   ... and {len(untracked) - 5} more")
            else:
                print("\n✨ working tree clean")
            
            # Show last commit
            print("\n📝 last commit:")
            result = subprocess.run(['git', 'log', '-1', '--oneline'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print(f"   {result.stdout.strip()}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ error getting status: {e}")
    
    def init_repository(self):
        """initialize git repository"""
        print("\n🚀 initialize repository")
        print("=" * 50)
        
        if self.is_git_repo:
            print("⚠️ already a git repository")
            return
        
        try:
            subprocess.run(['git', 'init'], check=True)
            print("✅ repository initialized successfully")
            self.refresh_repo_status()
            
            # add .gitignore
            print("\n📝 create .gitignore? (y/n): ", end='', flush=True)
            choice = get_single_key()
            print(choice)
            
            if choice.lower() == 'y':
                self.create_gitignore()
                
        except subprocess.CalledProcessError as e:
            print(f"❌ error initializing repository: {e}")
    
    def create_gitignore(self):
        """create basic .gitignore file"""
        gitignore_content = """# python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# macos
.DS_Store

# ide
.vscode/
.idea/
*.swp
*.swo

# logs
*.log

# database
*.db
*.sqlite3

# secrets
.env
config/secrets.json
"""
        
        try:
            with open('.gitignore', 'w') as f:
                f.write(gitignore_content)
            print("✅ .gitignore created")
            subprocess.run(['git', 'add', '.gitignore'], check=True)
            print("✅ .gitignore added to staging")
        except Exception as e:
            print(f"❌ error creating .gitignore: {e}")
    
    def add_files(self):
        """add files to staging area"""
        print("\n➕ add files")
        print("=" * 50)
        
        if not self.is_git_repo:
            print("❌ not a git repository")
            return
        
        print("1. add all files")
        print("2. add specific file")
        print("3. add by pattern")
        print("4. interactive add")
        print("c. cancel")
        
        print("\n👉 select option: ", end='', flush=True)
        choice = get_single_key()
        print(choice)
        
        try:
            if choice == '1':
                subprocess.run(['git', 'add', '.'], check=True)
                print("✅ all files added")
            elif choice == '2':
                filename = input("📝 enter filename: ").strip()
                if filename:
                    subprocess.run(['git', 'add', filename], check=True)
                    print(f"✅ {filename} added")
                else:
                    print("❌ no filename provided")
            elif choice == '3':
                pattern = input("📝 enter pattern (e.g., *.py): ").strip()
                if pattern:
                    subprocess.run(['git', 'add', pattern], check=True)
                    print(f"✅ files matching {pattern} added")
                else:
                    print("❌ no pattern provided")
            elif choice == '4':
                subprocess.run(['git', 'add', '-i'], check=False)
            elif choice == 'c':
                print("❌ add cancelled")
            else:
                print("❌ invalid choice")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ error adding files: {e}")
    
    def commit_changes(self):
        """commit staged changes"""
        print("\n💾 commit changes")
        print("=" * 50)
        
        if not self.is_git_repo:
            print("❌ not a git repository")
            return
        
        # check if there are staged changes
        try:
            result = subprocess.run(['git', 'diff', '--cached', '--quiet'], 
                                  capture_output=True)
            if result.returncode == 0:
                print("⚠️ no staged changes to commit")
                print("\n💡 hint: use 'add files' first")
                return
        except:
            pass
        
        print("commit message options:")
        print("1. auto-generated message")
        print("2. custom message")
        print("c. cancel")
        
        print("\n👉 select option: ", end='', flush=True)
        choice = get_single_key()
        print(choice)
        
        try:
            if choice == '1':
                # auto-generate message with Istanbul timezone
                if PYTZ_AVAILABLE:
                    try:
                        # Get Istanbul timezone
                        istanbul_tz = pytz.timezone('Europe/Istanbul')
                        timestamp = datetime.now(istanbul_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
                    except:
                        # Fallback to local time
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S +03:00")
                else:
                    # Fallback to local time if pytz not available
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S +03:00")
                
                # Get list of changed files for better commit message
                try:
                    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                          capture_output=True, text=True, check=True)
                    changed_files = result.stdout.strip().split('\n')
                    if changed_files and changed_files[0]:
                        num_files = len(changed_files)
                        if num_files == 1:
                            message = f"update: modified {changed_files[0]} at {timestamp}"
                        else:
                            message = f"update: modified {num_files} files at {timestamp}"
                    else:
                        message = f"update: automated commit at {timestamp}"
                except:
                    message = f"update: automated commit at {timestamp}"
                
                subprocess.run(['git', 'commit', '-m', message], check=True)
                print(f"✅ committed with message: {message}")
            elif choice == '2':
                message = input("📝 enter commit message: ").strip()
                if message:
                    subprocess.run(['git', 'commit', '-m', message], check=True)
                    print("✅ changes committed successfully")
                else:
                    print("❌ empty commit message")
            elif choice == 'c':
                print("❌ commit cancelled")
            else:
                print("❌ invalid choice")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ error committing changes: {e}")
    
    def push_to_remote(self):
        """push changes to remote repository"""
        print("\n🚀 push to remote")
        print("=" * 50)
        
        if not self.is_git_repo:
            print("❌ not a git repository")
            return
        
        try:
            # check if remote exists
            result = subprocess.run(['git', 'remote'], 
                                  capture_output=True, text=True, check=True)
            if not result.stdout.strip():
                print("❌ no remote repository configured")
                print("💡 use 'remote management' to add a remote")
                return
            
            # get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
            
            print(f"🌿 pushing branch: {current_branch}")
            print("📡 push options:")
            print("1. push to origin")
            print("2. push with upstream")
            print("3. force push (careful!)")
            print("c. cancel")
            
            print("\n👉 select option: ", end='', flush=True)
            choice = get_single_key()
            print(choice)
            
            if choice == '1':
                subprocess.run(['git', 'push'], check=True)
                print("✅ pushed successfully")
            elif choice == '2':
                subprocess.run(['git', 'push', '-u', 'origin', current_branch], check=True)
                print("✅ pushed and set upstream")
            elif choice == '3':
                print("⚠️ force push will overwrite remote!")
                print("are you sure? (y/n): ", end='', flush=True)
                confirm = get_single_key()
                print(confirm)
                if confirm.lower() == 'y':
                    subprocess.run(['git', 'push', '--force'], check=True)
                    print("✅ force pushed successfully")
                else:
                    print("❌ force push cancelled")
            elif choice == 'c':
                print("❌ push cancelled")
            else:
                print("❌ invalid choice")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ error pushing: {e}")
    
    def pull_from_remote(self):
        """pull changes from remote repository"""
        print("\n⬇️ pull from remote")
        print("=" * 50)
        
        if not self.is_git_repo:
            print("❌ not a git repository")
            return
        
        try:
            print("📥 pull options:")
            print("1. pull (merge)")
            print("2. pull with rebase")
            print("3. fetch only")
            print("c. cancel")
            
            print("\n👉 select option: ", end='', flush=True)
            choice = get_single_key()
            print(choice)
            
            if choice == '1':
                subprocess.run(['git', 'pull'], check=True)
                print("✅ pulled successfully")
            elif choice == '2':
                subprocess.run(['git', 'pull', '--rebase'], check=True)
                print("✅ pulled with rebase")
            elif choice == '3':
                subprocess.run(['git', 'fetch'], check=True)
                print("✅ fetched successfully")
            elif choice == 'c':
                print("❌ pull cancelled")
            else:
                print("❌ invalid choice")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ error pulling: {e}")
    
    def branch_management(self):
        """manage git branches"""
        print("\n🌿 branch management")
        print("=" * 50)
        
        if not self.is_git_repo:
            print("❌ not a git repository")
            return
        
        # show current branches
        try:
            result = subprocess.run(['git', 'branch'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print("📋 current branches:")
                print(result.stdout.lower())
        except:
            pass
        
        print("branch operations:")
        print("1. create new branch")
        print("2. switch branch")
        print("3. delete branch")
        print("4. rename branch")
        print("5. merge branch")
        print("c. cancel")
        
        print("\n👉 select option: ", end='', flush=True)
        choice = get_single_key()
        print(choice)
        
        try:
            if choice == '1':
                branch_name = input("📝 enter new branch name: ").strip()
                if branch_name:
                    subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
                    print(f"✅ created and switched to {branch_name}")
                else:
                    print("❌ invalid branch name")
                    
            elif choice == '2':
                branch_name = input("📝 enter branch name to switch: ").strip()
                if branch_name:
                    subprocess.run(['git', 'checkout', branch_name], check=True)
                    print(f"✅ switched to {branch_name}")
                else:
                    print("❌ invalid branch name")
                    
            elif choice == '3':
                branch_name = input("📝 enter branch name to delete: ").strip()
                if branch_name:
                    subprocess.run(['git', 'branch', '-d', branch_name], check=True)
                    print(f"✅ deleted branch {branch_name}")
                else:
                    print("❌ invalid branch name")
                    
            elif choice == '4':
                old_name = input("📝 enter current branch name: ").strip()
                new_name = input("📝 enter new branch name: ").strip()
                if old_name and new_name:
                    subprocess.run(['git', 'branch', '-m', old_name, new_name], check=True)
                    print(f"✅ renamed {old_name} to {new_name}")
                else:
                    print("❌ invalid branch names")
                    
            elif choice == '5':
                branch_name = input("📝 enter branch to merge: ").strip()
                if branch_name:
                    subprocess.run(['git', 'merge', branch_name], check=True)
                    print(f"✅ merged {branch_name}")
                else:
                    print("❌ invalid branch name")
                    
            elif choice == 'c':
                print("❌ branch operation cancelled")
            else:
                print("❌ invalid choice")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ error in branch operation: {e}")
    
    def remote_management(self):
        """manage remote repositories"""
        print("\n📡 remote management")
        print("=" * 50)
        
        if not self.is_git_repo:
            print("❌ not a git repository")
            return
        
        # show current remotes
        try:
            result = subprocess.run(['git', 'remote', '-v'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                print("📋 current remotes:")
                print(result.stdout.lower())
            else:
                print("⚠️ no remotes configured")
        except:
            pass
        
        print("\nremote operations:")
        print("1. add remote")
        print("2. remove remote")
        print("3. rename remote")
        print("4. change remote url")
        print("c. cancel")
        
        print("\n👉 select option: ", end='', flush=True)
        choice = get_single_key()
        print(choice)
        
        try:
            if choice == '1':
                # Automatically use hardcoded repository URL
                name = "origin"
                url = self.repo_url
                print(f"📝 adding remote: {name}")
                print(f"📝 repository url: {url}")
                
                # Check if origin already exists
                result = subprocess.run(['git', 'remote'], 
                                      capture_output=True, text=True)
                if name in result.stdout:
                    print("⚠️ origin already exists, updating url...")
                    subprocess.run(['git', 'remote', 'set-url', name, url], check=True)
                    print(f"✅ updated remote {name}")
                else:
                    subprocess.run(['git', 'remote', 'add', name, url], check=True)
                    print(f"✅ added remote {name}")
                    
            elif choice == '2':
                name = input("📝 remote name to remove: ").strip()
                if name:
                    subprocess.run(['git', 'remote', 'remove', name], check=True)
                    print(f"✅ removed remote {name}")
                else:
                    print("❌ invalid remote name")
                    
            elif choice == '3':
                old_name = input("📝 current remote name: ").strip()
                new_name = input("📝 new remote name: ").strip()
                if old_name and new_name:
                    subprocess.run(['git', 'remote', 'rename', old_name, new_name], check=True)
                    print(f"✅ renamed {old_name} to {new_name}")
                else:
                    print("❌ invalid remote names")
                    
            elif choice == '4':
                name = input("📝 remote name: ").strip()
                url = input("📝 new url: ").strip()
                if name and url:
                    subprocess.run(['git', 'remote', 'set-url', name, url], check=True)
                    print(f"✅ updated url for {name}")
                else:
                    print("❌ invalid remote details")
                    
            elif choice == 'c':
                print("❌ remote operation cancelled")
            else:
                print("❌ invalid choice")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ error in remote operation: {e}")
    
    def view_history(self):
        """view commit history"""
        print("\n📜 commit history")
        print("=" * 50)
        
        if not self.is_git_repo:
            print("❌ not a git repository")
            return
        
        print("history options:")
        print("1. recent commits (5)")
        print("2. all commits")
        print("3. detailed history")
        print("4. graph view")
        print("c. cancel")
        
        print("\n👉 select option: ", end='', flush=True)
        choice = get_single_key()
        print(choice)
        
        try:
            if choice == '1':
                result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                                      capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    print("📋 recent commits:")
                    print(result.stdout.lower())
                else:
                    print("⚠️ no commits found")
                    
            elif choice == '2':
                result = subprocess.run(['git', 'log', '--oneline'], 
                                      capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    print("📋 all commits:")
                    lines = result.stdout.strip().split('\n')
                    for line in lines[:20]:
                        print(line.lower())
                    if len(lines) > 20:
                        print(f"... and {len(lines) - 20} more commits")
                else:
                    print("⚠️ no commits found")
                    
            elif choice == '3':
                result = subprocess.run(['git', 'log', '--pretty=format:%h - %an, %ar : %s', '-5'], 
                                      capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    print("📋 detailed history:")
                    print(result.stdout.lower())
                else:
                    print("⚠️ no commits found")
                    
            elif choice == '4':
                result = subprocess.run(['git', 'log', '--graph', '--oneline', '-10'], 
                                      capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    print("📋 graph view:")
                    print(result.stdout.lower())
                else:
                    print("⚠️ no commits found")
                    
            elif choice == 'c':
                print("❌ history view cancelled")
            else:
                print("❌ invalid choice")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ error getting history: {e}")

# quick access functions
def show_git_status():
    """quick git status"""
    manager = GitManager()
    if manager.is_git_repo:
        manager.show_status()
    else:
        print("❌ not a git repository")

def quick_commit(message=None):
    """quick commit with optional message"""
    manager = GitManager()
    if not manager.is_git_repo:
        print("❌ not a git repository")
        return
    
    try:
        # add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # commit
        if not message:
            if PYTZ_AVAILABLE:
                try:
                    # Get Istanbul timezone
                    istanbul_tz = pytz.timezone('Europe/Istanbul')
                    timestamp = datetime.now(istanbul_tz).strftime("%Y-%m-%d %H:%M:%S %Z")
                except:
                    # Fallback to local time
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S +03:00")
            else:
                # Fallback to local time if pytz not available
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S +03:00")
            
            # Get changed files for better message
            try:
                result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                      capture_output=True, text=True, check=True)
                changed_files = result.stdout.strip().split('\n')
                if changed_files and changed_files[0]:
                    num_files = len(changed_files)
                    if num_files == 1:
                        message = f"update: modified {changed_files[0]} at {timestamp}"
                    else:
                        message = f"update: modified {num_files} files at {timestamp}"
                else:
                    message = f"update: automated commit at {timestamp}"
            except:
                message = f"update: automated commit at {timestamp}"
        
        subprocess.run(['git', 'commit', '-m', message], check=True)
        print(f"✅ committed: {message}")
    except subprocess.CalledProcessError as e:
        print(f"❌ error: {e}")

def quick_push():
    """quick push to origin"""
    manager = GitManager()
    if manager.is_git_repo:
        try:
            subprocess.run(['git', 'push'], check=True)
            print("✅ pushed successfully")
        except subprocess.CalledProcessError:
            try:
                # try with upstream
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                      capture_output=True, text=True, check=True)
                branch = result.stdout.strip()
                subprocess.run(['git', 'push', '-u', 'origin', branch], check=True)
                print("✅ pushed with upstream")
            except subprocess.CalledProcessError as e:
                print(f"❌ error pushing: {e}")
    else:
        print("❌ not a git repository")

def quick_pull():
    """quick pull from origin"""
    manager = GitManager()
    if manager.is_git_repo:
        try:
            subprocess.run(['git', 'pull'], check=True)
            print("✅ pulled successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ error pulling: {e}")
    else:
        print("❌ not a git repository")

def quick_branch(branch_name=None):
    """quick branch operations"""
    manager = GitManager()
    if not manager.is_git_repo:
        print("❌ not a git repository")
        return
    
    if branch_name:
        try:
            subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
            print(f"✅ created and switched to {branch_name}")
        except subprocess.CalledProcessError:
            try:
                subprocess.run(['git', 'checkout', branch_name], check=True)
                print(f"✅ switched to {branch_name}")
            except subprocess.CalledProcessError as e:
                print(f"❌ error: {e}")
    else:
        # show branches
        try:
            result = subprocess.run(['git', 'branch'], 
                                  capture_output=True, text=True, check=True)
            print("🌿 branches:")
            print(result.stdout.lower())
        except subprocess.CalledProcessError as e:
            print(f"❌ error: {e}")

# main entry point
if __name__ == "__main__":
    manager = GitManager()
    manager.show_main_menu()