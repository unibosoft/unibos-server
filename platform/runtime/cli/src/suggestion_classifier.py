#!/usr/bin/env python3
"""
Suggestion Classifier Module
Öneri havuzundaki önerileri zorluk derecesine göre sınıflandırır
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

class SuggestionClassifier:
    """Öneri sınıflandırma sistemi"""
    
    def __init__(self):
        self.difficulty_keywords = {
            'easy': {
                'keywords': ['basit', 'kolay', 'hızlı', 'minor', 'küçük', 'düzeltme', 'fix', 
                            'typo', 'renk', 'tema', 'görsel', 'ui', 'text', 'label', 'başlık'],
                'patterns': [r'sadece.*değiş', r'tek.*satır', r'birkaç.*dakika'],
                'time_estimate': '1-2 saat'
            },
            'medium': {
                'keywords': ['orta', 'modül', 'entegrasyon', 'optimize', 'iyileştir', 'geliştir',
                            'yeni özellik', 'api', 'cache', 'veritabanı', 'refactor'],
                'patterns': [r'yeni.*ekle', r'sistem.*kur', r'modül.*yaz'],
                'time_estimate': '3-5 saat'
            },
            'hard': {
                'keywords': ['zor', 'karmaşık', 'büyük', 'major', 'architecture', 'redesign',
                            'güvenlik', 'performance', 'ölçeklenebilir', 'altyapı', 'migration'],
                'patterns': [r'tamamen.*yeniden', r'büyük.*değişiklik', r'tüm.*sistem'],
                'time_estimate': '5+ saat'
            }
        }
        
        self.priority_keywords = {
            'critical': ['kritik', 'acil', 'güvenlik', 'crash', 'veri kaybı', 'hack'],
            'high': ['yüksek', 'önemli', 'kullanıcı deneyimi', 'performans', 'bug'],
            'medium': ['orta', 'iyileştirme', 'optimize', 'enhancement'],
            'low': ['düşük', 'kozmetik', 'nice-to-have', 'opsiyonel']
        }
    
    def classify_difficulty(self, suggestion: str) -> Tuple[str, str]:
        """
        Öneriyi zorluk derecesine göre sınıflandır
        Returns: (difficulty, time_estimate)
        """
        suggestion_lower = suggestion.lower()
        
        # Keyword ve pattern matching
        scores = {'easy': 0, 'medium': 0, 'hard': 0}
        
        for difficulty, config in self.difficulty_keywords.items():
            # Keyword matching
            for keyword in config['keywords']:
                if keyword in suggestion_lower:
                    scores[difficulty] += 2
            
            # Pattern matching
            for pattern in config['patterns']:
                if re.search(pattern, suggestion_lower):
                    scores[difficulty] += 3
        
        # Özel durumlar
        if any(word in suggestion_lower for word in ['tek satır', 'sadece bir', 'küçük bir']):
            scores['easy'] += 5
        
        if any(word in suggestion_lower for word in ['tüm sistem', 'büyük değişiklik', 'yeniden yaz']):
            scores['hard'] += 5
        
        # En yüksek skoru bul
        max_difficulty = max(scores, key=scores.get)
        
        # Eğer tüm skorlar 0 ise, default olarak medium
        if scores[max_difficulty] == 0:
            max_difficulty = 'medium'
        
        return max_difficulty, self.difficulty_keywords[max_difficulty]['time_estimate']
    
    def detect_priority(self, suggestion: str) -> str:
        """Öneri önceliğini tespit et"""
        suggestion_lower = suggestion.lower()
        
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword in suggestion_lower:
                    return priority
        
        # Default priority
        return 'medium'
    
    def parse_suggestions_file(self, file_path: Path) -> Dict[str, List[Dict]]:
        """CLAUDE_SUGGESTIONS.md dosyasını parse et ve sınıflandır"""
        if not file_path.exists():
            return {'easy': [], 'medium': [], 'hard': []}
        
        content = file_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        suggestions = {
            'easy': [],
            'medium': [],
            'hard': []
        }
        
        # Öneri havuzu bölümünü bul
        in_pool_section = False
        current_category = None
        
        for i, line in enumerate(lines):
            if '## 📈 Öneri Havuzu (Bekleyen)' in line:
                in_pool_section = True
                continue
            
            if in_pool_section:
                # Yeni bölüm başlangıcı kontrolü
                if line.startswith('##') and '📈' not in line:
                    break
                
                # Kategori başlığı
                if line.startswith('###'):
                    current_category = line.strip('# ').strip()
                    continue
                
                # Öneri satırı (- ile başlayan)
                if line.strip().startswith('-') and current_category:
                    suggestion_text = line.strip('- ').strip()
                    # Öneri havuzundaki ham metinleri al (manuel ekleme gibi açıklamaları temizle)
                    if '(manuel ekleme)' in suggestion_text:
                        suggestion_text = suggestion_text.replace('(manuel ekleme)', '').strip()
                    
                    if suggestion_text and not suggestion_text.startswith('*'):
                        difficulty, time_estimate = self.classify_difficulty(suggestion_text)
                        priority = self.detect_priority(suggestion_text)
                        
                        suggestion_obj = {
                            'text': suggestion_text,
                            'category': current_category,
                            'difficulty': difficulty,
                            'time_estimate': time_estimate,
                            'priority': priority,
                            'priority_icon': self._get_priority_icon(priority)
                        }
                        
                        suggestions[difficulty].append(suggestion_obj)
        
        return suggestions
    
    def _get_priority_icon(self, priority: str) -> str:
        """Öncelik için emoji icon döndür"""
        icons = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        return icons.get(priority, '🟢')
    
    def update_suggestions_file(self, file_path: Path, classified_suggestions: Dict[str, List[Dict]]) -> None:
        """Sınıflandırılmış önerileri dosyaya yaz"""
        if not file_path.exists():
            return
        
        content = file_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        # Manuel öneriler bölümünü bul ve güncelle
        new_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Manuel öneriler bölümünün başlangıcı
            if '## 💡 Manuel Öneriler (Kullanıcı Ekledi)' in line:
                new_lines.append(line)
                i += 1
                
                # Kolay bölümü
                new_lines.append('')
                new_lines.append('### Kolay Uygulanabilir (1-2 saat)')
                new_lines.append('*Bu bölüm otomatik sınıflandırılmış kolay önerileri içerir*')
                new_lines.append('')
                
                for suggestion in classified_suggestions.get('easy', []):
                    new_lines.append(f"- {suggestion['priority_icon']} **[{suggestion['category']}]** {suggestion['text']}")
                
                if not classified_suggestions.get('easy'):
                    new_lines.append('- *Henüz kolay öneri yok*')
                
                # Orta bölümü
                new_lines.append('')
                new_lines.append('### Orta Zorluk (3-5 saat)')
                new_lines.append('*Bu bölüm otomatik sınıflandırılmış orta zorluk önerileri içerir*')
                new_lines.append('')
                
                for suggestion in classified_suggestions.get('medium', []):
                    new_lines.append(f"- {suggestion['priority_icon']} **[{suggestion['category']}]** {suggestion['text']}")
                
                if not classified_suggestions.get('medium'):
                    new_lines.append('- *Henüz orta zorluk öneri yok*')
                
                # Zor bölümü
                new_lines.append('')
                new_lines.append('### Zor/Uzun Vadeli (5+ saat)')
                new_lines.append('*Bu bölüm otomatik sınıflandırılmış zor önerileri içerir*')
                new_lines.append('')
                
                for suggestion in classified_suggestions.get('hard', []):
                    new_lines.append(f"- {suggestion['priority_icon']} **[{suggestion['category']}]** {suggestion['text']}")
                
                if not classified_suggestions.get('hard'):
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
        
        # Son satırı güncelle
        if new_lines and new_lines[-1].startswith('*Son güncelleme:'):
            new_lines[-1] = f'*Son güncelleme: {timestamp}*'
        
        # Dosyayı yaz
        file_path.write_text('\n'.join(new_lines), encoding='utf-8')
    
    def generate_classified_report(self, classified_suggestions: Dict[str, List[Dict]]) -> str:
        """Sınıflandırılmış öneriler için rapor oluştur"""
        report = []
        report.append("📊 Öneri Havuzu Sınıflandırma Raporu")
        report.append("=" * 50)
        report.append("")
        
        total = sum(len(suggestions) for suggestions in classified_suggestions.values())
        
        report.append(f"Toplam öneri sayısı: {total}")
        report.append("")
        
        for difficulty in ['easy', 'medium', 'hard']:
            suggestions = classified_suggestions.get(difficulty, [])
            count = len(suggestions)
            percentage = (count / total * 100) if total > 0 else 0
            
            report.append(f"### {difficulty.capitalize()} ({self.difficulty_keywords[difficulty]['time_estimate']})")
            report.append(f"Öneri sayısı: {count} ({percentage:.1f}%)")
            
            if suggestions:
                report.append("")
                # Önceliğe göre sırala
                priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
                sorted_suggestions = sorted(suggestions, 
                                          key=lambda x: priority_order.get(x['priority'], 4))
                
                for suggestion in sorted_suggestions[:3]:  # İlk 3 öneri
                    report.append(f"  {suggestion['priority_icon']} [{suggestion['category']}] {suggestion['text'][:60]}...")
                
                if count > 3:
                    report.append(f"  ... ve {count - 3} öneri daha")
            
            report.append("")
        
        return '\n'.join(report)


def main():
    """CLI arayüzü"""
    import sys
    
    classifier = SuggestionClassifier()
    suggestions_file = Path('CLAUDE_SUGGESTIONS.md')
    
    if len(sys.argv) > 1 and sys.argv[1] == 'classify':
        print("🔄 Öneri havuzu sınıflandırılıyor...")
        
        # Önerileri parse et ve sınıflandır
        classified = classifier.parse_suggestions_file(suggestions_file)
        
        # Rapor oluştur ve göster
        report = classifier.generate_classified_report(classified)
        print(report)
        
        # Dosyayı güncelle
        classifier.update_suggestions_file(suggestions_file, classified)
        print("\n✅ CLAUDE_SUGGESTIONS.md güncellendi!")
        
    else:
        print("Kullanım: python suggestion_classifier.py classify")
        print("Öneri havuzundaki önerileri zorluk derecesine göre sınıflandırır")


if __name__ == "__main__":
    main()