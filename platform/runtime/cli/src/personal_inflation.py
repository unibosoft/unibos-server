#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏷️ kişisel enflasyon modülü - v250
bireysel enflasyon takip ve analiz sistemi

Author: berk hatırlı
Version: v250
Purpose: kişisel harcama alışkanlıklarına göre gerçek enflasyon hesaplama
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, field
import statistics
from decimal import Decimal, ROUND_HALF_UP

# unibos modüllerini import et
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unibos_logger import logger, LogCategory, LogLevel
from database_config import DATABASE_TYPE, get_connection_params

# PostgreSQL support
if DATABASE_TYPE == 'postgresql':
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        POSTGRES_AVAILABLE = True
    except ImportError:
        POSTGRES_AVAILABLE = False
        logger.warning("psycopg2 not installed, falling back to SQLite", 
                      category=LogCategory.DATABASE)
else:
    POSTGRES_AVAILABLE = False

# Renk kodları
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    BG_BLACK = "\033[40m"
    BG_YELLOW = "\033[43m"
    HEADER = "\033[95m"

@dataclass
class Product:
    """Ürün modeli"""
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    brand: str = ""
    barcode: str = ""
    unit: str = "adet"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class PriceEntry:
    """Fiyat girişi modeli"""
    id: Optional[int] = None
    product_id: int = 0
    price: Decimal = Decimal("0.00")
    quantity: float = 1.0
    store: str = ""
    location: str = ""
    recorded_at: datetime = field(default_factory=datetime.now)
    user_id: int = 1

@dataclass
class InflationStats:
    """Enflasyon istatistikleri"""
    period: str  # "30d", "90d", "365d", "all"
    start_date: datetime
    end_date: datetime
    overall_inflation: float
    category_inflation: Dict[str, float]
    product_count: int
    price_entry_count: int
    average_increase: float
    max_increase: Tuple[str, float]  # (product_name, percentage)
    min_increase: Tuple[str, float]  # (product_name, percentage)

class PersonalInflationCalculator:
    """Kişisel enflasyon hesaplayıcı ana sınıf"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Args:
            db_path: SQLite veritabanı yolu. None ise varsayılan kullanılır
        """
        self.base_path = Path("/Users/berkhatirli/Desktop/unibos")
        self.data_dir = self.base_path / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Database configuration
        self.use_postgres = DATABASE_TYPE == 'postgresql' and POSTGRES_AVAILABLE
        
        if self.use_postgres:
            self.db_config = get_connection_params()
            self.db_path = None
            logger.info("Using PostgreSQL database", category=LogCategory.DATABASE)
        else:
            # SQLite fallback
            self.db_path = db_path or str(self.data_dir / "personal_inflation.db")
            self.db_config = None
            if DATABASE_TYPE == 'postgresql' and not POSTGRES_AVAILABLE:
                logger.warning("PostgreSQL requested but not available, using SQLite", 
                             category=LogCategory.DATABASE)
        
        # Veritabanını başlat
        self._init_database()
        
        # Kategoriler
        self.categories = [
            "gıda", "temizlik", "kişisel bakım", "elektronik",
            "giyim", "ulaşım", "eğlence", "sağlık", "diğer"
        ]
        
        logger.info("Kişisel enflasyon modülü başlatıldı", 
                   category=LogCategory.MODULE)
    
    def _get_connection(self):
        """Get database connection"""
        if self.use_postgres:
            conn = psycopg2.connect(**self.db_config)
            # Use RealDictCursor for dict-like row access
            conn.cursor_factory = RealDictCursor
            return conn
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def _execute_query(self, cursor, query: str, params: tuple = ()):
        """Execute query with appropriate parameter style"""
        if self.use_postgres:
            # PostgreSQL uses %s for parameters
            query = query.replace('?', '%s')
        cursor.execute(query, params)
    
    def _fetchall_dict(self, cursor) -> List[Dict[str, Any]]:
        """Fetch all rows as dictionaries"""
        if self.use_postgres:
            # PostgreSQL with RealDictCursor
            return cursor.fetchall()
        else:
            # SQLite with Row factory
            return [dict(row) for row in cursor.fetchall()]
    
    def _init_database(self):
        """Initialize database"""
        if self.use_postgres:
            self._init_postgres_database()
        else:
            self._init_sqlite_database()
    
    def _init_sqlite_database(self):
        """SQLite veritabanını başlat"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Products tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    brand TEXT,
                    barcode TEXT UNIQUE,
                    unit TEXT DEFAULT 'adet',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Price history tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    quantity REAL DEFAULT 1.0,
                    store TEXT,
                    location TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER DEFAULT 1,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            # Users tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    settings TEXT,  -- JSON olarak saklanacak
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User baskets tablosu (favori ürünler)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_baskets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    weight REAL DEFAULT 1.0,  -- Sepetteki ağırlık
                    is_favorite BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    UNIQUE(user_id, product_id)
                )
            """)
            
            # Price alerts tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    target_price REAL,
                    alert_type TEXT,  -- 'below', 'above', 'change'
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            # Activity logs tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,  -- JSON olarak saklanacak
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # İndeksler
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_product ON price_history(product_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_date ON price_history(recorded_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_category ON products(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_basket_user ON user_baskets(user_id)")
            
            conn.commit()
            
        logger.info("SQLite veritabanı tabloları oluşturuldu", category=LogCategory.DATABASE)
    
    def _init_postgres_database(self):
        """PostgreSQL veritabanını başlat"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Products tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        category VARCHAR(100) NOT NULL,
                        brand VARCHAR(100),
                        barcode VARCHAR(50) UNIQUE,
                        unit VARCHAR(50) DEFAULT 'adet',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Price history tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS price_history (
                        id SERIAL PRIMARY KEY,
                        product_id INTEGER NOT NULL,
                        price DECIMAL(10,2) NOT NULL,
                        quantity DECIMAL(10,3) DEFAULT 1.0,
                        store VARCHAR(255),
                        location VARCHAR(255),
                        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        user_id INTEGER DEFAULT 1,
                        FOREIGN KEY (product_id) REFERENCES products(id)
                    )
                """)
                
                # Users tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE,
                        settings TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # User baskets tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_baskets (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        weight DECIMAL(5,2) DEFAULT 1.0,
                        is_favorite BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (product_id) REFERENCES products(id),
                        UNIQUE(user_id, product_id)
                    )
                """)
                
                # Price alerts tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS price_alerts (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        target_price DECIMAL(10,2),
                        alert_type VARCHAR(20),
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (product_id) REFERENCES products(id)
                    )
                """)
                
                # Activity logs tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activity_logs (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER,
                        action VARCHAR(255) NOT NULL,
                        details TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # İndeksler
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_product ON price_history(product_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_date ON price_history(recorded_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_category ON products(category)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_basket_user ON user_baskets(user_id)")
                
                conn.commit()
                
            logger.info("PostgreSQL veritabanı tabloları oluşturuldu", category=LogCategory.DATABASE)
            
        except Exception as e:
            logger.error(f"PostgreSQL veritabanı başlatılamadı: {e}", 
                        category=LogCategory.DATABASE)
            raise
    
    def add_product(self, name: str, category: str, brand: str = "", 
                   barcode: str = "", unit: str = "adet") -> Optional[int]:
        """Yeni ürün ekle"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Barkod varsa kontrol et
                if barcode:
                    if self.use_postgres:
                        cursor.execute("SELECT id FROM products WHERE barcode = %s", (barcode,))
                    else:
                        cursor.execute("SELECT id FROM products WHERE barcode = ?", (barcode,))
                    existing = cursor.fetchone()
                    if existing:
                        logger.warning(f"Ürün zaten mevcut: {barcode}", 
                                     category=LogCategory.MODULE)
                        return existing[0]
                
                # Boş değerleri NULL yap
                barcode_value = barcode if barcode else None
                brand_value = brand if brand else None
                
                if self.use_postgres:
                    cursor.execute("""
                        INSERT INTO products (name, category, brand, barcode, unit)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (name.lower(), category.lower(), brand_value, barcode_value, unit))
                    product_id = cursor.fetchone()[0]
                else:
                    cursor.execute("""
                        INSERT INTO products (name, category, brand, barcode, unit)
                        VALUES (?, ?, ?, ?, ?)
                    """, (name.lower(), category.lower(), brand_value, barcode_value, unit))
                    product_id = cursor.lastrowid
                
                conn.commit()
                
                logger.info(f"Yeni ürün eklendi: {name}", 
                           category=LogCategory.MODULE)
                
                return product_id
                
        except Exception as e:
            logger.error(f"Ürün eklenirken hata: {e}", 
                        category=LogCategory.MODULE)
            return None
    
    def add_price(self, product_id: int, price: float, quantity: float = 1.0,
                  store: str = "", location: str = "") -> bool:
        """Fiyat girişi ekle"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if self.use_postgres:
                    cursor.execute("""
                        INSERT INTO price_history (product_id, price, quantity, store, location)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (product_id, price, quantity, store, location))
                else:
                    cursor.execute("""
                        INSERT INTO price_history (product_id, price, quantity, store, location)
                        VALUES (?, ?, ?, ?, ?)
                    """, (product_id, price, quantity, store, location))
                
                conn.commit()
                
                # Fiyat alarmlarını kontrol et
                self._check_price_alerts(product_id, price)
                
                logger.info(f"Fiyat eklendi: {price} TL", 
                           category=LogCategory.MODULE)
                
                return True
                
        except Exception as e:
            logger.error(f"Fiyat eklenirken hata: {e}", 
                        category=LogCategory.MODULE)
            return False
    
    def calculate_inflation(self, period: str = "30d", 
                           category: Optional[str] = None,
                           user_id: int = 1) -> Optional[InflationStats]:
        """Enflasyon hesapla"""
        try:
            # Period'u parse et
            days = self._parse_period(period)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Her ürün için ilk ve son fiyatı bul
                if category:
                    product_query = "SELECT id, name, category FROM products WHERE category = ?"
                    cursor.execute(product_query, (category,))
                else:
                    cursor.execute("SELECT id, name, category FROM products")
                
                products = cursor.fetchall()
                rows = []
                
                for product in products:
                    # İlk fiyat
                    cursor.execute("""
                        SELECT price, recorded_at FROM price_history 
                        WHERE product_id = ? AND recorded_at >= ?
                        ORDER BY recorded_at ASC LIMIT 1
                    """, (product['id'], start_date))
                    first = cursor.fetchone()
                    
                    # Son fiyat
                    cursor.execute("""
                        SELECT price, recorded_at FROM price_history 
                        WHERE product_id = ? AND recorded_at <= ?
                        ORDER BY recorded_at DESC LIMIT 1
                    """, (product['id'], end_date))
                    last = cursor.fetchone()
                    
                    if first and last and first[0] != last[0]:
                        rows.append({
                            'id': product['id'],
                            'name': product['name'],
                            'category': product['category'],
                            'first_price': first[0],
                            'last_price': last[0],
                            'first_date': first[1],
                            'last_date': last[1]
                        })
                if not rows:
                    return None
                
                # Enflasyon hesapla
                inflations = []
                category_data = {}
                max_increase = ("", -999999.0)
                min_increase = ("", 999999.0)
                
                for row in rows:
                    if row['first_price'] > 0:
                        inflation = ((row['last_price'] - row['first_price']) / row['first_price']) * 100
                        inflations.append(inflation)
                        
                        # Kategori bazlı topla
                        if row['category'] not in category_data:
                            category_data[row['category']] = []
                        category_data[row['category']].append(inflation)
                        
                        # Min/Max bul
                        if inflation > max_increase[1]:
                            max_increase = (row['name'], inflation)
                        if inflation < min_increase[1]:
                            min_increase = (row['name'], inflation)
                
                # Kategori ortalamalarını hesapla
                category_inflation = {}
                for cat, values in category_data.items():
                    category_inflation[cat] = sum(values) / len(values)
                
                # İstatistikleri oluştur
                stats = InflationStats(
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    overall_inflation=sum(inflations) / len(inflations) if inflations else 0,
                    category_inflation=category_inflation,
                    product_count=len(rows),
                    price_entry_count=len(inflations),
                    average_increase=statistics.mean(inflations) if inflations else 0,
                    max_increase=max_increase,
                    min_increase=min_increase
                )
                
                return stats
                
        except Exception as e:
            logger.error(f"Enflasyon hesaplanırken hata: {e}", 
                        category=LogCategory.MODULE)
            return None
    
    def _parse_period(self, period: str) -> int:
        """Period string'ini güne çevir"""
        if period.endswith('d'):
            return int(period[:-1])
        elif period.endswith('m'):
            return int(period[:-1]) * 30
        elif period.endswith('y'):
            return int(period[:-1]) * 365
        elif period == 'all':
            return 36500  # 100 yıl
        else:
            return 30  # varsayılan
    
    def _check_price_alerts(self, product_id: int, new_price: float):
        """Fiyat alarmlarını kontrol et"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT pa.*, p.name 
                    FROM price_alerts pa
                    JOIN products p ON pa.product_id = p.id
                    WHERE pa.product_id = ? AND pa.is_active = 1
                """, (product_id,))
                
                alerts = cursor.fetchall()
                
                for alert in alerts:
                    triggered = False
                    
                    if alert[4] == 'below' and new_price < alert[3]:
                        triggered = True
                        logger.info(f"Fiyat alarmı: {alert[7]} - {new_price} TL (hedef: {alert[3]} TL altı)",
                                   category=LogCategory.MODULE)
                    elif alert[4] == 'above' and new_price > alert[3]:
                        triggered = True
                        logger.info(f"Fiyat alarmı: {alert[7]} - {new_price} TL (hedef: {alert[3]} TL üstü)",
                                   category=LogCategory.MODULE)
                    
                    if triggered:
                        # Alarmı deaktif et
                        cursor.execute("UPDATE price_alerts SET is_active = 0 WHERE id = ?", (alert[0],))
                        conn.commit()
                        
        except Exception as e:
            logger.error(f"Fiyat alarmı kontrolünde hata: {e}", 
                        category=LogCategory.MODULE)
    
    def get_products(self, category: Optional[str] = None, 
                    search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Ürünleri listele"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM products WHERE 1=1"
                params = []
                
                if category:
                    query += " AND category = ?"
                    params.append(category)
                
                if search:
                    query += " AND (name LIKE ? OR brand LIKE ?)"
                    params.extend([f"%{search}%", f"%{search}%"])
                
                query += " ORDER BY name"
                
                self._execute_query(cursor, query, tuple(params))
                return self._fetchall_dict(cursor)
                
        except Exception as e:
            logger.error(f"Ürünler listelenirken hata: {e}", 
                        category=LogCategory.MODULE)
            return []
    
    def get_price_history(self, product_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Fiyat geçmişini getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                since = datetime.now() - timedelta(days=days)
                
                cursor.execute("""
                    SELECT * FROM price_history 
                    WHERE product_id = ? AND recorded_at >= ?
                    ORDER BY recorded_at DESC
                """, (product_id, since))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Fiyat geçmişi alınırken hata: {e}", 
                        category=LogCategory.MODULE)
            return []
    
    def add_to_basket(self, user_id: int, product_id: int, 
                     weight: float = 1.0, is_favorite: bool = False) -> bool:
        """Kullanıcı sepetine ürün ekle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO user_baskets (user_id, product_id, weight, is_favorite)
                    VALUES (?, ?, ?, ?)
                """, (user_id, product_id, weight, is_favorite))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Sepete eklenirken hata: {e}", 
                        category=LogCategory.MODULE)
            return False
    
    def get_user_inflation(self, user_id: int, period: str = "30d") -> Optional[InflationStats]:
        """Kullanıcının sepetine göre enflasyon hesapla"""
        try:
            # Kullanıcı sepetini al
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT product_id, weight 
                    FROM user_baskets 
                    WHERE user_id = ?
                """, (user_id,))
                
                basket = cursor.fetchall()
                
                if not basket:
                    return self.calculate_inflation(period)
                
                # Ağırlıklı enflasyon hesapla
                # TODO: Implement weighted inflation calculation
                
                return self.calculate_inflation(period)
                
        except Exception as e:
            logger.error(f"Kullanıcı enflasyonu hesaplanırken hata: {e}", 
                        category=LogCategory.MODULE)
            return None
    
    def export_data(self, format: str = "json") -> Optional[str]:
        """Verileri dışa aktar"""
        try:
            export_dir = self.base_path / "exports"
            export_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format == "json":
                data = {
                    "products": self.get_products(),
                    "export_date": datetime.now().isoformat(),
                    "version": "v250"
                }
                
                export_file = export_dir / f"inflation_export_{timestamp}.json"
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                return str(export_file)
            
            # TODO: CSV, Excel export
            
        except Exception as e:
            logger.error(f"Veri dışa aktarılırken hata: {e}", 
                        category=LogCategory.MODULE)
            return None


# Terminal UI fonksiyonları
def show_inflation_menu():
    """Kişisel enflasyon modülü ana menüsü"""
    calc = PersonalInflationCalculator()
    
    while True:
        os.system('clear' if os.name != 'nt' else 'cls')
        
        # Başlık
        print(f"\n{Colors.BG_BLACK}{Colors.YELLOW}")
        print("  ╔════════════════════════════════════════╗")
        print("  ║       📊 KİŞİSEL ENFLASYON MODÜLÜ      ║")
        print("  ║            gerçek enflasyonunuz         ║")
        print("  ╚════════════════════════════════════════╝")
        print(f"{Colors.RESET}\n")
        
        # Son 30 günlük özet
        stats = calc.calculate_inflation("30d")
        if stats:
            print(f"  {Colors.CYAN}Son 30 Gün:{Colors.RESET}")
            print(f"  Genel Enflasyon: {Colors.YELLOW}{stats.overall_inflation:.2f}%{Colors.RESET}")
            print(f"  Ürün Sayısı: {stats.product_count}")
            print(f"  En Çok Artan: {stats.max_increase[0]} ({Colors.RED}+{stats.max_increase[1]:.1f}%{Colors.RESET})")
            print()
        
        # Menü seçenekleri
        print(f"  {Colors.GREEN}1.{Colors.RESET} 🛒 Yeni Ürün Ekle")
        print(f"  {Colors.GREEN}2.{Colors.RESET} 💰 Fiyat Girişi")
        print(f"  {Colors.GREEN}3.{Colors.RESET} 📊 Enflasyon Raporu")
        print(f"  {Colors.GREEN}4.{Colors.RESET} 📦 Ürün Listesi")
        print(f"  {Colors.GREEN}5.{Colors.RESET} 📈 Fiyat Geçmişi")
        print(f"  {Colors.GREEN}6.{Colors.RESET} ⭐ Favori Ürünler")
        print(f"  {Colors.GREEN}7.{Colors.RESET} 🔔 Fiyat Alarmları")
        print(f"  {Colors.GREEN}8.{Colors.RESET} 📤 Veri Dışa Aktar")
        print(f"  {Colors.GREEN}9.{Colors.RESET} 🔍 Ürün Ara")
        print(f"  {Colors.RED}0.{Colors.RESET} 🔙 Ana Menüye Dön")
        
        choice = input(f"\n  {Colors.YELLOW}Seçiminiz: {Colors.RESET}")
        
        if choice == '0':
            break
        elif choice == '1':
            add_product_ui(calc)
        elif choice == '2':
            add_price_ui(calc)
        elif choice == '3':
            show_inflation_report(calc)
        elif choice == '4':
            show_product_list(calc)
        elif choice == '5':
            show_price_history(calc)
        elif choice == '6':
            manage_favorites(calc)
        elif choice == '7':
            manage_price_alerts(calc)
        elif choice == '8':
            export_data_ui(calc)
        elif choice == '9':
            search_products(calc)

def add_product_ui(calc: PersonalInflationCalculator):
    """Ürün ekleme arayüzü"""
    print(f"\n{Colors.CYAN}=== Yeni Ürün Ekle ==={Colors.RESET}\n")
    
    name = input("Ürün adı: ").strip()
    if not name:
        return
    
    print("\nKategoriler:")
    for i, cat in enumerate(calc.categories, 1):
        print(f"{i}. {cat}")
    
    cat_choice = input("\nKategori seçin (1-9): ").strip()
    try:
        category = calc.categories[int(cat_choice) - 1]
    except:
        category = "diğer"
    
    brand = input("Marka (opsiyonel): ").strip()
    barcode = input("Barkod (opsiyonel): ").strip()
    
    # Birim seçimi
    print("\nBirim örnekleri: adet, kg, litre, paket, kutu, gram")
    unit = input("Birim (varsayılan: adet): ").strip()
    if not unit:
        unit = "adet"
    
    product_id = calc.add_product(name, category, brand, barcode, unit)
    
    if product_id:
        print(f"\n{Colors.GREEN}✓ Ürün başarıyla eklendi!{Colors.RESET}")
        
        # Hemen fiyat eklemek ister mi?
        if input("\nHemen fiyat eklemek ister misiniz? (e/h): ").lower() == 'e':
            add_price_for_product(calc, product_id, name)
    else:
        print(f"\n{Colors.RED}✗ Ürün eklenemedi!{Colors.RESET}")
    
    input("\nDevam etmek için Enter...")

def add_price_ui(calc: PersonalInflationCalculator):
    """Fiyat ekleme arayüzü"""
    print(f"\n{Colors.CYAN}=== Fiyat Girişi ==={Colors.RESET}\n")
    
    # Ürünleri listele
    products = calc.get_products()
    if not products:
        print(f"{Colors.RED}Henüz ürün eklenmemiş!{Colors.RESET}")
        input("\nDevam etmek için Enter...")
        return
    
    print("Ürünler:")
    for i, product in enumerate(products[:20], 1):  # İlk 20 ürün
        print(f"{i}. {product['name']} ({product['category']})")
    
    if len(products) > 20:
        print(f"\n...ve {len(products) - 20} ürün daha")
        print("Tüm listeyi görmek için '4. Ürün Listesi' kullanın")
    
    try:
        choice = int(input("\nÜrün numarası (0: Arama yap): "))
        
        if choice == 0:
            search_term = input("Ürün adı: ")
            products = calc.get_products(search=search_term)
            if not products:
                print(f"{Colors.RED}Ürün bulunamadı!{Colors.RESET}")
                input("\nDevam etmek için Enter...")
                return
            
            print("\nBulunan ürünler:")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product['name']} ({product['category']})")
            
            choice = int(input("\nÜrün numarası: "))
            product = products[choice - 1]
        else:
            product = products[choice - 1]
        
        add_price_for_product(calc, product['id'], product['name'])
        
    except (ValueError, IndexError):
        print(f"{Colors.RED}Geçersiz seçim!{Colors.RESET}")
        input("\nDevam etmek için Enter...")

def add_price_for_product(calc: PersonalInflationCalculator, product_id: int, product_name: str):
    """Belirli bir ürün için fiyat ekle"""
    print(f"\n{product_name} için fiyat girişi:")
    
    try:
        price = float(input("Fiyat (TL): "))
        quantity = float(input("Miktar (varsayılan: 1): ") or "1")
        store = input("Mağaza (opsiyonel): ").strip()
        location = input("Konum (opsiyonel): ").strip()
        
        if calc.add_price(product_id, price, quantity, store, location):
            print(f"\n{Colors.GREEN}✓ Fiyat başarıyla eklendi!{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}✗ Fiyat eklenemedi!{Colors.RESET}")
            
    except ValueError:
        print(f"{Colors.RED}Geçersiz fiyat!{Colors.RESET}")

def show_inflation_report(calc: PersonalInflationCalculator):
    """Enflasyon raporu göster"""
    print(f"\n{Colors.CYAN}=== Enflasyon Raporu ==={Colors.RESET}\n")
    
    periods = [
        ("Son 30 Gün", "30d"),
        ("Son 90 Gün", "90d"),
        ("Son 1 Yıl", "365d"),
        ("Tüm Zamanlar", "all")
    ]
    
    for period_name, period_code in periods:
        stats = calc.calculate_inflation(period_code)
        
        if stats and stats.product_count > 0:
            print(f"\n{Colors.YELLOW}{period_name}:{Colors.RESET}")
            print(f"Genel Enflasyon: {Colors.BOLD}{stats.overall_inflation:.2f}%{Colors.RESET}")
            print(f"Ürün Sayısı: {stats.product_count}")
            print(f"Fiyat Girişi: {stats.price_entry_count}")
            
            if stats.category_inflation:
                print("\nKategori Bazında:")
                for cat, inf in sorted(stats.category_inflation.items(), 
                                     key=lambda x: x[1], reverse=True):
                    color = Colors.RED if inf > 10 else Colors.YELLOW if inf > 5 else Colors.GREEN
                    print(f"  {cat}: {color}{inf:.2f}%{Colors.RESET}")
            
            print(f"\nEn Çok Artan: {stats.max_increase[0]} ({Colors.RED}+{stats.max_increase[1]:.1f}%{Colors.RESET})")
            print(f"En Az Artan: {stats.min_increase[0]} ({Colors.GREEN}+{stats.min_increase[1]:.1f}%{Colors.RESET})")
    
    input("\nDevam etmek için Enter...")

def show_product_list(calc: PersonalInflationCalculator):
    """Ürün listesini göster"""
    print(f"\n{Colors.CYAN}=== Ürün Listesi ==={Colors.RESET}\n")
    
    print("1. Tüm ürünler")
    print("2. Kategoriye göre")
    
    choice = input("\nSeçiminiz: ")
    
    if choice == '2':
        print("\nKategoriler:")
        for i, cat in enumerate(calc.categories, 1):
            print(f"{i}. {cat}")
        
        try:
            cat_idx = int(input("\nKategori seçin: ")) - 1
            category = calc.categories[cat_idx]
            products = calc.get_products(category=category)
        except:
            products = calc.get_products()
    else:
        products = calc.get_products()
    
    if not products:
        print(f"{Colors.RED}Ürün bulunamadı!{Colors.RESET}")
    else:
        print(f"\n{len(products)} ürün bulundu:\n")
        
        for product in products:
            print(f"📦 {product['name']}")
            print(f"   Kategori: {product['category']}")
            print(f"   Birim: {product['unit']}")
            if product['brand']:
                print(f"   Marka: {product['brand']}")
            if product['barcode']:
                print(f"   Barkod: {product['barcode']}")
            print()
    
    input("Devam etmek için Enter...")

def show_price_history(calc: PersonalInflationCalculator):
    """Fiyat geçmişini göster"""
    print(f"\n{Colors.CYAN}=== Fiyat Geçmişi ==={Colors.RESET}\n")
    
    # Ürün seç
    products = calc.get_products()
    if not products:
        print(f"{Colors.RED}Henüz ürün eklenmemiş!{Colors.RESET}")
        input("\nDevam etmek için Enter...")
        return
    
    search = input("Ürün adı ara (boş bırakın tüm ürünler): ").strip()
    if search:
        products = calc.get_products(search=search)
    
    if not products:
        print(f"{Colors.RED}Ürün bulunamadı!{Colors.RESET}")
        input("\nDevam etmek için Enter...")
        return
    
    print("\nÜrünler:")
    for i, product in enumerate(products[:10], 1):
        print(f"{i}. {product['name']} ({product['category']})")
    
    try:
        choice = int(input("\nÜrün seçin: ")) - 1
        product = products[choice]
        
        # Fiyat geçmişini al
        history = calc.get_price_history(product['id'], days=365)
        
        if not history:
            print(f"\n{Colors.RED}Bu ürün için fiyat geçmişi yok!{Colors.RESET}")
        else:
            print(f"\n{product['name']} - Fiyat Geçmişi:\n")
            
            for entry in history:
                date = datetime.fromisoformat(entry['recorded_at']).strftime("%d.%m.%Y %H:%M")
                print(f"{date}: {Colors.YELLOW}{entry['price']:.2f} TL{Colors.RESET}")
                if entry['store']:
                    print(f"           Mağaza: {entry['store']}")
                print()
        
    except (ValueError, IndexError):
        print(f"{Colors.RED}Geçersiz seçim!{Colors.RESET}")
    
    input("\nDevam etmek için Enter...")

def manage_favorites(calc: PersonalInflationCalculator):
    """Favori ürünleri yönet"""
    print(f"\n{Colors.CYAN}=== Favori Ürünler ==={Colors.RESET}\n")
    print("Bu özellik yakında eklenecek!")
    input("\nDevam etmek için Enter...")

def manage_price_alerts(calc: PersonalInflationCalculator):
    """Fiyat alarmlarını yönet"""
    print(f"\n{Colors.CYAN}=== Fiyat Alarmları ==={Colors.RESET}\n")
    print("Bu özellik yakında eklenecek!")
    input("\nDevam etmek için Enter...")

def export_data_ui(calc: PersonalInflationCalculator):
    """Veri dışa aktarma arayüzü"""
    print(f"\n{Colors.CYAN}=== Veri Dışa Aktar ==={Colors.RESET}\n")
    
    print("1. JSON formatında")
    print("2. CSV formatında (yakında)")
    print("3. Excel formatında (yakında)")
    
    choice = input("\nSeçiminiz: ")
    
    if choice == '1':
        export_file = calc.export_data("json")
        if export_file:
            print(f"\n{Colors.GREEN}✓ Veriler dışa aktarıldı:{Colors.RESET}")
            print(f"   {export_file}")
        else:
            print(f"\n{Colors.RED}✗ Dışa aktarma başarısız!{Colors.RESET}")
    else:
        print("Bu format henüz desteklenmiyor!")
    
    input("\nDevam etmek için Enter...")

def search_products(calc: PersonalInflationCalculator):
    """Ürün arama"""
    print(f"\n{Colors.CYAN}=== Ürün Ara ==={Colors.RESET}\n")
    
    search_term = input("Arama terimi: ").strip()
    
    if search_term:
        products = calc.get_products(search=search_term)
        
        if not products:
            print(f"\n{Colors.RED}'{search_term}' ile eşleşen ürün bulunamadı!{Colors.RESET}")
        else:
            print(f"\n{len(products)} ürün bulundu:\n")
            
            for product in products:
                print(f"📦 {product['name']}")
                print(f"   Kategori: {product['category']}")
                if product['brand']:
                    print(f"   Marka: {product['brand']}")
                print()
    
    input("\nDevam etmek için Enter...")


# Modül test
if __name__ == "__main__":
    show_inflation_menu()