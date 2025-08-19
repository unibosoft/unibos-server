#!/usr/bin/env python3
"""
Import users from old Unicorn database SQL backup to new UNIBOS database
Kullanıcıları hatasız import et ve login yapabilmelerini sağla
"""

import os
import sys
import django
import re
from datetime import datetime

# Django setup
sys.path.append('/Users/berkhatirli/Desktop/unibos/backend')
os.environ['SECRET_KEY'] = 'django-insecure-unibos-import-temp-key-2025'
os.environ['DATABASE_URL'] = 'postgresql://unibos_user:unibos_password@localhost:5432/unibos_db'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.emergency')
django.setup()

from django.contrib.auth.models import User
from apps.core.models import UserProfile
from django.db import transaction

def parse_user_data_from_sql():
    """SQL dosyasından kullanıcı verilerini parse et"""
    sql_file = '/Users/berkhatirli/Desktop/unibos/import/unicorn_db_backup_v030-beta_2025_05_22_19_50.sql'
    
    users = []
    
    # SQL dosyasını oku
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # auth_user tablosundan verileri çek
    # Pattern: INSERT INTO `auth_user` VALUES (...)
    pattern = r"INSERT INTO `auth_user` VALUES \((.*?)\);"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        values_str = match.group(1)
        
        # Kullanıcıları parse et
        # Format: (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
        user_pattern = r"\((\d+),'([^']*?)','([^']*?)',(\d+),'([^']*?)','([^']*?)','([^']*?)','([^']*?)',(\d+),(\d+),'([^']*?)'\)"
        
        for user_match in re.finditer(user_pattern, values_str):
            user_data = {
                'id': int(user_match.group(1)),
                'password_hash': user_match.group(2),
                'last_login': user_match.group(3) if user_match.group(3) != 'NULL' else None,
                'is_superuser': bool(int(user_match.group(4))),
                'username': user_match.group(5),
                'first_name': user_match.group(6),
                'last_name': user_match.group(7),
                'email': user_match.group(8),
                'is_staff': bool(int(user_match.group(9))),
                'is_active': bool(int(user_match.group(10))),
                'date_joined': user_match.group(11)
            }
            users.append(user_data)
    
    return users

def import_users():
    """Kullanıcıları import et"""
    print("🚀 Kullanıcı import işlemi başlıyor...")
    print("=" * 50)
    
    users_data = parse_user_data_from_sql()
    
    if not users_data:
        print("❌ SQL dosyasından kullanıcı verisi bulunamadı!")
        return
    
    print(f"📊 {len(users_data)} kullanıcı bulundu")
    print("-" * 50)
    
    imported = 0
    updated = 0
    skipped = 0
    
    # Özel şifre mapping (berkhatirli için)
    special_passwords = {
        'berkhatirli': 'Unib0s_Str0ng_2025!'  # Güçlü şifre
    }
    
    with transaction.atomic():
        for user_data in users_data:
            username = user_data['username']
            
            try:
                # Kullanıcı var mı kontrol et
                if User.objects.filter(username=username).exists():
                    user = User.objects.get(username=username)
                    
                    # berkhatirli için özel işlem
                    if username == 'berkhatirli':
                        # Email'i güncelle
                        user.email = user_data['email']
                        user.first_name = user_data['first_name']
                        user.last_name = user_data['last_name']
                        user.is_staff = user_data['is_staff']
                        user.is_superuser = user_data['is_superuser']
                        user.is_active = user_data['is_active']
                        
                        # Özel şifre belirle
                        user.set_password(special_passwords[username])
                        user.save()
                        
                        print(f"✅ Güncellendi: {username} - Şifre: {special_passwords[username]}")
                        updated += 1
                    else:
                        print(f"⚠️  {username} zaten mevcut, atlanıyor...")
                        skipped += 1
                    continue
                
                # Yeni kullanıcı oluştur
                user = User.objects.create(
                    username=username,
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_staff=user_data['is_staff'],
                    is_superuser=user_data['is_superuser'],
                    is_active=user_data['is_active']
                )
                
                # Şifre belirle
                if username in special_passwords:
                    password = special_passwords[username]
                else:
                    # Diğer kullanıcılar için varsayılan şifre
                    password = 'Unicorn2025!'
                
                user.set_password(password)
                user.save()
                
                # GSM numarası ekle (varsa)
                phone_numbers = {
                    'berkhatirli': '5323672225',
                    'beyhan': '5551234567',  # Örnek
                    'ersan': '5551234568',   # Örnek
                }
                
                if username in phone_numbers:
                    profile, created = UserProfile.objects.get_or_create(
                        user=user,
                        defaults={'phone_number': phone_numbers[username]}
                    )
                    if created:
                        print(f"  📱 Telefon eklendi: {phone_numbers[username]}")
                
                print(f"✅ Import edildi: {username} ({user_data['email']}) - Şifre: {password}")
                imported += 1
                
            except Exception as e:
                print(f"❌ Hata: {username} import edilemedi - {str(e)}")
    
    print("\n" + "=" * 50)
    print("📊 Import Özeti:")
    print(f"  ✅ Başarıyla import edilen: {imported} kullanıcı")
    print(f"  🔄 Güncellenen: {updated} kullanıcı")
    print(f"  ⚠️  Atlanan (zaten mevcut): {skipped} kullanıcı")
    print("=" * 50)
    
    # berkhatirli için özel bilgi
    if 'berkhatirli' in [u['username'] for u in users_data]:
        print("\n🔐 berkhatirli kullanıcısı için:")
        print(f"  Kullanıcı adı: berkhatirli")
        print(f"  Şifre: {special_passwords.get('berkhatirli', 'Unicorn2025!')}")
        print(f"  Email: berk@berkinatolyesi.com")
        print(f"  Süper kullanıcı: Evet")
    
    print("\n💡 Diğer kullanıcılar için varsayılan şifre: Unicorn2025!")
    print("✨ Import işlemi tamamlandı!")

if __name__ == "__main__":
    import_users()