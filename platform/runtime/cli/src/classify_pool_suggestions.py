#!/usr/bin/env python3
"""
Pool Suggestions Classifier
Öneri havuzundaki önerileri manuel öneriler bölümüne sınıflandırarak aktarır
"""

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import re

def classify_suggestion(text):
    """Öneriyi zorluk derecesine göre sınıflandır"""
    text_lower = text.lower()
    
    # Kolay (1-2 saat)
    easy_keywords = ['basit', 'kolay', 'hızlı', 'minor', 'küçük', 'düzeltme', 'fix', 
                     'typo', 'renk', 'tema', 'görsel', 'ui', 'text', 'label', 'başlık',
                     'dark/light tema', 'klavye kısayol']
    
    # Zor (5+ saat)
    hard_keywords = ['güvenlik', 'security', 'jwt', 'injection', 'xss', 'büyük', 'major',
                     'architecture', 'redesign', 'altyapı', 'migration', 'multiplayer',
                     'mesh network', 'websocket', 'cdn']
    
    # Öncelik tespiti
    if any(word in text_lower for word in ['güvenlik', 'security', 'jwt', 'injection', 'xss']):
        priority = '🔴'  # Kritik
    elif any(word in text_lower for word in ['performans', 'optimize', 'query', 'n+1']):
        priority = '🟠'  # Yüksek
    elif any(word in text_lower for word in ['kullanıcı deneyimi', 'ui', 'tema']):
        priority = '🟡'  # Orta
    else:
        priority = '🟢'  # Düşük
    
    # Zorluk tespiti
    if any(keyword in text_lower for keyword in easy_keywords):
        return 'easy', priority
    elif any(keyword in text_lower for keyword in hard_keywords):
        return 'hard', priority
    else:
        return 'medium', priority

def main():
    file_path = Path('CLAUDE_SUGGESTIONS.md')
    content = file_path.read_text(encoding='utf-8')
    lines = content.splitlines()
    
    # Öneri havuzundaki önerileri topla
    pool_suggestions = {
        'Güvenlik': [],
        'Performans': [],
        'Kullanıcı Deneyimi': [],
        'Yeni Özellikler': []
    }
    
    current_category = None
    in_pool = False
    
    for line in lines:
        if '## 📈 Öneri Havuzu (Bekleyen)' in line:
            in_pool = True
            continue
        
        if in_pool:
            if line.startswith('##') and '📈' not in line:
                break
            
            if line.startswith('###'):
                current_category = line.strip('# ').strip()
            elif line.strip().startswith('-') and current_category in pool_suggestions:
                suggestion = line.strip('- ').strip()
                if suggestion and not suggestion.startswith('*'):
                    # Manuel ekleme notunu temizle
                    suggestion = suggestion.replace('(manuel ekleme)', '').strip()
                    pool_suggestions[current_category].append(suggestion)
    
    # Önerileri sınıflandır
    classified = {
        'easy': [],
        'medium': [],
        'hard': []
    }
    
    for category, suggestions in pool_suggestions.items():
        for suggestion in suggestions:
            difficulty, priority = classify_suggestion(suggestion)
            classified[difficulty].append({
                'text': suggestion,
                'category': category,
                'priority': priority
            })
    
    # Dosyayı güncelle
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if '## 💡 Manuel Öneriler (Kullanıcı Ekledi)' in line:
            new_lines.append(line)
            
            # Kolay öneriler
            new_lines.append('')
            new_lines.append('### Kolay Uygulanabilir (1-2 saat)')
            new_lines.append('*Öneri havuzundan otomatik sınıflandırılmış kolay öneriler*')
            new_lines.append('')
            
            if classified['easy']:
                for item in classified['easy']:
                    new_lines.append(f"- {item['priority']} **[{item['category']}]** {item['text']}")
            else:
                new_lines.append('- *Henüz kolay öneri yok*')
            
            # Orta öneriler
            new_lines.append('')
            new_lines.append('### Orta Zorluk (3-5 saat)')
            new_lines.append('*Öneri havuzundan otomatik sınıflandırılmış orta zorluk öneriler*')
            new_lines.append('')
            
            if classified['medium']:
                for item in classified['medium']:
                    new_lines.append(f"- {item['priority']} **[{item['category']}]** {item['text']}")
            else:
                new_lines.append('- *Henüz orta zorluk öneri yok*')
            
            # Zor öneriler
            new_lines.append('')
            new_lines.append('### Zor/Uzun Vadeli (5+ saat)')
            new_lines.append('*Öneri havuzundan otomatik sınıflandırılmış zor öneriler*')
            new_lines.append('')
            
            if classified['hard']:
                for item in classified['hard']:
                    new_lines.append(f"- {item['priority']} **[{item['category']}]** {item['text']}")
            else:
                new_lines.append('- *Henüz zor öneri yok*')
            
            # Öneri havuzu bölümüne kadar atla
            while i < len(lines) and '## 📈 Öneri Havuzu (Bekleyen)' not in lines[i]:
                i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    # Son güncelleme zamanını güncelle
    istanbul_tz = ZoneInfo('Europe/Istanbul')
    now = datetime.now(istanbul_tz)
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S +03:00')
    
    if new_lines and new_lines[-1].startswith('*Son güncelleme:'):
        new_lines[-1] = f'*Son güncelleme: {timestamp}*'
    
    # Dosyayı yaz
    file_path.write_text('\n'.join(new_lines), encoding='utf-8')
    
    # Rapor göster
    print("📊 Öneri Havuzu Sınıflandırma Raporu")
    print("=" * 50)
    print(f"\nToplam öneri sayısı: {sum(len(s) for s in classified.values())}")
    print(f"- Kolay: {len(classified['easy'])}")
    print(f"- Orta: {len(classified['medium'])}")
    print(f"- Zor: {len(classified['hard'])}")
    print("\n✅ CLAUDE_SUGGESTIONS.md güncellendi!")

if __name__ == "__main__":
    main()