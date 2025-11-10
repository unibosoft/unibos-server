#!/usr/bin/env python3
"""
Administration UI module for UNIBOS
Integrated with main UI framework with arrow navigation
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

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

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def move_cursor(x, y):
    """Move cursor to position"""
    print(f'\033[{y};{x}H', end='')

def get_terminal_size():
    """Get terminal dimensions"""
    try:
        import shutil
        cols, lines = shutil.get_terminal_size()
        return cols, lines
    except:
        return 80, 24

def hide_cursor():
    """Hide terminal cursor"""
    print('\033[?25l', end='')

def show_cursor():
    """Show terminal cursor"""
    print('\033[?25h', end='')

def get_single_key(timeout=None):
    """Get single key press (stub for integration)"""
    # This will be handled by the main UI framework
    return None

def draw_box(x, y, width, height, title="", color=Colors.CYAN):
    """Draw a box (stub for integration)"""
    # This will be handled by the main UI framework
    pass

try:
    # Suppress warnings in UI context
    import sys
    import io
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    
    from database.db_manager import DatabaseManager
    
    # Restore stderr
    sys.stderr = old_stderr
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


class AdministrationUI:
    """Administration UI integrated with main framework"""
    
    def __init__(self):
        """Initialize administration UI"""
        self.db = DatabaseManager()
        self.current_menu = 'main'
        self.menu_index = 0
        self.submenu_index = 0
        self.running = True
        self.message = ""
        
        # Menu items
        self.main_menu_items = [
            ('solitaire', '🎮 solitaire management', 'game statistics & monitoring'),
            ('users', '👥 user management', 'manage user accounts'),
            ('system', '⚙️ system settings', 'configure system options'),
            ('logs', '📋 system logs', 'view system activity'),
            ('back', '← back to tools', 'return to tools menu')
        ]
        
        self.solitaire_menu_items = [
            ('stats', '📊 view statistics', 'overall game statistics'),
            ('active', '🎯 active games', 'currently playing sessions'),
            ('players', '👥 player rankings', 'top players leaderboard'),
            ('history', '📜 game history', 'recent game sessions'),
            ('clean', '🧹 cleanup sessions', 'remove old abandoned games'),
            ('back', '← back', 'return to main menu')
        ]
        
    def draw_content(self, x, y, width, height):
        """Draw the administration content"""
        # Clear content area first
        for line in range(y, y + height):
            move_cursor(x, line)
            print(' ' * width, end='')
        
        # Draw based on current menu
        if self.current_menu == 'main':
            self.draw_main_menu(x, y, width, height)
        elif self.current_menu == 'solitaire':
            self.draw_solitaire_menu(x, y, width, height)
        elif self.current_menu == 'solitaire_stats':
            self.draw_solitaire_stats(x, y, width, height)
        elif self.current_menu == 'active_games':
            self.draw_active_games(x, y, width, height)
        elif self.current_menu == 'top_players':
            self.draw_top_players(x, y, width, height)
        elif self.current_menu == 'cleanup':
            self.draw_cleanup(x, y, width, height)
            
    def draw_main_menu(self, x, y, width, height):
        """Draw main administration menu"""
        # Title
        move_cursor(x + 2, y)
        print(f"{Colors.BOLD}{Colors.YELLOW}🔐 administration panel{Colors.RESET}")
        
        # Menu items
        start_y = y + 2
        for idx, (key, label, desc) in enumerate(self.main_menu_items):
            item_y = start_y + idx * 2
            if item_y >= y + height - 2:
                break
                
            move_cursor(x + 4, item_y)
            if idx == self.menu_index:
                print(f"{Colors.CYAN}▶ {label}{Colors.RESET}")
                move_cursor(x + 6, item_y + 1)
                print(f"{Colors.DIM}{desc}{Colors.RESET}")
            else:
                print(f"  {Colors.WHITE}{label}{Colors.RESET}")
                
        # Show message if any
        if self.message:
            move_cursor(x + 2, y + height - 3)
            print(f"{Colors.GREEN}{self.message}{Colors.RESET}")
            
    def draw_solitaire_menu(self, x, y, width, height):
        """Draw solitaire administration menu"""
        # Title
        move_cursor(x + 2, y)
        print(f"{Colors.BOLD}{Colors.GREEN}🎮 solitaire administration{Colors.RESET}")
        
        # Menu items
        start_y = y + 2
        for idx, (key, label, desc) in enumerate(self.solitaire_menu_items):
            item_y = start_y + idx * 2
            if item_y >= y + height - 2:
                break
                
            move_cursor(x + 4, item_y)
            if idx == self.submenu_index:
                print(f"{Colors.CYAN}▶ {label}{Colors.RESET}")
                move_cursor(x + 6, item_y + 1)
                print(f"{Colors.DIM}{desc}{Colors.RESET}")
            else:
                print(f"  {Colors.WHITE}{label}{Colors.RESET}")
                
    def draw_solitaire_stats(self, x, y, width, height):
        """Draw solitaire statistics"""
        stats = self.get_solitaire_stats()
        
        # Title
        move_cursor(x + 2, y)
        print(f"{Colors.BOLD}{Colors.YELLOW}📊 solitaire statistics{Colors.RESET}")
        
        if not stats:
            move_cursor(x + 4, y + 2)
            print(f"{Colors.RED}error loading statistics{Colors.RESET}")
            return
            
        line_y = y + 2
        
        # Today's stats
        today = stats['today']
        move_cursor(x + 4, line_y)
        print(f"{Colors.CYAN}today's statistics:{Colors.RESET}")
        line_y += 1
        
        stats_lines = [
            f"games played: {today[0] or 0}",
            f"games won: {today[1] or 0}",
            f"games abandoned: {today[2] or 0}"
        ]
        
        if today[0] and today[0] > 0:
            win_rate = (today[1] or 0) / today[0] * 100
            stats_lines.append(f"win rate: {win_rate:.1f}%")
            if today[3]:
                stats_lines.append(f"average moves: {today[3]:.0f}")
            if today[4]:
                stats_lines.append(f"average score: {today[4]:.0f}")
                
        for line in stats_lines:
            if line_y >= y + height - 4:
                break
            move_cursor(x + 6, line_y)
            print(line)
            line_y += 1
            
        # All-time stats
        line_y += 1
        if line_y < y + height - 4:
            all_time = stats['all_time']
            move_cursor(x + 4, line_y)
            print(f"{Colors.CYAN}all-time statistics:{Colors.RESET}")
            line_y += 1
            
            all_time_lines = [
                f"total games: {all_time[0] or 0}",
                f"total wins: {all_time[1] or 0}"
            ]
            
            if all_time[0] and all_time[0] > 0:
                win_rate = (all_time[1] or 0) / all_time[0] * 100
                all_time_lines.append(f"win rate: {win_rate:.1f}%")
            if all_time[2]:
                all_time_lines.append(f"highest score: {all_time[2]}")
                
            for line in all_time_lines:
                if line_y >= y + height - 2:
                    break
                move_cursor(x + 6, line_y)
                print(line)
                line_y += 1
                
        # Back option
        move_cursor(x + 2, y + height - 2)
        print(f"{Colors.DIM}press [b] to go back{Colors.RESET}")
        
    def draw_active_games(self, x, y, width, height):
        """Draw active games list"""
        games = self.get_active_games()
        
        # Title
        move_cursor(x + 2, y)
        print(f"{Colors.BOLD}{Colors.GREEN}🎯 active solitaire games{Colors.RESET}")
        
        if not games:
            move_cursor(x + 4, y + 2)
            print(f"{Colors.DIM}no active games{Colors.RESET}")
        else:
            # Header
            move_cursor(x + 4, y + 2)
            print(f"{Colors.CYAN}player           moves  score  time{Colors.RESET}")
            move_cursor(x + 4, y + 3)
            print(f"{Colors.DIM}{'-' * 36}{Colors.RESET}")
            
            # Games
            line_y = y + 4
            for game in games[:10]:  # Show max 10 games
                if line_y >= y + height - 2:
                    break
                    
                session_id, player, moves, score, time_played, started = game
                
                # Format time
                if time_played:
                    mins = int(time_played // 60)
                    secs = int(time_played % 60)
                    time_str = f"{mins}:{secs:02d}"
                else:
                    time_str = "0:00"
                    
                # Format player name
                player_name = (player or "anonymous")[:15]
                
                move_cursor(x + 4, line_y)
                print(f"{player_name:<15}  {moves or 0:<5}  {score or 0:<5}  {time_str}")
                line_y += 1
                
        # Back option
        move_cursor(x + 2, y + height - 2)
        print(f"{Colors.DIM}press [b] to go back{Colors.RESET}")
        
    def draw_top_players(self, x, y, width, height):
        """Draw top players leaderboard"""
        players = self.get_top_players()
        
        # Title
        move_cursor(x + 2, y)
        print(f"{Colors.BOLD}{Colors.YELLOW}👥 top solitaire players{Colors.RESET}")
        
        if not players:
            move_cursor(x + 4, y + 2)
            print(f"{Colors.DIM}no player data{Colors.RESET}")
        else:
            # Header
            move_cursor(x + 4, y + 2)
            print(f"{Colors.CYAN}rank  player         played  won  win%{Colors.RESET}")
            move_cursor(x + 4, y + 3)
            print(f"{Colors.DIM}{'-' * 40}{Colors.RESET}")
            
            # Players
            line_y = y + 4
            for idx, player in enumerate(players[:10], 1):
                if line_y >= y + height - 2:
                    break
                    
                name, played, won, best_score, avg_score = player
                win_rate = (won / played * 100) if played > 0 else 0
                
                # Color code rank
                if idx == 1:
                    rank_color = Colors.YELLOW
                elif idx <= 3:
                    rank_color = Colors.CYAN
                else:
                    rank_color = Colors.WHITE
                    
                # Format name
                player_name = (name or "unknown")[:13]
                
                move_cursor(x + 4, line_y)
                print(f"{rank_color}{idx:<4}{Colors.RESET}  {player_name:<13}  {played:<6}  {won:<3}  {win_rate:>4.0f}%")
                line_y += 1
                
        # Back option
        move_cursor(x + 2, y + height - 2)
        print(f"{Colors.DIM}press [b] to go back{Colors.RESET}")
        
    def draw_cleanup(self, x, y, width, height):
        """Draw cleanup confirmation"""
        move_cursor(x + 2, y)
        print(f"{Colors.BOLD}{Colors.YELLOW}🧹 cleanup old sessions{Colors.RESET}")
        
        move_cursor(x + 4, y + 2)
        print(f"this will remove abandoned games older than 7 days")
        
        move_cursor(x + 4, y + 4)
        print(f"{Colors.YELLOW}press [y] to confirm or [n] to cancel{Colors.RESET}")
        
    def get_solitaire_stats(self):
        """Get solitaire statistics from database"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return None
                
            cur = conn.cursor()
            
            # Get today's stats
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
                    COUNT(CASE WHEN is_won = 1 THEN 1 END) as games_won,
                    MAX(score) as highest_score,
                    MIN(CASE WHEN is_won = 1 THEN time_played END) as fastest_win
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
            return None
            
    def get_active_games(self):
        """Get currently active solitaire games"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
                
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
                WHERE s.is_completed = 0
                ORDER BY s.started_at DESC
                LIMIT 10
            """)
            
            games = cur.fetchall()
            cur.close()
            conn.close()
            
            return games
            
        except Exception:
            return []
            
    def get_top_players(self):
        """Get top solitaire players"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
                
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    p.display_name,
                    COUNT(s.id) as games_played,
                    COUNT(CASE WHEN s.is_won = 1 THEN 1 END) as games_won,
                    MAX(s.score) as best_score,
                    AVG(s.score) as avg_score
                FROM solitaire_solitaireplayer p
                LEFT JOIN solitaire_solitairegamesession s ON p.id = s.player_id
                WHERE s.is_completed = 1
                GROUP BY p.id, p.display_name
                HAVING COUNT(s.id) > 0
                ORDER BY games_won DESC, best_score DESC
                LIMIT 10
            """)
            
            players = cur.fetchall()
            cur.close()
            conn.close()
            
            return players
            
        except Exception:
            return []
            
    def cleanup_old_sessions(self):
        """Clean up old abandoned sessions"""
        try:
            conn = self.db.get_connection()
            if not conn:
                self.message = "database connection failed"
                return
                
            cur = conn.cursor()
            
            # Count sessions to delete
            cur.execute("""
                SELECT COUNT(*) 
                FROM solitaire_solitairegamesession
                WHERE is_abandoned = 1 
                AND started_at < date('now', '-7 days')
            """)
            
            count = cur.fetchone()[0]
            
            if count == 0:
                self.message = "no old sessions to clean"
            else:
                # Delete old sessions
                cur.execute("""
                    DELETE FROM solitaire_solitairegamesession
                    WHERE is_abandoned = 1 
                    AND started_at < date('now', '-7 days')
                """)
                
                conn.commit()
                self.message = f"deleted {count} old sessions"
                
            cur.close()
            conn.close()
            
        except Exception as e:
            self.message = f"cleanup failed: {str(e)}"
            
    def handle_input(self, key):
        """Handle keyboard input"""
        if self.current_menu == 'main':
            if key in ['\x1b[A', 'w']:  # Up arrow or W
                self.menu_index = max(0, self.menu_index - 1)
            elif key in ['\x1b[B', 's']:  # Down arrow or S
                self.menu_index = min(len(self.main_menu_items) - 1, self.menu_index + 1)
            elif key in ['\r', ' ']:  # Enter or Space
                selected = self.main_menu_items[self.menu_index][0]
                if selected == 'solitaire':
                    self.current_menu = 'solitaire'
                    self.submenu_index = 0
                elif selected == 'back':
                    return False  # Exit
                else:
                    self.message = f"{selected} not yet implemented"
            elif key in ['q', '\x1b']:  # Q or ESC
                return False
                
        elif self.current_menu == 'solitaire':
            if key in ['\x1b[A', 'w']:  # Up arrow or W
                self.submenu_index = max(0, self.submenu_index - 1)
            elif key in ['\x1b[B', 's']:  # Down arrow or S
                self.submenu_index = min(len(self.solitaire_menu_items) - 1, self.submenu_index + 1)
            elif key in ['\r', ' ']:  # Enter or Space
                selected = self.solitaire_menu_items[self.submenu_index][0]
                if selected == 'stats':
                    self.current_menu = 'solitaire_stats'
                elif selected == 'active':
                    self.current_menu = 'active_games'
                elif selected == 'players':
                    self.current_menu = 'top_players'
                elif selected == 'clean':
                    self.current_menu = 'cleanup'
                elif selected == 'back':
                    self.current_menu = 'main'
                    self.menu_index = 0
                else:
                    self.message = f"{selected} not yet implemented"
            elif key in ['b', '\x1b']:  # B or ESC
                self.current_menu = 'main'
                self.menu_index = 0
                
        elif self.current_menu in ['solitaire_stats', 'active_games', 'top_players']:
            if key in ['b', '\x1b', 'q']:  # Back
                self.current_menu = 'solitaire'
                self.submenu_index = 0
                
        elif self.current_menu == 'cleanup':
            if key == 'y':
                self.cleanup_old_sessions()
                self.current_menu = 'solitaire'
                self.submenu_index = 0
            elif key in ['n', '\x1b', 'b']:
                self.current_menu = 'solitaire'
                self.submenu_index = 0
                
        return True