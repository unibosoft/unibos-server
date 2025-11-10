#!/usr/bin/env python3
"""
Claude Health Monitor - Claude CLI sağlık durumu takip sistemi
Timeout tespiti, recovery mekanizması ve periyodik kontroller
"""

import time
import threading
import subprocess
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import signal
import psutil

class ClaudeHealthMonitor:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.health_file = self.base_path / 'data' / 'claude_health.json'
        self.timeout_threshold = 30  # seconds
        self.check_interval = 5  # seconds
        self.monitoring_thread = None
        self.is_monitoring = False
        self.health_data = self.load_health_data()
        self.current_session = None
        
    def load_health_data(self) -> Dict:
        """Load health monitoring data"""
        if self.health_file.exists():
            try:
                with open(self.health_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'sessions': [],
            'timeouts': [],
            'recoveries': [],
            'statistics': {
                'total_sessions': 0,
                'successful_sessions': 0,
                'timeout_count': 0,
                'recovery_count': 0,
                'average_response_time': 0
            }
        }
    
    def save_health_data(self):
        """Save health monitoring data"""
        os.makedirs(self.health_file.parent, exist_ok=True)
        with open(self.health_file, 'w', encoding='utf-8') as f:
            json.dump(self.health_data, f, indent=2, ensure_ascii=False)
    
    def start_session(self, session_id: str, command: str):
        """Start monitoring a new Claude session"""
        self.current_session = {
            'id': session_id,
            'command': command,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'response_time': None,
            'timeout_detected': False
        }
        self.health_data['sessions'].append(self.current_session)
        self.health_data['statistics']['total_sessions'] += 1
        self.save_health_data()
        
        # Start monitoring thread
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitor_session)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def end_session(self, success: bool = True):
        """End current session monitoring"""
        if self.current_session:
            end_time = datetime.now()
            start_time = datetime.fromisoformat(self.current_session['start_time'])
            response_time = (end_time - start_time).total_seconds()
            
            self.current_session['end_time'] = end_time.isoformat()
            self.current_session['response_time'] = response_time
            self.current_session['status'] = 'completed' if success else 'failed'
            
            if success:
                self.health_data['statistics']['successful_sessions'] += 1
                
            # Update average response time
            total_sessions = self.health_data['statistics']['successful_sessions']
            if total_sessions > 0:
                avg_time = self.health_data['statistics']['average_response_time']
                new_avg = ((avg_time * (total_sessions - 1)) + response_time) / total_sessions
                self.health_data['statistics']['average_response_time'] = new_avg
            
            self.save_health_data()
            self.current_session = None
            self.is_monitoring = False
    
    def _monitor_session(self):
        """Monitor current session for timeouts"""
        start_time = datetime.now()
        
        while self.is_monitoring:
            elapsed = (datetime.now() - start_time).total_seconds()
            
            if elapsed > self.timeout_threshold and self.current_session:
                if not self.current_session['timeout_detected']:
                    self.current_session['timeout_detected'] = True
                    self._handle_timeout()
            
            time.sleep(self.check_interval)
    
    def _handle_timeout(self):
        """Handle timeout situation"""
        print(f"\n⚠️ Claude timeout tespit edildi! ({self.timeout_threshold} saniye)")
        
        timeout_event = {
            'session_id': self.current_session['id'],
            'timestamp': datetime.now().isoformat(),
            'threshold': self.timeout_threshold,
            'command': self.current_session['command']
        }
        
        self.health_data['timeouts'].append(timeout_event)
        self.health_data['statistics']['timeout_count'] += 1
        self.save_health_data()
        
        # Attempt recovery
        recovery_success = self._attempt_recovery()
        if recovery_success:
            print("✅ Recovery başarılı!")
        else:
            print("❌ Recovery başarısız!")
    
    def _attempt_recovery(self) -> bool:
        """Attempt to recover from timeout"""
        recovery_event = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.current_session['id'],
            'method': None,
            'success': False
        }
        
        try:
            # Method 1: Send interrupt signal
            print("🔄 Recovery Method 1: Interrupt signal gönderiliyor...")
            # Find claude process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'claude' in str(proc.info.get('cmdline', '')).lower():
                    os.kill(proc.info['pid'], signal.SIGINT)
                    time.sleep(2)
                    recovery_event['method'] = 'interrupt_signal'
                    recovery_event['success'] = True
                    break
            
            # Method 2: Kill and restart
            if not recovery_event['success']:
                print("🔄 Recovery Method 2: Process restart deneniyor...")
                subprocess.run(['pkill', '-f', 'claude'], capture_output=True)
                time.sleep(1)
                recovery_event['method'] = 'process_restart'
                recovery_event['success'] = True
            
        except Exception as e:
            print(f"❌ Recovery hatası: {e}")
            recovery_event['error'] = str(e)
        
        self.health_data['recoveries'].append(recovery_event)
        if recovery_event['success']:
            self.health_data['statistics']['recovery_count'] += 1
        
        self.save_health_data()
        return recovery_event['success']
    
    def get_health_status(self) -> Dict:
        """Get current health status"""
        status = {
            'is_healthy': True,
            'current_session': self.current_session,
            'recent_timeouts': [],
            'statistics': self.health_data['statistics'],
            'recommendations': []
        }
        
        # Check recent timeouts
        now = datetime.now()
        for timeout in self.health_data['timeouts'][-10:]:  # Last 10 timeouts
            timeout_time = datetime.fromisoformat(timeout['timestamp'])
            if (now - timeout_time).total_seconds() < 3600:  # Last hour
                status['recent_timeouts'].append(timeout)
        
        # Determine health
        timeout_rate = 0
        if self.health_data['statistics']['total_sessions'] > 0:
            timeout_rate = (self.health_data['statistics']['timeout_count'] / 
                          self.health_data['statistics']['total_sessions'])
        
        if timeout_rate > 0.3:  # 30% timeout rate
            status['is_healthy'] = False
            status['recommendations'].append("Yüksek timeout oranı tespit edildi. Claude CLI'ı yeniden başlatmayı deneyin.")
        
        if len(status['recent_timeouts']) > 3:
            status['is_healthy'] = False
            status['recommendations'].append("Son 1 saatte çok fazla timeout. Sistem kaynaklarını kontrol edin.")
        
        avg_response = self.health_data['statistics']['average_response_time']
        if avg_response > 60:  # 1 minute average
            status['recommendations'].append("Ortalama yanıt süresi yüksek. Daha basit görevler deneyin.")
        
        return status
    
    def display_health_report(self):
        """Display health report"""
        status = self.get_health_status()
        
        print("\n" + "="*60)
        print("🏥 Claude Health Monitor - Sağlık Raporu")
        print("="*60)
        
        # Overall status
        health_emoji = "✅" if status['is_healthy'] else "❌"
        print(f"\nGenel Durum: {health_emoji} {'Sağlıklı' if status['is_healthy'] else 'Sorunlu'}")
        
        # Statistics
        stats = status['statistics']
        print(f"\n📊 İstatistikler:")
        print(f"  • Toplam oturum: {stats['total_sessions']}")
        print(f"  • Başarılı oturum: {stats['successful_sessions']}")
        print(f"  • Timeout sayısı: {stats['timeout_count']}")
        print(f"  • Recovery sayısı: {stats['recovery_count']}")
        print(f"  • Ortalama yanıt süresi: {stats['average_response_time']:.2f} saniye")
        
        # Success rate
        if stats['total_sessions'] > 0:
            success_rate = (stats['successful_sessions'] / stats['total_sessions']) * 100
            timeout_rate = (stats['timeout_count'] / stats['total_sessions']) * 100
            print(f"  • Başarı oranı: {success_rate:.1f}%")
            print(f"  • Timeout oranı: {timeout_rate:.1f}%")
        
        # Current session
        if status['current_session']:
            print(f"\n🔄 Aktif Oturum:")
            print(f"  • ID: {status['current_session']['id']}")
            print(f"  • Komut: {status['current_session']['command']}")
            print(f"  • Başlangıç: {status['current_session']['start_time']}")
        
        # Recent timeouts
        if status['recent_timeouts']:
            print(f"\n⚠️ Son Timeout'lar (son 1 saat):")
            for timeout in status['recent_timeouts'][-5:]:
                print(f"  • {timeout['timestamp']} - {timeout['command']}")
        
        # Recommendations
        if status['recommendations']:
            print(f"\n💡 Öneriler:")
            for rec in status['recommendations']:
                print(f"  • {rec}")
        
        print("\n" + "="*60)
    
    def start_background_monitoring(self):
        """Start background health monitoring"""
        def periodic_check():
            while True:
                time.sleep(300)  # Check every 5 minutes
                
                # Check for zombie Claude processes
                zombie_count = 0
                for proc in psutil.process_iter(['pid', 'name', 'status']):
                    if 'claude' in str(proc.info.get('name', '')).lower():
                        if proc.info.get('status') == psutil.STATUS_ZOMBIE:
                            zombie_count += 1
                            try:
                                proc.kill()
                            except:
                                pass
                
                if zombie_count > 0:
                    print(f"\n🧟 {zombie_count} zombie Claude process temizlendi")
                
                # Auto-save health data
                self.save_health_data()
        
        monitor_thread = threading.Thread(target=periodic_check)
        monitor_thread.daemon = True
        monitor_thread.start()


# Integration helper functions
def with_health_monitoring(func):
    """Decorator to add health monitoring to Claude operations"""
    def wrapper(*args, **kwargs):
        monitor = ClaudeHealthMonitor()
        session_id = f"session_{int(time.time())}"
        command = kwargs.get('command', 'unknown')
        
        monitor.start_session(session_id, command)
        try:
            result = func(*args, **kwargs)
            monitor.end_session(success=True)
            return result
        except Exception as e:
            monitor.end_session(success=False)
            raise e
    
    return wrapper


if __name__ == "__main__":
    # Test the health monitor
    monitor = ClaudeHealthMonitor()
    monitor.display_health_report()
    
    # Start background monitoring
    monitor.start_background_monitoring()
    print("\n🏥 Claude Health Monitor başlatıldı (arka planda çalışıyor)")