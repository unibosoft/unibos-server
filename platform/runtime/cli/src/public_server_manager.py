#!/usr/bin/env python3
"""
UNIBOS Public Server Manager
Centralized server deployment and management for Ubuntu/Oracle VM
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from datetime import datetime
import shutil
import socket

# Optional imports with fallback
try:
    import psycopg2
    from psycopg2 import sql
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("⚠️ Warning: psycopg2 not installed. Database features will be limited.")
    print("  To install: pip install psycopg2-binary")

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    print("⚠️ Warning: paramiko not installed. SSH features will be limited.")
    print("  To install: pip install paramiko")


class PublicServerManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.backend_path = self.base_path / "backend"
        self.config_file = self.base_path / "server_config.json"
        self.config = self.load_config()
        
    def load_config(self):
        """Load server configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "server": {
                "host": "rocksteady.local",
                "ip": "",
                "ssh_user": "ubuntu",
                "ssh_port": 22,
                "deploy_path": "/opt/unibos"
            },
            "database": {
                "host": "rocksteady.local",
                "port": 5432,
                "name": "unibos_central",
                "user": "unibos_admin",
                "password": "",
                "pool_size": 20
            },
            "redis": {
                "host": "rocksteady.local",
                "port": 6379,
                "db": 0
            },
            "nginx": {
                "domain": "unibos.local",
                "ssl_enabled": False,
                "port": 80
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def display_menu(self):
        """Display public server management menu"""
        os.system('clear' if platform.system() != 'Windows' else 'cls')
        
        print("\n" + "="*60)
        print("🌐 PUBLIC SERVER MANAGEMENT")
        print("="*60)
        print(f"server: {self.config['server']['host']}")
        print(f"database: {self.config['database']['host']}:{self.config['database']['port']}")
        print("="*60)
        
        options = [
            "1. server configuration",
            "2. deploy to server",
            "3. database setup",
            "4. sync data",
            "5. server status",
            "6. backup management",
            "7. ssl certificate",
            "8. logs viewer",
            "9. restart services",
            "0. back"
        ]
        
        for option in options:
            print(f"  {option}")
        
        print("="*60)
        return input("select option: ").strip()
    
    def configure_server(self):
        """Configure server settings"""
        print("\n🔧 server configuration")
        print("-" * 40)
        
        print("\ncurrent settings:")
        print(f"  host: {self.config['server']['host']}")
        print(f"  ip: {self.config['server'].get('ip', 'not set')}")
        print(f"  ssh user: {self.config['server']['ssh_user']}")
        print(f"  deploy path: {self.config['server']['deploy_path']}")
        
        if input("\nupdate settings? (y/n): ").lower() == 'y':
            self.config['server']['host'] = input(f"server hostname [{self.config['server']['host']}]: ") or self.config['server']['host']
            self.config['server']['ip'] = input(f"server ip [{self.config['server'].get('ip', '')}]: ") or self.config['server'].get('ip', '')
            self.config['server']['ssh_user'] = input(f"ssh user [{self.config['server']['ssh_user']}]: ") or self.config['server']['ssh_user']
            self.config['server']['deploy_path'] = input(f"deploy path [{self.config['server']['deploy_path']}]: ") or self.config['server']['deploy_path']
            
            # Database configuration
            print("\n📊 database configuration:")
            self.config['database']['host'] = input(f"db host [{self.config['database']['host']}]: ") or self.config['database']['host']
            self.config['database']['port'] = int(input(f"db port [{self.config['database']['port']}]: ") or self.config['database']['port'])
            self.config['database']['name'] = input(f"db name [{self.config['database']['name']}]: ") or self.config['database']['name']
            self.config['database']['user'] = input(f"db user [{self.config['database']['user']}]: ") or self.config['database']['user']
            
            db_pass = input("db password (leave empty to keep current): ")
            if db_pass:
                self.config['database']['password'] = db_pass
            
            self.save_config()
            print("\n✅ configuration saved!")
    
    def deploy_to_server(self):
        """Deploy UNIBOS to public server"""
        if not PARAMIKO_AVAILABLE:
            print("❌ paramiko is required for deployment")
            print("   Install with: pip install paramiko")
            return
            
        print("\n🚀 deploying to public server")
        print("-" * 40)
        
        # Create deployment package
        print("📦 creating deployment package...")
        deploy_script = self.create_deploy_script()
        
        # Connect via SSH
        print(f"🔗 connecting to {self.config['server']['host']}...")
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=self.config['server'].get('ip') or self.config['server']['host'],
                port=self.config['server'].get('ssh_port', 22),
                username=self.config['server']['ssh_user'],
                password=input("ssh password: ")
            )
            
            # Upload deployment script
            sftp = ssh.open_sftp()
            sftp.put(str(deploy_script), '/tmp/deploy_unibos.sh')
            sftp.close()
            
            # Execute deployment
            print("⚙️ executing deployment...")
            stdin, stdout, stderr = ssh.exec_command('bash /tmp/deploy_unibos.sh')
            
            for line in stdout:
                print(f"  {line.strip()}")
            
            errors = stderr.read().decode()
            if errors:
                print(f"⚠️ warnings: {errors}")
            
            ssh.close()
            print("\n✅ deployment completed!")
            
        except Exception as e:
            print(f"❌ deployment failed: {e}")
    
    def create_deploy_script(self):
        """Create deployment script for Ubuntu"""
        script_path = self.base_path / "deploy_ubuntu.sh"
        
        script_content = f"""#!/bin/bash
# UNIBOS Ubuntu Deployment Script
# Generated: {datetime.now().isoformat()}

set -e

echo "🚀 Starting UNIBOS deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
echo "🔧 Installing dependencies..."
sudo apt-get install -y \\
    python3.11 python3.11-venv python3-pip \\
    postgresql postgresql-contrib postgis \\
    redis-server nginx git \\
    build-essential libpq-dev \\
    supervisor ufw

# Setup PostgreSQL
echo "🗄️ Setting up PostgreSQL..."
sudo -u postgres psql << EOF
CREATE USER {self.config['database']['user']} WITH PASSWORD '{self.config['database']['password']}';
CREATE DATABASE {self.config['database']['name']} OWNER {self.config['database']['user']};
GRANT ALL PRIVILEGES ON DATABASE {self.config['database']['name']} TO {self.config['database']['user']};
\\c {self.config['database']['name']};
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;
EOF

# Configure PostgreSQL for remote access
echo "🔌 Configuring PostgreSQL for remote connections..."
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/*/main/postgresql.conf
echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
sudo systemctl restart postgresql

# Setup deployment directory
echo "📁 Setting up deployment directory..."
sudo mkdir -p {self.config['server']['deploy_path']}
sudo chown $USER:$USER {self.config['server']['deploy_path']}

# Clone repository (or copy files)
cd {self.config['server']['deploy_path']}
if [ -d ".git" ]; then
    git pull origin main
else
    # Copy files from local deployment package
    echo "📋 Copying application files..."
fi

# Setup Python virtual environment
echo "🐍 Setting up Python environment..."
cd {self.config['server']['deploy_path']}/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment variables
echo "⚙️ Configuring environment..."
cat > .env << EOL
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS={self.config['nginx']['domain']},{self.config['server']['host']},{self.config['server'].get('ip', '')}
DATABASE_URL=postgresql://{self.config['database']['user']}:{self.config['database']['password']}@{self.config['database']['host']}:{self.config['database']['port']}/{self.config['database']['name']}
REDIS_URL=redis://{self.config['redis']['host']}:{self.config['redis']['port']}/{self.config['redis']['db']}
CORS_ALLOWED_ORIGINS=http://{self.config['nginx']['domain']},https://{self.config['nginx']['domain']}
EOL

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser
echo "👤 Creating superuser..."
python manage.py shell << PYTHON
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@unibos.local', 'unibos2025')
    print("Superuser created: admin / unibos2025")
PYTHON

# Setup Gunicorn with Supervisor
echo "🦄 Setting up Gunicorn..."
sudo tee /etc/supervisor/conf.d/unibos.conf > /dev/null << EOL
[program:unibos]
command={self.config['server']['deploy_path']}/backend/venv/bin/gunicorn \\
    unibos_backend.wsgi:application \\
    --bind 127.0.0.1:8000 \\
    --workers 4 \\
    --timeout 120
directory={self.config['server']['deploy_path']}/backend
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/unibos/gunicorn.log
environment=PATH="{self.config['server']['deploy_path']}/backend/venv/bin"
EOL

# Setup Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/unibos > /dev/null << EOL
server {{
    listen 80;
    server_name {self.config['nginx']['domain']} {self.config['server']['host']} {self.config['server'].get('ip', '')};
    
    client_max_body_size 100M;
    
    location /static/ {{
        alias {self.config['server']['deploy_path']}/backend/static/;
    }}
    
    location /media/ {{
        alias {self.config['server']['deploy_path']}/backend/media/;
    }}
    
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\$http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
}}
EOL

sudo ln -sf /etc/nginx/sites-available/unibos /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5432/tcp  # PostgreSQL
sudo ufw allow 6379/tcp  # Redis
sudo ufw --force enable

# Create log directory
sudo mkdir -p /var/log/unibos
sudo chown $USER:$USER /var/log/unibos

# Start services
echo "▶️ Starting services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start unibos

echo "✅ Deployment completed!"
echo "🌐 Access UNIBOS at: http://{self.config['nginx']['domain']}"
echo "👤 Admin credentials: admin / unibos2025"
"""
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        script_path.chmod(0o755)
        return script_path
    
    def setup_database(self):
        """Setup centralized database"""
        if not PSYCOPG2_AVAILABLE:
            print("❌ psycopg2 is required for database setup")
            print("   Install with: pip install psycopg2-binary")
            return
            
        print("\n🗄️ database setup")
        print("-" * 40)
        
        print("creating centralized database structure...")
        
        try:
            # Connect to PostgreSQL
            conn = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database='postgres',
                user=self.config['database']['user'],
                password=self.config['database']['password']
            )
            conn.autocommit = True
            cur = conn.cursor()
            
            # Create database if not exists
            cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [self.config['database']['name']])
            if not cur.fetchone():
                cur.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(self.config['database']['name'])
                ))
                print(f"✅ database '{self.config['database']['name']}' created")
            
            cur.close()
            conn.close()
            
            # Connect to the new database
            conn = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database=self.config['database']['name'],
                user=self.config['database']['user'],
                password=self.config['database']['password']
            )
            cur = conn.cursor()
            
            # Enable extensions
            extensions = ['postgis', 'pg_trgm', 'btree_gin', 'uuid-ossp']
            for ext in extensions:
                cur.execute(f"CREATE EXTENSION IF NOT EXISTS {ext}")
                print(f"  ✓ extension '{ext}' enabled")
            
            conn.commit()
            cur.close()
            conn.close()
            
            print("\n✅ database setup completed!")
            
        except Exception as e:
            print(f"❌ database setup failed: {e}")
    
    def check_server_status(self):
        """Check server and services status"""
        print("\n📊 server status")
        print("-" * 40)
        
        # Check server connectivity
        print("🔍 checking connectivity...")
        
        # Ping test
        hostname = self.config['server'].get('ip') or self.config['server']['host']
        response = os.system(f"ping -c 1 {hostname} > /dev/null 2>&1")
        
        if response == 0:
            print(f"  ✅ server {hostname} is reachable")
        else:
            print(f"  ❌ server {hostname} is not reachable")
            return
        
        if not PARAMIKO_AVAILABLE:
            print("⚠️  SSH status check requires paramiko")
            return
            
        # Check services via SSH
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=hostname,
                port=self.config['server'].get('ssh_port', 22),
                username=self.config['server']['ssh_user'],
                password=input("ssh password: ")
            )
            
            # Check services
            services = [
                ('nginx', 'systemctl is-active nginx'),
                ('postgresql', 'systemctl is-active postgresql'),
                ('redis', 'systemctl is-active redis-server'),
                ('gunicorn', 'supervisorctl status unibos | grep RUNNING')
            ]
            
            print("\n📋 service status:")
            for service_name, command in services:
                stdin, stdout, stderr = ssh.exec_command(command)
                status = stdout.read().decode().strip()
                
                if 'active' in status or 'RUNNING' in status:
                    print(f"  ✅ {service_name}: running")
                else:
                    print(f"  ❌ {service_name}: not running")
            
            # Check disk usage
            stdin, stdout, stderr = ssh.exec_command("df -h /")
            disk_info = stdout.read().decode().strip().split('\n')[1].split()
            print(f"\n💾 disk usage: {disk_info[2]}/{disk_info[1]} ({disk_info[4]} used)")
            
            # Check memory
            stdin, stdout, stderr = ssh.exec_command("free -h | grep Mem")
            mem_info = stdout.read().decode().strip().split()
            print(f"🧠 memory: {mem_info[2]}/{mem_info[1]} used")
            
            ssh.close()
            
        except Exception as e:
            print(f"❌ status check failed: {e}")
    
    def sync_data(self):
        """Sync data between local and remote"""
        print("\n🔄 data synchronization")
        print("-" * 40)
        
        options = [
            "1. push local data to server",
            "2. pull server data to local",
            "3. bidirectional sync",
            "0. back"
        ]
        
        for opt in options:
            print(f"  {opt}")
        
        choice = input("\nselect option: ").strip()
        
        if choice == '1':
            self.push_data()
        elif choice == '2':
            self.pull_data()
        elif choice == '3':
            self.bidirectional_sync()
    
    def push_data(self):
        """Push local data to server"""
        print("\n⬆️ pushing data to server...")
        
        # Create backup first
        backup_file = self.base_path / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        # Dump local database
        subprocess.run([
            'pg_dump',
            '-h', 'localhost',
            '-U', 'unibos_user',
            '-d', 'unibos_db',
            '-f', str(backup_file),
            '--no-owner',
            '--no-privileges'
        ])
        
        print(f"  ✓ local backup created: {backup_file.name}")
        
        # Transfer and restore on server
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            hostname = self.config['server'].get('ip') or self.config['server']['host']
            ssh.connect(
                hostname=hostname,
                port=self.config['server'].get('ssh_port', 22),
                username=self.config['server']['ssh_user'],
                password=input("ssh password: ")
            )
            
            # Upload backup
            sftp = ssh.open_sftp()
            remote_path = f"/tmp/{backup_file.name}"
            sftp.put(str(backup_file), remote_path)
            sftp.close()
            
            print(f"  ✓ backup uploaded to server")
            
            # Restore on server
            restore_cmd = f"""
                PGPASSWORD='{self.config['database']['password']}' psql \
                -h {self.config['database']['host']} \
                -U {self.config['database']['user']} \
                -d {self.config['database']['name']} \
                < {remote_path}
            """
            
            stdin, stdout, stderr = ssh.exec_command(restore_cmd)
            errors = stderr.read().decode()
            
            if errors:
                print(f"  ⚠️ restore warnings: {errors[:200]}")
            else:
                print(f"  ✓ data restored on server")
            
            ssh.close()
            print("\n✅ data push completed!")
            
        except Exception as e:
            print(f"❌ data push failed: {e}")
    
    def run(self):
        """Run public server manager"""
        while True:
            choice = self.display_menu()
            
            if choice == '1':
                self.configure_server()
            elif choice == '2':
                self.deploy_to_server()
            elif choice == '3':
                self.setup_database()
            elif choice == '4':
                self.sync_data()
            elif choice == '5':
                self.check_server_status()
            elif choice == '6':
                print("🔧 backup management - coming soon")
            elif choice == '7':
                print("🔒 ssl certificate - coming soon")
            elif choice == '8':
                print("📋 logs viewer - coming soon")
            elif choice == '9':
                print("🔄 restart services - coming soon")
            elif choice == '0':
                break
            else:
                print("❌ invalid option")
            
            if choice != '0':
                input("\npress enter to continue...")


if __name__ == "__main__":
    manager = PublicServerManager()
    manager.run()