#!/usr/bin/env python3
"""
Web Forge Server Integration - Provides server management for UNIBOS Web Forge interface
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from datetime import datetime

class WebForgeServerIntegration:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.server_manager_path = self.base_path / 'src' / 'simple_server_manager.py'
        
    def get_server_status(self):
        """Get status of both servers in JSON format"""
        try:
            # Check backend
            backend_result = subprocess.run(
                'lsof -i :8000 -sTCP:LISTEN -t',
                shell=True,
                capture_output=True,
                text=True
            )
            backend_running = len(backend_result.stdout.strip()) > 0
            
            # Check frontend
            frontend_result = subprocess.run(
                'lsof -i :3000 -sTCP:LISTEN -t',
                shell=True,
                capture_output=True,
                text=True
            )
            frontend_running = len(frontend_result.stdout.strip()) > 0
            
            return {
                "backend": {
                    "status": "running" if backend_running else "stopped",
                    "port": 8000,
                    "url": "http://localhost:8000" if backend_running else None,
                    "api_url": "http://localhost:8000/api/" if backend_running else None,
                    "admin_url": "http://localhost:8000/admin/" if backend_running else None
                },
                "frontend": {
                    "status": "running" if frontend_running else "stopped",
                    "port": 3000,
                    "url": "http://localhost:3000" if frontend_running else None
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def start_backend(self):
        """Start backend server"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.server_manager_path), 'start-backend'],
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def stop_backend(self):
        """Stop backend server"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.server_manager_path), 'stop-backend'],
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def restart_backend(self):
        """Restart backend server"""
        self.stop_backend()
        return self.start_backend()
    
    def start_frontend(self):
        """Start frontend server"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.server_manager_path), 'start-frontend'],
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def stop_frontend(self):
        """Stop frontend server"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.server_manager_path), 'stop-frontend'],
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def restart_frontend(self):
        """Restart frontend server"""
        self.stop_frontend()
        return self.start_frontend()
    
    def start_all(self):
        """Start all servers"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.server_manager_path), 'start'],
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def stop_all(self):
        """Stop all servers"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.server_manager_path), 'stop'],
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def restart_all(self):
        """Restart all servers"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.server_manager_path), 'restart'],
                capture_output=True,
                text=True
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """Command line interface for testing"""
    if len(sys.argv) < 2:
        print("Web Forge Server Integration")
        print("\nUsage: python3 src/webforge_server_integration.py [command]")
        print("\nCommands:")
        print("  status        - Get server status (JSON)")
        print("  start         - Start all servers")
        print("  stop          - Stop all servers")
        print("  restart       - Restart all servers")
        print("  start-backend - Start backend server")
        print("  stop-backend  - Stop backend server")
        print("  start-frontend- Start frontend server")
        print("  stop-frontend - Stop frontend server")
        return
    
    integration = WebForgeServerIntegration()
    command = sys.argv[1]
    
    # Map commands to methods
    commands = {
        'status': lambda: print(json.dumps(integration.get_server_status(), indent=2)),
        'start': lambda: print(json.dumps(integration.start_all(), indent=2)),
        'stop': lambda: print(json.dumps(integration.stop_all(), indent=2)),
        'restart': lambda: print(json.dumps(integration.restart_all(), indent=2)),
        'start-backend': lambda: print(json.dumps(integration.start_backend(), indent=2)),
        'stop-backend': lambda: print(json.dumps(integration.stop_backend(), indent=2)),
        'restart-backend': lambda: print(json.dumps(integration.restart_backend(), indent=2)),
        'start-frontend': lambda: print(json.dumps(integration.start_frontend(), indent=2)),
        'stop-frontend': lambda: print(json.dumps(integration.stop_frontend(), indent=2)),
        'restart-frontend': lambda: print(json.dumps(integration.restart_frontend(), indent=2)),
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")

# This can be imported by web_forge.py for integration
if __name__ == "__main__":
    main()