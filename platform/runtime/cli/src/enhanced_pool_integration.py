#!/usr/bin/env python3
"""
Enhanced Pool Display Integration
Integrates with existing claude_cli.py to provide better pool display
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
from collections import defaultdict
from suggestion_pool_display import EnhancedPoolDisplay, Colors


class PoolDisplayIntegration:
    """Integration layer for enhanced pool display in claude_cli"""
    
    def __init__(self, claude_cli_instance):
        self.cli = claude_cli_instance
        self.display = EnhancedPoolDisplay()
        self.current_filter = 'all'
        self.filter_value = None
        self.cached_suggestions = None
    
    def show_enhanced_pool(self):
        """Enhanced pool display with interactive features"""
        while True:
            self.cli.clear_screen()
            
            # Load suggestions
            suggestions = self.display.load_pool_suggestions()
            self.cached_suggestions = suggestions
            
            if not suggestions:
                print(f"{Colors.YELLOW}No suggestions found in pool{Colors.RESET}")
                input(f"\n{Colors.DIM}Press Enter to return...{Colors.RESET}")
                return
            
            # Display based on current filter
            self.display.display_header()
            self.display.display_stats_bar(suggestions)
            
            if self.current_filter == 'compact':
                self.display.display_compact_view(suggestions)
            elif self.current_filter == 'stats':
                self.display.display_priority_distribution(suggestions)
            else:
                count = self.display.display_suggestions_grouped(
                    suggestions, 
                    self.current_filter, 
                    self.filter_value
                )
            
            # Show options
            self._show_action_menu()
            
            # Get user input
            choice = input(f"\n{Colors.BLUE}Select option: {Colors.RESET}").strip().lower()
            
            if choice == 'q' or choice == 'skip':
                return
            elif choice == 'a':
                self.current_filter = 'all'
                self.filter_value = None
            elif choice == 'c':
                self._filter_by_category(suggestions)
            elif choice == 'p':
                self._filter_by_priority()
            elif choice == 'v':
                self.current_filter = 'compact'
            elif choice == 's':
                self.current_filter = 'stats'
            elif choice.startswith('d'):
                self._handle_development_trigger(choice, suggestions)
            elif choice == 'all':
                self._promote_all_suggestions(suggestions)
            elif ',' in choice or choice.isdigit():
                self._handle_promotion(choice, suggestions)
    
    def _show_action_menu(self):
        """Show available actions"""
        print(f"\n{Colors.BOLD}⚡ Actions:{Colors.RESET}")
        print(f"{'─'*80}")
        print(f"  • Enter number(s) to promote (e.g., {Colors.CYAN}1,3,5{Colors.RESET})")
        print(f"  • Enter '{Colors.CYAN}all{Colors.RESET}' to promote all")
        print(f"  • Enter '{Colors.CYAN}d{Colors.RESET}' + number for Claude development (e.g., {Colors.CYAN}d3{Colors.RESET})")
        print(f"  • Enter '{Colors.CYAN}a/c/p/v/s{Colors.RESET}' for filters")
        print(f"  • Enter '{Colors.CYAN}q{Colors.RESET}' or '{Colors.CYAN}skip{Colors.RESET}' to return")
        print(f"{'─'*80}")
    
    def _filter_by_category(self, suggestions: Dict[str, List[Dict]]):
        """Interactive category filter"""
        categories = self.display.get_category_list(suggestions)
        
        print(f"\n{Colors.BOLD}Select Category:{Colors.RESET}")
        for i, category in enumerate(categories, 1):
            icon = self.display.category_icons.get(category, '📌')
            color = self.display.category_colors.get(category, Colors.WHITE)
            count = len(suggestions[category])
            print(f"  {i}. {color}{icon} {category}{Colors.RESET} ({count} items)")
        
        try:
            selection = input(f"\n{Colors.BLUE}Category number: {Colors.RESET}")
            idx = int(selection) - 1
            if 0 <= idx < len(categories):
                self.current_filter = 'category'
                self.filter_value = categories[idx]
            else:
                print(f"{Colors.RED}Invalid selection{Colors.RESET}")
        except:
            print(f"{Colors.RED}Invalid input{Colors.RESET}")
    
    def _filter_by_priority(self):
        """Interactive priority filter"""
        print(f"\n{Colors.BOLD}Select Priority:{Colors.RESET}")
        priorities = ['critical', 'high', 'medium', 'low']
        
        for i, priority in enumerate(priorities, 1):
            badge = self.display.priority_badges.get(priority, priority)
            print(f"  {i}. {badge}")
        
        try:
            selection = input(f"\n{Colors.BLUE}Priority number: {Colors.RESET}")
            idx = int(selection) - 1
            if 0 <= idx < len(priorities):
                self.current_filter = 'priority'
                self.filter_value = priorities[idx]
            else:
                print(f"{Colors.RED}Invalid selection{Colors.RESET}")
        except:
            print(f"{Colors.RED}Invalid input{Colors.RESET}")
    
    def _handle_development_trigger(self, choice: str, suggestions: Dict[str, List[Dict]]):
        """Handle development trigger for a specific suggestion"""
        try:
            # Get all suggestions in order
            all_suggestions = self.display.format_for_selection(suggestions)
            
            # Extract number
            dev_index = int(choice[1:].strip()) - 1
            
            if 0 <= dev_index < len(all_suggestions):
                suggestion = all_suggestions[dev_index]
                self.cli.trigger_claude_development(
                    suggestion['text'], 
                    suggestion['category']
                )
            else:
                print(f"{Colors.RED}Invalid suggestion number{Colors.RESET}")
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        except:
            print(f"{Colors.RED}Invalid development selection{Colors.RESET}")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
    
    def _handle_promotion(self, choice: str, suggestions: Dict[str, List[Dict]]):
        """Handle promotion of selected suggestions"""
        try:
            all_suggestions = self.display.format_for_selection(suggestions)
            
            # Parse selection
            if ',' in choice:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
            else:
                indices = [int(choice.strip()) - 1]
            
            # Validate indices
            valid_indices = [i for i in indices if 0 <= i < len(all_suggestions)]
            
            if valid_indices:
                selected_suggestions = [all_suggestions[i] for i in valid_indices]
                self._promote_suggestions(selected_suggestions)
            else:
                print(f"{Colors.RED}Invalid selection{Colors.RESET}")
                input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        except:
            print(f"{Colors.RED}Invalid selection format{Colors.RESET}")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
    
    def _promote_all_suggestions(self, suggestions: Dict[str, List[Dict]]):
        """Promote all suggestions to active list"""
        all_suggestions = self.display.format_for_selection(suggestions)
        
        if len(all_suggestions) > 20:
            confirm = input(f"\n{Colors.YELLOW}This will promote {len(all_suggestions)} suggestions. Continue? (y/n): {Colors.RESET}")
            if confirm.lower() != 'y':
                return
        
        self._promote_suggestions(all_suggestions)
    
    def _promote_suggestions(self, selected_suggestions: List[Dict]):
        """Actually promote the suggestions using Claude"""
        print(f"\n{Colors.YELLOW}Promoting {len(selected_suggestions)} suggestions...{Colors.RESET}")
        
        # Prepare context for Claude
        context = f"""
You are updating the CLAUDE_SUGGESTIONS.md file.
The user has selected {len(selected_suggestions)} suggestions from the pool to promote to active list.

Selected pool suggestions:
"""
        for item in selected_suggestions:
            priority_icon = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(item['priority'], '🟢')
            
            context += f"\n- {priority_icon} [{item['category']}] {item['text']}"
        
        context += """

Please incorporate these into the active suggestions list.
You should:
1. Evaluate each pool suggestion based on its priority
2. Add proper Sorun/Çözüm/Dosya details
3. Replace lower priority items if needed
4. Keep the most important/relevant suggestions
5. Maintain proper formatting

Return ONLY the updated suggestions content in the exact format required.
"""
        
        response, error = self.cli.execute_claude_command(
            "Update active suggestions with selected pool items",
            context
        )
        
        if error:
            print(f"{Colors.RED}Error: {error}{Colors.RESET}")
        else:
            # Save the updated suggestions
            self.cli.save_suggestions_to_file(response)
            print(f"\n{Colors.GREEN}✅ Suggestions promoted successfully{Colors.RESET}")
            
            # Show what was promoted
            print(f"\n{Colors.CYAN}Promoted suggestions:{Colors.RESET}")
            for item in selected_suggestions:
                print(f"  • {item['text'][:60]}...")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")


def integrate_enhanced_display(claude_cli_instance):
    """Factory function to create integration instance"""
    return PoolDisplayIntegration(claude_cli_instance)


# Example integration point for claude_cli.py:
"""
# In claude_cli.py, replace show_pool_suggestions method with:

def show_pool_suggestions(self):
    from enhanced_pool_integration import integrate_enhanced_display
    enhanced_display = integrate_enhanced_display(self)
    enhanced_display.show_enhanced_pool()
"""