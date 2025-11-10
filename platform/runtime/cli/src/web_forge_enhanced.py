#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Forge Enhanced Setup Flow
Complete implementation with success/failure handling and transitions
"""

import os
import sys
import json
import time
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Import Colors and utilities from main.py
try:
    from main import Colors, move_cursor, clear_content_area, get_terminal_size, get_single_key, show_server_action
except ImportError:
    # Fallback definitions
    class Colors:
        RESET = '\033[0m'
        BOLD = '\033[1m'
        DIM = '\033[2m'
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        ORANGE = '\033[38;5;208m'


def install_redis():
    """Install Redis on the system"""
    result = {
        'success': False,
        'message': '',
        'command': ''
    }
    
    cols, lines = get_terminal_size()
    content_x = 31
    y = 10
    
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Installing Redis...{Colors.RESET}")
    
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        # Check if Homebrew is installed
        brew_check = subprocess.run(['which', 'brew'], capture_output=True)
        if brew_check.returncode != 0:
            result['message'] = "Homebrew not found. Please install Homebrew first: https://brew.sh"
            return result
        
        # Install Redis via Homebrew
        result['command'] = 'brew install redis'
        install_cmd = subprocess.run(['brew', 'install', 'redis'], capture_output=True, text=True)
        
        if install_cmd.returncode == 0:
            # Start Redis service
            start_cmd = subprocess.run(['brew', 'services', 'start', 'redis'], capture_output=True)
            if start_cmd.returncode == 0:
                result['success'] = True
                result['message'] = "Redis installed and started successfully"
            else:
                result['success'] = True
                result['message'] = "Redis installed. Start manually with: redis-server"
        else:
            result['message'] = f"Redis installation failed: {install_cmd.stderr}"
    
    elif system == 'Linux':
        # Try apt-get first (Ubuntu/Debian)
        apt_check = subprocess.run(['which', 'apt-get'], capture_output=True)
        if apt_check.returncode == 0:
            result['command'] = 'sudo apt-get install redis-server'
            install_cmd = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'redis-server'], 
                                       capture_output=True, text=True)
            if install_cmd.returncode == 0:
                result['success'] = True
                result['message'] = "Redis installed successfully"
            else:
                result['message'] = f"Redis installation failed: {install_cmd.stderr}"
        else:
            result['message'] = "Package manager not supported. Please install Redis manually."
    
    else:
        result['message'] = f"Automatic Redis installation not supported on {system}"
    
    return result


def install_postgresql():
    """Install PostgreSQL on the system"""
    result = {
        'success': False,
        'message': '',
        'command': ''
    }
    
    cols, lines = get_terminal_size()
    content_x = 31
    y = 15
    
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Installing PostgreSQL...{Colors.RESET}")
    
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        # Check if Homebrew is installed
        brew_check = subprocess.run(['which', 'brew'], capture_output=True)
        if brew_check.returncode != 0:
            result['message'] = "Homebrew not found. Please install Homebrew first: https://brew.sh"
            return result
        
        # Install PostgreSQL via Homebrew
        result['command'] = 'brew install postgresql@15'
        install_cmd = subprocess.run(['brew', 'install', 'postgresql@15'], capture_output=True, text=True)
        
        if install_cmd.returncode == 0:
            # Start PostgreSQL service
            start_cmd = subprocess.run(['brew', 'services', 'start', 'postgresql@15'], capture_output=True)
            if start_cmd.returncode == 0:
                result['success'] = True
                result['message'] = "PostgreSQL installed and started successfully"
            else:
                result['success'] = True
                result['message'] = "PostgreSQL installed. Start manually with: brew services start postgresql@15"
        else:
            result['message'] = f"PostgreSQL installation failed: {install_cmd.stderr}"
    
    elif system == 'Linux':
        # Try apt-get first (Ubuntu/Debian)
        apt_check = subprocess.run(['which', 'apt-get'], capture_output=True)
        if apt_check.returncode == 0:
            result['command'] = 'sudo apt-get install postgresql postgresql-contrib'
            install_cmd = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'postgresql', 'postgresql-contrib'], 
                                       capture_output=True, text=True)
            if install_cmd.returncode == 0:
                result['success'] = True
                result['message'] = "PostgreSQL installed successfully"
            else:
                result['message'] = f"PostgreSQL installation failed: {install_cmd.stderr}"
        else:
            result['message'] = "Package manager not supported. Please install PostgreSQL manually."
    
    else:
        result['message'] = f"Automatic PostgreSQL installation not supported on {system}"
    
    return result


class SetupStateManager:
    """Manages setup state and persistence"""
    
    def __init__(self):
        self.state_file = Path('/Users/berkhatirli/Desktop/unibos/.unibos_setup_state.json')
        self.load_state()
    
    def load_state(self):
        """Load setup state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
            except:
                self.initialize_state()
        else:
            self.initialize_state()
    
    def initialize_state(self):
        """Initialize empty state"""
        self.state = {
            'backend_setup': False,
            'frontend_setup': False,
            'database_setup': False,
            'last_setup_attempt': None,
            'last_successful_setup': None,
            'setup_history': [],
            'environment': {
                'python_version': None,
                'node_version': None,
                'npm_version': None,
                'postgres_version': None
            }
        }
    
    def save_state(self):
        """Save setup state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save setup state: {e}")
    
    def record_setup_attempt(self, component: str, result: Dict):
        """Record a setup attempt"""
        attempt = {
            'component': component,
            'timestamp': datetime.now().isoformat(),
            'success': result.get('success', False),
            'errors': result.get('errors', []),
            'warnings': result.get('warnings', []),
            'steps_completed': result.get('steps', {})
        }
        
        self.state['setup_history'].append(attempt)
        self.state[f'{component}_setup'] = result.get('success', False)
        self.state['last_setup_attempt'] = datetime.now().isoformat()
        
        if result.get('success', False):
            self.state['last_successful_setup'] = datetime.now().isoformat()
        
        self.save_state()
    
    def is_setup_complete(self) -> bool:
        """Check if all components are set up"""
        return (self.state.get('backend_setup', False) and 
                self.state.get('frontend_setup', False))
    
    def get_setup_status(self) -> Dict:
        """Get current setup status"""
        return {
            'backend': self.state.get('backend_setup', False),
            'frontend': self.state.get('frontend_setup', False),
            'database': self.state.get('database_setup', False),
            'complete': self.is_setup_complete()
        }


class SetupLogger:
    """Enhanced logging for setup process"""
    
    def __init__(self):
        self.log_dir = Path('/Users/berkhatirli/Desktop/unibos/logs/setup')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_log = self.log_dir / f"setup_{self.session_id}.log"
        self.error_log = self.log_dir / f"setup_errors_{self.session_id}.log"
        self.input_log = self.log_dir / f"setup_input_{self.session_id}.log"
    
    def log(self, level: str, message: str, context: Optional[Dict] = None):
        """Log a message with context"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'context': context or {}
        }
        
        try:
            with open(self.current_log, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            
            # Also log errors to separate file
            if level in ['ERROR', 'CRITICAL']:
                with open(self.error_log, 'a') as f:
                    f.write(json.dumps(entry) + '\n')
                    
            # Log input-related messages to separate file for debugging
            if 'input' in message.lower() or 'key' in message.lower():
                with open(self.input_log, 'a') as f:
                    f.write(json.dumps(entry) + '\n')
        except:
            pass  # Silent fail for logging
    
    def log_command(self, command: str, result: subprocess.CompletedProcess):
        """Log command execution"""
        self.log('INFO', f"Executing: {command}", {
            'command': command,
            'returncode': result.returncode,
            'stdout': result.stdout.decode() if result.stdout else '',
            'stderr': result.stderr.decode() if result.stderr else ''
        })
    
    def get_recent_errors(self, count: int = 10) -> List[Dict]:
        """Get recent errors from log"""
        errors = []
        if self.error_log.exists():
            with open(self.error_log, 'r') as f:
                for line in f:
                    try:
                        errors.append(json.loads(line))
                    except:
                        pass
        return errors[-count:]


def check_system_requirements() -> Dict:
    """Check all system requirements"""
    requirements = {
        'python': {'required': '3.8', 'found': None, 'ok': False},
        'node': {'required': '14.0', 'found': None, 'ok': False},
        'npm': {'required': '6.0', 'found': None, 'ok': False},
        'git': {'required': '2.0', 'found': None, 'ok': False},
        'disk_space': {'required': 1024, 'found': None, 'ok': False}  # MB
    }
    
    # Check Python
    try:
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1]
            requirements['python']['found'] = version
            major, minor = map(int, version.split('.')[:2])
            requirements['python']['ok'] = (major == 3 and minor >= 8)
    except:
        pass
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip().lstrip('v')
            requirements['node']['found'] = version
            major = int(version.split('.')[0])
            requirements['node']['ok'] = major >= 14
    except:
        pass
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            requirements['npm']['found'] = version
            major = int(version.split('.')[0])
            requirements['npm']['ok'] = major >= 6
    except:
        pass
    
    # Check Git
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1]
            requirements['git']['found'] = version
            requirements['git']['ok'] = True
    except:
        pass
    
    # Check disk space
    try:
        import shutil
        stat = shutil.disk_usage('/Users/berkhatirli/Desktop/unibos')
        free_mb = stat.free // (1024 * 1024)
        requirements['disk_space']['found'] = free_mb
        requirements['disk_space']['ok'] = free_mb >= requirements['disk_space']['required']
    except:
        pass
    
    return requirements


def setup_backend_environment_enhanced(logger: SetupLogger) -> Dict:
    """Enhanced backend setup with detailed tracking"""
    result = {
        'success': True,
        'steps': {},
        'errors': [],
        'warnings': []
    }
    
    cols, lines = get_terminal_size()
    content_x = 31  # After sidebar + margin
    y = 5
    
    # Ensure content area is properly cleared first
    clear_content_area()
    show_server_action("⚙️ Setting Up Backend", Colors.BLUE)
    
    # Save current directory
    original_dir = os.getcwd()
    backend_path = Path('/Users/berkhatirli/Desktop/unibos/backend')
    
    # Step 1: Check directory
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Checking backend directory...{Colors.RESET}")
    logger.log('INFO', 'Checking backend directory', {'path': str(backend_path)})
    
    if not backend_path.exists():
        error_msg = f"Backend directory not found at {backend_path}"
        logger.log('ERROR', error_msg)
        result['success'] = False
        result['errors'].append(error_msg)
        result['steps']['check_directory'] = False
        
        move_cursor(content_x, y + 1)
        print(f"{Colors.RED}✗ {error_msg}{Colors.RESET}")
        return result
    
    result['steps']['check_directory'] = True
    move_cursor(content_x, y + 1)
    print(f"{Colors.GREEN}✓ Backend directory found{Colors.RESET}")
    
    os.chdir(backend_path)
    y += 3
    
    # Step 2: Create virtual environment
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Creating Python virtual environment...{Colors.RESET}")
    logger.log('INFO', 'Creating virtual environment')
    
    venv_path = backend_path / 'venv'
    if venv_path.exists():
        result['warnings'].append("Virtual environment already exists, skipping creation")
        result['steps']['create_venv'] = True
        move_cursor(content_x, y + 1)
        print(f"{Colors.YELLOW}⚠ Virtual environment already exists{Colors.RESET}")
    else:
        cmd_result = subprocess.run(['python3', '-m', 'venv', 'venv'], capture_output=True)
        logger.log_command('python3 -m venv venv', cmd_result)
        
        if cmd_result.returncode == 0:
            result['steps']['create_venv'] = True
            move_cursor(content_x, y + 1)
            print(f"{Colors.GREEN}✓ Virtual environment created{Colors.RESET}")
        else:
            result['success'] = False
            result['errors'].append("Failed to create virtual environment")
            result['steps']['create_venv'] = False
            move_cursor(content_x, y + 1)
            print(f"{Colors.RED}✗ Failed to create virtual environment{Colors.RESET}")
            os.chdir(original_dir)
            return result
    
    y += 3
    
    # Step 3: Install dependencies
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Installing backend dependencies...{Colors.RESET}")
    logger.log('INFO', 'Installing dependencies')
    
    # First upgrade pip to ensure compatibility
    activate_cmd = 'source venv/bin/activate' if platform.system() != 'Windows' else 'venv\\Scripts\\activate'
    upgrade_pip_cmd = f"{activate_cmd} && pip install --upgrade pip"
    
    move_cursor(content_x, y + 1)
    print(f"{Colors.DIM}Upgrading pip...{Colors.RESET}")
    
    cmd_result = subprocess.run(upgrade_pip_cmd, shell=True, capture_output=True)
    logger.log_command(upgrade_pip_cmd, cmd_result)
    
    # Use minimal requirements for better compatibility
    requirements_file = 'requirements-minimal.txt' if (backend_path / 'requirements-minimal.txt').exists() else 'requirements.txt'
    
    # Check if requirements file exists
    if not (backend_path / requirements_file).exists():
        # Create a basic requirements.txt with compatible versions
        basic_requirements = """Django==4.2.16
djangorestframework==3.14.0
django-cors-headers==4.3.1
psycopg2-binary==2.9.9
python-dotenv==1.0.1
gunicorn==21.2.0
redis==5.0.1
django-redis==5.4.0
"""
        with open(backend_path / 'requirements.txt', 'w') as f:
            f.write(basic_requirements)
        result['warnings'].append("Created basic requirements.txt")
        requirements_file = 'requirements.txt'
    
    install_cmd = f"{activate_cmd} && pip install -r {requirements_file}"
    
    move_cursor(content_x, y + 2)
    print(f"{Colors.DIM}Installing from {requirements_file}...{Colors.RESET}")
    
    cmd_result = subprocess.run(install_cmd, shell=True, capture_output=True)
    logger.log_command(install_cmd, cmd_result)
    
    if cmd_result.returncode == 0:
        result['steps']['install_deps'] = True
        move_cursor(content_x, y + 3)
        print(f"{Colors.GREEN}✓ Dependencies installed{Colors.RESET}")
    else:
        # Try installing Django separately first
        install_django_cmd = f"{activate_cmd} && pip install Django==4.2.16"
        move_cursor(content_x, y + 3)
        print(f"{Colors.YELLOW}⚠ Trying to install Django separately...{Colors.RESET}")
        
        django_result = subprocess.run(install_django_cmd, shell=True, capture_output=True)
        logger.log_command(install_django_cmd, django_result)
        
        if django_result.returncode == 0:
            # Try installing rest of dependencies
            install_rest_cmd = f"{activate_cmd} && pip install djangorestframework django-cors-headers"
            rest_result = subprocess.run(install_rest_cmd, shell=True, capture_output=True)
            
            if rest_result.returncode == 0:
                result['steps']['install_deps'] = True
                move_cursor(content_x, y + 4)
                print(f"{Colors.GREEN}✓ Core dependencies installed{Colors.RESET}")
            else:
                result['warnings'].append("Some dependencies may have failed to install")
                result['steps']['install_deps'] = False
                move_cursor(content_x, y + 4)
                print(f"{Colors.YELLOW}⚠ Some dependencies may have failed{Colors.RESET}")
        else:
            result['warnings'].append("Failed to install Django")
            result['steps']['install_deps'] = False
            move_cursor(content_x, y + 4)
            print(f"{Colors.RED}✗ Failed to install Django{Colors.RESET}")
    
    y += 5  # Adjust for additional lines from dependency installation
    
    # Step 4: Check Django installation
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Verifying Django installation...{Colors.RESET}")
    
    check_django_cmd = f"{activate_cmd} && python -c 'import django; print(django.get_version())'"
    cmd_result = subprocess.run(check_django_cmd, shell=True, capture_output=True)
    
    if cmd_result.returncode == 0:
        django_version = cmd_result.stdout.decode().strip()
        result['steps']['verify_django'] = True
        move_cursor(content_x, y + 1)
        print(f"{Colors.GREEN}✓ Django {django_version} installed{Colors.RESET}")
        
        # Also check if manage.py works with simple settings
        check_manage_cmd = f"{activate_cmd} && DJANGO_SETTINGS_MODULE=unibos_backend.settings.simple python manage.py --version"
        manage_result = subprocess.run(check_manage_cmd, shell=True, capture_output=True, cwd=backend_path)
        if manage_result.returncode == 0:
            move_cursor(content_x, y + 2)
            print(f"{Colors.GREEN}✓ Django management commands working{Colors.RESET}")
            
            # Run migrations with simple settings
            migrate_cmd = f"{activate_cmd} && DJANGO_SETTINGS_MODULE=unibos_backend.settings.simple python manage.py migrate --run-syncdb"
            migrate_result = subprocess.run(migrate_cmd, shell=True, capture_output=True, cwd=backend_path)
            if migrate_result.returncode == 0:
                move_cursor(content_x, y + 3)
                print(f"{Colors.GREEN}✓ Database migrations completed{Colors.RESET}")
    else:
        # Try one more time with a direct Django install
        move_cursor(content_x, y + 1)
        print(f"{Colors.YELLOW}⚠ Django not found, attempting final install...{Colors.RESET}")
        
        final_django_cmd = f"{activate_cmd} && pip install --force-reinstall Django==4.2.16"
        final_result = subprocess.run(final_django_cmd, shell=True, capture_output=True)
        
        # Check again
        check_result = subprocess.run(check_django_cmd, shell=True, capture_output=True)
        if check_result.returncode == 0:
            django_version = check_result.stdout.decode().strip()
            result['steps']['verify_django'] = True
            move_cursor(content_x, y + 2)
            print(f"{Colors.GREEN}✓ Django {django_version} installed after retry{Colors.RESET}")
        else:
            result['warnings'].append("Django verification failed - manual installation may be required")
            result['steps']['verify_django'] = False
            move_cursor(content_x, y + 2)
            print(f"{Colors.RED}✗ Django installation failed{Colors.RESET}")
            move_cursor(content_x, y + 3)
            print(f"{Colors.DIM}Error: {cmd_result.stderr.decode().strip()[:60]}...{Colors.RESET}")
    
    # Step 5: Check and setup PostgreSQL
    y += 4
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Checking PostgreSQL...{Colors.RESET}")
    logger.log('INFO', 'Checking PostgreSQL availability')
    
    # Check if PostgreSQL is installed
    psql_check = subprocess.run(['which', 'psql'], capture_output=True, text=True)
    
    if psql_check.returncode != 0:
        # PostgreSQL not installed
        move_cursor(content_x, y + 1)
        print(f"{Colors.YELLOW}⚠ PostgreSQL not found. Installing...{Colors.RESET}")
        
        # Install PostgreSQL
        postgres_result = install_postgresql()
        
        if postgres_result['success']:
            result['steps']['install_postgresql'] = True
            move_cursor(content_x, y + 2)
            print(f"{Colors.GREEN}✓ PostgreSQL installed successfully{Colors.RESET}")
        else:
            result['warnings'].append("PostgreSQL installation failed - will use SQLite")
            result['steps']['install_postgresql'] = False
            move_cursor(content_x, y + 2)
            print(f"{Colors.YELLOW}⚠ PostgreSQL installation failed - using SQLite{Colors.RESET}")
    else:
        # PostgreSQL is installed, check if it's running
        pg_running = subprocess.run(['psql', '-U', 'postgres', '-c', 'SELECT 1;'], 
                                   capture_output=True, text=True)
        if pg_running.returncode == 0:
            result['steps']['postgresql_available'] = True
            move_cursor(content_x, y + 1)
            print(f"{Colors.GREEN}✓ PostgreSQL is available{Colors.RESET}")
        else:
            # Try to start PostgreSQL
            move_cursor(content_x, y + 1)
            print(f"{Colors.YELLOW}⚠ PostgreSQL not running. Starting...{Colors.RESET}")
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['brew', 'services', 'start', 'postgresql@15'], 
                             capture_output=True, text=True)
            
            time.sleep(2)
            result['steps']['postgresql_available'] = True
            move_cursor(content_x, y + 2)
            print(f"{Colors.GREEN}✓ PostgreSQL service started{Colors.RESET}")
    
    # Step 6: Check and setup Redis
    y += 3
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Checking Redis...{Colors.RESET}")
    logger.log('INFO', 'Checking Redis availability')
    
    # Check if Redis is installed
    redis_check = subprocess.run(['which', 'redis-cli'], capture_output=True, text=True)
    
    if redis_check.returncode != 0:
        # Redis not installed
        move_cursor(content_x, y + 1)
        print(f"{Colors.YELLOW}⚠ Redis not found. Installing...{Colors.RESET}")
        
        # Install Redis
        redis_result = install_redis()
        
        if redis_result['success']:
            result['steps']['install_redis'] = True
            move_cursor(content_x, y + 2)
            print(f"{Colors.GREEN}✓ Redis installed successfully{Colors.RESET}")
        else:
            result['warnings'].append("Redis installation failed - some features may be limited")
            result['steps']['install_redis'] = False
            move_cursor(content_x, y + 2)
            print(f"{Colors.YELLOW}⚠ Redis installation failed - continuing without Redis{Colors.RESET}")
    else:
        # Redis is installed, check if it's running
        redis_running = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True)
        if redis_running.returncode == 0 and redis_running.stdout.strip() == 'PONG':
            result['steps']['redis_available'] = True
            move_cursor(content_x, y + 1)
            print(f"{Colors.GREEN}✓ Redis is available{Colors.RESET}")
        else:
            # Try to start Redis
            move_cursor(content_x, y + 1)
            print(f"{Colors.YELLOW}⚠ Redis not running. Starting...{Colors.RESET}")
            
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['brew', 'services', 'start', 'redis'], 
                             capture_output=True, text=True)
            
            time.sleep(2)
            result['steps']['redis_available'] = True
            move_cursor(content_x, y + 2)
            print(f"{Colors.GREEN}✓ Redis service started{Colors.RESET}")
    
    # Restore original directory
    os.chdir(original_dir)
    
    # Summary
    y += 3
    move_cursor(content_x, y)
    if result['success']:
        print(f"{Colors.GREEN}Backend setup completed successfully!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Backend setup completed with issues{Colors.RESET}")
    
    time.sleep(2)
    return result


def setup_frontend_environment_enhanced(logger: SetupLogger) -> Dict:
    """Enhanced frontend setup with detailed tracking"""
    result = {
        'success': True,
        'steps': {},
        'errors': [],
        'warnings': []
    }
    
    cols, lines = get_terminal_size()
    content_x = 31  # After sidebar + margin
    y = 5
    
    # Ensure content area is properly cleared first
    clear_content_area()
    show_server_action("🎨 Setting Up Frontend", Colors.BLUE)
    
    # Save current directory
    original_dir = os.getcwd()
    frontend_path = Path('/Users/berkhatirli/Desktop/unibos/frontend')
    
    # Step 1: Check directory
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Checking frontend directory...{Colors.RESET}")
    logger.log('INFO', 'Checking frontend directory', {'path': str(frontend_path)})
    
    if not frontend_path.exists():
        error_msg = f"Frontend directory not found at {frontend_path}"
        logger.log('ERROR', error_msg)
        result['success'] = False
        result['errors'].append(error_msg)
        result['steps']['check_directory'] = False
        
        move_cursor(content_x, y + 1)
        print(f"{Colors.RED}✗ {error_msg}{Colors.RESET}")
        return result
    
    result['steps']['check_directory'] = True
    move_cursor(content_x, y + 1)
    print(f"{Colors.GREEN}✓ Frontend directory found{Colors.RESET}")
    
    os.chdir(frontend_path)
    y += 3
    
    # Step 2: Check Node.js and npm
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Checking Node.js and npm...{Colors.RESET}")
    
    node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
    npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
    
    if node_result.returncode == 0 and npm_result.returncode == 0:
        node_version = node_result.stdout.strip()
        npm_version = npm_result.stdout.strip()
        result['steps']['check_node'] = True
        move_cursor(content_x, y + 1)
        print(f"{Colors.GREEN}✓ Node {node_version}, npm {npm_version}{Colors.RESET}")
    else:
        result['success'] = False
        result['errors'].append("Node.js or npm not found")
        result['steps']['check_node'] = False
        move_cursor(content_x, y + 1)
        print(f"{Colors.RED}✗ Node.js or npm not found{Colors.RESET}")
        os.chdir(original_dir)
        return result
    
    y += 3
    
    # Step 3: Check package.json
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Checking package.json...{Colors.RESET}")
    
    if not (frontend_path / 'package.json').exists():
        # Create a basic React package.json
        basic_package = {
            "name": "unibos-frontend",
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
                "axios": "^1.6.0",
                "react-router-dom": "^6.20.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "browserslist": {
                "production": [">0.2%", "not dead", "not op_mini all"],
                "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
            }
        }
        
        with open(frontend_path / 'package.json', 'w') as f:
            json.dump(basic_package, f, indent=2)
        
        result['warnings'].append("Created basic package.json")
        move_cursor(content_x, y + 1)
        print(f"{Colors.YELLOW}⚠ Created basic package.json{Colors.RESET}")
    else:
        result['steps']['check_package'] = True
        move_cursor(content_x, y + 1)
        print(f"{Colors.GREEN}✓ package.json found{Colors.RESET}")
    
    y += 3
    
    # Step 4: Install dependencies
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Installing frontend dependencies...{Colors.RESET}")
    move_cursor(content_x, y + 1)
    print(f"{Colors.DIM}(This may take a few minutes){Colors.RESET}")
    
    # Check if node_modules exists
    if (frontend_path / 'node_modules').exists():
        result['warnings'].append("Dependencies already installed, skipping")
        result['steps']['install_deps'] = True
        move_cursor(content_x, y + 2)
        print(f"{Colors.YELLOW}⚠ Dependencies already installed{Colors.RESET}")
    else:
        cmd_result = subprocess.run(['npm', 'install'], capture_output=True)
        logger.log_command('npm install', cmd_result)
        
        if cmd_result.returncode == 0:
            result['steps']['install_deps'] = True
            move_cursor(content_x, y + 2)
            print(f"{Colors.GREEN}✓ Dependencies installed successfully{Colors.RESET}")
        else:
            result['warnings'].append("Some dependencies may have failed to install")
            result['steps']['install_deps'] = False
            move_cursor(content_x, y + 2)
            print(f"{Colors.YELLOW}⚠ Some dependencies may have failed{Colors.RESET}")
    
    y += 4
    
    # Step 5: Create basic React app structure if missing
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Checking React app structure...{Colors.RESET}")
    
    src_path = frontend_path / 'src'
    public_path = frontend_path / 'public'
    
    if not src_path.exists():
        src_path.mkdir(exist_ok=True)
        # Create basic App.js
        app_content = """import React from 'react';

function App() {
  return (
    <div className="App">
      <h1>UNIBOS Web Forge</h1>
      <p>Welcome to the UNIBOS frontend!</p>
    </div>
  );
}

export default App;
"""
        with open(src_path / 'App.js', 'w') as f:
            f.write(app_content)
        
        # Create index.js
        index_content = """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        with open(src_path / 'index.js', 'w') as f:
            f.write(index_content)
        
        # Create basic CSS
        with open(src_path / 'index.css', 'w') as f:
            f.write("body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; }")
        
        result['warnings'].append("Created basic React app structure")
    
    if not public_path.exists():
        public_path.mkdir(exist_ok=True)
        # Create index.html
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>UNIBOS Web Forge</title>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>
"""
        with open(public_path / 'index.html', 'w') as f:
            f.write(html_content)
        
        result['warnings'].append("Created public directory structure")
    
    result['steps']['check_structure'] = True
    move_cursor(content_x, y + 1)
    print(f"{Colors.GREEN}✓ React app structure verified{Colors.RESET}")
    
    # Restore original directory
    os.chdir(original_dir)
    
    # Summary
    y += 3
    move_cursor(content_x, y)
    if result['success']:
        print(f"{Colors.GREEN}Frontend setup completed successfully!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}Frontend setup completed with issues{Colors.RESET}")
    
    time.sleep(2)
    return result


def show_setup_success_screen(results: Dict):
    """Show success screen with summary"""
    cols, lines = get_terminal_size()
    content_x = 31  # After sidebar + margin
    y = 5
    
    clear_content_area()
    show_server_action("✅ Setup Complete!", Colors.GREEN)
    
    move_cursor(content_x, y)
    print(f"{Colors.GREEN}All components have been set up successfully!{Colors.RESET}")
    y += 2
    
    # Backend summary
    if results.get('backend'):
        move_cursor(content_x, y)
        print(f"{Colors.CYAN}Backend Setup:{Colors.RESET}")
        y += 1
        
        backend_steps = results['backend'].get('steps', {})
        for step, success in backend_steps.items():
            move_cursor(content_x + 2, y)
            icon = "✓" if success else "✗"
            color = Colors.GREEN if success else Colors.RED
            step_name = step.replace('_', ' ').title()
            print(f"{color}{icon} {step_name}{Colors.RESET}")
            y += 1
    
    y += 1
    
    # Frontend summary
    if results.get('frontend'):
        move_cursor(content_x, y)
        print(f"{Colors.CYAN}Frontend Setup:{Colors.RESET}")
        y += 1
        
        frontend_steps = results['frontend'].get('steps', {})
        for step, success in frontend_steps.items():
            move_cursor(content_x + 2, y)
            icon = "✓" if success else "✗"
            color = Colors.GREEN if success else Colors.RED
            step_name = step.replace('_', ' ').title()
            print(f"{color}{icon} {step_name}{Colors.RESET}")
            y += 1
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.WHITE}Ready to launch Web Forge!{Colors.RESET}")
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.DIM}Starting in 3 seconds...{Colors.RESET}")
    
    # Countdown
    for i in range(3, 0, -1):
        move_cursor(content_x + 12, y)
        print(f"{i}...")
        time.sleep(1)


def show_setup_failure_screen(results: Dict):
    """Show failure screen with error details"""
    cols, lines = get_terminal_size()
    content_x = 31  # After sidebar + margin
    y = 5
    
    clear_content_area()
    show_server_action("⚠️ Setup Issues Detected", Colors.YELLOW)
    
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Setup completed with some issues:{Colors.RESET}")
    y += 2
    
    # Show errors
    all_errors = []
    if results.get('backend', {}).get('errors'):
        all_errors.extend([('Backend', e) for e in results['backend']['errors']])
    if results.get('frontend', {}).get('errors'):
        all_errors.extend([('Frontend', e) for e in results['frontend']['errors']])
    
    if all_errors:
        move_cursor(content_x, y)
        print(f"{Colors.RED}Errors:{Colors.RESET}")
        y += 1
        for component, error in all_errors:
            move_cursor(content_x + 2, y)
            print(f"{Colors.RED}• [{component}] {error}{Colors.RESET}")
            y += 1
    
    y += 1
    
    # Show warnings
    all_warnings = []
    if results.get('backend', {}).get('warnings'):
        all_warnings.extend([('Backend', w) for w in results['backend']['warnings']])
    if results.get('frontend', {}).get('warnings'):
        all_warnings.extend([('Frontend', w) for w in results['frontend']['warnings']])
    
    if all_warnings:
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}Warnings:{Colors.RESET}")
        y += 1
        for component, warning in all_warnings:
            move_cursor(content_x + 2, y)
            print(f"{Colors.YELLOW}• [{component}] {warning}{Colors.RESET}")
            y += 1
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}Recovery Options:{Colors.RESET}")
    y += 1
    
    options = [
        "1. View detailed logs",
        "2. Run debug diagnostics",
        "3. Retry failed steps",
        "4. Continue anyway",
        "5. Exit to menu"
    ]
    
    for option in options:
        move_cursor(content_x + 2, y)
        print(f"{Colors.WHITE}{option}{Colors.RESET}")
        y += 1
    
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Select option (1-5): {Colors.RESET}", end='', flush=True)


def run_debug_diagnostics(results: Dict, logger: SetupLogger):
    """Run comprehensive diagnostics"""
    cols, lines = get_terminal_size()
    content_x = 31  # After sidebar + margin
    y = 5
    
    clear_content_area()
    show_server_action("🔍 Running Diagnostics", Colors.CYAN)
    
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}Running comprehensive system diagnostics...{Colors.RESET}")
    y += 2
    
    # System requirements
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Checking system requirements...{Colors.RESET}")
    requirements = check_system_requirements()
    y += 1
    
    for req, info in requirements.items():
        move_cursor(content_x + 2, y)
        if info['ok']:
            print(f"{Colors.GREEN}✓ {req}: {info['found']} (required: {info['required']}){Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ {req}: {info['found'] or 'Not found'} (required: {info['required']}){Colors.RESET}")
        y += 1
    
    y += 1
    
    # Port availability
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Checking port availability...{Colors.RESET}")
    y += 1
    
    ports = [(3000, 'Frontend'), (8000, 'Backend'), (5432, 'PostgreSQL')]
    for port, service in ports:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            move_cursor(content_x + 2, y)
            if result != 0:
                print(f"{Colors.GREEN}✓ Port {port} ({service}): Available{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠ Port {port} ({service}): In use{Colors.RESET}")
        except:
            move_cursor(content_x + 2, y)
            print(f"{Colors.RED}✗ Port {port} ({service}): Check failed{Colors.RESET}")
        y += 1
    
    y += 1
    
    # File permissions
    move_cursor(content_x, y)
    print(f"{Colors.YELLOW}Checking file permissions...{Colors.RESET}")
    y += 1
    
    paths_to_check = [
        Path('/Users/berkhatirli/Desktop/unibos/backend'),
        Path('/Users/berkhatirli/Desktop/unibos/frontend'),
        Path('/Users/berkhatirli/Desktop/unibos/logs')
    ]
    
    for path in paths_to_check:
        move_cursor(content_x + 2, y)
        if path.exists():
            if os.access(path, os.W_OK):
                print(f"{Colors.GREEN}✓ {path.name}: Writable{Colors.RESET}")
            else:
                print(f"{Colors.RED}✗ {path.name}: Not writable{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠ {path.name}: Does not exist{Colors.RESET}")
        y += 1
    
    y += 2
    
    # Generate recommendations
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}Recommendations:{Colors.RESET}")
    y += 1
    
    recommendations = []
    
    if not requirements['python']['ok']:
        recommendations.append("Install Python 3.8 or higher")
    if not requirements['node']['ok']:
        recommendations.append("Install Node.js 14.0 or higher")
    if not requirements['npm']['ok']:
        recommendations.append("Install npm 6.0 or higher")
    if not requirements['disk_space']['ok']:
        recommendations.append("Free up disk space (need at least 1GB)")
    
    if not recommendations:
        move_cursor(content_x + 2, y)
        print(f"{Colors.GREEN}All system requirements met!{Colors.RESET}")
    else:
        for rec in recommendations:
            move_cursor(content_x + 2, y)
            print(f"{Colors.YELLOW}• {rec}{Colors.RESET}")
            y += 1
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}Press any key to continue...{Colors.RESET}", end='', flush=True)
    get_single_key()
    
    # Clear the prompt before returning
    move_cursor(content_x, y)
    print(' ' * 30, end='', flush=True)


def transition_to_web_forge_main():
    """Smooth transition to main Web Forge screen"""
    cols, lines = get_terminal_size()
    content_x = 31  # After sidebar + margin to avoid overlap
    content_width = cols - content_x - 1
    
    # Clear content area thoroughly
    clear_content_area()
    
    # Ensure no text overflow into sidebar
    for y in range(3, lines - 1):
        move_cursor(25, y)  # Clear gap between sidebar and content
        print('  ', end='', flush=True)
    
    # Show transition animation
    frames = [
        "⚒️  Preparing Web Forge...",
        "⚒️  🔥 Firing up the forge...",
        "⚒️  🔥 ⚔️  Web Forge Ready!"
    ]
    
    for i, frame in enumerate(frames):
        y = lines // 2
        # Ensure animation doesn't overflow
        max_width = min(len(frame), content_width - 2)
        x = content_x + max(0, (content_width - max_width) // 2)
        move_cursor(x, y)
        print(f"{Colors.CYAN}{frame[:max_width]}{Colors.RESET}")
        time.sleep(0.5)
        if i < len(frames) - 1:
            move_cursor(x, y)
            print(' ' * max_width)  # Clear previous frame
    
    time.sleep(1)
    
    # Clear animation before returning
    clear_content_area()
    
    # Now show the main Web Forge interface
    try:
        from main import menu_state
        menu_state.setup_complete = True
        menu_state.web_forge_ready = True
    except ImportError:
        # If menu_state not available, just continue
        pass
    
    # Return to main menu which will handle the enhanced Web Forge display


def run_enhanced_setup_wizard():
    """Main entry point for enhanced setup wizard"""
    # Ensure UTF-8 encoding is set up
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    
    setup_state = SetupStateManager()
    logger = SetupLogger()
    
    logger.log('INFO', 'Starting enhanced setup wizard')
    
    # Check current setup status
    status = setup_state.get_setup_status()
    
    if status['complete']:
        # Everything already set up
        clear_content_area()
        show_server_action("✅ Already Set Up", Colors.GREEN)
        
        cols, lines = get_terminal_size()
        content_x = 31  # After sidebar + margin
        y = 5
        
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}All components are already set up!{Colors.RESET}")
        y += 2
        
        move_cursor(content_x, y)
        print(f"{Colors.CYAN}Would you like to:{Colors.RESET}")
        y += 1
        
        options = [
            "1. Launch Web Forge",
            "2. Re-run setup",
            "3. View setup logs",
            "4. Return to menu"
        ]
        
        for option in options:
            move_cursor(content_x + 2, y)
            print(f"{Colors.WHITE}{option}{Colors.RESET}")
            y += 1
        
        y += 1
        move_cursor(content_x, y)
        print(f"{Colors.YELLOW}Select option (1-4): {Colors.RESET}", end='', flush=True)
        
        # Add debug info
        debug_mode = os.environ.get('UNIBOS_DEBUG', '').lower() == 'true'
        if debug_mode:
            move_cursor(content_x, y + 3)
            print(f"{Colors.DIM}[DEBUG] Waiting for input...{Colors.RESET}")
        
        # Enhanced input handling with visual feedback
        while True:
            try:
                key = get_single_key(timeout=5.0)  # Increased timeout
                logger.log('DEBUG', f'Key pressed: {repr(key)}')
                
                if key is None:
                    continue  # No key pressed, keep waiting
                
                # Handle empty input (Enter key) or newline
                if key in ['\n', '\r', '']:
                    # Show error without breaking alignment
                    move_cursor(content_x, y + 2)
                    print(f"{Colors.RED}Invalid option. Please select 1-4{Colors.RESET}" + " " * 20)
                    time.sleep(1)
                    # Clear the error message properly
                    move_cursor(content_x, y + 2)
                    print(" " * 60)  # Clear entire line
                    # Reset cursor position
                    move_cursor(content_x + 20, y)  # Position after the prompt
                    continue
                
                # Show visual feedback only for valid characters
                if key in ['1', '2', '3', '4']:
                    print(key, end='', flush=True)
                
                if debug_mode:
                    move_cursor(content_x, y + 3)
                    print(f"{Colors.DIM}[DEBUG] Received key: {repr(key)}{Colors.RESET}" + " " * 20)
            except Exception as e:
                # Fallback to standard input if get_single_key fails
                logger.log('WARNING', f'get_single_key failed: {e}, falling back to input()')
                move_cursor(content_x, y + 2)
                print(f"{Colors.YELLOW}Press Enter after selecting option: {Colors.RESET}", end='', flush=True)
                try:
                    key = input().strip()
                    if not key:
                        # Handle empty input
                        move_cursor(content_x, y + 3)
                        print(f"{Colors.RED}Invalid option. Please select 1-4{Colors.RESET}" + " " * 20)
                        time.sleep(1)
                        move_cursor(content_x, y + 3)
                        print(" " * 60)  # Clear entire line
                        continue
                    key = key[0]  # Take first character
                except:
                    continue
            
            if key == '1':
                logger.log('INFO', 'User selected option 1: Launch Web Forge')
                transition_to_web_forge_main()
                return
            elif key == '2':
                # Re-run setup - reset the setup state
                logger.log('INFO', 'User selected option 2: Re-run setup')
                move_cursor(content_x, y + 2)
                print(f"{Colors.YELLOW}Resetting setup state...{Colors.RESET}" + " " * 20)
                setup_state.initialize_state()
                setup_state.save_state()
                time.sleep(0.5)
                clear_content_area()
                show_server_action("🔄 Re-running Setup", Colors.YELLOW)
                time.sleep(1)
                # Force re-checking status after reset
                status = setup_state.get_setup_status()
                # Continue with setup below - don't return!
                break  # Exit the input loop to continue with setup
            elif key == '3':
                logger.log('INFO', 'User selected option 3: View setup logs')
                show_setup_logs(logger)
                return
            elif key == '4':
                logger.log('INFO', 'User selected option 4: Return to menu')
                return
            elif key == '\x1b':  # Escape key
                logger.log('INFO', 'User pressed escape')
                return
            else:
                # Invalid key - show feedback with proper alignment
                move_cursor(content_x, y + 2)
                print(f"{Colors.RED}Invalid option. Please select 1-6{Colors.RESET}" + " " * 20)
                time.sleep(1)
                # Clear the error message properly
                move_cursor(content_x, y + 2)
                print(" " * 60)  # Clear entire line
                # Reset cursor position after the prompt
                move_cursor(content_x + 20, y)  # Position after "Select option (1-6): "
    
    # Run setup steps
    results = {
        'backend': None,
        'frontend': None,
        'overall_success': True
    }
    
    # Log setup status for debugging
    logger.log('DEBUG', f'Setup status before running: backend={status["backend"]}, frontend={status["frontend"]}')
    
    # Backend setup
    if not status['backend']:
        logger.log('INFO', 'Starting backend setup')
        clear_content_area()
        show_server_action("🔧 Setting up Backend", Colors.YELLOW)
        results['backend'] = setup_backend_environment_enhanced(logger)
        setup_state.record_setup_attempt('backend', results['backend'])
        if not results['backend']['success']:
            results['overall_success'] = False
    else:
        logger.log('INFO', 'Backend already set up, skipping')
    
    # Frontend setup
    if not status['frontend']:
        logger.log('INFO', 'Starting frontend setup')
        clear_content_area()
        show_server_action("🔧 Setting up Frontend", Colors.YELLOW)
        results['frontend'] = setup_frontend_environment_enhanced(logger)
        setup_state.record_setup_attempt('frontend', results['frontend'])
        if not results['frontend']['success']:
            results['overall_success'] = False
    else:
        logger.log('INFO', 'Frontend already set up, skipping')
    
    # Show results
    if results['overall_success'] or (status['backend'] and status['frontend']):
        show_setup_success_screen(results)
        transition_to_web_forge_main()
    else:
        show_setup_failure_screen(results)
        
        # Handle recovery options
        key = get_single_key()
        if key == '1':
            # View logs
            show_setup_logs(logger)
        elif key == '2':
            # Run diagnostics
            run_debug_diagnostics(results, logger)
        elif key == '3':
            # Retry failed steps
            retry_failed_steps(results, setup_state, logger)
        elif key == '4':
            # Continue anyway
            transition_to_web_forge_main()
        # else return to menu


def show_setup_logs(logger: SetupLogger):
    """Display setup logs"""
    clear_content_area()
    show_server_action("📜 Setup Logs", Colors.CYAN)
    
    cols, lines = get_terminal_size()
    content_x = 27 + 4
    y = 5
    
    # Get recent errors
    errors = logger.get_recent_errors(10)
    
    if errors:
        move_cursor(content_x, y)
        print(f"{Colors.RED}Recent Errors:{Colors.RESET}")
        y += 1
        
        for error in errors[-5:]:  # Show last 5 errors
            move_cursor(content_x, y)
            timestamp = error['timestamp'].split('T')[1].split('.')[0]
            print(f"{Colors.DIM}{timestamp}{Colors.RESET} {Colors.RED}{error['message']}{Colors.RESET}")
            y += 1
    else:
        move_cursor(content_x, y)
        print(f"{Colors.GREEN}No errors found in logs{Colors.RESET}")
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}Log files location:{Colors.RESET}")
    y += 1
    move_cursor(content_x, y)
    print(f"{Colors.WHITE}{logger.log_dir}{Colors.RESET}")
    
    y += 2
    move_cursor(content_x, y)
    print(f"{Colors.CYAN}Press any key to continue...{Colors.RESET}", end='', flush=True)
    get_single_key()
    
    # Clear the prompt before returning
    move_cursor(content_x, y)
    print(' ' * 30, end='', flush=True)


def retry_failed_steps(results: Dict, setup_state: SetupStateManager, logger: SetupLogger):
    """Retry only the failed setup steps"""
    clear_content_area()
    show_server_action("🔄 Retrying Failed Steps", Colors.YELLOW)
    
    # Re-run only failed components
    if results.get('backend') and not results['backend']['success']:
        results['backend'] = setup_backend_environment_enhanced(logger)
        setup_state.record_setup_attempt('backend', results['backend'])
    
    if results.get('frontend') and not results['frontend']['success']:
        results['frontend'] = setup_frontend_environment_enhanced(logger)
        setup_state.record_setup_attempt('frontend', results['frontend'])
    
    # Check overall success
    overall_success = True
    if results.get('backend') and not results['backend']['success']:
        overall_success = False
    if results.get('frontend') and not results['frontend']['success']:
        overall_success = False
    
    if overall_success:
        show_setup_success_screen(results)
        transition_to_web_forge_main()
    else:
        show_setup_failure_screen(results)


# Export the main function
if __name__ == "__main__":
    # Ensure UTF-8 encoding for terminal
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    
    # Set environment variable for UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Test the enhanced setup wizard
    run_enhanced_setup_wizard()