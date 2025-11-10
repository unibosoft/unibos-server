#!/usr/bin/env python3
"""
Enhanced Suggestion Pool Display Module
Gelişmiş öneri havuzu görüntüleme sistemi
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
from collections import defaultdict
from datetime import datetime

class Colors:
    """ANSI color codes for terminal output"""
    # Base colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    REVERSE = '\033[7m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BLACK = '\033[40m'
    
    # Reset
    RESET = '\033[0m'


class EnhancedPoolDisplay:
    """Enhanced suggestion pool display with better visualization"""
    
    def __init__(self):
        self.category_icons = {
            'Güvenlik': '🛡️',
            'Performans': '⚡',
            'Kullanıcı Deneyimi': '👤',
            'Yeni Özellikler': '✨',
            'Genel': '📌',
            'UI/UX': '🎨',
            'Database': '🗄️',
            'API': '🔌',
            'Testing': '🧪',
            'Documentation': '📚'
        }
        
        self.category_colors = {
            'Güvenlik': Colors.BRIGHT_RED,
            'Performans': Colors.BRIGHT_YELLOW,
            'Kullanıcı Deneyimi': Colors.BRIGHT_CYAN,
            'Yeni Özellikler': Colors.BRIGHT_MAGENTA,
            'Genel': Colors.WHITE,
            'UI/UX': Colors.BRIGHT_BLUE,
            'Database': Colors.GREEN,
            'API': Colors.YELLOW,
            'Testing': Colors.CYAN,
            'Documentation': Colors.BLUE
        }
        
        self.priority_badges = {
            'critical': f'{Colors.BG_RED}{Colors.WHITE} CRITICAL {Colors.RESET}',
            'high': f'{Colors.BG_YELLOW}{Colors.BLACK} HIGH {Colors.RESET}',
            'medium': f'{Colors.BG_BLUE}{Colors.WHITE} MEDIUM {Colors.RESET}',
            'low': f'{Colors.BG_GREEN}{Colors.WHITE} LOW {Colors.RESET}'
        }
        
        self.filter_options = {
            'all': 'All Suggestions',
            'category': 'Filter by Category',
            'priority': 'Filter by Priority',
            'recent': 'Recently Added',
            'trending': 'Most Requested'
        }
    
    def load_pool_suggestions(self) -> Dict[str, List[Dict]]:
        """Load and parse pool suggestions with enhanced metadata"""
        suggestions_by_category = defaultdict(list)
        
        suggestions_file = Path('CLAUDE_SUGGESTIONS.md')
        if not suggestions_file.exists():
            return dict(suggestions_by_category)
        
        content = suggestions_file.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        in_pool_section = False
        current_category = None
        suggestion_index = 0
        
        for i, line in enumerate(lines):
            if '## 📈 Öneri Havuzu' in line:
                in_pool_section = True
                continue
            elif in_pool_section and line.startswith('## '):
                break
            elif in_pool_section and line.startswith('### '):
                current_category = line.strip('# ').strip()
            elif in_pool_section and line.strip().startswith('-') and current_category:
                suggestion_text = line.strip('- ').strip()
                if suggestion_text and not suggestion_text.startswith('*'):
                    suggestion_index += 1
                    
                    # Extract priority if present
                    priority = 'medium'  # default
                    if '[critical]' in suggestion_text.lower():
                        priority = 'critical'
                    elif '[high]' in suggestion_text.lower():
                        priority = 'high'
                    elif '[low]' in suggestion_text.lower():
                        priority = 'low'
                    
                    # Clean text
                    clean_text = re.sub(r'\[(critical|high|medium|low)\]', '', suggestion_text, flags=re.IGNORECASE).strip()
                    
                    suggestions_by_category[current_category].append({
                        'id': suggestion_index,
                        'text': clean_text,
                        'category': current_category,
                        'priority': priority,
                        'line_index': i
                    })
        
        return dict(suggestions_by_category)
    
    def display_header(self):
        """Display enhanced header with stats"""
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}📚 AUTO SUGGESTIONS POOL - ENHANCED VIEW{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.DIM}Intelligent suggestion management system{Colors.RESET}")
        print()
    
    def display_stats_bar(self, suggestions_by_category: Dict[str, List[Dict]]):
        """Display statistics bar with category counts"""
        total_count = sum(len(items) for items in suggestions_by_category.values())
        
        print(f"{Colors.BOLD}📊 Pool Statistics:{Colors.RESET}")
        print(f"{'─'*80}")
        
        # Category breakdown
        stats_line = ""
        for category, items in suggestions_by_category.items():
            icon = self.category_icons.get(category, '📌')
            color = self.category_colors.get(category, Colors.WHITE)
            count = len(items)
            stats_line += f"{color}{icon} {category}: {count}{Colors.RESET}  "
        
        print(stats_line)
        print(f"{'─'*80}")
        print(f"{Colors.BOLD}Total: {total_count} suggestions{Colors.RESET}")
        print()
    
    def display_suggestions_grouped(self, suggestions_by_category: Dict[str, List[Dict]], 
                                  filter_mode: str = 'all', 
                                  filter_value: Optional[str] = None):
        """Display suggestions with grouping and enhanced formatting"""
        
        displayed_count = 0
        
        for category, suggestions in suggestions_by_category.items():
            # Apply filters
            if filter_mode == 'category' and filter_value and category != filter_value:
                continue
            
            filtered_suggestions = suggestions
            if filter_mode == 'priority' and filter_value:
                filtered_suggestions = [s for s in suggestions if s['priority'] == filter_value]
            
            if not filtered_suggestions:
                continue
            
            # Category header
            icon = self.category_icons.get(category, '📌')
            color = self.category_colors.get(category, Colors.WHITE)
            
            print(f"\n{color}{Colors.BOLD}{icon} {category.upper()}{Colors.RESET}")
            print(f"{color}{'─' * (len(category) + 4)}{Colors.RESET}")
            
            # Sort by priority
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            filtered_suggestions.sort(key=lambda x: priority_order.get(x['priority'], 4))
            
            # Display suggestions
            for suggestion in filtered_suggestions:
                displayed_count += 1
                
                # Format with priority badge
                badge = self.priority_badges.get(suggestion['priority'], '')
                
                # Truncate long text
                text = suggestion['text']
                if len(text) > 70:
                    text = text[:67] + '...'
                
                print(f"{Colors.DIM}{displayed_count:3d}.{Colors.RESET} {badge} {text}")
        
        return displayed_count
    
    def display_compact_view(self, suggestions_by_category: Dict[str, List[Dict]], max_per_category: int = 3):
        """Display compact view with limited items per category"""
        print(f"\n{Colors.BOLD}🎯 Quick Overview (Top {max_per_category} per category):{Colors.RESET}")
        print(f"{'─'*80}")
        
        for category, suggestions in suggestions_by_category.items():
            if not suggestions:
                continue
            
            icon = self.category_icons.get(category, '📌')
            color = self.category_colors.get(category, Colors.WHITE)
            
            # Sort by priority
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            sorted_suggestions = sorted(suggestions, key=lambda x: priority_order.get(x['priority'], 4))
            
            print(f"\n{color}{icon} {category}{Colors.RESET}")
            
            for i, suggestion in enumerate(sorted_suggestions[:max_per_category]):
                text = suggestion['text']
                if len(text) > 60:
                    text = text[:57] + '...'
                
                priority_indicator = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(suggestion['priority'], '⚪')
                
                print(f"  {priority_indicator} {text}")
            
            remaining = len(suggestions) - max_per_category
            if remaining > 0:
                print(f"  {Colors.DIM}... and {remaining} more{Colors.RESET}")
    
    def display_filter_menu(self):
        """Display filter options menu"""
        print(f"\n{Colors.BOLD}🔍 Filter Options:{Colors.RESET}")
        print(f"{'─'*80}")
        print(f"  {Colors.CYAN}[A]{Colors.RESET} All suggestions")
        print(f"  {Colors.CYAN}[C]{Colors.RESET} Filter by category")
        print(f"  {Colors.CYAN}[P]{Colors.RESET} Filter by priority")
        print(f"  {Colors.CYAN}[V]{Colors.RESET} Compact view")
        print(f"  {Colors.CYAN}[S]{Colors.RESET} Statistics only")
        print(f"{'─'*80}")
    
    def display_priority_distribution(self, suggestions_by_category: Dict[str, List[Dict]]):
        """Display priority distribution chart"""
        priority_counts = defaultdict(int)
        
        for suggestions in suggestions_by_category.values():
            for s in suggestions:
                priority_counts[s['priority']] += 1
        
        print(f"\n{Colors.BOLD}📈 Priority Distribution:{Colors.RESET}")
        print(f"{'─'*80}")
        
        total = sum(priority_counts.values())
        for priority in ['critical', 'high', 'medium', 'low']:
            count = priority_counts.get(priority, 0)
            percentage = (count / total * 100) if total > 0 else 0
            bar_length = int(percentage / 2)  # Scale to fit in 50 chars
            
            badge = self.priority_badges.get(priority, priority.upper())
            bar = '█' * bar_length
            
            print(f"{badge:20} {bar:<50} {count:3d} ({percentage:5.1f}%)")
        
        print(f"{'─'*80}")
    
    def get_category_list(self, suggestions_by_category: Dict[str, List[Dict]]) -> List[str]:
        """Get list of available categories"""
        return sorted(suggestions_by_category.keys())
    
    def format_for_selection(self, suggestions_by_category: Dict[str, List[Dict]]) -> List[Dict]:
        """Format all suggestions for easy selection"""
        all_suggestions = []
        
        for category, suggestions in suggestions_by_category.items():
            for suggestion in suggestions:
                all_suggestions.append(suggestion)
        
        # Sort by priority then by ID
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_suggestions.sort(key=lambda x: (priority_order.get(x['priority'], 4), x['id']))
        
        return all_suggestions


def demonstrate_enhanced_display():
    """Demonstrate the enhanced display capabilities"""
    display = EnhancedPoolDisplay()
    
    # Load suggestions
    suggestions = display.load_pool_suggestions()
    
    if not suggestions:
        print(f"{Colors.YELLOW}No suggestions found in pool{Colors.RESET}")
        return
    
    # Main display
    display.display_header()
    display.display_stats_bar(suggestions)
    
    # Show compact view first
    display.display_compact_view(suggestions)
    
    # Show filter menu
    display.display_filter_menu()
    
    # Show priority distribution
    display.display_priority_distribution(suggestions)
    
    print(f"\n{Colors.DIM}This enhanced display provides better organization and filtering capabilities{Colors.RESET}")


if __name__ == "__main__":
    demonstrate_enhanced_display()