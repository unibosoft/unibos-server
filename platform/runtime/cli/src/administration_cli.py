#!/usr/bin/env python3
"""
administration cli module
provides administrative functions for unibos cli
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from database.db_manager import DatabaseManager
except ImportError:
    # If DatabaseManager not available, create a simple one
    class DatabaseManager:
        def __init__(self):
            self.conn = None
            
        def get_connection(self):
            """Get database connection"""
            try:
                import sqlite3
                # Try SQLite first as fallback
                conn = sqlite3.connect(Path(__file__).parent.parent / 'backend' / 'db.sqlite3')
                return conn
            except:
                return None

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    ORANGE = '\033[38;5;208m'
    GRAY = '\033[90m'
    DIM = '\033[2m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'


class AdministrationCLI:
    """CLI administration interface"""
    
    def __init__(self):
        """Initialize administration CLI"""
        self.db = DatabaseManager()
        self.current_section = 'main'
        self.running = True
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def draw_header(self):
        """Draw administration header"""
        print(f"\n{Colors.CYAN}{'─' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}  🔐 administration panel{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}\n")
        
    def draw_menu(self):
        """Draw main administration menu"""
        options = [
            ('solitaire', '🎮 solitaire management'),
            ('users', '👥 user management'),
            ('system', '⚙️ system settings'),
            ('logs', '📋 system logs'),
            ('back', '← back to main menu')
        ]
        
        print(f"{Colors.BOLD}administration modules:{Colors.RESET}\n")
        for key, label in options:
            print(f"  {Colors.CYAN}[{key[0]}]{Colors.RESET} {label}")
        print()
        
    def draw_solitaire_menu(self):
        """Draw solitaire administration menu"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎮 solitaire administration{Colors.RESET}\n")
        
        options = [
            ('stats', '📊 view statistics'),
            ('active', '🎯 active games'),
            ('players', '👥 player rankings'),
            ('history', '📜 game history'),
            ('clean', '🧹 cleanup old sessions'),
            ('back', '← back')
        ]
        
        for key, label in options:
            print(f"  {Colors.CYAN}[{key[0]}]{Colors.RESET} {label}")
        print()
        
    def get_solitaire_stats(self):
        """Get solitaire statistics from database"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            
            # Get today's stats (SQLite compatible)
            cur.execute("""
                SELECT 
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN is_won = 1 THEN 1 END) as games_won,
                    COUNT(CASE WHEN is_abandoned = 1 THEN 1 END) as games_abandoned,
                    AVG(moves_count) as avg_moves,
                    AVG(score) as avg_score,
                    AVG(time_played) as avg_time
                FROM solitaire_solitairegamesession
                WHERE DATE(started_at) = DATE('now')
            """)
            
            today_stats = cur.fetchone()
            
            # Get all-time stats
            cur.execute("""
                SELECT 
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN is_won = true THEN 1 END) as games_won,
                    MAX(score) as highest_score,
                    MIN(CASE WHEN is_won = true THEN time_played END) as fastest_win
                FROM solitaire_solitairegamesession
            """)
            
            all_time_stats = cur.fetchone()
            
            cur.close()
            conn.close()
            
            return {
                'today': today_stats,
                'all_time': all_time_stats
            }
            
        except Exception as e:
            print(f"{Colors.RED}error getting stats: {e}{Colors.RESET}")
            return None
            
    def display_solitaire_stats(self):
        """Display solitaire statistics"""
        stats = self.get_solitaire_stats()
        if not stats:
            return
            
        self.clear_screen()
        print(f"\n{Colors.BOLD}{Colors.YELLOW}📊 solitaire statistics{Colors.RESET}\n")
        
        # Today's stats
        today = stats['today']
        print(f"{Colors.CYAN}today's statistics:{Colors.RESET}")
        print(f"  games played: {today[0] or 0}")
        print(f"  games won: {today[1] or 0}")
        print(f"  games abandoned: {today[2] or 0}")
        if today[0] and today[0] > 0:
            win_rate = (today[1] or 0) / today[0] * 100
            print(f"  win rate: {win_rate:.1f}%")
            print(f"  average moves: {today[3]:.0f}" if today[3] else "  average moves: n/a")
            print(f"  average score: {today[4]:.0f}" if today[4] else "  average score: n/a")
            print(f"  average time: {today[5]:.0f}s" if today[5] else "  average time: n/a")
        
        # All-time stats
        all_time = stats['all_time']
        print(f"\n{Colors.CYAN}all-time statistics:{Colors.RESET}")
        print(f"  total games: {all_time[0] or 0}")
        print(f"  total wins: {all_time[1] or 0}")
        if all_time[0] and all_time[0] > 0:
            win_rate = (all_time[1] or 0) / all_time[0] * 100
            print(f"  win rate: {win_rate:.1f}%")
        print(f"  highest score: {all_time[2] or 0}")
        if all_time[3]:
            print(f"  fastest win: {all_time[3]:.0f}s")
            
    def get_active_games(self):
        """Get currently active solitaire games"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    s.session_id,
                    p.display_name,
                    s.moves_count,
                    s.score,
                    s.time_played,
                    s.started_at
                FROM solitaire_solitairegamesession s
                JOIN solitaire_solitaireplayer p ON s.player_id = p.id
                WHERE s.is_completed = false
                ORDER BY s.started_at DESC
                LIMIT 10
            """)
            
            games = cur.fetchall()
            cur.close()
            conn.close()
            
            return games
            
        except Exception as e:
            print(f"{Colors.RED}error getting active games: {e}{Colors.RESET}")
            return []
            
    def display_active_games(self):
        """Display active solitaire games"""
        games = self.get_active_games()
        
        self.clear_screen()
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎯 active solitaire games{Colors.RESET}\n")
        
        if not games:
            print(f"{Colors.DIM}no active games{Colors.RESET}")
            return
            
        # Display header
        print(f"{Colors.CYAN}{'player':<20} {'moves':<10} {'score':<10} {'time':<10} {'started':<20}{Colors.RESET}")
        print(f"{Colors.DIM}{'-'*70}{Colors.RESET}")
        
        # Display games
        for game in games:
            session_id, player, moves, score, time_played, started = game
            
            # Format time
            if time_played:
                mins = int(time_played // 60)
                secs = int(time_played % 60)
                time_str = f"{mins}:{secs:02d}"
            else:
                time_str = "0:00"
                
            # Format started time
            if started:
                time_ago = datetime.now() - started.replace(tzinfo=None)
                if time_ago.days > 0:
                    started_str = f"{time_ago.days}d ago"
                elif time_ago.seconds > 3600:
                    started_str = f"{time_ago.seconds // 3600}h ago"
                elif time_ago.seconds > 60:
                    started_str = f"{time_ago.seconds // 60}m ago"
                else:
                    started_str = "just now"
            else:
                started_str = "unknown"
                
            print(f"{player[:20]:<20} {moves or 0:<10} {score or 0:<10} {time_str:<10} {started_str:<20}")
            
    def get_top_players(self):
        """Get top solitaire players"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    p.display_name,
                    COUNT(s.id) as games_played,
                    COUNT(CASE WHEN s.is_won = true THEN 1 END) as games_won,
                    MAX(s.score) as best_score,
                    AVG(s.score) as avg_score
                FROM solitaire_solitaireplayer p
                LEFT JOIN solitaire_solitairegamesession s ON p.id = s.player_id
                WHERE s.is_completed = true
                GROUP BY p.id, p.display_name
                HAVING COUNT(s.id) > 0
                ORDER BY games_won DESC, best_score DESC
                LIMIT 10
            """)
            
            players = cur.fetchall()
            cur.close()
            conn.close()
            
            return players
            
        except Exception as e:
            print(f"{Colors.RED}error getting top players: {e}{Colors.RESET}")
            return []
            
    def display_top_players(self):
        """Display top solitaire players"""
        players = self.get_top_players()
        
        self.clear_screen()
        print(f"\n{Colors.BOLD}{Colors.YELLOW}👥 top solitaire players{Colors.RESET}\n")
        
        if not players:
            print(f"{Colors.DIM}no player data{Colors.RESET}")
            return
            
        # Display header
        print(f"{Colors.CYAN}{'rank':<6} {'player':<20} {'played':<10} {'won':<10} {'win %':<10} {'best':<10}{Colors.RESET}")
        print(f"{Colors.DIM}{'-'*76}{Colors.RESET}")
        
        # Display players
        for idx, player in enumerate(players, 1):
            name, played, won, best_score, avg_score = player
            win_rate = (won / played * 100) if played > 0 else 0
            
            # Color code rank
            if idx == 1:
                rank_color = Colors.YELLOW
            elif idx <= 3:
                rank_color = Colors.CYAN
            else:
                rank_color = Colors.RESET
                
            print(f"{rank_color}{idx:<6}{Colors.RESET} {name[:20]:<20} {played:<10} {won:<10} {win_rate:<10.1f} {best_score or 0:<10}")
            
    def cleanup_old_sessions(self):
        """Clean up old abandoned solitaire sessions"""
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            
            # Count sessions to delete (older than 7 days and abandoned)
            cur.execute("""
                SELECT COUNT(*) 
                FROM solitaire_solitairegamesession
                WHERE is_abandoned = true 
                AND started_at < CURRENT_DATE - INTERVAL '7 days'
            """)
            
            count = cur.fetchone()[0]
            
            if count == 0:
                print(f"{Colors.GREEN}no old sessions to clean{Colors.RESET}")
                return
                
            print(f"{Colors.YELLOW}found {count} old abandoned sessions{Colors.RESET}")
            confirm = input(f"{Colors.CYAN}delete these sessions? (y/n): {Colors.RESET}")
            
            if confirm.lower() == 'y':
                # Delete old sessions
                cur.execute("""
                    DELETE FROM solitaire_solitairegamesession
                    WHERE is_abandoned = true 
                    AND started_at < CURRENT_DATE - INTERVAL '7 days'
                """)
                
                conn.commit()
                print(f"{Colors.GREEN}deleted {count} old sessions{Colors.RESET}")
            else:
                print(f"{Colors.DIM}cleanup cancelled{Colors.RESET}")
                
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"{Colors.RED}error during cleanup: {e}{Colors.RESET}")
            
    def handle_solitaire_admin(self):
        """Handle solitaire administration menu"""
        while True:
            self.clear_screen()
            self.draw_header()
            self.draw_solitaire_menu()
            
            choice = input(f"{Colors.CYAN}select option: {Colors.RESET}").lower()
            
            if choice == 's':
                self.display_solitaire_stats()
                input(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
            elif choice == 'a':
                self.display_active_games()
                input(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
            elif choice == 'p':
                self.display_top_players()
                input(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
            elif choice == 'h':
                print(f"{Colors.DIM}game history not yet implemented{Colors.RESET}")
                input(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
            elif choice == 'c':
                self.cleanup_old_sessions()
                input(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
            elif choice == 'b' or choice == 'q':
                break
                
    def run(self):
        """Run administration CLI"""
        while self.running:
            self.clear_screen()
            self.draw_header()
            self.draw_menu()
            
            choice = input(f"{Colors.CYAN}select module: {Colors.RESET}").lower()
            
            if choice == 's':
                self.handle_solitaire_admin()
            elif choice == 'u':
                print(f"{Colors.DIM}user management not yet implemented{Colors.RESET}")
                input(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
            elif choice == 'y':
                print(f"{Colors.DIM}system settings not yet implemented{Colors.RESET}")
                input(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
            elif choice == 'l':
                print(f"{Colors.DIM}system logs not yet implemented{Colors.RESET}")
                input(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
            elif choice == 'b' or choice == 'q':
                self.running = False
                break
                

if __name__ == "__main__":
    admin = AdministrationCLI()
    admin.run()