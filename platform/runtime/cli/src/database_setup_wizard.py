#!/usr/bin/env python3
"""
🧙 UNIBOS Database Setup Wizard
PostgreSQL ve gerekli paketleri otomatik kuran sihirbaz
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

# Renkler
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'

class DatabaseSetupWizard:
    """Veritabanı kurulum sihirbazı"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.has_postgres = self.check_postgresql()
        self.has_pip_packages = self.check_pip_packages()
        
    def check_postgresql(self) -> bool:
        """PostgreSQL kurulu mu kontrol et"""
        try:
            result = subprocess.run(['psql', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def check_postgresql_running(self) -> bool:
        """PostgreSQL servisi çalışıyor mu kontrol et"""
        try:
            # macOS'ta önce mevcut kullanıcı ile dene
            if self.system == "darwin":
                # Önce pg_isready ile kontrol et (varsa)
                try:
                    result = subprocess.run(['pg_isready'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return True
                except FileNotFoundError:
                    # pg_isready yoksa devam et
                    pass
                    
                # Alternatif: mevcut kullanıcı ile dene
                import getpass
                current_user = getpass.getuser()
                result = subprocess.run(['psql', '-U', current_user, '-d', 'postgres', '-c', 'SELECT 1;'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True
                    
            # Diğer sistemler veya macOS'ta başarısız olursa postgres kullanıcısı ile dene
            result = subprocess.run(['psql', '-U', 'postgres', '-c', 'SELECT 1;'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def check_pip_packages(self) -> bool:
        """Gerekli Python paketleri kurulu mu"""
        try:
            import psycopg2
            import sqlalchemy
            import alembic
            return True
        except ImportError:
            return False
    
    def run_wizard(self):
        """Kurulum sihirbazını çalıştır"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🧙 UNIBOS Database Setup Wizard{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")
        
        # Durum özeti
        print(f"{Colors.YELLOW}📊 Sistem Durumu:{Colors.RESET}")
        print(f"İşletim Sistemi: {self.system}")
        print(f"PostgreSQL: {'✅ Kurulu' if self.has_postgres else '❌ Kurulu değil'}")
        if self.has_postgres:
            is_running = self.check_postgresql_running()
            print(f"PostgreSQL Servisi: {'✅ Çalışıyor' if is_running else '❌ Çalışmıyor'}")
        print(f"Python Paketleri: {'✅ Kurulu' if self.has_pip_packages else '❌ Eksik'}\n")
        
        # Seçenekler
        print(f"{Colors.YELLOW}Seçenekler:{Colors.RESET}")
        print(f"1. 🚀 Tam kurulum (PostgreSQL + Python paketleri)")
        print(f"2. 📦 Sadece Python paketlerini kur")
        print(f"3. 🗄️ Sadece PostgreSQL kur")
        print(f"4. 🔧 Veritabanı oluştur (PostgreSQL zaten kurulu)")
        print(f"5. ▶️  PostgreSQL servisini başlat")
        print(f"6. 👤 PostgreSQL kullanıcısı oluştur (manuel)")
        print(f"7. 📋 Kurulum talimatlarını göster")
        print(f"8. 🏃 SQLite ile devam et (kurulum yapma)")
        print(f"q. Çıkış\n")
        
        choice = input(f"{Colors.BLUE}Seçiminiz: {Colors.RESET}")
        
        if choice == '1':
            self.full_installation()
        elif choice == '2':
            self.install_python_packages()
        elif choice == '3':
            self.install_postgresql()
        elif choice == '4':
            self.create_database()
        elif choice == '5':
            self.start_postgresql_service()
        elif choice == '6':
            self.create_postgresql_user()
        elif choice == '7':
            self.show_instructions()
        elif choice == '8':
            print(f"\n{Colors.GREEN}✅ SQLite ile devam ediliyor...{Colors.RESET}")
            return True
        elif choice == 'q':
            return False
        else:
            print(f"\n{Colors.RED}❌ Geçersiz seçim!{Colors.RESET}")
            time.sleep(2)
            return self.run_wizard()
        
        return True
    
    def full_installation(self):
        """Tam kurulum"""
        print(f"\n{Colors.CYAN}🚀 Tam kurulum başlatılıyor...{Colors.RESET}\n")
        
        # Önce PostgreSQL
        if not self.has_postgres:
            if not self.install_postgresql():
                return
        
        # Sonra Python paketleri
        if not self.has_pip_packages:
            self.install_python_packages()
        
        # Veritabanı oluştur
        self.create_database()
        
        # Veritabanı tablolarını oluştur
        print(f"\n{Colors.CYAN}🔨 Veritabanı tabloları oluşturuluyor...{Colors.RESET}")
        try:
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from database.models import create_tables
            create_tables()
            print(f"{Colors.GREEN}✅ Veritabanı tabloları oluşturuldu!{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Tablolar oluşturulamadı: {e}{Colors.RESET}")
        
        print(f"\n{Colors.GREEN}✅ Kurulum tamamlandı!{Colors.RESET}")
        print(f"{Colors.YELLOW}Program yeniden başlatılıyor...{Colors.RESET}")
        time.sleep(3)
        
        # Programı yeniden başlat
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    def install_python_packages(self):
        """Python paketlerini kur"""
        print(f"\n{Colors.CYAN}📦 Python paketleri kuruluyor...{Colors.RESET}")
        
        packages = ['psycopg2-binary', 'sqlalchemy', 'alembic']
        
        for package in packages:
            print(f"\nKuruluyor: {package}")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ {package} kuruldu{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌ {package} kurulumu başarısız:{Colors.RESET}")
                print(result.stderr)
        
        # requirements.txt güncelle
        self.update_requirements()
        
        # Veritabanı tabloları oluştur
        print(f"\n{Colors.CYAN}🔨 Veritabanı tabloları oluşturuluyor...{Colors.RESET}")
        try:
            # Database modüllerini import et
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from database.models import create_tables
            create_tables()
            print(f"{Colors.GREEN}✅ Veritabanı tabloları oluşturuldu!{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Tablolar zaten mevcut veya hata: {e}{Colors.RESET}")
        
        return True
    
    def install_postgresql(self):
        """PostgreSQL kur"""
        print(f"\n{Colors.CYAN}🗄️ PostgreSQL kuruluyor...{Colors.RESET}")
        
        if self.system == "darwin":  # macOS
            return self.install_postgresql_macos()
        elif self.system == "linux":
            return self.install_postgresql_linux()
        elif self.system == "windows":
            return self.install_postgresql_windows()
        else:
            print(f"{Colors.RED}❌ Desteklenmeyen işletim sistemi!{Colors.RESET}")
            return False
    
    def install_postgresql_macos(self):
        """macOS için PostgreSQL kurulumu"""
        # Homebrew kontrolü
        brew_check = subprocess.run(['which', 'brew'], 
                                  capture_output=True, text=True)
        
        if brew_check.returncode != 0:
            print(f"{Colors.YELLOW}Homebrew bulunamadı!{Colors.RESET}")
            print("Homebrew kurmak için:")
            print('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
            
            install = input("\nHomebrew'i şimdi kurmak ister misiniz? (e/h): ")
            if install.lower() == 'e':
                os.system('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
            else:
                return False
        
        # PostgreSQL kurulumu
        print("\n📦 PostgreSQL kuruluyor...")
        result = subprocess.run(['brew', 'install', 'postgresql@15'],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✅ PostgreSQL kuruldu!{Colors.RESET}")
            
            # Servisi başlat
            subprocess.run(['brew', 'services', 'start', 'postgresql@15'])
            print(f"{Colors.GREEN}✅ PostgreSQL servisi başlatıldı!{Colors.RESET}")
            
            return True
        else:
            print(f"{Colors.RED}❌ Kurulum başarısız:{Colors.RESET}")
            print(result.stderr)
            return False
    
    def install_postgresql_linux(self):
        """Linux için PostgreSQL kurulumu"""
        # Distro tespiti
        if os.path.exists("/etc/debian_version"):
            # Debian/Ubuntu
            print("Debian/Ubuntu tespit edildi.")
            
            cmds = [
                ['sudo', 'apt', 'update'],
                ['sudo', 'apt', 'install', '-y', 'postgresql', 'postgresql-contrib']
            ]
            
            for cmd in cmds:
                print(f"\nÇalıştırılıyor: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"{Colors.RED}❌ Hata:{Colors.RESET}")
                    print(result.stderr)
                    return False
            
            # Servisi başlat
            subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'])
            subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'])
            
            print(f"{Colors.GREEN}✅ PostgreSQL kuruldu ve başlatıldı!{Colors.RESET}")
            return True
            
        elif os.path.exists("/etc/redhat-release"):
            # RedHat/CentOS/Fedora
            print("RedHat/CentOS/Fedora tespit edildi.")
            
            cmds = [
                ['sudo', 'dnf', 'install', '-y', 'postgresql', 'postgresql-server']
            ]
            
            for cmd in cmds:
                print(f"\nÇalıştırılıyor: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"{Colors.RED}❌ Hata:{Colors.RESET}")
                    print(result.stderr)
                    return False
            
            # DB initialize
            subprocess.run(['sudo', 'postgresql-setup', '--initdb'])
            
            # Servisi başlat
            subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'])
            subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'])
            
            print(f"{Colors.GREEN}✅ PostgreSQL kuruldu ve başlatıldı!{Colors.RESET}")
            return True
        
        else:
            print(f"{Colors.YELLOW}Linux dağıtımı tespit edilemedi.{Colors.RESET}")
            print("Manuel kurulum için: https://www.postgresql.org/download/linux/")
            return False
    
    def install_postgresql_windows(self):
        """Windows için PostgreSQL kurulumu"""
        print(f"{Colors.YELLOW}Windows için otomatik kurulum:{Colors.RESET}")
        print("\n1. PostgreSQL installer'ı indiriliyor...")
        
        # Chocolatey kontrolü
        choco_check = subprocess.run(['where', 'choco'], 
                                   capture_output=True, text=True, shell=True)
        
        if choco_check.returncode == 0:
            print("Chocolatey bulundu!")
            install = input("\nPostgreSQL'i Chocolatey ile kurmak ister misiniz? (e/h): ")
            
            if install.lower() == 'e':
                result = subprocess.run(['choco', 'install', 'postgresql', '-y'],
                                      capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    print(f"{Colors.GREEN}✅ PostgreSQL kuruldu!{Colors.RESET}")
                    return True
                else:
                    print(f"{Colors.RED}❌ Kurulum başarısız:{Colors.RESET}")
                    print(result.stderr)
        
        # Manuel kurulum talimatları
        print(f"\n{Colors.YELLOW}Manuel kurulum adımları:{Colors.RESET}")
        print("1. https://www.postgresql.org/download/windows/ adresine gidin")
        print("2. 'Download the installer' butonuna tıklayın")
        print("3. Windows x86-64 için en son sürümü indirin")
        print("4. İndirilen .exe dosyasını çalıştırın")
        print("5. Kurulum sırasında:")
        print("   - Password: unibos123")
        print("   - Port: 5432 (varsayılan)")
        print("6. Kurulum tamamlandıktan sonra bu wizard'ı tekrar çalıştırın")
        
        input(f"\n{Colors.CYAN}Devam etmek için Enter'a basın...{Colors.RESET}")
        return False
    
    def create_database(self):
        """Veritabanı ve kullanıcı oluştur"""
        print(f"\n{Colors.CYAN}🗄️ Veritabanı oluşturuluyor...{Colors.RESET}")
        
        # PostgreSQL servisinin çalıştığından emin ol
        if self.system == "darwin":  # macOS
            print(f"\n{Colors.YELLOW}PostgreSQL servisi kontrol ediliyor...{Colors.RESET}")
            # Önce servisi başlatmayı dene
            start_result = subprocess.run(['brew', 'services', 'start', 'postgresql@15'], 
                                        capture_output=True, text=True)
            if start_result.returncode != 0:
                # postgresql@15 yoksa postgresql dene
                subprocess.run(['brew', 'services', 'start', 'postgresql'], 
                             capture_output=True, text=True)
            
            # Biraz bekle
            import time
            time.sleep(2)
            print(f"{Colors.GREEN}✅ PostgreSQL servisi başlatıldı{Colors.RESET}")
        
        elif self.system == "linux":
            print(f"\n{Colors.YELLOW}PostgreSQL servisi kontrol ediliyor...{Colors.RESET}")
            subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], 
                         capture_output=True, text=True)
            time.sleep(2)
        
        # macOS için özel kontrol
        if self.system == "darwin":
            # Önce mevcut kullanıcının veritabanı erişimi var mı kontrol et
            import getpass
            current_user = getpass.getuser()
            
            # Kullanıcının PostgreSQL'de var olup olmadığını kontrol et
            check_user = subprocess.run(['psql', '-U', current_user, '-d', 'postgres', '-c', 'SELECT 1;'],
                                      capture_output=True, text=True)
            
            if check_user.returncode != 0:
                print(f"\n{Colors.YELLOW}⚠️  PostgreSQL kullanıcısı '{current_user}' bulunamadı.{Colors.RESET}")
                print(f"{Colors.CYAN}Kullanıcı oluşturuluyor...{Colors.RESET}")
                
                # createuser komutunu postgres kullanıcısı ile çalıştır
                create_user_cmd = f"sudo -u postgres createuser -s {current_user}"
                print(f"Çalıştırılıyor: {create_user_cmd}")
                os.system(create_user_cmd)
                
                # Kullanıcı için veritabanı oluştur
                create_db_cmd = f"sudo -u postgres createdb {current_user}"
                print(f"Çalıştırılıyor: {create_db_cmd}")
                os.system(create_db_cmd)
        
        if self.system == "windows":
            # Windows için createdb komutu
            commands = [
                ['createdb', 'unibos'],
                ['psql', '-d', 'postgres', '-c', "CREATE USER unibos WITH PASSWORD 'unibos123';"],
                ['psql', '-d', 'postgres', '-c', "GRANT ALL PRIVILEGES ON DATABASE unibos TO unibos;"]
            ]
        else:
            # Unix sistemler için
            commands = []
            
            # Veritabanı oluştur
            commands.append(['createdb', 'unibos'])
            
            # Kullanıcı oluştur (hata varsa devam et)
            commands.append(['psql', '-d', 'postgres', '-c', "CREATE USER unibos WITH PASSWORD 'unibos123';"])
            
            # Yetkileri ver
            commands.append(['psql', '-d', 'postgres', '-c', "GRANT ALL PRIVILEGES ON DATABASE unibos TO unibos;"])
        
        for cmd in commands:
            print(f"\nÇalıştırılıyor: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                # Bilinen hatalar için özel kontroller
                if "already exists" in result.stderr:
                    print(f"{Colors.YELLOW}⚠️ Zaten mevcut, devam ediliyor...{Colors.RESET}")
                elif "role \"unibos\" already exists" in result.stderr:
                    print(f"{Colors.YELLOW}⚠️ Kullanıcı zaten mevcut{Colors.RESET}")
                elif cmd[3].startswith("CREATE USER"):
                    # Kullanıcı oluşturma hatası - sudo ile dene
                    if self.system != "windows":
                        print("sudo ile deneniyor...")
                        sudo_cmd = ['sudo', '-u', 'postgres'] + cmd
                        result = subprocess.run(sudo_cmd, capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            print(f"{Colors.GREEN}✅ Başarılı!{Colors.RESET}")
                        elif "already exists" in result.stderr:
                            print(f"{Colors.YELLOW}⚠️ Kullanıcı zaten mevcut{Colors.RESET}")
                        else:
                            print(f"{Colors.RED}Hata devam ediyor: {result.stderr}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}❌ Hata:{Colors.RESET}")
                    print(result.stderr)
            else:
                print(f"{Colors.GREEN}✅ Başarılı{Colors.RESET}")
        
        # .env dosyası oluştur
        self.create_env_file()
        
        print(f"\n{Colors.GREEN}✅ Veritabanı kurulumu tamamlandı!{Colors.RESET}")
        return True
    
    def create_env_file(self):
        """Çevre değişkenleri dosyası oluştur"""
        env_path = Path.cwd() / '.env'
        
        if not env_path.exists():
            env_content = """# UNIBOS Database Configuration
UNIBOS_DB_HOST=localhost
UNIBOS_DB_PORT=5432
UNIBOS_DB_NAME=unibos
UNIBOS_DB_USER=unibos
UNIBOS_DB_PASSWORD=unibos123
"""
            env_path.write_text(env_content)
            print(f"{Colors.GREEN}✅ .env dosyası oluşturuldu{Colors.RESET}")
    
    def update_requirements(self):
        """requirements.txt'yi güncelle"""
        req_path = Path.cwd() / 'requirements.txt'
        
        if req_path.exists():
            content = req_path.read_text()
            
            packages = ['psycopg2-binary', 'sqlalchemy', 'alembic']
            lines = content.strip().split('\n')
            
            for package in packages:
                if package not in content:
                    lines.append(package)
            
            req_path.write_text('\n'.join(lines) + '\n')
            print(f"{Colors.GREEN}✅ requirements.txt güncellendi{Colors.RESET}")
    
    def show_instructions(self):
        """Kurulum talimatlarını göster"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}📋 PostgreSQL Kurulum Talimatları{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")
        
        if self.system == "darwin":
            print(f"{Colors.YELLOW}macOS için:{Colors.RESET}")
            print("1. Homebrew kurulu değilse:")
            print('   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
            print("\n2. PostgreSQL kurulumu:")
            print("   brew install postgresql@15")
            print("   brew services start postgresql@15")
            
        elif self.system == "linux":
            print(f"{Colors.YELLOW}Linux için:{Colors.RESET}")
            print("\nDebian/Ubuntu:")
            print("   sudo apt update")
            print("   sudo apt install postgresql postgresql-contrib")
            print("   sudo systemctl start postgresql")
            print("\nRedHat/CentOS/Fedora:")
            print("   sudo dnf install postgresql postgresql-server")
            print("   sudo postgresql-setup --initdb")
            print("   sudo systemctl start postgresql")
            
        elif self.system == "windows":
            print(f"{Colors.YELLOW}Windows için:{Colors.RESET}")
            print("1. https://www.postgresql.org/download/windows/")
            print("2. Installer'ı indirip çalıştırın")
            print("3. Kurulum sırasında password: unibos123")
        
        print(f"\n{Colors.YELLOW}Python paketleri:{Colors.RESET}")
        print("pip install psycopg2-binary sqlalchemy alembic")
        
        print(f"\n{Colors.YELLOW}Veritabanı oluşturma:{Colors.RESET}")
        print("createdb unibos")
        print('psql -d unibos -c "CREATE USER unibos WITH PASSWORD \'unibos123\';"')
        print('psql -d unibos -c "GRANT ALL PRIVILEGES ON DATABASE unibos TO unibos;"')
        
        input(f"\n{Colors.CYAN}Devam etmek için Enter'a basın...{Colors.RESET}")
    
    def start_postgresql_service(self):
        """PostgreSQL servisini başlat"""
        print(f"\n{Colors.CYAN}▶️  PostgreSQL servisi başlatılıyor...{Colors.RESET}")
        
        if self.system == "darwin":  # macOS
            # Try postgresql@15 first
            result = subprocess.run(['brew', 'services', 'start', 'postgresql@15'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                # Try postgresql
                result = subprocess.run(['brew', 'services', 'start', 'postgresql'], 
                                      capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ PostgreSQL servisi başlatıldı!{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌ Servis başlatılamadı:{Colors.RESET}")
                print(result.stderr)
                
        elif self.system == "linux":
            result = subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ PostgreSQL servisi başlatıldı!{Colors.RESET}")
                
                # Enable service to start on boot
                subprocess.run(['sudo', 'systemctl', 'enable', 'postgresql'], 
                             capture_output=True, text=True)
            else:
                print(f"{Colors.RED}❌ Servis başlatılamadı:{Colors.RESET}")
                print(result.stderr)
                
        elif self.system == "windows":
            print(f"{Colors.YELLOW}Windows için:{Colors.RESET}")
            print("1. Başlat menüsünden 'services.msc' çalıştırın")
            print("2. 'postgresql' servisini bulun")
            print("3. Sağ tıklayıp 'Start' seçin")
        
        # Test connection - daha uzun bekle
        print(f"\n{Colors.YELLOW}⏳ PostgreSQL servisinin hazır olması bekleniyor...{Colors.RESET}")
        
        # 10 saniye boyunca kontrol et
        for i in range(10):
            time.sleep(1)
            if self.check_postgresql_running():
                print(f"\n{Colors.GREEN}✅ PostgreSQL başarıyla çalışıyor!{Colors.RESET}")
                
                # macOS için ek bilgi
                if self.system == "darwin":
                    print(f"\n{Colors.CYAN}ℹ️  macOS İpucu:{Colors.RESET}")
                    print(f"PostgreSQL artık hazır! Eğer bağlantı sorunları yaşarsanız:")
                    print(f"1. {Colors.YELLOW}createuser -s $(whoami){Colors.RESET} komutuyla kullanıcınızı oluşturun")
                    print(f"2. {Colors.YELLOW}createdb $(whoami){Colors.RESET} komutuyla varsayılan veritabanınızı oluşturun")
                    print(f"3. {Colors.YELLOW}psql -d postgres{Colors.RESET} ile doğrudan bağlanmayı deneyin")
                    print(f"\n{Colors.GREEN}✨ Tebrikler! Artık '4. Veritabanı oluştur' seçeneğini kullanabilirsiniz.{Colors.RESET}")
                return
                
        print(f"\n{Colors.YELLOW}⚠️ PostgreSQL servisi başlatıldı ancak henüz bağlantı kabul etmiyor.{Colors.RESET}")
        print(f"\n{Colors.CYAN}Muhtemel çözümler:{Colors.RESET}")
        print(f"1. Birkaç saniye daha bekleyin")
        print(f"2. {Colors.YELLOW}brew services restart postgresql@15{Colors.RESET} ile yeniden başlatın")
        print(f"3. {Colors.YELLOW}/usr/local/var/log/postgresql@15.log{Colors.RESET} dosyasını kontrol edin")
        
        input(f"\n{Colors.CYAN}Devam etmek için Enter'a basın...{Colors.RESET}")
    
    def create_postgresql_user(self):
        """PostgreSQL kullanıcısı manuel oluştur"""
        print(f"\n{Colors.CYAN}👤 PostgreSQL Kullanıcısı Oluşturuluyor...{Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}Aşağıdaki komutları sırayla çalıştırın:{Colors.RESET}\n")
        
        if self.system == "darwin" or self.system == "linux":
            print("1. PostgreSQL'e bağlan:")
            print(f"   {Colors.GREEN}sudo -u postgres psql{Colors.RESET}")
            print("\n2. Kullanıcı oluştur:")
            print(f"   {Colors.GREEN}CREATE USER unibos WITH PASSWORD 'unibos123';{Colors.RESET}")
            print("\n3. Veritabanı oluştur:")
            print(f"   {Colors.GREEN}CREATE DATABASE unibos OWNER unibos;{Colors.RESET}")
            print("\n4. Yetkileri ver:")
            print(f"   {Colors.GREEN}GRANT ALL PRIVILEGES ON DATABASE unibos TO unibos;{Colors.RESET}")
            print("\n5. Çıkış yap:")
            print(f"   {Colors.GREEN}\\q{Colors.RESET}")
        
        print(f"\n{Colors.YELLOW}Alternatif (tek satırda):{Colors.RESET}")
        print(f"{Colors.GREEN}sudo -u postgres psql -c \"CREATE USER unibos WITH PASSWORD 'unibos123';CREATE DATABASE unibos OWNER unibos;\"{Colors.RESET}")
        
        input(f"\n{Colors.CYAN}Devam etmek için Enter'a basın...{Colors.RESET}")
    
    def clear_screen(self):
        """Ekranı temizle"""
        os.system('cls' if os.name == 'nt' else 'clear')

# Ana fonksiyon
def run_setup_wizard():
    """Setup wizard'ı çalıştır"""
    wizard = DatabaseSetupWizard()
    return wizard.run_wizard()

if __name__ == "__main__":
    run_setup_wizard()