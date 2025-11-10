#!/usr/bin/env python3
"""
Administration menu module for UNIBOS
Works exactly like version_manager with proper sidebar integration
"""

import sys
import time
import subprocess
from pathlib import Path

# Database connection handling
class DatabaseManager:
    """Simple database manager for administration"""
    def __init__(self):
        self.conn = None
        
    def get_connection(self):
        """Get database connection - SQLite fallback"""
        try:
            import sqlite3
            # Use Django's SQLite database
            db_path = Path(__file__).parent.parent / 'backend' / 'db.sqlite3'
            if db_path.exists():
                conn = sqlite3.connect(db_path)
                return conn
        except Exception:
            pass
        return None

def get_administration_options():
    """Get administration menu options - structured like version manager"""
    return [
        # Solitaire Management
        ("header", "🎮 solitaire management", ""),
        ("solitaire_stats", "📊 view statistics", "overall game statistics"),
        ("solitaire_active", "🎯 active games", "currently playing sessions"),
        ("solitaire_players", "👥 player rankings", "top players leaderboard"),
        ("solitaire_cleanup", "🧹 cleanup sessions", "remove old abandoned games"),
        ("separator", "---", "---"),
        
        # User Management
        ("header", "👥 user management", ""),
        ("user_list", "📋 list users", "view all system users"),
        ("user_permissions", "🔐 permissions", "manage user permissions"),
        ("separator", "---", "---"),
        
        # System Management
        ("header", "⚙️ system management", ""),
        ("system_settings", "🔧 settings", "configure system options"),
        ("system_logs", "📋 view logs", "system activity logs"),
        ("system_health", "💚 health check", "system status overview"),
    ]

def draw_administration_menu():
    """Draw administration menu interface - exactly like version manager"""
    from main import (Colors, move_cursor, get_terminal_size, menu_state)
    
    cols, lines = get_terminal_size()
    content_x = 27  # After sidebar
    content_width = cols - content_x - 2
    
    # Get menu options
    options = get_administration_options()
    
    # Clear content area properly with ANSI escape sequences
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')  # Clear to end of line
    sys.stdout.flush()
    
    # Title - lowercase like version manager
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.CYAN}🔐 administration{Colors.RESET}")
    
    # Description - lowercase
    move_cursor(content_x + 2, 5)
    print(f"{Colors.YELLOW}system control & monitoring{Colors.RESET}")
    
    # Draw menu options
    y = 7
    option_index = 0
    
    for i, (key, name, desc) in enumerate(options):
        if key == "header":
            # Section header - blue like version manager
            move_cursor(content_x + 2, y)
            print(f"{Colors.BOLD}{Colors.BLUE}{name}{Colors.RESET}")
            y += 1
        elif key == "separator":
            # Separator line
            move_cursor(content_x + 2, y)
            print(f"{Colors.DIM}{'─' * 40}{Colors.RESET}")
            y += 1
        else:
            # Menu option
            is_selected = (option_index == menu_state.administration_index)
            
            move_cursor(content_x + 2, y)
            if is_selected:
                # Orange background selection like version manager
                print(f"{Colors.BG_ORANGE}{Colors.BLACK}{Colors.BOLD} → {name:<30} {Colors.RESET}", end='')
                # Show description on the right
                if desc:
                    print(f" {Colors.DIM}{desc}{Colors.RESET}")
                else:
                    print()
            else:
                print(f"   {name:<30}", end='')
                if desc:
                    print(f" {Colors.DIM}{desc}{Colors.RESET}")
                else:
                    print()
            
            option_index += 1
            y += 1
        
        # Prevent overflow
        if y >= lines - 3:
            break
    
    # Ensure everything is displayed
    sys.stdout.flush()

def show_solitaire_stats():
    """Display solitaire statistics"""
    from main import (Colors, move_cursor, get_terminal_size, get_single_key,
                      clear_screen, draw_header, draw_sidebar, draw_footer)
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Title
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.YELLOW}📊 solitaire statistics{Colors.RESET}")
    
    # Get stats from database
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        if not conn:
            move_cursor(content_x + 2, 5)
            print(f"{Colors.RED}database connection failed{Colors.RESET}")
        else:
            cur = conn.cursor()
            
            # Today's stats
            cur.execute("""
                SELECT 
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN is_won = 1 THEN 1 END) as games_won,
                    COUNT(CASE WHEN is_abandoned = 1 THEN 1 END) as games_abandoned,
                    AVG(moves_count) as avg_moves,
                    AVG(score) as avg_score
                FROM solitaire_solitairegamesession
                WHERE DATE(started_at) = DATE('now')
            """)
            today = cur.fetchone()
            
            # All-time stats
            cur.execute("""
                SELECT 
                    COUNT(*) as total_games,
                    COUNT(CASE WHEN is_won = 1 THEN 1 END) as games_won,
                    MAX(score) as highest_score
                FROM solitaire_solitairegamesession
            """)
            all_time = cur.fetchone()
            
            cur.close()
            conn.close()
            
            # Display today's stats
            y = 5
            move_cursor(content_x + 2, y)
            print(f"{Colors.CYAN}today's statistics:{Colors.RESET}")
            y += 2
            
            stats = [
                f"games played: {today[0] or 0}",
                f"games won: {today[1] or 0}",
                f"games abandoned: {today[2] or 0}"
            ]
            
            if today[0] and today[0] > 0:
                win_rate = (today[1] or 0) / today[0] * 100
                stats.append(f"win rate: {win_rate:.1f}%")
                if today[3]:
                    stats.append(f"average moves: {today[3]:.0f}")
                if today[4]:
                    stats.append(f"average score: {today[4]:.0f}")
            
            for stat in stats:
                move_cursor(content_x + 4, y)
                print(stat)
                y += 1
            
            # Display all-time stats
            y += 1
            move_cursor(content_x + 2, y)
            print(f"{Colors.CYAN}all-time statistics:{Colors.RESET}")
            y += 2
            
            all_stats = [
                f"total games: {all_time[0] or 0}",
                f"total wins: {all_time[1] or 0}"
            ]
            
            if all_time[0] and all_time[0] > 0:
                win_rate = (all_time[1] or 0) / all_time[0] * 100
                all_stats.append(f"win rate: {win_rate:.1f}%")
            if all_time[2]:
                all_stats.append(f"highest score: {all_time[2]}")
            
            for stat in all_stats:
                move_cursor(content_x + 4, y)
                print(stat)
                y += 1
                
    except Exception as e:
        move_cursor(content_x + 2, 5)
        print(f"{Colors.RED}error loading statistics{Colors.RESET}")
    
    # Press any key message
    move_cursor(content_x + 2, lines - 4)
    print(f"{Colors.DIM}press any key to return...{Colors.RESET}")
    sys.stdout.flush()
    
    # Wait for key
    get_single_key()
    
    # Redraw menu properly like version manager
    draw_administration_menu()

def administration_menu():
    """Administration submenu with system control tools - exactly like version_manager"""
    from main import (clear_screen, draw_header, draw_footer, draw_sidebar,
                      get_single_key, get_terminal_size, Colors, menu_state,
                      hide_cursor, draw_header_time_only, show_cursor, draw_main_screen)
    
    # Set submenu state
    menu_state.in_submenu = 'administration'
    menu_state.administration_index = 0
    
    # Clear screen and redraw everything to start fresh
    clear_screen()
    draw_header()
    
    # Debug: Check if menu items are initialized
    import sys
    if not hasattr(menu_state, 'modules') or not menu_state.modules:
        # Initialize menu items if not already done
        from main import initialize_menu_items
        initialize_menu_items()
    
    # Force sidebar redraw to ensure dimmed state is applied
    menu_state.last_sidebar_cache_key = None
    # Use simple sidebar for proper display
    draw_sidebar()
    
    # Clear input buffer before starting
    TERMIOS_AVAILABLE = True
    try:
        import termios
    except ImportError:
        TERMIOS_AVAILABLE = False
    
    if TERMIOS_AVAILABLE:
        try:
            import termios
            for _ in range(3):
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                time.sleep(0.01)
        except:
            pass
    
    # Draw administration menu
    draw_administration_menu()
    draw_footer()
    
    # Hide cursor for better visual experience
    hide_cursor()
    
    # Track last footer update time for clock
    last_footer_update = time.time()
    
    
    while menu_state.in_submenu == 'administration':
        # Update header time every second
        current_time = time.time()
        if current_time - last_footer_update >= 1.0:
            draw_header_time_only()  # Use time-only update to prevent flickering
            last_footer_update = current_time
        
        # Get user input
        key = get_single_key(timeout=0.1)
        
        if key:
            # Get current options
            options = get_administration_options()
            # Filter out headers and separators for navigation
            selectable_options = [(k, n, d) for k, n, d in options if k not in ["header", "separator"]]
            
            if key in ['\x1b[A', 'k', 'K']:  # Up arrow or k
                if menu_state.administration_index > 0:
                    menu_state.administration_index -= 1
                    # Redraw header to prevent black spaces
                    draw_header()
                    draw_administration_menu()
            
            elif key in ['\x1b[B', 'j', 'J']:  # Down arrow or j
                if menu_state.administration_index < len(selectable_options) - 1:
                    menu_state.administration_index += 1
                    # Redraw header to prevent black spaces
                    draw_header()
                    draw_administration_menu()
            
            elif key == '\r' or key == '\x1b[C':  # Enter or Right arrow - FIXED
                if 0 <= menu_state.administration_index < len(selectable_options):
                    selected_key = selectable_options[menu_state.administration_index][0]
                    
                    if selected_key == "solitaire_stats":
                        show_solitaire_stats()
                        # Redraw menu properly after returning
                        draw_administration_menu()
                    
                    elif selected_key == "solitaire_active":
                        # Show active games
                        show_active_games()
                        # Redraw menu after returning like version manager
                        menu_state.in_submenu = 'administration'
                        # Clear caches to force fresh redraw
                        menu_state.last_sidebar_cache_key = None
                        if hasattr(menu_state, 'last_content_cache_key'):
                            menu_state.last_content_cache_key = None
                        # Clear and redraw everything
                        clear_screen()
                        draw_header()
                        draw_sidebar()
                        draw_administration_menu()
                        draw_footer()
                        # Force a full flush
                        sys.stdout.flush()
                    
                    elif selected_key == "solitaire_players":
                        # Show player rankings
                        show_player_rankings()
                        # Redraw menu after returning like version manager
                        menu_state.in_submenu = 'administration'
                        # Clear caches to force fresh redraw
                        menu_state.last_sidebar_cache_key = None
                        if hasattr(menu_state, 'last_content_cache_key'):
                            menu_state.last_content_cache_key = None
                        # Clear and redraw everything
                        clear_screen()
                        draw_header()
                        draw_sidebar()
                        draw_administration_menu()
                        draw_footer()
                        # Force a full flush
                        sys.stdout.flush()
                    
                    elif selected_key == "solitaire_cleanup":
                        # Cleanup sessions
                        cleanup_sessions()
                        # Redraw menu after returning like version manager
                        menu_state.in_submenu = 'administration'
                        # Clear caches to force fresh redraw
                        menu_state.last_sidebar_cache_key = None
                        if hasattr(menu_state, 'last_content_cache_key'):
                            menu_state.last_content_cache_key = None
                        # Clear and redraw everything
                        clear_screen()
                        draw_header()
                        draw_sidebar()
                        draw_administration_menu()
                        draw_footer()
                        # Force a full flush
                        sys.stdout.flush()
                    
                    else:
                        # Not implemented yet
                        print(f"\n{Colors.YELLOW}{selected_key} coming soon...{Colors.RESET}")
                        time.sleep(2)
                        draw_administration_menu()
            
            elif key in ['\x1b', '\x1b[D', 'q', 'Q']:  # ESC, Left Arrow, or q to exit
                # Exit administration menu - CRITICAL STATE RESET
                menu_state.in_submenu = None  # Clear submenu state FIRST
                
                # Update navigation position
                menu_state.current_section = 1  # tools section
                menu_state.selected_index = 6  # administration is at index 6 in tools
                
                # Clear any cache that might cause stale renders
                menu_state.last_sidebar_cache_key = None
                if hasattr(menu_state, 'sidebar_cache'):
                    menu_state.sidebar_cache = {}
                if hasattr(menu_state, '_sidebar_highlight_cache'):
                    delattr(menu_state, '_sidebar_highlight_cache')
                
                # Use the standard exit pattern like version_manager
                clear_screen()
                draw_main_screen()
                break
        
        # Small sleep to prevent CPU spinning
        time.sleep(0.01)
    
    # Show cursor when exiting
    show_cursor()

def show_active_games():
    """Display active solitaire games"""
    from main import (Colors, move_cursor, get_terminal_size, get_single_key)
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Title
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.GREEN}🎯 active solitaire games{Colors.RESET}")
    
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        if not conn:
            move_cursor(content_x + 2, 5)
            print(f"{Colors.RED}database connection failed{Colors.RESET}")
        else:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    s.session_id,
                    p.display_name,
                    s.moves_count,
                    s.score,
                    s.time_played
                FROM solitaire_solitairegamesession s
                JOIN solitaire_solitaireplayer p ON s.player_id = p.id
                WHERE s.is_completed = 0
                ORDER BY s.started_at DESC
                LIMIT 10
            """)
            
            games = cur.fetchall()
            cur.close()
            conn.close()
            
            if not games:
                move_cursor(content_x + 2, 5)
                print(f"{Colors.DIM}no active games{Colors.RESET}")
            else:
                # Header
                y = 5
                move_cursor(content_x + 2, y)
                print(f"{Colors.CYAN}{'player':<20} {'moves':<10} {'score':<10} {'time':<10}{Colors.RESET}")
                y += 1
                move_cursor(content_x + 2, y)
                print(f"{Colors.DIM}{'-' * 50}{Colors.RESET}")
                y += 2
                
                # Games
                for game in games:
                    session_id, player, moves, score, time_played = game
                    
                    # Format time
                    if time_played:
                        mins = int(time_played // 60)
                        secs = int(time_played % 60)
                        time_str = f"{mins}:{secs:02d}"
                    else:
                        time_str = "0:00"
                    
                    player_name = (player or "anonymous")[:18]
                    
                    move_cursor(content_x + 2, y)
                    print(f"{player_name:<20} {moves or 0:<10} {score or 0:<10} {time_str:<10}")
                    y += 1
                    
                    if y >= lines - 4:
                        break
                        
    except Exception as e:
        move_cursor(content_x + 2, 5)
        print(f"{Colors.RED}error loading games{Colors.RESET}")
    
    # Press any key message
    move_cursor(content_x + 2, lines - 4)
    print(f"{Colors.DIM}press any key to return...{Colors.RESET}")
    sys.stdout.flush()
    
    # Wait for key
    get_single_key()

def show_player_rankings():
    """Display top player rankings"""
    from main import (Colors, move_cursor, get_terminal_size, get_single_key)
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Title
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.YELLOW}👥 top solitaire players{Colors.RESET}")
    
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        if not conn:
            move_cursor(content_x + 2, 5)
            print(f"{Colors.RED}database connection failed{Colors.RESET}")
        else:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    p.display_name,
                    COUNT(s.id) as games_played,
                    COUNT(CASE WHEN s.is_won = 1 THEN 1 END) as games_won,
                    MAX(s.score) as best_score
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
            
            if not players:
                move_cursor(content_x + 2, 5)
                print(f"{Colors.DIM}no player data{Colors.RESET}")
            else:
                # Header
                y = 5
                move_cursor(content_x + 2, y)
                print(f"{Colors.CYAN}{'rank':<6} {'player':<20} {'played':<10} {'won':<10} {'win%':<8}{Colors.RESET}")
                y += 1
                move_cursor(content_x + 2, y)
                print(f"{Colors.DIM}{'-' * 54}{Colors.RESET}")
                y += 2
                
                # Players
                for idx, player in enumerate(players, 1):
                    name, played, won, best_score = player
                    win_rate = (won / played * 100) if played > 0 else 0
                    
                    # Color code rank
                    if idx == 1:
                        rank_color = Colors.YELLOW
                    elif idx <= 3:
                        rank_color = Colors.CYAN
                    else:
                        rank_color = Colors.WHITE
                    
                    player_name = (name or "unknown")[:18]
                    
                    move_cursor(content_x + 2, y)
                    print(f"{rank_color}{idx:<6}{Colors.RESET} {player_name:<20} {played:<10} {won:<10} {win_rate:>7.1f}%")
                    y += 1
                    
                    if y >= lines - 4:
                        break
                        
    except Exception as e:
        move_cursor(content_x + 2, 5)
        print(f"{Colors.RED}error loading rankings{Colors.RESET}")
    
    # Press any key message
    move_cursor(content_x + 2, lines - 4)
    print(f"{Colors.DIM}press any key to return...{Colors.RESET}")
    sys.stdout.flush()
    
    # Wait for key
    get_single_key()

def cleanup_sessions():
    """Clean up old abandoned sessions"""
    from main import (Colors, move_cursor, get_terminal_size, get_single_key)
    
    cols, lines = get_terminal_size()
    content_x = 27
    
    # Clear content area
    for y in range(2, lines - 2):
        move_cursor(content_x, y)
        sys.stdout.write('\033[K')
    sys.stdout.flush()
    
    # Title
    move_cursor(content_x + 2, 3)
    print(f"{Colors.BOLD}{Colors.YELLOW}🧹 cleanup old sessions{Colors.RESET}")
    
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        if not conn:
            move_cursor(content_x + 2, 5)
            print(f"{Colors.RED}database connection failed{Colors.RESET}")
        else:
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
                move_cursor(content_x + 2, 5)
                print(f"{Colors.GREEN}no old sessions to clean{Colors.RESET}")
            else:
                move_cursor(content_x + 2, 5)
                print(f"found {Colors.YELLOW}{count}{Colors.RESET} abandoned sessions older than 7 days")
                
                move_cursor(content_x + 2, 7)
                print(f"press {Colors.CYAN}[y]{Colors.RESET} to delete or {Colors.CYAN}[n]{Colors.RESET} to cancel")
                
                sys.stdout.flush()
                
                # Wait for user input
                key = get_single_key()
                
                if key and key.lower() == 'y':
                    # Delete old sessions
                    cur.execute("""
                        DELETE FROM solitaire_solitairegamesession
                        WHERE is_abandoned = 1 
                        AND started_at < date('now', '-7 days')
                    """)
                    
                    conn.commit()
                    
                    move_cursor(content_x + 2, 9)
                    print(f"{Colors.GREEN}✓ deleted {count} old sessions{Colors.RESET}")
                else:
                    move_cursor(content_x + 2, 9)
                    print(f"{Colors.DIM}cleanup cancelled{Colors.RESET}")
            
            cur.close()
            conn.close()
            
    except Exception as e:
        move_cursor(content_x + 2, 5)
        print(f"{Colors.RED}error during cleanup: {str(e)[:40]}{Colors.RESET}")
    
    # Press any key message
    move_cursor(content_x + 2, lines - 4)
    print(f"{Colors.DIM}press any key to return...{Colors.RESET}")
    sys.stdout.flush()
    
    # Wait for key
    get_single_key()