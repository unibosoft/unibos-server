#!/usr/bin/env python3
"""
Suggestion Display Enhancement Module
Manuel önerileri daha iyi görüntüleme ve filtreleme sistemi
"""

from pathlib import Path
from typing import Dict, List, Tuple
import re

class SuggestionDisplay:
    """Öneri görüntüleme ve filtreleme sistemi"""
    
    def __init__(self):
        self.difficulty_filters = {
            'all': 'Tüm Öneriler',
            'easy': 'Kolay (1-2 saat)',
            'medium': 'Orta (3-5 saat)', 
            'hard': 'Zor (5+ saat)'
        }
        
        self.priority_icons = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        self.difficulty_colors = {
            'easy': '\033[92m',      # Green
            'medium': '\033[93m',    # Yellow
            'hard': '\033[91m'       # Red
        }
    
    def load_manual_suggestions_extended(self) -> Dict[str, List[Dict]]:
        """Manuel önerileri detaylı bilgilerle yükle"""
        suggestions = {
            'easy': [],
            'medium': [],
            'hard': []
        }
        
        suggestions_file = Path('CLAUDE_SUGGESTIONS.md')
        if not suggestions_file.exists():
            return suggestions
        
        content = suggestions_file.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        in_manual_section = False
        current_difficulty = None
        
        for line in lines:
            if '## 💡 Manuel Öneriler' in line:
                in_manual_section = True
                continue
            elif in_manual_section and line.startswith('## '):
                break
            elif in_manual_section and line.startswith('### '):
                if 'Kolay' in line:
                    current_difficulty = 'easy'
                elif 'Orta' in line:
                    current_difficulty = 'medium'
                elif 'Zor' in line:
                    current_difficulty = 'hard'
            elif in_manual_section and line.strip().startswith('-') and current_difficulty:
                # Parse detailed format: - 🟢 **[Category]** Text
                match = re.match(r'-\s*([🔴🟠🟡🟢])\s*\*\*\[(.*?)\]\*\*\s*(.*)', line)
                if match:
                    priority_icon, category, text = match.groups()
                    suggestions[current_difficulty].append({
                        'text': text,
                        'category': category,
                        'priority_icon': priority_icon,
                        'priority': self._get_priority_from_icon(priority_icon),
                        'difficulty': current_difficulty
                    })
                else:
                    # Simple format
                    text = line.strip('- ').strip()
                    if text and not text.startswith('*'):
                        suggestions[current_difficulty].append({
                            'text': text,
                            'category': 'Genel',
                            'priority_icon': '🟢',
                            'priority': 'low',
                            'difficulty': current_difficulty
                        })
        
        return suggestions
    
    def _get_priority_from_icon(self, icon: str) -> str:
        """Icon'dan priority level çıkar"""
        icon_to_priority = {
            '🔴': 'critical',
            '🟠': 'high',
            '🟡': 'medium',
            '🟢': 'low'
        }
        return icon_to_priority.get(icon, 'low')
    
    def format_suggestion_display(self, suggestions: Dict[str, List[Dict]], 
                                 filter_difficulty: str = 'all',
                                 max_display: int = 10) -> List[str]:
        """Önerileri görüntüleme için formatla"""
        lines = []
        
        # Filtre uygula
        if filter_difficulty == 'all':
            # Öncelik sırasına göre karma liste
            all_suggestions = []
            for difficulty in ['easy', 'medium', 'hard']:
                all_suggestions.extend(suggestions.get(difficulty, []))
            
            # Önceliğe göre sırala
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            all_suggestions.sort(key=lambda x: priority_order.get(x['priority'], 4))
            
            # İlk N tanesini göster
            for i, suggestion in enumerate(all_suggestions[:max_display]):
                diff_color = self.difficulty_colors[suggestion['difficulty']]
                lines.append(
                    f"  {i+1}. {suggestion['priority_icon']} "
                    f"{diff_color}[{suggestion['difficulty']}]\033[0m "
                    f"**{suggestion['category']}** - {suggestion['text']}"
                )
            
            # Kalan sayı
            remaining = len(all_suggestions) - max_display
            if remaining > 0:
                lines.append(f"\n  \033[90m...ve {remaining} öneri daha havuzda bekliyor\033[0m")
        
        else:
            # Belirli zorluk seviyesi
            filtered = suggestions.get(filter_difficulty, [])
            
            # Önceliğe göre sırala
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            filtered.sort(key=lambda x: priority_order.get(x['priority'], 4))
            
            for i, suggestion in enumerate(filtered[:max_display]):
                lines.append(
                    f"  {i+1}. {suggestion['priority_icon']} "
                    f"**{suggestion['category']}** - {suggestion['text']}"
                )
            
            # Kalan sayı
            remaining = len(filtered) - max_display
            if remaining > 0:
                lines.append(f"\n  \033[90m...ve {remaining} {filter_difficulty} öneri daha var\033[0m")
        
        return lines
    
    def get_summary_stats(self, suggestions: Dict[str, List[Dict]]) -> Dict[str, int]:
        """Öneri istatistiklerini getir"""
        stats = {
            'total': 0,
            'easy': len(suggestions.get('easy', [])),
            'medium': len(suggestions.get('medium', [])),
            'hard': len(suggestions.get('hard', [])),
            'critical': 0,
            'high': 0,
            'medium_priority': 0,
            'low': 0
        }
        
        stats['total'] = stats['easy'] + stats['medium'] + stats['hard']
        
        # Öncelik sayıları
        for difficulty in suggestions.values():
            for suggestion in difficulty:
                priority = suggestion.get('priority', 'low')
                if priority == 'critical':
                    stats['critical'] += 1
                elif priority == 'high':
                    stats['high'] += 1
                elif priority == 'medium':
                    stats['medium_priority'] += 1
                else:
                    stats['low'] += 1
        
        return stats


def test_display():
    """Test fonksiyonu"""
    display = SuggestionDisplay()
    suggestions = display.load_manual_suggestions_extended()
    
    print("📊 Manuel Öneri İstatistikleri:")
    stats = display.get_summary_stats(suggestions)
    print(f"Toplam: {stats['total']} öneri")
    print(f"- Kolay: {stats['easy']}")
    print(f"- Orta: {stats['medium']}")
    print(f"- Zor: {stats['hard']}")
    print()
    
    print("🎯 Tüm Öneriler (karma):")
    for line in display.format_suggestion_display(suggestions, 'all', 5):
        print(line)
    
    print("\n🟢 Sadece Kolay Öneriler:")
    for line in display.format_suggestion_display(suggestions, 'easy', 5):
        print(line)


if __name__ == "__main__":
    test_display()