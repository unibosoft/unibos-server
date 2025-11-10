#!/usr/bin/env python3
"""
CLI Content Renderers - Module-specific content rendering
=========================================================
This module provides custom content renderers for different modules
and tools in the unibos cli, ensuring consistent rendering across
all modules.
"""

import sys
import time
import platform
from datetime import datetime
from typing import Optional, List, Tuple
from cli_context_manager import ContentRenderer, CLIContext, Colors


class ModulePreviewRenderer(ContentRenderer):
    """Base class for module preview renderers"""
    
    def draw_title(self, x: int, y: int, title: str = ""):
        """Draw a title without box frame"""
        if title:
            # Make title lowercase for consistency
            title_lower = title.lower()
            sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.CYAN}{title_lower}{Colors.RESET}")
    
    def draw_feature_list(self, x: int, y: int, features: List[Tuple[str, str]]):
        """Draw a list of features with icons"""
        for i, (icon, text) in enumerate(features):
            if i >= 10:  # Limit to prevent overflow
                break
            sys.stdout.write(f"\033[{y + i};{x}H{icon} {text}")


class WIMMPreviewRenderer(ModulePreviewRenderer):
    """Preview renderer for WIMM (Where Is My Money)"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        # Clear area completely
        self.clear(x, y, width, height)
        
        # Draw title without box
        self.draw_title(x, y, "wimm")
        
        # Original v428 content with colors (without box, start at y+2)
        y_pos = y + 2
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}description:{Colors.RESET} {Colors.CYAN}financial management system{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}status:{Colors.RESET} {Colors.GREEN}ready{Colors.RESET}")
        y_pos += 2
        
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}module:{Colors.RESET} {Colors.BOLD}{Colors.CYAN}where is my money{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}type:{Colors.RESET} financial manager")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}accounts:{Colors.RESET} multi-currency")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}invoices:{Colors.RESET} in/out tracking")
        y_pos += 2
        
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}features:{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} cash flow")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} p&l reports")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} transaction history")
        
        sys.stdout.flush()


class WIMSPreviewRenderer(ModulePreviewRenderer):
    """Preview renderer for WIMS (Where Is My Stuff)"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        # Clear area completely
        self.clear(x, y, width, height)
        
        # Draw title without box
        self.draw_title(x, y, "wims")
        
        # Original v428 content with colors (without box)
        y_pos = y + 2
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}description:{Colors.RESET} {Colors.CYAN}inventory management{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}status:{Colors.RESET} {Colors.GREEN}ready{Colors.RESET}")
        y_pos += 2
        
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}module:{Colors.RESET} {Colors.BOLD}{Colors.CYAN}where is my stuff{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}type:{Colors.RESET} inventory manager")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}tracking:{Colors.RESET} qr/barcode")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}locations:{Colors.RESET} multi-warehouse")
        y_pos += 2
        
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}features:{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} stock tracking")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} movement history")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} expiry alerts")
        
        sys.stdout.flush()


class CurrenciesPreviewRenderer(ModulePreviewRenderer):
    """Preview renderer for Currencies module"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        # Clear area completely
        self.clear(x, y, width, height)
        
        # Draw title without box
        self.draw_title(x, y, "currencies")
        
        # Original v428 content with colors (without box)
        y_pos = y + 2
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}description:{Colors.RESET} {Colors.CYAN}real-time currency exchange{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}status:{Colors.RESET} {Colors.GREEN}ready{Colors.RESET}")
        y_pos += 2
        
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}data source:{Colors.RESET} {Colors.BOLD}{Colors.CYAN}tcmb + coingecko{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}update interval:{Colors.RESET} real-time")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}currencies:{Colors.RESET} {Colors.MAGENTA}150+{Colors.RESET} supported")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}crypto:{Colors.RESET} top {Colors.MAGENTA}100{Colors.RESET} coins")
        y_pos += 2
        
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}features:{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} portfolio tracking")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} price alerts")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} historical charts")
        
        sys.stdout.flush()


class PersonalInflationPreviewRenderer(ModulePreviewRenderer):
    """Preview renderer for Personal Inflation module"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        # Clear area completely
        self.clear(x, y, width, height)
        
        # Draw title without box
        self.draw_title(x, y, "personal inflation")
        
        # Original v428 content with colors (without box)
        y_pos = y + 2
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}description:{Colors.RESET} {Colors.CYAN}track personal inflation{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}status:{Colors.RESET} {Colors.GREEN}ready{Colors.RESET}")
        y_pos += 2
        
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}calculation method:{Colors.RESET} personal basket")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}categories:{Colors.RESET} customizable")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}data privacy:{Colors.RESET} {Colors.GREEN}100% local{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}accuracy:{Colors.RESET} {Colors.MAGENTA}±0.5%{Colors.RESET}")
        y_pos += 2
        
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}features:{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} product tracking")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} trend analysis")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} savings tips")
        
        sys.stdout.flush()


class DocumentsMenuRenderer(ContentRenderer):
    """Menu renderer for Documents module with submenu items"""
    
    def __init__(self):
        self.menu_items = [
            ("browse", "📁 browse documents", "view and manage documents"),
            ("search", "🔍 search", "full-text document search"),
            ("upload", "📤 upload", "upload new documents"),
            ("ocr", "📸 ocr scanner", "extract text from images"),
            ("invoice_processor", "🧾 invoice processor", "process invoices with ai"),
            ("tags", "🏷️ tag manager", "manage document tags"),
            ("analytics", "📊 analytics", "document statistics"),
        ]
        self.selected_index = 0
        self.active = False
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        """Render documents submenu"""
        # Clear area completely
        self.clear(x, y, width, height)
        
        # Module header (lowercase)
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.BLUE}📄 documents menu{Colors.RESET}")
        sys.stdout.write(f"\033[{y + 1};{x}H{Colors.DIM}{'─' * min(40, width - 2)}{Colors.RESET}")
        
        # Menu items
        y_pos = y + 3
        for i, (key, name, desc) in enumerate(self.menu_items):
            if y_pos + 2 < y + height - 3:
                # Highlight selected item
                if i == self.selected_index:
                    sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BG_BLUE}{Colors.WHITE} {name:<38} {Colors.RESET}")
                else:
                    sys.stdout.write(f"\033[{y_pos};{x}H  {name}")
                
                sys.stdout.write(f"\033[{y_pos + 1};{x + 4}H{Colors.DIM}{desc}{Colors.RESET}")
                y_pos += 2
        
        # Instructions
        sys.stdout.write(f"\033[{y + height - 2};{x}H{Colors.DIM}↑↓ navigate | enter select | esc back{Colors.RESET}")
        sys.stdout.flush()
    
    def handle_key(self, key: str) -> tuple:
        """Handle key input for menu navigation"""
        if key == '\033[A':  # Up arrow
            self.selected_index = max(0, self.selected_index - 1)
            return True, None
        elif key == '\033[B':  # Down arrow
            self.selected_index = min(len(self.menu_items) - 1, self.selected_index + 1)
            return True, None
        elif key == '\r' or key == '\n':  # Enter
            selected_key = self.menu_items[self.selected_index][0]
            return True, selected_key
        elif key == '\033':  # Escape
            return False, None
        return True, None


class DocumentsPreviewRenderer(ModulePreviewRenderer):
    """Preview renderer for Documents module"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        # Clear area completely
        self.clear(x, y, width, height)
        
        # Title with emoji
        y_pos = y
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}{Colors.CYAN}# 🎯 documents{Colors.RESET}")
        y_pos += 2
        
        # 📋 Overview section
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}{Colors.BLUE}## 📋 overview{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}Hintelligent document management system with advanced OCR")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}Hprocessing, AI-powered analysis, and automated extraction")
        y_pos += 2
        
        # 🔧 Current capabilities section
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}{Colors.BLUE}## 🔧 current capabilities{Colors.RESET}")
        y_pos += 1
        
        # Fully functional features
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.GREEN}### ✅ fully functional{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H- {Colors.BOLD}multi-format OCR{Colors.RESET} - extracts text from JPG, PNG, PDF")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H- {Colors.BOLD}AI invoice processing{Colors.RESET} - parses receipts with 77.8% accuracy")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H- {Colors.BOLD}batch upload{Colors.RESET} - processes 50-100 documents simultaneously")
        y_pos += 2
        
        # In development features
        if y_pos < y + height - 8:
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}### 🚧 in development{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H- multi-language OCR (English, Arabic in testing)")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H- handwriting recognition")
            y_pos += 2
        
        # 💻 Technical implementation
        if y_pos < y + height - 6:
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}{Colors.BLUE}## 💻 technical implementation{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}core components and architecture powering this module{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H- Document model - main document storage with metadata")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H- OCRProcessor - text extraction pipeline")
        
        # Development status at bottom
        sys.stdout.write(f"\033[{y + height - 4};{x}H{Colors.BOLD}## 🛠️ development status{Colors.RESET}")
        sys.stdout.write(f"\033[{y + height - 3};{x}H{Colors.YELLOW}completion: 78% 🚧{Colors.RESET}")
        
        # Launch hint
        sys.stdout.write(f"\033[{y + height - 2};{x}H{Colors.DIM}press enter to launch • ← back to menu{Colors.RESET}")
        sys.stdout.flush()


class CCTVPreviewRenderer(ModulePreviewRenderer):
    """Preview renderer for CCTV module"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        # Clear area completely
        self.clear(x, y, width, height)
        
        # Module header (lowercase)
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.RED}📹 cctv system{Colors.RESET}")
        sys.stdout.write(f"\033[{y + 1};{x}H{Colors.DIM}{'─' * min(40, width - 2)}{Colors.RESET}")
        
        # Description
        y_pos = y + 3
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.CYAN}comprehensive surveillance management{Colors.RESET}")
        
        # Features
        y_pos += 2
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}key features:{Colors.RESET}")
        y_pos += 1
        
        features = [
            ("📹", "multi-camera support"),
            ("🎥", "live streaming view"),
            ("💾", "continuous recording"),
            ("🚨", "motion detection alerts"),
            ("🤖", "AI object recognition"),
            ("📅", "scheduled recording"),
            ("🔍", "event timeline search"),
            ("☁️", "cloud backup support"),
        ]
        
        self.draw_feature_list(x + 2, y_pos, features)
        
        # Camera status
        if height > 20:
            y_pos = y + 16
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}system status:{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}cameras online:{Colors.RESET} {Colors.GREEN}4/4{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}recording:{Colors.RESET} {Colors.GREEN}active{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}storage:{Colors.RESET} 72% available")
        
        # Shortcuts
        sys.stdout.write(f"\033[{y + height - 3};{x}H{Colors.BOLD}shortcuts:{Colors.RESET}")
        sys.stdout.write(f"\033[{y + height - 2};{x + 2}H{Colors.DIM}enter - view | l - live feed | r - recordings{Colors.RESET}")
        sys.stdout.flush()


class RecariaPreviewRenderer(ModulePreviewRenderer):
    """Preview renderer for Recaria module"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        # Clear area completely
        self.clear(x, y, width, height)
        
        # Title with emoji
        y_pos = y
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}{Colors.CYAN}# 🪐 recaria{Colors.RESET}")
        y_pos += 2
        
        # 📋 Overview section
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}{Colors.BLUE}## 📋 overview{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}Hspace exploration and consciousness simulation game exploring")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H8 billion minds across past, present, and future timelines")
        y_pos += 2
        
        # 🔧 Current capabilities section
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}{Colors.BLUE}## 🔧 current capabilities{Colors.RESET}")
        y_pos += 1
        
        # Fully functional features
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.GREEN}### ✅ fully functional{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H- {Colors.BOLD}consciousness simulation{Colors.RESET} - explore individual minds")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H- {Colors.BOLD}timeline navigation{Colors.RESET} - travel through past/present/future")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H- {Colors.BOLD}collective mind access{Colors.RESET} - tap into global consciousness")
        y_pos += 2
        
        # In development features
        if y_pos < y + height - 8:
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}### 🚧 in development{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H- multiplayer consciousness sharing")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H- quantum communication protocols")
            y_pos += 2
        
        # 💻 Technical implementation
        if y_pos < y + height - 6:
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}{Colors.BLUE}## 💻 technical implementation{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}game engine and consciousness simulation framework{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H- RecariaGame class - main game engine and state")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x}H- ConsciousnessSimulator - mind exploration system")
        
        # Development status at bottom
        sys.stdout.write(f"\033[{y + height - 4};{x}H{Colors.BOLD}## 🛠️ development status{Colors.RESET}")
        sys.stdout.write(f"\033[{y + height - 3};{x}H{Colors.GREEN}completion: 65% 🚧{Colors.RESET}")
        
        # Launch hint
        sys.stdout.write(f"\033[{y + height - 2};{x}H{Colors.DIM}press enter to launch • ← back to menu{Colors.RESET}")
        sys.stdout.flush()


class BirlikteyizPreviewRenderer(ModulePreviewRenderer):
    """Preview renderer for Birlikteyiz module"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        # Clear area completely
        self.clear(x, y, width, height)
        
        # Draw title without box
        self.draw_title(x, y, "birlikteyiz")
        
        # Original v428 content with colors (without box)
        y_pos = y + 2
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}description:{Colors.RESET} {Colors.CYAN}emergency mesh network{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}status:{Colors.RESET} {Colors.GREEN}ready{Colors.RESET}")
        y_pos += 2
        
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}network type:{Colors.RESET} {Colors.BOLD}{Colors.CYAN}lora mesh{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}range:{Colors.RESET} {Colors.MAGENTA}15km{Colors.RESET} (open area)")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}encryption:{Colors.RESET} aes-256")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}nodes active:{Colors.RESET} {Colors.GREEN}42{Colors.RESET}")
        y_pos += 2
        
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.YELLOW}use cases:{Colors.RESET}")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} emergency communication")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} earthquake response")
        y_pos += 1
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.DIM}•{Colors.RESET} off-grid messaging")
        
        sys.stdout.flush()


class AdministrationPreviewRenderer(ModulePreviewRenderer):
    """Preview renderer for Administration module"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        # Clear area completely
        self.clear(x, y, width, height)
        
        # Module header (lowercase)
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.RED}⚙️ administration{Colors.RESET}")
        sys.stdout.write(f"\033[{y + 1};{x}H{Colors.DIM}{'─' * min(40, width - 2)}{Colors.RESET}")
        
        # Description
        y_pos = y + 3
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.CYAN}system administration & configuration{Colors.RESET}")
        
        # Features
        y_pos += 2
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}key features:{Colors.RESET}")
        y_pos += 1
        
        features = [
            ("👤", "user management"),
            ("🔐", "access control"),
            ("⚙️", "system configuration"),
            ("📊", "performance monitoring"),
            ("🔄", "backup & restore"),
            ("📝", "audit logging"),
            ("🛡️", "security settings"),
            ("🔧", "maintenance tools"),
        ]
        
        self.draw_feature_list(x + 2, y_pos, features)
        
        # System info
        if height > 20:
            y_pos = y + 16
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}system health:{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}uptime:{Colors.RESET} 14d 3h 27m")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}cpu usage:{Colors.RESET} 23%")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}memory:{Colors.RESET} 4.2/8.0 GB")
        
        # Shortcuts
        sys.stdout.write(f"\033[{y + height - 3};{x}H{Colors.BOLD}shortcuts:{Colors.RESET}")
        sys.stdout.write(f"\033[{y + height - 2};{x + 2}H{Colors.DIM}enter - manage | u - users | s - settings{Colors.RESET}")
        sys.stdout.flush()


class AIBuilderPreviewRenderer(ModulePreviewRenderer):
    """Preview renderer for AI Builder module"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        # Clear area completely
        self.clear(x, y, width, height)
        
        # Module header (lowercase)
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.CYAN}🤖 ai builder{Colors.RESET}")
        sys.stdout.write(f"\033[{y + 1};{x}H{Colors.DIM}{'─' * min(40, width - 2)}{Colors.RESET}")
        
        # Description
        y_pos = y + 3
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.CYAN}ai-powered development assistant{Colors.RESET}")
        
        # Features
        y_pos += 2
        sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}key features:{Colors.RESET}")
        y_pos += 1
        
        features = [
            ("🧠", "claude ai integration"),
            ("💻", "code generation"),
            ("🔍", "code review & analysis"),
            ("📚", "documentation generation"),
            ("🐛", "bug detection & fixes"),
            ("🎯", "architecture suggestions"),
            ("⚡", "performance optimization"),
            ("🔄", "refactoring assistance"),
        ]
        
        self.draw_feature_list(x + 2, y_pos, features)
        
        # AI stats
        if height > 20:
            y_pos = y + 16
            sys.stdout.write(f"\033[{y_pos};{x}H{Colors.BOLD}ai statistics:{Colors.RESET}")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}suggestions today:{Colors.RESET} 47")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}code generated:{Colors.RESET} 2,341 lines")
            y_pos += 1
            sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.DIM}accuracy rate:{Colors.RESET} {Colors.GREEN}94%{Colors.RESET}")
        
        # Shortcuts
        sys.stdout.write(f"\033[{y + height - 3};{x}H{Colors.BOLD}shortcuts:{Colors.RESET}")
        sys.stdout.write(f"\033[{y + height - 2};{x + 2}H{Colors.DIM}enter - chat | g - generate | a - analyze{Colors.RESET}")
        sys.stdout.flush()


class InvoiceProcessorRenderer(ContentRenderer):
    """Renderer for Invoice Processor module"""
    
    def __init__(self):
        try:
            from invoice_processor_cli import invoice_processor_cli
            self.processor = invoice_processor_cli
        except ImportError:
            self.processor = None
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        """Render invoice processor interface"""
        if self.processor:
            # Use the processor's own rendering
            self.processor.render_main_menu(x, y, width, height)
        else:
            # Fallback if module not available
            self.clear(x, y, width, height)
            sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.CYAN}invoice processor{Colors.RESET}")
            sys.stdout.write(f"\033[{y + 2};{x}H{Colors.RED}module not available{Colors.RESET}")
            sys.stdout.write(f"\033[{y + 3};{x}H{Colors.DIM}please check installation{Colors.RESET}")
            sys.stdout.flush()


class ToolsMenuRenderer(ContentRenderer):
    """Renderer for the tools submenu"""
    
    def __init__(self):
        self.tool_items = [
            ("system_info", "📊 system information", "view system details"),
            ("security_tools", "🔒 security tools", "security utilities"),
            ("setup_manager", "🔧 setup manager", "initial setup"),
            ("repair_tools", "🛠️ repair tools", "fix issues"),
            ("git", "📦 git manager", "version control"),
            ("web_interface", "🌐 web interface", "browser ui"),
        ]
        self.selected_index = 0
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        """Render tools menu"""
        # Clear area
        self.clear(x, y, width, height)
        
        # Draw title
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.GREEN}🛠️ tools{Colors.RESET}")
        
        # Display tool items
        y_pos = y + 2
        for i, (key, name, desc) in enumerate(self.tool_items):
            if y_pos + 2 < y + height:
                sys.stdout.write(f"\033[{y_pos};{x + 2}H")
                
                # Highlight selected item
                if i == self.selected_index:
                    sys.stdout.write(f"{Colors.BG_BLUE}{Colors.WHITE} {name:<35} {Colors.RESET}")
                else:
                    sys.stdout.write(f"  {name}")
                
                sys.stdout.write(f"\033[{y_pos + 1};{x + 4}H{Colors.DIM}{desc}{Colors.RESET}")
                y_pos += 2
        
        # Instructions
        sys.stdout.write(f"\033[{y + height - 2};{x + 2}H{Colors.DIM}↑↓ navigate | enter select | esc back{Colors.RESET}")
        sys.stdout.flush()


class SystemInfoRenderer(ContentRenderer):
    """Renderer for system information screen"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        """Render system information"""
        # Clear area
        self.clear(x, y, width, height)
        
        # Draw title
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.BLUE}📊 system information{Colors.RESET}")
        
        # Get system information
        import platform
        try:
            import psutil
            cpu_usage = f"{psutil.cpu_percent(interval=0.1)}%"
            memory = psutil.virtual_memory()
            memory_total = f"{memory.total / (1024**3):.1f} GB"
            memory_used = f"{memory.used / (1024**3):.1f} GB ({memory.percent}%)"
            disk = psutil.disk_usage('/')
            disk_total = f"{disk.total / (1024**3):.1f} GB"
            disk_free = f"{disk.free / (1024**3):.1f} GB ({100 - disk.percent:.1f}% free)"
        except ImportError:
            cpu_usage = "N/A (psutil not installed)"
            memory_total = "N/A"
            memory_used = "N/A"
            disk_total = "N/A"
            disk_free = "N/A"
        
        # Display information
        y_pos = y + 2
        sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.BOLD}system information:{Colors.RESET}")
        y_pos += 2
        
        # System details
        details = [
            ("hostname", platform.node()),
            ("platform", platform.system()),
            ("architecture", platform.machine()),
            ("python", platform.python_version()),
            ("", ""),  # Spacer
            ("cpu cores", str(platform.machine())),
            ("cpu usage", cpu_usage),
            ("", ""),  # Spacer
            ("memory total", memory_total),
            ("memory used", memory_used),
            ("", ""),  # Spacer
            ("disk total", disk_total),
            ("disk free", disk_free),
        ]
        
        for label, value in details:
            if y_pos < y + height - 2:
                sys.stdout.write(f"\033[{y_pos};{x + 2}H")
                if label:
                    sys.stdout.write(f"{Colors.DIM}{label}:{Colors.RESET} {value}")
                y_pos += 1
        
        # Press any key hint
        sys.stdout.write(f"\033[{y + height - 2};{x + 2}H{Colors.DIM}press any key to return{Colors.RESET}")
        sys.stdout.flush()


class SecurityToolsRenderer(ContentRenderer):
    """Renderer for security tools screen"""
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        """Render security tools"""
        # Clear area
        self.clear(x, y, width, height)
        
        # Draw title
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.RED}🔒 security tools{Colors.RESET}")
        
        # Security information
        y_pos = y + 2
        sys.stdout.write(f"\033[{y_pos};{x + 2}H{Colors.BOLD}network security:{Colors.RESET}")
        y_pos += 2
        
        # Try to get network security info
        try:
            import socket
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            details = [
                ("hostname", hostname),
                ("ip address", ip_address),
                ("firewall status", "checking..."),
                ("open ports", "scanning..."),
                ("active connections", "analyzing..."),
                ("", ""),  # Spacer
                ("security level", "moderate"),
            ]
        except Exception as e:
            details = [
                ("status", "Error getting network info"),
                ("error", str(e)),
            ]
        
        for label, value in details:
            if y_pos < y + height - 2:
                sys.stdout.write(f"\033[{y_pos};{x + 2}H")
                if label:
                    sys.stdout.write(f"{Colors.DIM}{label}:{Colors.RESET} {value}")
                y_pos += 1
        
        # Press any key hint
        sys.stdout.write(f"\033[{y + height - 2};{x + 2}H{Colors.DIM}press any key to return{Colors.RESET}")
        sys.stdout.flush()


class WebForgeRenderer(ContentRenderer):
    """Renderer for Web Forge menu"""
    
    def __init__(self):
        self.options = [
            ("start_all", "🚀 start all servers", "start django & react"),
            ("stop_all", "🛑 stop all servers", "stop all running servers"),
            ("restart_all", "🔄 restart all servers", "restart django & react"),
            ("", "", ""),
            ("start_django", "🐍 start django", "start backend server"),
            ("start_react", "⚛️  start react", "start frontend server"),
            ("", "", ""),
            ("status", "📊 server status", "check server status"),
            ("logs", "📜 view logs", "view server logs"),
            ("", "", ""),
            ("open_browser", "🌐 open in browser", "open web interface"),
        ]
        self.selected_index = 0
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        """Render Web Forge menu"""
        # Clear area
        self.clear(x, y, width, height)
        
        # Draw title
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.CYAN}🌐 web forge{Colors.RESET}")
        
        # Display options
        y_pos = y + 2
        selectable_index = 0
        
        for key, name, desc in self.options:
            if y_pos < y + height - 2:
                if key:  # Only selectable items
                    sys.stdout.write(f"\033[{y_pos};{x + 2}H")
                    if selectable_index == self.selected_index:
                        sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.WHITE} {name:<30} {Colors.RESET}")
                    else:
                        sys.stdout.write(f"  {name}")
                    
                    if desc:
                        sys.stdout.write(f"\033[{y_pos};{x + 35}H{Colors.DIM}{desc}{Colors.RESET}")
                    
                    selectable_index += 1
                y_pos += 1
        
        # Instructions
        sys.stdout.write(f"\033[{y + height - 2};{x + 2}H{Colors.DIM}↑↓ navigate | enter select | q quit{Colors.RESET}")
        sys.stdout.flush()


class VersionManagerRenderer(ContentRenderer):
    """Renderer for Version Manager menu"""
    
    def __init__(self):
        self.options = [
            ("current", "📊 current version", "show current version info"),
            ("history", "📜 version history", "view version history"),
            ("increment", "⬆️  increment version", "bump version number"),
            ("", "", ""),
            ("git_status", "📦 git status", "check git status"),
            ("git_commit", "💾 commit changes", "create git commit"),
            ("git_push", "🚀 push to remote", "push to remote repo"),
            ("", "", ""),
            ("archive", "📚 archive logs", "archive old logs"),
            ("clean", "🧹 clean temp files", "remove temporary files"),
        ]
        self.selected_index = 0
    
    def render(self, context: CLIContext, x: int, y: int, width: int, height: int):
        """Render Version Manager menu"""
        # Clear area
        self.clear(x, y, width, height)
        
        # Draw title
        sys.stdout.write(f"\033[{y};{x}H{Colors.BOLD}{Colors.MAGENTA}📊 version manager{Colors.RESET}")
        
        # Display options
        y_pos = y + 2
        selectable_index = 0
        
        for key, name, desc in self.options:
            if y_pos < y + height - 2:
                if key:  # Only selectable items
                    sys.stdout.write(f"\033[{y_pos};{x + 2}H")
                    if selectable_index == self.selected_index:
                        sys.stdout.write(f"{Colors.BG_ORANGE}{Colors.WHITE} {name:<30} {Colors.RESET}")
                    else:
                        sys.stdout.write(f"  {name}")
                    
                    if desc:
                        sys.stdout.write(f"\033[{y_pos};{x + 35}H{Colors.DIM}{desc}{Colors.RESET}")
                    
                    selectable_index += 1
                y_pos += 1
        
        # Instructions
        sys.stdout.write(f"\033[{y + height - 2};{x + 2}H{Colors.DIM}↑↓ navigate | enter select | q quit{Colors.RESET}")
        sys.stdout.flush()


# Register renderers with the context
def register_all_renderers(context: CLIContext):
    """Register all custom content renderers"""
    # Module preview renderers
    context.register_content_renderer('wimm', WIMMPreviewRenderer())
    context.register_content_renderer('wims', WIMSPreviewRenderer())
    context.register_content_renderer('currencies', CurrenciesPreviewRenderer())
    context.register_content_renderer('kisisel', PersonalInflationPreviewRenderer())
    context.register_content_renderer('documents', DocumentsPreviewRenderer())
    context.register_content_renderer('documents_menu', DocumentsMenuRenderer())
    context.register_content_renderer('cctv', CCTVPreviewRenderer())
    context.register_content_renderer('recaria', RecariaPreviewRenderer())
    context.register_content_renderer('birlikteyiz', BirlikteyizPreviewRenderer())
    context.register_content_renderer('invoice_processor', InvoiceProcessorRenderer())
    
    # Tool renderers
    context.register_content_renderer('tools', ToolsMenuRenderer())
    context.register_content_renderer('system_info', SystemInfoRenderer())
    context.register_content_renderer('security_tools', SecurityToolsRenderer())
    context.register_content_renderer('administration', AdministrationPreviewRenderer())
    
    # Dev tool renderers
    context.register_content_renderer('ai_builder', AIBuilderPreviewRenderer())
    context.register_content_renderer('web_forge', WebForgeRenderer())
    context.register_content_renderer('version_manager', VersionManagerRenderer())