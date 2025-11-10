#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
communication_logger.py - UNIBOS Communication Log Management
Handles real-time logging of Claude-User conversations
"""

import os
import json
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import time

class CommunicationLogger:
    """Manages communication logs between Claude and User"""
    
    def __init__(self, base_path: str = None):
        """Initialize communication logger"""
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.current_log_file = None
        self.start_version = None
        self.current_version = None
        self.messages = []
        self.last_update = None
        self.update_interval = 15  # seconds
        self.update_thread = None
        self.is_active = False
        
        # İstanbul timezone
        self.istanbul_tz = timezone(timedelta(hours=3))
        
    def get_current_version(self) -> str:
        """Get current version from VERSION.json"""
        try:
            version_file = self.base_path / "src" / "VERSION.json"
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('version', 'v000')
        except:
            pass
        return 'v000'
    
    def start_new_log(self, initial_message: str = None):
        """Start a new communication log"""
        self.start_version = self.get_current_version()
        self.current_version = self.start_version
        
        # Create log filename
        timestamp = datetime.now(self.istanbul_tz).strftime('%Y%m%d_%H%M')
        self.current_log_file = self.base_path / f"CLAUDE_COMMUNICATION_LOG_{self.start_version}_to_{self.current_version}_{timestamp}.md"
        
        # Initialize log content
        self.messages = []
        if initial_message:
            self.add_message("User", initial_message)
        
        # Create initial log file
        self._write_log()
        
        # Start update thread
        self.is_active = True
        self.update_thread = threading.Thread(target=self._periodic_update, daemon=True)
        self.update_thread.start()
    
    def add_message(self, sender: str, message: str):
        """Add a message to the log"""
        if not self.is_active:
            return
            
        timestamp = datetime.now(self.istanbul_tz).strftime('%Y-%m-%d %H:%M:%S')
        self.messages.append({
            'timestamp': timestamp,
            'sender': sender,
            'message': message
        })
        
        # Update log immediately for important messages
        if sender == "System" or "error" in message.lower() or "hata" in message.lower():
            self._write_log()
    
    def update_version(self, new_version: str):
        """Update the current version and rename log file if needed"""
        if new_version != self.current_version:
            old_version = self.current_version
            self.current_version = new_version
            
            # Rename log file
            if self.current_log_file and self.current_log_file.exists():
                timestamp = datetime.now(self.istanbul_tz).strftime('%Y%m%d_%H%M')
                new_filename = f"CLAUDE_COMMUNICATION_LOG_{self.start_version}_to_{self.current_version}_{timestamp}.md"
                new_path = self.base_path / new_filename
                
                try:
                    self.current_log_file.rename(new_path)
                    self.current_log_file = new_path
                    self.add_message("System", f"Version updated: {old_version} → {new_version}")
                except:
                    pass
    
    def _write_log(self):
        """Write current messages to log file"""
        if not self.current_log_file:
            return
            
        try:
            content = f"""# CLAUDE COMMUNICATION LOG

**Başlangıç Versiyonu**: {self.start_version}
**Bitiş Versiyonu**: {self.current_version}
**Tarih**: {datetime.now(self.istanbul_tz).strftime('%Y-%m-%d %H:%M:%S')} +03:00
**Durum**: {'Aktif' if self.is_active else 'Tamamlandı'}

---

## 📋 İletişim Kayıtları

"""
            
            for msg in self.messages:
                sender_emoji = "👤" if msg['sender'] == "User" else "🤖" if msg['sender'] == "Claude" else "⚙️"
                content += f"\n### {sender_emoji} {msg['sender']} - {msg['timestamp']}\n\n"
                content += f"{msg['message']}\n\n"
                content += "---\n"
            
            # Add summary
            content += f"\n## 📊 Özet\n\n"
            content += f"- **Toplam Mesaj**: {len(self.messages)}\n"
            content += f"- **Kullanıcı Mesajları**: {len([m for m in self.messages if m['sender'] == 'User'])}\n"
            content += f"- **Claude Mesajları**: {len([m for m in self.messages if m['sender'] == 'Claude'])}\n"
            content += f"- **Sistem Mesajları**: {len([m for m in self.messages if m['sender'] == 'System'])}\n"
            
            # Check for unresolved issues
            unresolved = []
            for msg in self.messages:
                if any(keyword in msg['message'].lower() for keyword in ['hata', 'error', 'sorun', 'problem', 'devam ediyor']):
                    unresolved.append(msg['message'][:100] + "...")
            
            if unresolved:
                content += f"\n### ⚠️ Çözülmemiş Konular\n\n"
                for issue in unresolved[:5]:  # Show max 5
                    content += f"- {issue}\n"
            
            # Write to file
            with open(self.current_log_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.last_update = time.time()
            
        except Exception as e:
            print(f"Error writing communication log: {e}")
    
    def _periodic_update(self):
        """Periodically update the log file"""
        while self.is_active:
            time.sleep(self.update_interval)
            
            # Only update if there are new messages since last update
            if self.messages and (not self.last_update or time.time() - self.last_update > self.update_interval):
                self._write_log()
    
    def stop_logging(self, final_message: str = None):
        """Stop logging and finalize the log"""
        if final_message:
            self.add_message("System", final_message)
        
        self.is_active = False
        
        # Final write
        self._write_log()
        
        # Wait for thread to finish
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
    
    def get_active_logs(self) -> List[Path]:
        """Get list of active communication logs"""
        # Pattern 1: New format (vXXX_to_vYYY)
        versioned_logs = list(self.base_path.glob("CLAUDE_COMMUNICATION_LOG_v*_to_v*_*.md"))
        
        # Pattern 2: Old format
        standard_logs = list(self.base_path.glob("CLAUDE_COMMUNICATION_LOG_*.md"))
        
        # Combine and deduplicate
        all_logs = versioned_logs
        for log in standard_logs:
            if "_to_v" not in log.name and log not in all_logs:
                all_logs.append(log)
        
        # Sort by modification time (newest first)
        return sorted(all_logs, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def cleanup_old_logs(self, keep_count: int = 3):
        """Remove old communication logs beyond keep_count"""
        logs = self.get_active_logs()
        
        if len(logs) > keep_count:
            for log in logs[keep_count:]:
                try:
                    log.unlink()
                    print(f"Removed old log: {log.name}")
                except:
                    pass

# Global instance
comm_logger = CommunicationLogger()