#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Forge Launch Script
Handles starting both backend and frontend servers
"""

import os
import sys
import subprocess
import time
import signal
import socket
from pathlib import Path
from typing import List, Optional

# Import Colors from main.py
try:
    from main import Colors
except ImportError:
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


class WebForgeServer:
    """Manages Web Forge server processes"""
    
    def __init__(self):
        self.base_path = Path('/Users/berkhatirli/Desktop/unibos')
        self.backend_path = self.base_path / 'backend'
        self.frontend_path = self.base_path / 'frontend'
        self.processes: List[subprocess.Popen] = []
        
    def check_port(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result != 0  # True if port is available
        except:
            return False
    
    def start_backend(self) -> Optional[subprocess.Popen]:
        """Start Django backend server"""
        print(f"{Colors.CYAN}Starting backend server...{Colors.RESET}")
        
        if not self.check_port(8000):
            print(f"{Colors.YELLOW}⚠ Port 8000 is already in use{Colors.RESET}")
            return None
        
        # Activate virtual environment and run Django with simple settings
        activate_cmd = 'source venv/bin/activate' if sys.platform != 'win32' else 'venv\\Scripts\\activate'
        server_cmd = f"{activate_cmd} && DJANGO_SETTINGS_MODULE=unibos_backend.settings.simple python manage.py runserver 0.0.0.0:8000"
        
        try:
            process = subprocess.Popen(
                server_cmd,
                shell=True,
                cwd=self.backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if sys.platform != 'win32' else None
            )
            
            # Wait a moment to check if it started successfully
            time.sleep(2)
            
            if process.poll() is None:
                print(f"{Colors.GREEN}✓ Backend server started on http://localhost:8000{Colors.RESET}")
                return process
            else:
                stderr = process.stderr.read().decode() if process.stderr else ""
                print(f"{Colors.RED}✗ Backend server failed to start{Colors.RESET}")
                if stderr:
                    print(f"{Colors.DIM}Error: {stderr[:200]}...{Colors.RESET}")
                return None
                
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to start backend: {e}{Colors.RESET}")
            return None
    
    def start_frontend(self) -> Optional[subprocess.Popen]:
        """Start React frontend server"""
        print(f"{Colors.CYAN}Starting frontend server...{Colors.RESET}")
        
        if not self.check_port(3000):
            print(f"{Colors.YELLOW}⚠ Port 3000 is already in use{Colors.RESET}")
            return None
        
        # Check if node_modules exists
        if not (self.frontend_path / 'node_modules').exists():
            print(f"{Colors.YELLOW}⚠ Frontend dependencies not installed{Colors.RESET}")
            print(f"{Colors.YELLOW}  Run: cd frontend && npm install{Colors.RESET}")
            return None
        
        try:
            # Set environment variable to avoid opening browser automatically
            env = os.environ.copy()
            env['BROWSER'] = 'none'
            
            process = subprocess.Popen(
                ['npm', 'start'],
                cwd=self.frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                preexec_fn=os.setsid if sys.platform != 'win32' else None
            )
            
            # Wait a moment to check if it started successfully
            time.sleep(3)
            
            if process.poll() is None:
                print(f"{Colors.GREEN}✓ Frontend server started on http://localhost:3000{Colors.RESET}")
                return process
            else:
                stderr = process.stderr.read().decode() if process.stderr else ""
                print(f"{Colors.RED}✗ Frontend server failed to start{Colors.RESET}")
                if stderr:
                    print(f"{Colors.DIM}Error: {stderr[:200]}...{Colors.RESET}")
                return None
                
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to start frontend: {e}{Colors.RESET}")
            return None
    
    def start_servers(self) -> bool:
        """Start both backend and frontend servers"""
        print(f"\n{Colors.BOLD}🔥 Starting Web Forge servers...{Colors.RESET}\n")
        
        # Start backend
        backend_process = self.start_backend()
        if backend_process:
            self.processes.append(backend_process)
        else:
            print(f"{Colors.RED}Failed to start backend server{Colors.RESET}")
            return False
        
        print()  # Empty line for spacing
        
        # Start frontend
        frontend_process = self.start_frontend()
        if frontend_process:
            self.processes.append(frontend_process)
        else:
            print(f"{Colors.YELLOW}Frontend server not started{Colors.RESET}")
            # Backend can run without frontend
        
        print(f"\n{Colors.GREEN}{'='*50}{Colors.RESET}")
        print(f"{Colors.GREEN}Web Forge is running!{Colors.RESET}")
        print(f"{Colors.CYAN}Backend:  http://localhost:8000{Colors.RESET}")
        print(f"{Colors.CYAN}Frontend: http://localhost:3000{Colors.RESET}")
        print(f"{Colors.GREEN}{'='*50}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Press Ctrl+C to stop all servers{Colors.RESET}\n")
        
        return True
    
    def stop_servers(self):
        """Stop all running servers"""
        print(f"\n{Colors.YELLOW}Stopping servers...{Colors.RESET}")
        
        for process in self.processes:
            try:
                if sys.platform != 'win32':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
            except:
                try:
                    process.kill()
                except:
                    pass
        
        # Wait for processes to terminate
        for process in self.processes:
            try:
                process.wait(timeout=5)
            except:
                pass
        
        print(f"{Colors.GREEN}✓ All servers stopped{Colors.RESET}")
    
    def run(self):
        """Main run loop"""
        if not self.start_servers():
            return
        
        try:
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
                # Check if processes are still running
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        print(f"{Colors.YELLOW}⚠ Server process {i+1} has stopped{Colors.RESET}")
                        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Interrupt received{Colors.RESET}")
        finally:
            self.stop_servers()


def main():
    """Main entry point"""
    # Ensure UTF-8 encoding
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    
    server = WebForgeServer()
    server.run()


if __name__ == "__main__":
    main()