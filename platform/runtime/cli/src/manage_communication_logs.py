#!/usr/bin/env python3
"""
📋 Communication Log Manager
Ana dizindeki communication log'larını yönetir ve maksimum 3 adet tutar

Author: berk hatırlı
Version: v254
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import shutil

class CommunicationLogManager:
    def __init__(self):
        self.base_path = Path("/Users/berkhatirli/Desktop/unibos")
        self.max_logs = 3
        self.log_pattern = "CLAUDE_COMMUNICATION_LOG_*.md"
        
    def get_comm_logs(self):
        """Tüm communication log'larını tarih sırasına göre getir"""
        logs = []
        for log_file in self.base_path.glob(self.log_pattern):
            # Dosya adından timestamp'i çıkar
            parts = log_file.stem.split('_')
            if len(parts) >= 6:
                try:
                    # Format: CLAUDE_COMMUNICATION_LOG_vXXX_to_vYYY_YYYYMMDD_HHMM
                    date_str = parts[5]
                    time_str = parts[6] if len(parts) > 6 else "0000"
                    timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M")
                    logs.append((log_file, timestamp))
                except:
                    # Eski format veya parse edilemeyen dosyalar
                    # Modification time'a göre sırala
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    logs.append((log_file, mtime))
                    
        # Tarihe göre sırala (en yeni önce)
        logs.sort(key=lambda x: x[1], reverse=True)
        return logs
    
    def cleanup_old_logs(self):
        """Eski communication log'larını sil (sadece son 3'ü tut)"""
        logs = self.get_comm_logs()
        
        if len(logs) <= self.max_logs:
            print(f"✅ {len(logs)} communication log mevcut (limit: {self.max_logs})")
            return 0
            
        # Silinecek log'ları belirle
        logs_to_remove = logs[self.max_logs:]
        removed_count = 0
        
        print(f"📋 Toplam {len(logs)} communication log bulundu")
        print(f"🗑️  {len(logs_to_remove)} eski log silinecek")
        
        for log_file, timestamp in logs_to_remove:
            try:
                print(f"   - Siliniyor: {log_file.name}")
                log_file.unlink()
                removed_count += 1
            except Exception as e:
                print(f"   ❌ Hata: {log_file.name} silinemedi: {e}")
                
        print(f"✅ {removed_count} eski log silindi, {self.max_logs} log tutuldu")
        return removed_count
    
    def list_logs(self):
        """Mevcut communication log'larını listele"""
        logs = self.get_comm_logs()
        
        print(f"\n📋 Communication Log'ları ({len(logs)} adet):")
        print("=" * 60)
        
        for i, (log_file, timestamp) in enumerate(logs):
            status = "✅ Tutulacak" if i < self.max_logs else "🗑️  Silinecek"
            print(f"{i+1}. {log_file.name}")
            print(f"   Tarih: {timestamp.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Durum: {status}")
            print()
            
    def create_new_log(self, from_version, to_version):
        """Yeni communication log oluştur ve eski log'ları temizle"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"CLAUDE_COMMUNICATION_LOG_{from_version}_to_{to_version}_{timestamp}.md"
        filepath = self.base_path / filename
        
        # Yeni log oluştur
        content = f"""# {filename.replace('.md', '')}

## 📊 Oturum Bilgileri

**Başlangıç Tarihi:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} +03:00
**Başlangıç Versiyonu:** {from_version}
**Platform:** macOS

## 🚀 Başlangıç Durumu

### Mevcut Durum
- {from_version} versiyonu başarıyla arşivlendi
- Communication log otomatik yönetimi aktif

## 💬 Sohbet Geçmişi

**[{datetime.now().strftime('%H:%M')}]** Claude: Yeni oturum başlatıldı.

## 🎯 Devam Eden Konular

1. **Bekleyen görevler buraya eklenecek**

## 📝 Notlar

- Communication log'lar otomatik olarak yönetiliyor (max {self.max_logs} adet)

---
*Bu log {from_version}'den {to_version}'e geçiş sürecini dokumenteeder.*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ Yeni log oluşturuldu: {filename}")
        
        # Eski log'ları temizle
        self.cleanup_old_logs()
        
        return filepath


def main():
    """Ana fonksiyon"""
    manager = CommunicationLogManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "list":
            manager.list_logs()
        elif command == "cleanup":
            manager.cleanup_old_logs()
        elif command == "create" and len(sys.argv) >= 4:
            from_version = sys.argv[2]
            to_version = sys.argv[3]
            manager.create_new_log(from_version, to_version)
        else:
            print("Kullanım:")
            print("  python manage_communication_logs.py list     - Log'ları listele")
            print("  python manage_communication_logs.py cleanup  - Eski log'ları temizle")
            print("  python manage_communication_logs.py create v254 v255  - Yeni log oluştur")
    else:
        # Varsayılan: cleanup
        manager.cleanup_old_logs()


if __name__ == "__main__":
    main()