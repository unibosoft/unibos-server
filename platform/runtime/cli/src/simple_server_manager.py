#!/usr/bin/env python3
"""
UNIBOS Simple Server Manager - Manages backend and frontend servers without external dependencies
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

class SimpleServerManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.backend_path = self.base_path / 'backend'
        self.frontend_path = self.base_path / 'frontend'
        self.backend_pid_file = self.base_path / '.backend.pid'
        self.frontend_pid_file = self.base_path / '.frontend.pid'
        
    def check_port_mac(self, port):
        """Check if a port is in use on macOS"""
        result = subprocess.run(
            f'lsof -i :{port} -sTCP:LISTEN -t',
            shell=True,
            capture_output=True,
            text=True
        )
        return len(result.stdout.strip()) == 0
    
    def kill_port_mac(self, port):
        """Kill process on port for macOS"""
        result = subprocess.run(
            f'lsof -i :{port} -sTCP:LISTEN -t',
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                    print(f"Killed process {pid} on port {port}")
                except:
                    pass
            time.sleep(1)
            return True
        return False
    
    def start_backend(self):
        """Start the backend server"""
        print("\n🚀 Starting Backend Server...")
        
        # Check if already running
        if not self.check_port_mac(8000):
            print("⚠️  Port 8000 is already in use!")
            print("Killing existing process...")
            self.kill_port_mac(8000)
            time.sleep(2)
        
        # Change to backend directory
        os.chdir(self.backend_path)
        
        # Create startup script
        startup_script = '''#!/bin/bash
cd "$(dirname "$0")"

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install minimal requirements
echo "Installing requirements..."
pip install -q django djangorestframework django-cors-headers python-dotenv

# Set Django settings
export DJANGO_SETTINGS_MODULE=unibos_backend.settings.emergency

# Run migrations
python manage.py migrate --run-syncdb >/dev/null 2>&1

# Create superuser if needed
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@unibos.com', 'unibos123')
    print('Created default superuser (admin/unibos123)')
" 2>/dev/null

# Start server
echo "Backend server starting on http://localhost:8000"
exec python manage.py runserver 0.0.0.0:8000
'''
        
        # Write temporary startup script
        temp_script = self.backend_path / '.temp_start.sh'
        temp_script.write_text(startup_script)
        temp_script.chmod(0o755)
        
        # Start backend process
        process = subprocess.Popen(
            ['/bin/bash', str(temp_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        
        # Save PID
        self.backend_pid_file.write_text(str(process.pid))
        
        # Wait for startup
        print("Waiting for backend to start...")
        time.sleep(5)
        
        # Check if running
        if process.poll() is None:
            print("✅ Backend server started on http://localhost:8000")
            print("   - API: http://localhost:8000/api/")
            print("   - Admin: http://localhost:8000/admin/")
            return True
        else:
            print("❌ Backend server failed to start")
            stderr = process.stderr.read().decode('utf-8')
            if stderr:
                print(f"Error: {stderr}")
            return False
    
    def start_frontend(self):
        """Start the frontend server with improved error handling"""
        print("\n🎨 Starting Frontend Server...")
        
        # Check if already running
        if not self.check_port_mac(3000):
            print("⚠️  Port 3000 is already in use!")
            print("Killing existing process...")
            self.kill_port_mac(3000)
            time.sleep(2)
        
        # Change to frontend directory
        os.chdir(self.frontend_path)
        
        # Check if node_modules exists
        if not (self.frontend_path / 'node_modules').exists():
            print("📦 Installing frontend dependencies...")
            print("This may take a few minutes...")
            result = subprocess.run(
                ['npm', 'install', '--legacy-peer-deps'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("⚠️  npm install failed, trying with --force")
                subprocess.run(['npm', 'install', '--force'], check=False)
        
        # Create .env if not exists
        env_file = self.frontend_path / '.env'
        if not env_file.exists():
            env_file.write_text('''REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_VERSION=v312
''')
        
        # Start frontend process with better handling
        env = os.environ.copy()
        env['BROWSER'] = 'none'
        env['DISABLE_ESLINT_PLUGIN'] = 'true'
        env['CI'] = 'false'  # Disable CI mode to prevent build failures
        
        # Use nohup for better process management
        log_file = self.frontend_path / 'frontend.log'
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                ['npm', 'start'],
                stdout=log,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                env=env,
                start_new_session=True  # Detach from parent process
            )
        
        # Save PID
        self.frontend_pid_file.write_text(str(process.pid))
        
        # Wait for frontend to actually start
        print("⏳ Waiting for frontend to compile...")
        print("   (This may take up to 60 seconds on first start)")
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < 60:  # Increased timeout to 60 seconds
            check_count += 1
            
            # Check if port is in use
            if not self.check_port_mac(3000):
                # Port is in use, frontend started
                print("✅ Frontend is running on http://localhost:3000")
                return True
            
            # Check if process is still alive
            if process.poll() is not None:
                print("❌ Frontend process exited unexpectedly")
                # Try to read log file for errors
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        last_lines = f.readlines()[-10:]
                        if last_lines:
                            print("Last log lines:")
                            for line in last_lines:
                                print(f"  {line.strip()}")
                return False
            
            # Show progress dots
            if check_count % 5 == 0:
                print(f"   Still compiling... ({int(time.time() - start_time)}s)")
            
            time.sleep(2)
        
        # Check one more time
        if not self.check_port_mac(3000):
            print("✅ Frontend is running on http://localhost:3000")
            return True
        
        print("⚠️  Frontend is taking longer than expected to start")
        print("   Check the log file at: " + str(log_file))
        print("   The server may still be compiling in the background")
        
        # Process is still alive, so return True
        if process.poll() is None:
            return True
        
        return False
    
    def stop_backend(self):
        """Stop the backend server"""
        print("\n🛑 Stopping Backend Server...")
        
        # Try PID file first
        if self.backend_pid_file.exists():
            try:
                pid = int(self.backend_pid_file.read_text())
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                self.backend_pid_file.unlink()
                print("✅ Backend server stopped")
                return True
            except:
                pass
        
        # Kill by port
        if self.kill_port_mac(8000):
            print("✅ Backend server stopped")
            return True
        
        print("Backend server not running")
        return False
    
    def stop_frontend(self):
        """Stop the frontend server"""
        print("\n🛑 Stopping Frontend Server...")
        
        # Try PID file first
        if self.frontend_pid_file.exists():
            try:
                pid = int(self.frontend_pid_file.read_text())
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
                self.frontend_pid_file.unlink()
                print("✅ Frontend server stopped")
                return True
            except:
                pass
        
        # Kill by port
        if self.kill_port_mac(3000):
            print("✅ Frontend server stopped")
            return True
        
        print("Frontend server not running")
        return False
    
    def status(self):
        """Check status of both servers"""
        backend_running = not self.check_port_mac(8000)
        frontend_running = not self.check_port_mac(3000)
        
        print("\n=== 🖥️  UNIBOS Server Status ===")
        print(f"Backend:  {'🟢 Running' if backend_running else '🔴 Stopped'} (port 8000)")
        print(f"Frontend: {'🟢 Running' if frontend_running else '🔴 Stopped'} (port 3000)")
        
        if backend_running:
            print("\n📡 Backend URLs:")
            print("  - API: http://localhost:8000/api/")
            print("  - Admin: http://localhost:8000/admin/")
        
        if frontend_running:
            print("\n🌐 Frontend URL:")
            print("  - App: http://localhost:3000")
        
        return {'backend': backend_running, 'frontend': frontend_running}
    
    def start_all(self):
        """Start both servers"""
        print("\n🚀 Starting UNIBOS servers...")
        
        backend_ok = self.start_backend()
        if backend_ok:
            time.sleep(3)
            frontend_ok = self.start_frontend()
        else:
            frontend_ok = False
        
        print("\n" + "="*40)
        if backend_ok and frontend_ok:
            print("✅ All servers started successfully!")
        else:
            print("⚠️  Some servers failed to start")
        
        self.status()
        
        if backend_ok and frontend_ok:
            print("\n💡 Tips:")
            print("  - Use 'python3 src/simple_server_manager.py status' to check server status")
            print("  - Use 'python3 src/simple_server_manager.py stop' to stop all servers")
            print("  - Logs are being written to terminal where servers are running")
        
        return backend_ok and frontend_ok
    
    def stop_all(self):
        """Stop both servers"""
        print("\n🛑 Stopping UNIBOS servers...")
        self.stop_backend()
        self.stop_frontend()
        print("\n✅ All servers stopped")
        return True
    
    def restart_all(self):
        """Restart both servers with improved handling"""
        print("\n🔄 Restarting UNIBOS servers...")
        
        # First stop all servers
        print("\n🛑 Stopping servers...")
        self.stop_backend()
        self.stop_frontend()
        
        # Clear any lingering processes
        self.kill_port_mac(8000)
        self.kill_port_mac(3000)
        
        # Wait a bit longer for complete shutdown
        print("⏳ Waiting for complete shutdown...")
        time.sleep(3)
        
        # Start servers one by one
        print("\n🚀 Starting servers...")
        backend_ok = self.start_backend()
        
        if backend_ok:
            # Give backend time to fully initialize
            time.sleep(3)
            frontend_ok = self.start_frontend()
        else:
            frontend_ok = False
            print("❌ Backend failed to start, skipping frontend")
        
        # Show final status
        print("\n" + "="*40)
        if backend_ok and frontend_ok:
            print("✅ All servers restarted successfully!")
        elif backend_ok:
            print("⚠️  Backend restarted but frontend failed")
        else:
            print("❌ Restart failed")
        
        self.status()
        return backend_ok and frontend_ok

def main():
    if len(sys.argv) < 2:
        print("UNIBOS Simple Server Manager")
        print("\nUsage: python3 src/simple_server_manager.py [command]")
        print("\nCommands:")
        print("  start         - Start both backend and frontend servers")
        print("  stop          - Stop both servers")
        print("  restart       - Restart both servers")
        print("  status        - Check server status")
        print("  start-backend - Start only backend server")
        print("  start-frontend- Start only frontend server")
        print("  stop-backend  - Stop only backend server")
        print("  stop-frontend - Stop only frontend server")
        return
    
    manager = SimpleServerManager()
    command = sys.argv[1]
    
    commands = {
        'start': manager.start_all,
        'stop': manager.stop_all,
        'restart': manager.restart_all,
        'status': manager.status,
        'start-backend': manager.start_backend,
        'start-frontend': manager.start_frontend,
        'stop-backend': manager.stop_backend,
        'stop-frontend': manager.stop_frontend,
    }
    
    if command in commands:
        try:
            commands[command]()
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            print("Stopping servers...")
            manager.stop_all()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: " + ", ".join(commands.keys()))

if __name__ == "__main__":
    main()