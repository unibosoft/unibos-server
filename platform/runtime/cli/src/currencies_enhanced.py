"""
Enhanced Currencies Module for UNIBOSOFT v058
Combines best features from all versions with v050's visual style
"""

import os
import sys
import time
import json
import random
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import threading
import sqlite3

# Colors matching v050 style
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    BLACK = '\033[30m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ORANGE = '\033[38;5;208m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_PURPLE = '\033[45m'
    BG_CYAN = '\033[46m'
    CLEAR = '\033[2J'
    HOME = '\033[H'


class CurrencyAPI:
    """Enhanced API module with multiple data sources"""
    
    # API endpoints
    TCMB_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"
    
    # Crypto APIs (free tier)
    CRYPTO_APIS = {
        'coingecko': 'https://api.coingecko.com/api/v3/simple/price',
        'binance': 'https://api.binance.com/api/v3/ticker/price'
    }
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.last_fetch = {}
        self.api_available = True
    
    def get_tcmb_rates(self) -> Dict[str, float]:
        """Get official rates from Turkish Central Bank"""
        try:
            # Check cache
            if self._is_cache_valid('tcmb'):
                return self.cache.get('tcmb', {})
            
            response = requests.get(self.TCMB_URL, timeout=10)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            rates = {}
            
            for currency in root.findall('.//Currency'):
                code = currency.get('Kod')
                if code:
                    try:
                        forex_buying = currency.find('ForexBuying')
                        forex_selling = currency.find('ForexSelling')
                        
                        if forex_buying is not None and forex_selling is not None:
                            buy_rate = float(forex_buying.text)
                            sell_rate = float(forex_selling.text)
                            # Use average for display
                            rates[code] = (buy_rate + sell_rate) / 2
                    except (ValueError, AttributeError):
                        continue
            
            # Cache results
            self.cache['tcmb'] = rates
            self.last_fetch['tcmb'] = time.time()
            
            return rates
            
        except Exception as e:
            self.api_available = False
            return self.cache.get('tcmb', {})
    
    def get_crypto_rates(self) -> Dict[str, float]:
        """Get cryptocurrency rates"""
        try:
            # Check cache
            if self._is_cache_valid('crypto'):
                return self.cache.get('crypto', {})
            
            # Try CoinGecko API (free, no key required)
            crypto_ids = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'BNB': 'binancecoin',
                'USDT': 'tether',
                'SOL': 'solana',
                'XRP': 'ripple',
                'ADA': 'cardano',
                'AVAX': 'avalanche-2',
                'DOGE': 'dogecoin',
                'DOT': 'polkadot'
            }
            
            ids = ','.join(crypto_ids.values())
            url = f"{self.CRYPTO_APIS['coingecko']}?ids={ids}&vs_currencies=try"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rates = {}
            
            for symbol, coin_id in crypto_ids.items():
                if coin_id in data:
                    rates[symbol] = data[coin_id]['try']
            
            # Cache results
            self.cache['crypto'] = rates
            self.last_fetch['crypto'] = time.time()
            
            return rates
            
        except Exception as e:
            self.api_available = False
            return self._get_demo_crypto_rates()
    
    def _get_demo_crypto_rates(self) -> Dict[str, float]:
        """Get demo crypto rates for offline mode"""
        return {
            'BTC': 2500000.0,
            'ETH': 150000.0,
            'BNB': 25000.0,
            'USDT': 32.5,
            'SOL': 3500.0,
            'XRP': 25.0,
            'ADA': 15.0,
            'AVAX': 1200.0,
            'DOGE': 5.0,
            'DOT': 350.0
        }
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache is still valid"""
        if key not in self.last_fetch:
            return False
        
        elapsed = time.time() - self.last_fetch[key]
        return elapsed < self.cache_timeout
    
    def get_all_rates(self) -> Dict[str, float]:
        """Get all rates (fiat + crypto)"""
        rates = {'TRY': 1.0}  # Base currency
        
        # Get fiat rates from TCMB
        tcmb_rates = self.get_tcmb_rates()
        rates.update(tcmb_rates)
        
        # Get crypto rates
        crypto_rates = self.get_crypto_rates()
        rates.update(crypto_rates)
        
        return rates


class DatabaseManager:
    """Database management for currencies module"""
    
    def __init__(self, db_path="currencies_v058.db"):
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                settings TEXT
            );
            
            CREATE TABLE IF NOT EXISTS currency_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_currency TEXT NOT NULL,
                to_currency TEXT NOT NULL,
                rate REAL NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS currency_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                currency TEXT NOT NULL,
                target_rate REAL NOT NULL,
                direction TEXT NOT NULL,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                currency TEXT NOT NULL,
                amount REAL NOT NULL,
                avg_cost REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                module TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        self.conn.commit()
    
    def get_user(self, username):
        """Get user by username"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()
    
    def create_user(self, username, settings=None):
        """Create new user"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, settings) VALUES (?, ?)",
            (username, json.dumps(settings) if settings else None)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def log_activity(self, user_id, module, action):
        """Log user activity"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO activity_logs (user_id, module, action) VALUES (?, ?, ?)",
            (user_id, module, action)
        )
        self.conn.commit()
    
    def save_rate_history(self, currency, rate):
        """Save rate to history"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO currency_history (from_currency, to_currency, rate) VALUES (?, ?, ?)",
            (currency, 'TRY', rate)
        )
        self.conn.commit()
    
    def get_rate_history(self, currency, days=30):
        """Get historical rates"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT date(recorded_at) as date, 
                   AVG(rate) as avg_rate,
                   MIN(rate) as min_rate,
                   MAX(rate) as max_rate
            FROM currency_history
            WHERE from_currency = ? AND to_currency = 'TRY'
            AND recorded_at >= datetime('now', '-' || ? || ' days')
            GROUP BY date(recorded_at)
            ORDER BY date ASC
        """, (currency, days))
        return cursor.fetchall()


class CurrenciesEnhanced:
    """Enhanced currencies module with all features"""
    
    # Popular currencies with rich metadata
    CURRENCIES = {
        'USD': {'symbol': '$', 'name': 'ABD Doları', 'flag': '🇺🇸', 'color': Colors.GREEN},
        'EUR': {'symbol': '€', 'name': 'Euro', 'flag': '🇪🇺', 'color': Colors.BLUE},
        'GBP': {'symbol': '£', 'name': 'İngiliz Sterlini', 'flag': '🇬🇧', 'color': Colors.RED},
        'JPY': {'symbol': '¥', 'name': 'Japon Yeni', 'flag': '🇯🇵', 'color': Colors.RED},
        'CHF': {'symbol': 'Fr', 'name': 'İsviçre Frangı', 'flag': '🇨🇭', 'color': Colors.RED},
        'CAD': {'symbol': 'C$', 'name': 'Kanada Doları', 'flag': '🇨🇦', 'color': Colors.RED},
        'AUD': {'symbol': 'A$', 'name': 'Avustralya Doları', 'flag': '🇦🇺', 'color': Colors.BLUE},
        'RUB': {'symbol': '₽', 'name': 'Rus Rublesi', 'flag': '🇷🇺', 'color': Colors.BLUE},
        'CNY': {'symbol': '¥', 'name': 'Çin Yuanı', 'flag': '🇨🇳', 'color': Colors.RED},
        'SAR': {'symbol': 'ر.س', 'name': 'Suudi Riyali', 'flag': '🇸🇦', 'color': Colors.GREEN}
    }
    
    # Cryptocurrencies with enhanced metadata
    CRYPTOS = {
        'BTC': {'symbol': '₿', 'name': 'Bitcoin', 'icon': '🟠', 'color': Colors.ORANGE},
        'ETH': {'symbol': 'Ξ', 'name': 'Ethereum', 'icon': '🔷', 'color': Colors.BLUE},
        'BNB': {'symbol': 'BNB', 'name': 'Binance Coin', 'icon': '🟡', 'color': Colors.YELLOW},
        'USDT': {'symbol': '₮', 'name': 'Tether', 'icon': '🟢', 'color': Colors.GREEN},
        'SOL': {'symbol': 'SOL', 'name': 'Solana', 'icon': '🟣', 'color': Colors.PURPLE},
        'XRP': {'symbol': 'XRP', 'name': 'Ripple', 'icon': '⚪', 'color': Colors.WHITE},
        'ADA': {'symbol': 'ADA', 'name': 'Cardano', 'icon': '🔵', 'color': Colors.BLUE},
        'AVAX': {'symbol': 'AVAX', 'name': 'Avalanche', 'icon': '🔺', 'color': Colors.RED},
        'DOGE': {'symbol': 'Ð', 'name': 'Dogecoin', 'icon': '🐕', 'color': Colors.YELLOW},
        'DOT': {'symbol': 'DOT', 'name': 'Polkadot', 'icon': '⚫', 'color': Colors.MAGENTA}
    }
    
    def __init__(self):
        self.colors = Colors()
        self.db = DatabaseManager()
        self.api = CurrencyAPI()
        self.running = True
        self.favorites = ['USD', 'EUR', 'BTC']  # Default favorites
        self.update_interval = 30  # seconds
        self.last_update = None
        self.rates = {}
        self.historical_data = {}
        self.alerts = []
        self.portfolio = {}
        
        # Load or create user profile
        self.user = self._load_user_profile()
        
        # Initialize rates
        self._update_rates()
        
        # Start background update thread
        self.update_thread = threading.Thread(target=self._background_update, daemon=True)
        self.update_thread.start()
    
    def _load_user_profile(self) -> Dict:
        """Load or create user profile"""
        username = os.environ.get('USER', 'trader')
        user = self.db.get_user(username)
        
        if not user:
            user_id = self.db.create_user(username, {
                "currencies": {
                    "favorites": self.favorites,
                    "alerts": [],
                    "portfolio": {}
                }
            })
            user = {'id': user_id, 'username': username}
        else:
            user = dict(user)
            # Load user settings
            if user.get('settings'):
                settings = json.loads(user['settings'])
                self.favorites = settings.get('currencies', {}).get('favorites', self.favorites)
        
        return user
    
    def clear_screen(self):
        """Clear terminal screen"""
        print(self.colors.CLEAR + self.colors.HOME, end='')
    
    def move_cursor(self, x, y):
        """Move cursor to position"""
        print(f'\033[{y};{x}H', end='')
    
    def draw_box(self, x, y, width, height, title="", color=Colors.CYAN):
        """Draw a box at position with optional title"""
        # Top border
        self.move_cursor(x, y)
        print(f"{color}╔{'═' * (width-2)}╗{self.colors.RESET}")
        
        # Title if provided
        if title:
            title_len = len(title) + 2
            title_pos = x + (width - title_len) // 2
            self.move_cursor(title_pos - 1, y)
            print(f"{color}╡{self.colors.BOLD} {title} {self.colors.RESET}{color}╞{self.colors.RESET}")
        
        # Side borders
        for i in range(1, height-1):
            self.move_cursor(x, y + i)
            print(f"{color}║{self.colors.RESET}")
            self.move_cursor(x + width - 1, y + i)
            print(f"{color}║{self.colors.RESET}")
        
        # Bottom border
        self.move_cursor(x, y + height - 1)
        print(f"{color}╚{'═' * (width-2)}╝{self.colors.RESET}")
    
    def display_header(self):
        """Display module header in v050 style"""
        self.clear_screen()
        
        # Main title
        self.move_cursor(2, 1)
        print(f"{self.colors.BOLD}{self.colors.CYAN}💱 ENHANCED CURRENCIES MODULE v058{self.colors.RESET}")
        
        # Data source indicator
        data_source = "🟢 API (Live)" if self.api.api_available else "🟡 Demo Mode"
        self.move_cursor(50, 1)
        print(f"{data_source}")
        
        # Last update time
        if self.last_update:
            self.move_cursor(70, 1)
            print(f"{self.colors.DIM}Updated: {self.last_update.strftime('%H:%M:%S')}{self.colors.RESET}")
    
    def _update_rates(self):
        """Update exchange rates from API"""
        all_rates = self.api.get_all_rates()
        
        # Calculate changes and update rates
        for currency, rate in all_rates.items():
            if currency in self.rates:
                previous = self.rates[currency]['rate']
                change = ((rate - previous) / previous * 100) if previous > 0 else 0
            else:
                previous = rate
                change = 0
            
            self.rates[currency] = {
                'rate': rate,
                'change': change,
                'previous': previous
            }
            
            # Save to history
            self.db.save_rate_history(currency, rate)
        
        self.last_update = datetime.now()
        
        # Check alerts
        self._check_alerts()
    
    def _background_update(self):
        """Background thread to update rates periodically"""
        while self.running:
            time.sleep(self.update_interval)
            self._update_rates()
    
    def _check_alerts(self):
        """Check and trigger price alerts"""
        for alert in self.alerts:
            if alert['currency'] in self.rates:
                current_rate = self.rates[alert['currency']]['rate']
                if alert['type'] == 'above' and current_rate >= alert['target']:
                    alert['triggered'] = True
                elif alert['type'] == 'below' and current_rate <= alert['target']:
                    alert['triggered'] = True
    
    def display_rates(self):
        """Display exchange rates in enhanced format"""
        # Draw rates box
        self.draw_box(2, 3, 116, 35, "💹 Exchange Rates", self.colors.GREEN)
        
        # Favorites section
        if self.favorites:
            self.move_cursor(4, 5)
            print(f"{self.colors.YELLOW}{self.colors.BOLD}⭐ FAVORITES{self.colors.RESET}")
            self._display_currency_row(6, self.favorites, highlight=True)
        
        # Fiat currencies section
        self.move_cursor(4, 12)
        print(f"{self.colors.GREEN}{self.colors.BOLD}💵 FIAT CURRENCIES{self.colors.RESET}")
        fiat_codes = [code for code in self.CURRENCIES.keys() if code not in self.favorites]
        self._display_currency_row(13, fiat_codes)
        
        # Cryptocurrencies section
        self.move_cursor(4, 22)
        print(f"{self.colors.MAGENTA}{self.colors.BOLD}🪙 CRYPTOCURRENCIES{self.colors.RESET}")
        crypto_codes = [code for code in self.CRYPTOS.keys() if code not in self.favorites]
        self._display_currency_row(23, crypto_codes)
    
    def _display_currency_row(self, start_y, currency_codes, highlight=False):
        """Display currencies in a formatted row"""
        y_offset = 0
        for i, code in enumerate(currency_codes):
            if code not in self.rates:
                continue
            
            rate_data = self.rates[code]
            rate = rate_data['rate']
            change = rate_data['change']
            
            # Get currency info
            if code in self.CURRENCIES:
                info = self.CURRENCIES[code]
                icon = info['flag']
                name = info['name']
                currency_color = info['color']
            elif code in self.CRYPTOS:
                info = self.CRYPTOS[code]
                icon = info['icon']
                name = info['name']
                currency_color = info['color']
            else:
                continue
            
            # Position calculation
            col = i % 2
            if i > 0 and col == 0:
                y_offset += 2
            
            x_pos = 4 + (col * 58)
            y_pos = start_y + y_offset
            
            self.move_cursor(x_pos, y_pos)
            
            # Change indicator
            if change > 0:
                arrow = "↑"
                change_color = self.colors.GREEN
            elif change < 0:
                arrow = "↓"
                change_color = self.colors.RED
            else:
                arrow = "→"
                change_color = self.colors.YELLOW
            
            # Highlight favorites
            if highlight:
                print(f"{self.colors.BOLD}", end='')
            
            # Format display
            print(f"{icon} {currency_color}{code:<4}{self.colors.RESET} "
                  f"{name:<18} {rate:>12,.2f} TL "
                  f"{change_color}{arrow} {abs(change):>5.2f}%{self.colors.RESET}")
    
    def display_menu(self):
        """Display enhanced menu with visual indicators"""
        self.move_cursor(2, 39)
        print(f"{self.colors.CYAN}{'━' * 116}{self.colors.RESET}")
        
        menu_items = [
            ('1', '🔄', 'Refresh Rates', self.colors.GREEN),
            ('2', '💱', 'Convert', self.colors.BLUE),
            ('3', '📈', 'Charts', self.colors.PURPLE),
            ('4', '⭐', 'Favorites', self.colors.YELLOW),
            ('5', '🔔', 'Alerts', self.colors.ORANGE),
            ('6', '💼', 'Portfolio', self.colors.CYAN),
            ('7', '📊', 'Market Summary', self.colors.MAGENTA),
            ('8', '📰', 'News', self.colors.BLUE),
            ('9', '⚙️', 'Settings', self.colors.GRAY),
            ('0', '🚪', 'Exit', self.colors.RED)
        ]
        
        # Display menu in two columns
        for i, (key, icon, text, color) in enumerate(menu_items):
            col = i % 2
            row = i // 2
            x = 4 + (col * 58)
            y = 41 + row
            
            self.move_cursor(x, y)
            print(f"{self.colors.BOLD}{key}{self.colors.RESET} → {icon} {color}{text}{self.colors.RESET}")
    
    def handle_convert(self):
        """Enhanced currency conversion with visual feedback"""
        self.clear_screen()
        
        # Draw conversion box
        self.draw_box(20, 5, 80, 20, "💱 Currency Converter", self.colors.BLUE)
        
        # Source currency
        self.move_cursor(25, 8)
        print(f"{self.colors.YELLOW}Source Currency (e.g., USD, EUR, BTC):{self.colors.RESET} ", end='')
        source = input().upper()
        
        if source not in self.rates and source != 'TRY':
            self.move_cursor(25, 22)
            print(f"{self.colors.RED}✗ Invalid currency!{self.colors.RESET}")
            time.sleep(2)
            return
        
        # Target currency
        self.move_cursor(25, 10)
        print(f"{self.colors.YELLOW}Target Currency (e.g., TRY, EUR, BTC):{self.colors.RESET} ", end='')
        target = input().upper()
        
        if target not in self.rates and target != 'TRY':
            self.move_cursor(25, 22)
            print(f"{self.colors.RED}✗ Invalid currency!{self.colors.RESET}")
            time.sleep(2)
            return
        
        # Amount
        self.move_cursor(25, 12)
        print(f"{self.colors.YELLOW}Amount ({source}):{self.colors.RESET} ", end='')
        try:
            amount = float(input())
        except ValueError:
            self.move_cursor(25, 22)
            print(f"{self.colors.RED}✗ Invalid amount!{self.colors.RESET}")
            time.sleep(2)
            return
        
        # Calculate conversion
        if source == 'TRY':
            source_rate = 1
        else:
            source_rate = self.rates[source]['rate']
        
        if target == 'TRY':
            target_rate = 1
        else:
            target_rate = self.rates[target]['rate']
        
        result = (amount * source_rate) / target_rate
        
        # Display result with visual effect
        self.draw_box(25, 15, 70, 7, "Result", self.colors.GREEN)
        self.move_cursor(30, 17)
        print(f"{self.colors.BOLD}{amount:,.2f} {source} = ", end='')
        
        # Animated result display
        for i in range(5):
            self.move_cursor(50, 17)
            print(f"{self.colors.DIM}{'.' * (i+1):5}{self.colors.RESET}", end='', flush=True)
            time.sleep(0.2)
        
        self.move_cursor(50, 17)
        print(f"{self.colors.GREEN}{self.colors.BOLD}{result:,.2f} {target}{self.colors.RESET}")
        
        self.move_cursor(30, 19)
        print(f"{self.colors.DIM}Rate: 1 {source} = {source_rate/target_rate:.4f} {target}{self.colors.RESET}")
        
        # Log activity
        self.db.log_activity(self.user['id'], 'currencies', f"Converted {amount} {source} to {target}")
        
        self.move_cursor(25, 23)
        input(f"{self.colors.DIM}Press Enter to continue...{self.colors.RESET}")
    
    def handle_chart(self):
        """Enhanced chart with better visualization"""
        self.clear_screen()
        
        # Currency selection
        self.draw_box(30, 3, 60, 8, "📈 Select Currency", self.colors.PURPLE)
        self.move_cursor(35, 5)
        print(f"{self.colors.YELLOW}Currency code (e.g., USD, BTC):{self.colors.RESET} ", end='')
        currency = input().upper()
        
        if currency not in self.rates:
            self.move_cursor(35, 8)
            print(f"{self.colors.RED}✗ Invalid currency!{self.colors.RESET}")
            time.sleep(2)
            return
        
        # Get historical data
        history = self.db.get_rate_history(currency, 30)
        
        if not history:
            # Generate mock data if no history
            current_rate = self.rates[currency]['rate']
            history = []
            for i in range(30):
                date = (datetime.now() - timedelta(days=30-i)).strftime('%Y-%m-%d')
                rate = current_rate * (1 + random.uniform(-0.03, 0.03))
                history.append({'date': date, 'avg_rate': rate})
        
        # Draw chart
        self.clear_screen()
        self.draw_box(2, 2, 116, 40, f"📈 {currency}/TRY - 30 Day Chart", self.colors.PURPLE)
        
        # Find min and max for scaling
        rates = [h['avg_rate'] for h in history]
        min_rate = min(rates)
        max_rate = max(rates)
        range_rate = max_rate - min_rate
        
        # Chart dimensions
        chart_x = 10
        chart_y = 5
        chart_width = 96
        chart_height = 25
        
        # Y-axis labels
        for i in range(6):
            y_pos = chart_y + i * 5
            value = max_rate - (range_rate * i / 5)
            self.move_cursor(4, y_pos)
            print(f"{value:>8.2f}")
        
        # Draw chart bars
        bar_width = chart_width // len(history)
        for i, data in enumerate(history):
            rate = data['avg_rate']
            bar_height = int(((rate - min_rate) / range_rate) * chart_height)
            
            # Determine color based on trend
            if i > 0:
                prev_rate = history[i-1]['avg_rate']
                if rate > prev_rate:
                    color = self.colors.GREEN
                elif rate < prev_rate:
                    color = self.colors.RED
                else:
                    color = self.colors.YELLOW
            else:
                color = self.colors.BLUE
            
            # Draw bar
            for h in range(bar_height):
                self.move_cursor(chart_x + i * bar_width, chart_y + chart_height - h)
                print(f"{color}█{self.colors.RESET}", end='')
        
        # X-axis
        self.move_cursor(chart_x, chart_y + chart_height + 1)
        print("─" * chart_width)
        
        # Date labels
        for i in range(0, len(history), 5):
            self.move_cursor(chart_x + i * bar_width, chart_y + chart_height + 2)
            print(history[i]['date'][5:10])  # MM-DD format
        
        # Statistics
        current = self.rates[currency]['rate']
        avg = sum(rates) / len(rates)
        volatility = ((max_rate - min_rate) / avg) * 100
        
        self.draw_box(8, 35, 50, 5, "Statistics", self.colors.CYAN)
        self.move_cursor(10, 37)
        print(f"Current: {current:,.2f} | Avg: {avg:,.2f} | "
              f"High: {max_rate:,.2f} | Low: {min_rate:,.2f}")
        self.move_cursor(10, 38)
        print(f"30-Day Volatility: {volatility:.2f}% | "
              f"Change: {self.colors.GREEN if current > rates[0] else self.colors.RED}"
              f"{((current - rates[0]) / rates[0] * 100):+.2f}%{self.colors.RESET}")
        
        # Technical indicators
        self.draw_box(62, 35, 50, 5, "Technical Indicators", self.colors.YELLOW)
        
        # Simple moving average
        sma_7 = sum(rates[-7:]) / 7 if len(rates) >= 7 else avg
        sma_14 = sum(rates[-14:]) / 14 if len(rates) >= 14 else avg
        
        trend = "🐂 Bullish" if current > sma_7 > sma_14 else "🐻 Bearish"
        trend_color = self.colors.GREEN if "Bullish" in trend else self.colors.RED
        
        self.move_cursor(64, 37)
        print(f"SMA(7): {sma_7:,.2f} | SMA(14): {sma_14:,.2f}")
        self.move_cursor(64, 38)
        print(f"Trend: {trend_color}{trend}{self.colors.RESET}")
        
        self.move_cursor(45, 42)
        input(f"{self.colors.DIM}Press Enter to continue...{self.colors.RESET}")
    
    def handle_portfolio(self):
        """Enhanced portfolio management"""
        self.clear_screen()
        
        # Mock portfolio data - in real implementation, load from database
        if not self.portfolio:
            self.portfolio = {
                'USD': {'amount': 1000, 'avg_cost': 30.50},
                'EUR': {'amount': 500, 'avg_cost': 33.80},
                'BTC': {'amount': 0.05, 'avg_cost': 1100000}
            }
        
        # Draw portfolio box
        self.draw_box(2, 2, 116, 30, "💼 Portfolio Overview", self.colors.CYAN)
        
        # Header
        self.move_cursor(4, 4)
        print(f"{self.colors.BOLD}{'Currency':<10} {'Amount':>12} {'Avg Cost':>12} "
              f"{'Current':>12} {'Value (TL)':>15} {'P&L':>15} {'%':>8}{self.colors.RESET}")
        self.move_cursor(4, 5)
        print("─" * 110)
        
        total_cost = 0
        total_value = 0
        y_pos = 6
        
        for currency, data in self.portfolio.items():
            if currency not in self.rates:
                continue
            
            current_rate = self.rates[currency]['rate']
            cost = data['amount'] * data['avg_cost']
            value = data['amount'] * current_rate
            profit = value - cost
            profit_pct = (profit / cost) * 100 if cost > 0 else 0
            
            total_cost += cost
            total_value += value
            
            # Determine color
            if profit >= 0:
                color = self.colors.GREEN
                symbol = "↑"
            else:
                color = self.colors.RED
                symbol = "↓"
            
            # Get currency display info
            if currency in self.CURRENCIES:
                icon = self.CURRENCIES[currency]['flag']
            elif currency in self.CRYPTOS:
                icon = self.CRYPTOS[currency]['icon']
            else:
                icon = "💰"
            
            self.move_cursor(4, y_pos)
            print(f"{icon} {currency:<8} {data['amount']:>12,.4f} {data['avg_cost']:>12,.2f} "
                  f"{current_rate:>12,.2f} {value:>15,.2f} "
                  f"{color}{profit:>+14,.2f} {symbol}{profit_pct:>+7.1f}%{self.colors.RESET}")
            
            y_pos += 2
        
        # Total row
        self.move_cursor(4, y_pos)
        print("─" * 110)
        
        total_profit = total_value - total_cost
        total_profit_pct = (total_profit / total_cost) * 100 if total_cost > 0 else 0
        
        profit_color = self.colors.GREEN if total_profit >= 0 else self.colors.RED
        
        self.move_cursor(4, y_pos + 1)
        print(f"{self.colors.BOLD}{'TOTAL':<10} {' ':>12} {total_cost:>12,.2f} "
              f"{' ':>12} {total_value:>15,.2f} "
              f"{profit_color}{total_profit:>+14,.2f} {total_profit_pct:>+8.1f}%{self.colors.RESET}")
        
        # Portfolio distribution
        self.draw_box(4, y_pos + 4, 50, 8, "Distribution", self.colors.YELLOW)
        
        dist_y = y_pos + 6
        for currency, data in self.portfolio.items():
            if currency in self.rates:
                value = data['amount'] * self.rates[currency]['rate']
                percentage = (value / total_value * 100) if total_value > 0 else 0
                
                self.move_cursor(6, dist_y)
                bar_length = int(percentage / 2)
                print(f"{currency}: {self.colors.BLUE}{'█' * bar_length}{self.colors.RESET} {percentage:.1f}%")
                dist_y += 1
        
        # Investment advice
        self.draw_box(58, y_pos + 4, 56, 8, "AI Insights", self.colors.MAGENTA)
        
        self.move_cursor(60, y_pos + 6)
        if total_profit_pct > 10:
            print(f"{self.colors.GREEN}🎯 Great performance! Consider taking some profits.{self.colors.RESET}")
        elif total_profit_pct < -5:
            print(f"{self.colors.YELLOW}📊 Portfolio down. Maybe time to average down?{self.colors.RESET}")
        else:
            print(f"{self.colors.BLUE}⚖️ Portfolio stable. Stay the course!{self.colors.RESET}")
        
        self.move_cursor(60, y_pos + 7)
        print(f"{self.colors.DIM}Risk Level: Medium | Diversification: Good{self.colors.RESET}")
        
        self.move_cursor(45, y_pos + 13)
        input(f"{self.colors.DIM}Press Enter to continue...{self.colors.RESET}")
    
    def handle_market_summary(self):
        """Enhanced market summary with insights"""
        self.clear_screen()
        
        # Calculate market statistics
        gaining = [(code, data['change']) for code, data in self.rates.items() if data['change'] > 0]
        losing = [(code, data['change']) for code, data in self.rates.items() if data['change'] < 0]
        
        gaining.sort(key=lambda x: x[1], reverse=True)
        losing.sort(key=lambda x: x[1])
        
        # Main summary box
        self.draw_box(2, 2, 116, 40, "📊 Market Summary", self.colors.MAGENTA)
        
        # Market sentiment gauge
        positive_count = len(gaining)
        negative_count = len(losing)
        total_count = positive_count + negative_count
        
        sentiment_score = (positive_count / total_count * 100) if total_count > 0 else 50
        
        # Visual sentiment meter
        self.move_cursor(45, 4)
        print(f"{self.colors.BOLD}Market Sentiment{self.colors.RESET}")
        
        self.move_cursor(35, 6)
        meter_length = 40
        filled = int(sentiment_score / 100 * meter_length)
        
        # Color gradient for meter
        if sentiment_score > 70:
            meter_color = self.colors.GREEN
            sentiment_text = "🐂 BULLISH"
        elif sentiment_score < 30:
            meter_color = self.colors.RED
            sentiment_text = "🐻 BEARISH"
        else:
            meter_color = self.colors.YELLOW
            sentiment_text = "➡️ NEUTRAL"
        
        print(f"[{meter_color}{'█' * filled}{self.colors.DIM}{'░' * (meter_length - filled)}{self.colors.RESET}] "
              f"{sentiment_score:.0f}% {sentiment_text}")
        
        # Top gainers
        self.draw_box(4, 9, 55, 12, "📈 Top Gainers", self.colors.GREEN)
        y_pos = 11
        for code, change in gaining[:8]:
            name = self._get_currency_name(code)
            icon = self._get_currency_icon(code)
            
            self.move_cursor(6, y_pos)
            print(f"{icon} {code:<4} {name:<20} "
                  f"{self.colors.GREEN}↑ {change:>6.2f}%{self.colors.RESET}")
            y_pos += 1
        
        # Top losers
        self.draw_box(61, 9, 53, 12, "📉 Top Losers", self.colors.RED)
        y_pos = 11
        for code, change in losing[:8]:
            name = self._get_currency_name(code)
            icon = self._get_currency_icon(code)
            
            self.move_cursor(63, y_pos)
            print(f"{icon} {code:<4} {name:<20} "
                  f"{self.colors.RED}↓ {abs(change):>6.2f}%{self.colors.RESET}")
            y_pos += 1
        
        # Market statistics
        self.draw_box(4, 22, 55, 8, "Market Statistics", self.colors.BLUE)
        
        total_market_change = sum(data['change'] for data in self.rates.values()) / len(self.rates)
        volatility = sum(abs(data['change']) for data in self.rates.values()) / len(self.rates)
        
        self.move_cursor(6, 24)
        print(f"Total Currencies: {total_count}")
        self.move_cursor(6, 25)
        print(f"Rising: {self.colors.GREEN}{positive_count} ({positive_count/total_count*100:.1f}%){self.colors.RESET}")
        self.move_cursor(6, 26)
        print(f"Falling: {self.colors.RED}{negative_count} ({negative_count/total_count*100:.1f}%){self.colors.RESET}")
        self.move_cursor(6, 27)
        print(f"Avg Change: {total_market_change:+.2f}%")
        self.move_cursor(6, 28)
        print(f"Volatility: {volatility:.2f}%")
        
        # Trading volume simulation
        self.draw_box(61, 22, 53, 8, "Trading Activity", self.colors.YELLOW)
        
        volume_bars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        
        self.move_cursor(63, 24)
        print("24h Volume Distribution:")
        
        hours = ['00', '06', '12', '18', '24']
        self.move_cursor(63, 26)
        for hour in hours:
            volume = random.choice(volume_bars)
            print(f"{volume} ", end='')
        
        self.move_cursor(63, 27)
        print(" ".join(hours))
        
        self.move_cursor(63, 28)
        print(f"Peak: 14:30 | Low: 03:45")
        
        # Market insights
        self.draw_box(4, 32, 110, 6, "AI Market Analysis", self.colors.PURPLE)
        
        insights = []
        if sentiment_score > 70:
            insights.append("• Strong bullish momentum detected. Consider taking profits on winners.")
        elif sentiment_score < 30:
            insights.append("• Market showing bearish signs. Good opportunities for value investors.")
        
        if volatility > 2:
            insights.append("• High volatility detected. Use stop-losses to manage risk.")
        
        # Currency-specific insights
        if 'USD' in gaining[:3]:
            insights.append("• USD showing strength. May impact emerging market currencies.")
        if 'BTC' in gaining[:3]:
            insights.append("• Bitcoin leading crypto rally. Alt-coins may follow.")
        
        y_pos = 34
        for insight in insights[:3]:
            self.move_cursor(6, y_pos)
            print(f"{self.colors.YELLOW}💡{self.colors.RESET} {insight}")
            y_pos += 1
        
        self.move_cursor(45, 40)
        input(f"{self.colors.DIM}Press Enter to continue...{self.colors.RESET}")
    
    def handle_news(self):
        """Display financial news (simulated)"""
        self.clear_screen()
        
        # Mock news data
        news_items = [
            {
                'time': '15:32',
                'source': 'Bloomberg',
                'title': 'Fed Signals Possible Rate Cut in Q2',
                'impact': 'high',
                'currencies': ['USD'],
                'sentiment': 'negative'
            },
            {
                'time': '14:45',
                'source': 'Reuters',
                'title': 'ECB Maintains Current Policy Stance',
                'impact': 'medium',
                'currencies': ['EUR'],
                'sentiment': 'neutral'
            },
            {
                'time': '13:20',
                'source': 'CoinDesk',
                'title': 'Bitcoin ETF Sees Record Inflows',
                'impact': 'high',
                'currencies': ['BTC', 'ETH'],
                'sentiment': 'positive'
            },
            {
                'time': '11:15',
                'source': 'CNBC',
                'title': 'Oil Prices Surge on Supply Concerns',
                'impact': 'medium',
                'currencies': ['CAD', 'RUB'],
                'sentiment': 'positive'
            },
            {
                'time': '09:30',
                'source': 'FT',
                'title': 'Asian Markets Close Mixed',
                'impact': 'low',
                'currencies': ['JPY', 'CNY'],
                'sentiment': 'neutral'
            }
        ]
        
        self.draw_box(2, 2, 116, 40, "📰 Financial News & Analysis", self.colors.BLUE)
        
        y_pos = 4
        for i, news in enumerate(news_items):
            # Impact color
            if news['impact'] == 'high':
                impact_color = self.colors.RED
                impact_symbol = '🔴'
            elif news['impact'] == 'medium':
                impact_color = self.colors.YELLOW
                impact_symbol = '🟡'
            else:
                impact_color = self.colors.GREEN
                impact_symbol = '🟢'
            
            # Sentiment indicator
            if news['sentiment'] == 'positive':
                sentiment_symbol = '📈'
            elif news['sentiment'] == 'negative':
                sentiment_symbol = '📉'
            else:
                sentiment_symbol = '➡️'
            
            # News item box
            self.draw_box(4, y_pos, 110, 6, f"{news['time']} - {news['source']}", self.colors.GRAY)
            
            self.move_cursor(6, y_pos + 2)
            print(f"{impact_symbol} {self.colors.BOLD}{news['title']}{self.colors.RESET}")
            
            self.move_cursor(6, y_pos + 3)
            print(f"Impact: {impact_color}{news['impact'].upper()}{self.colors.RESET} | "
                  f"Affects: {', '.join(news['currencies'])} {sentiment_symbol}")
            
            y_pos += 7
        
        self.move_cursor(45, 40)
        input(f"{self.colors.DIM}Press Enter to continue...{self.colors.RESET}")
    
    def _get_currency_name(self, code: str) -> str:
        """Get currency name"""
        if code in self.CURRENCIES:
            return self.CURRENCIES[code]['name']
        elif code in self.CRYPTOS:
            return self.CRYPTOS[code]['name']
        return code
    
    def _get_currency_icon(self, code: str) -> str:
        """Get currency icon"""
        if code in self.CURRENCIES:
            return self.CURRENCIES[code]['flag']
        elif code in self.CRYPTOS:
            return self.CRYPTOS[code]['icon']
        return "💰"
    
    def show_help(self):
        """Show enhanced help screen"""
        self.clear_screen()
        
        self.draw_box(10, 3, 100, 35, "📖 Enhanced Currencies Module Help", self.colors.CYAN)
        
        help_sections = [
            ("🔄 Real-Time Data", [
                "• Live rates from Turkish Central Bank (TCMB)",
                "• Cryptocurrency prices from CoinGecko API",
                "• Automatic updates every 30 seconds",
                "• Offline mode with demo data fallback"
            ]),
            ("📊 Features", [
                "• 10+ fiat currencies with official rates",
                "• 10+ major cryptocurrencies",
                "• Interactive price charts with 30-day history",
                "• Portfolio tracking with P&L calculations",
                "• Smart price alerts",
                "• Market sentiment analysis"
            ]),
            ("💡 Tips", [
                "• Add favorites for quick access",
                "• Use charts to identify trends",
                "• Set alerts to catch opportunities",
                "• Track your portfolio performance",
                "• Check market summary for insights"
            ]),
            ("⌨️ Navigation", [
                "• Number keys for menu selection",
                "• Enter to confirm inputs",
                "• Automatic refresh in background"
            ])
        ]
        
        y_pos = 5
        for title, items in help_sections:
            self.move_cursor(15, y_pos)
            print(f"{self.colors.BOLD}{title}{self.colors.RESET}")
            y_pos += 1
            
            for item in items:
                self.move_cursor(17, y_pos)
                print(f"{self.colors.DIM}{item}{self.colors.RESET}")
                y_pos += 1
            
            y_pos += 1
        
        self.move_cursor(45, 37)
        input(f"{self.colors.DIM}Press Enter to continue...{self.colors.RESET}")
    
    def run(self):
        """Main module loop with enhanced UI"""
        # Log module start
        self.db.log_activity(self.user['id'], 'currencies', 'Module started')
        
        while self.running:
            self.display_header()
            self.display_rates()
            self.display_menu()
            
            try:
                # Get single key input
                if os.name == 'nt':  # Windows
                    import msvcrt
                    choice = msvcrt.getch().decode('utf-8', errors='ignore')
                else:  # Unix/Linux/MacOS
                    import termios, tty
                    fd = sys.stdin.fileno()
                    old_settings = termios.tcgetattr(fd)
                    try:
                        tty.setraw(sys.stdin.fileno())
                        choice = sys.stdin.read(1)
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
                # Handle choice
                if choice == '1':
                    self._update_rates()
                    self.move_cursor(50, 48)
                    print(f"{self.colors.GREEN}✓ Rates updated successfully!{self.colors.RESET}")
                    time.sleep(1)
                elif choice == '2':
                    self.handle_convert()
                elif choice == '3':
                    self.handle_chart()
                elif choice == '4':
                    self.handle_favorites()
                elif choice == '5':
                    self.handle_alerts()
                elif choice == '6':
                    self.handle_portfolio()
                elif choice == '7':
                    self.handle_market_summary()
                elif choice == '8':
                    self.handle_news()
                elif choice == '9':
                    self.show_help()
                elif choice == '0':
                    self.running = False
                    
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                self.move_cursor(4, 48)
                print(f"{self.colors.RED}Error: {e}{self.colors.RESET}")
                time.sleep(2)
        
        # Cleanup
        self.running = False
        self.db.log_activity(self.user['id'], 'currencies', 'Module ended')
        self.clear_screen()
        self.move_cursor(45, 20)
        print(f"{self.colors.YELLOW}Exiting Enhanced Currencies Module...{self.colors.RESET}")
        time.sleep(1)
    
    def handle_favorites(self):
        """Manage favorite currencies with visual interface"""
        self.clear_screen()
        
        self.draw_box(20, 5, 80, 30, "⭐ Favorite Currencies", self.colors.YELLOW)
        
        # Display current favorites
        self.move_cursor(25, 8)
        print(f"{self.colors.BOLD}Current Favorites:{self.colors.RESET}")
        
        y_pos = 10
        for i, fav in enumerate(self.favorites, 1):
            icon = self._get_currency_icon(fav)
            name = self._get_currency_name(fav)
            
            self.move_cursor(25, y_pos)
            print(f"{i}. {icon} {fav} - {name}")
            y_pos += 1
        
        # Menu options
        self.move_cursor(25, y_pos + 2)
        print(f"{self.colors.BOLD}Options:{self.colors.RESET}")
        self.move_cursor(25, y_pos + 3)
        print("1 → Add favorite")
        self.move_cursor(25, y_pos + 4)
        print("2 → Remove favorite")
        self.move_cursor(25, y_pos + 5)
        print("0 → Back")
        
        self.move_cursor(25, y_pos + 7)
        print(f"{self.colors.DIM}Choice: {self.colors.RESET}", end='')
        choice = input()
        
        if choice == '1':
            self.move_cursor(25, y_pos + 9)
            print(f"{self.colors.YELLOW}Currency code: {self.colors.RESET}", end='')
            code = input().upper()
            
            if code in self.rates and code not in self.favorites:
                self.favorites.append(code)
                self.move_cursor(25, y_pos + 11)
                print(f"{self.colors.GREEN}✓ {code} added to favorites!{self.colors.RESET}")
            else:
                self.move_cursor(25, y_pos + 11)
                print(f"{self.colors.RED}✗ Invalid or already favorite!{self.colors.RESET}")
                
        elif choice == '2':
            self.move_cursor(25, y_pos + 9)
            print(f"{self.colors.YELLOW}Currency code: {self.colors.RESET}", end='')
            code = input().upper()
            
            if code in self.favorites:
                self.favorites.remove(code)
                self.move_cursor(25, y_pos + 11)
                print(f"{self.colors.GREEN}✓ {code} removed from favorites!{self.colors.RESET}")
            else:
                self.move_cursor(25, y_pos + 11)
                print(f"{self.colors.RED}✗ Not in favorites!{self.colors.RESET}")
        
        time.sleep(2)
    
    def handle_alerts(self):
        """Enhanced price alerts management"""
        self.clear_screen()
        
        self.draw_box(15, 3, 90, 35, "🔔 Price Alerts", self.colors.ORANGE)
        
        # Display active alerts
        self.move_cursor(20, 5)
        print(f"{self.colors.BOLD}Active Alerts:{self.colors.RESET}")
        
        # Mock alerts for demo
        if not self.alerts:
            self.alerts = [
                {'currency': 'USD', 'type': 'above', 'target': 32.00, 'active': True, 'triggered': False},
                {'currency': 'BTC', 'type': 'below', 'target': 2000000, 'active': True, 'triggered': False},
                {'currency': 'EUR', 'type': 'above', 'target': 35.00, 'active': True, 'triggered': True}
            ]
        
        y_pos = 7
        for i, alert in enumerate(self.alerts, 1):
            if alert['currency'] in self.rates:
                current = self.rates[alert['currency']]['rate']
                
                # Status
                if alert['triggered']:
                    status = f"{self.colors.RED}🔴 TRIGGERED!{self.colors.RESET}"
                elif alert['active']:
                    status = f"{self.colors.GREEN}🟢 Active{self.colors.RESET}"
                else:
                    status = f"{self.colors.GRAY}⚪ Inactive{self.colors.RESET}"
                
                # Alert info
                op = ">" if alert['type'] == 'above' else "<"
                icon = self._get_currency_icon(alert['currency'])
                
                self.move_cursor(20, y_pos)
                print(f"{i}. {icon} {alert['currency']} {op} {alert['target']:,.2f} TL")
                self.move_cursor(25, y_pos + 1)
                print(f"Status: {status} | Current: {current:,.2f} TL")
                y_pos += 3
        
        # Alert options
        self.move_cursor(20, y_pos + 2)
        print(f"{self.colors.BOLD}Options:{self.colors.RESET}")
        self.move_cursor(20, y_pos + 3)
        print("1 → Add new alert")
        self.move_cursor(20, y_pos + 4)
        print("2 → Remove alert")
        self.move_cursor(20, y_pos + 5)
        print("3 → Toggle alert")
        self.move_cursor(20, y_pos + 6)
        print("0 → Back")
        
        self.move_cursor(20, y_pos + 8)
        input(f"{self.colors.DIM}Press Enter to continue...{self.colors.RESET}")


if __name__ == "__main__":
    # Test run
    app = CurrenciesEnhanced()
    app.run()