#!/usr/bin/env python3
"""
🗄️ UNIBOS Database Manager
Otomatik veritabanı seçimi ve yönetimi - PostgreSQL varsa kullan, yoksa SQLite
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Try PostgreSQL first, fallback to SQLite
DB_TYPE = "sqlite"  # Default
ENGINE = None
Session = None

try:
    import psycopg2
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # PostgreSQL bağlantısını test et
    def test_postgresql_connection() -> bool:
        """PostgreSQL'e bağlanmayı dene"""
        try:
            # Önce çevre değişkenlerinden oku
            db_config = {
                'host': os.getenv('UNIBOS_DB_HOST', 'localhost'),
                'port': os.getenv('UNIBOS_DB_PORT', '5432'),
                'database': os.getenv('UNIBOS_DB_NAME', 'unibos'),
                'user': os.getenv('UNIBOS_DB_USER', 'unibos'),
                'password': os.getenv('UNIBOS_DB_PASSWORD', 'unibos123'),
            }
            
            # Test bağlantısı
            conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            test_engine = create_engine(conn_str, echo=False)
            test_engine.connect().close()
            
            return True
        except Exception as e:
            print(f"PostgreSQL bağlantısı başarısız: {e}")
            return False
    
    if test_postgresql_connection():
        DB_TYPE = "postgresql"
        print("✅ PostgreSQL kullanılıyor")
    else:
        print("⚠️ PostgreSQL bulunamadı, SQLite kullanılacak")
        
except ImportError:
    print("⚠️ psycopg2 kurulu değil, SQLite kullanılacak")

# SQLite veya PostgreSQL engine oluştur
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    if DB_TYPE == "postgresql":
        from database.config import DATABASE_URL
        ENGINE = create_engine(DATABASE_URL, echo=False)
    else:
        # SQLite kullan
        db_path = Path.home() / '.unibos' / 'unibos.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        DATABASE_URL = f"sqlite:///{db_path}"
        ENGINE = create_engine(DATABASE_URL, echo=False)
        print(f"✅ SQLite kullanılıyor: {db_path}")

    # Session oluştur
    Session = sessionmaker(bind=ENGINE)
    
except ImportError as e:
    print(f"⚠️ SQLAlchemy kurulu değil: {e}")
    print("📦 Lütfen şu komutu çalıştırın: pip install sqlalchemy psycopg2-binary")
    ENGINE = None
    Session = None

# Auto-install helper
def auto_install_postgresql():
    """PostgreSQL otomatik kurulum denemesi"""
    system = sys.platform
    
    if system == "darwin":  # macOS
        print("\n🍎 macOS tespit edildi. PostgreSQL kurulumu için:")
        print("1. Homebrew kurulu mu kontrol ediliyor...")
        
        # Homebrew kontrolü
        brew_check = os.system("which brew > /dev/null 2>&1")
        if brew_check == 0:
            print("✅ Homebrew bulundu!")
            
            response = input("\nPostgreSQL'i Homebrew ile kurmak ister misiniz? (e/h): ")
            if response.lower() == 'e':
                print("\n📦 PostgreSQL kuruluyor...")
                os.system("brew install postgresql")
                os.system("brew services start postgresql")
                
                print("\n🗄️ Veritabanı oluşturuluyor...")
                os.system("createdb unibos")
                os.system("""psql -d unibos -c "CREATE USER unibos WITH PASSWORD 'unibos123';" """)
                os.system("""psql -d unibos -c "GRANT ALL PRIVILEGES ON DATABASE unibos TO unibos;" """)
                
                print("\n✅ PostgreSQL kurulumu tamamlandı!")
                return True
        else:
            print("❌ Homebrew bulunamadı. Önce Homebrew kurmanız gerekiyor:")
            print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    
    elif system == "linux":
        print("\n🐧 Linux tespit edildi. PostgreSQL kurulumu için:")
        
        # Distro tespiti
        if os.path.exists("/etc/debian_version"):
            print("Debian/Ubuntu tespit edildi.")
            response = input("\nPostgreSQL'i apt ile kurmak ister misiniz? (e/h): ")
            if response.lower() == 'e':
                print("\n📦 PostgreSQL kuruluyor...")
                os.system("sudo apt update")
                os.system("sudo apt install postgresql postgresql-contrib -y")
                os.system("sudo systemctl start postgresql")
                
                print("\n🗄️ Veritabanı oluşturuluyor...")
                os.system("sudo -u postgres createdb unibos")
                os.system("""sudo -u postgres psql -c "CREATE USER unibos WITH PASSWORD 'unibos123';" """)
                os.system("""sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE unibos TO unibos;" """)
                
                print("\n✅ PostgreSQL kurulumu tamamlandı!")
                return True
                
    elif system == "win32":
        print("\n🪟 Windows tespit edildi.")
        print("PostgreSQL'i manuel olarak kurmanız gerekiyor:")
        print("1. https://www.postgresql.org/download/windows/ adresine gidin")
        print("2. Installer'ı indirip çalıştırın")
        print("3. Kurulum sırasında 'unibos' kullanıcısı ve veritabanı oluşturun")
    
    return False

# Otomatik kurulum teklifi
def offer_auto_install():
    """PostgreSQL kurulmamışsa otomatik kurulum teklif et"""
    if DB_TYPE == "sqlite":
        print("\n💡 PostgreSQL kullanmak daha iyi performans sağlar.")
        response = input("PostgreSQL kurmak ister misiniz? (e/h): ")
        
        if response.lower() == 'e':
            if auto_install_postgresql():
                print("\n🔄 Veritabanı bağlantısı yeniden kontrol ediliyor...")
                # Program yeniden başlatılmalı
                print("⚠️ Değişikliklerin geçerli olması için programı yeniden başlatın.")
                sys.exit(0)

# Export
__all__ = ['ENGINE', 'Session', 'DB_TYPE', 'DATABASE_URL', 'offer_auto_install']