#!/usr/bin/env python3
"""
🧠 UNIBOS Intelligent Command Processor
Kullanıcı komutlarını derin anlama ve işleme sistemi

Bu sistem kullanıcının ne demek istediğini anlar ve doğru aksiyonu alır.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

# UNIBOS imports
from unibos_agent_system import AgentRole
from agent_session_manager import CommandType

# Renkler
class Colors:
    RESET = "\033[0m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"

class UserIntent(Enum):
    """Kullanıcı niyeti türleri"""
    SEARCH_FEATURE = "search_feature"          # Bir özelliği aramak
    ANALYZE_CODE = "analyze_code"              # Kod analizi
    FIND_IMPLEMENTATION = "find_implementation" # İmplementasyon bulmak
    COMPARE_VERSIONS = "compare_versions"      # Versiyon karşılaştırma
    IMPROVE_CODE = "improve_code"              # Kod iyileştirme
    FIX_ISSUE = "fix_issue"                   # Sorun çözme

@dataclass
class ProcessedCommand:
    """İşlenmiş komut"""
    original_text: str
    intent: UserIntent
    target: str  # Ne aranıyor/analiz ediliyor
    context: Dict[str, Any]
    confidence: float
    actions: List[Dict[str, Any]]  # Yapılacak işlemler

class IntelligentCommandProcessor:
    """Akıllı komut işleyici"""
    
    def __init__(self):
        self.original_text = ""  # Güven skoru hesabı için
        # Proje yapısı bilgisi
        self.project_structure = {
            'currencies': {
                'main_file': 'src/currencies_enhanced.py',
                'features': ['döviz', 'currency', 'exchange', 'rate']
            },
            'inflation': {
                'main_file': 'projects/kisiselenflasyon/inflation.py',
                'features': ['kişisel enflasyon', 'inflation', 'enflasyon', 'personal']
            },
            'git': {
                'main_file': 'src/git_manager.py',
                'features': ['git', 'commit', 'version', 'versiyon']
            },
            'claude': {
                'main_file': 'src/claude_cli.py',
                'features': ['claude', 'ai', 'agent', 'ajan']
            }
        }
        
        # Komut pattern'leri
        self.command_patterns = {
            UserIntent.SEARCH_FEATURE: [
                r'(.+) özelliğini (.+) ara',
                r'(.+) özelliğini eski versiyonlarda ara',
                r'(.+) nerede kullanılmış',
                r'(.+) bul',
                r'find (.+)',
                r'search (.+)',
                r'(.+) için eski versiyonları tara',
                r'(.+) için eski versiyonlarda ara',
                r'(.+) eski versiyonları(.*)tara',
                r'(.+) bilimi(.*)için(.*)versiyonları(.*)tara'
            ],
            UserIntent.ANALYZE_CODE: [
                r'(.+) analiz et',
                r'(.+) incele',
                r'analyze (.+)',
                r'(.+) modülünü (.+) açısından incele'
            ],
            UserIntent.FIND_IMPLEMENTATION: [
                r'(.+) nasıl implement edilmiş',
                r'(.+) implementasyonu',
                r'(.+) kodu nerede'
            ]
        }
    
    def process_command(self, user_input: str) -> ProcessedCommand:
        """Kullanıcı komutunu işle ve anlamlandır"""
        self.original_text = user_input  # Güven skoru için sakla
        user_input_lower = user_input.lower()
        
        # 1. Niyeti tespit et
        intent = self._detect_intent(user_input_lower)
        
        # 2. Hedefi bul (ne aranıyor?)
        target = self._extract_target(user_input_lower, intent)
        
        # 3. İlgili modülü/dosyayı bul
        module_info = self._find_relevant_module(target)
        
        # 4. Bağlam bilgisi çıkar
        context = self._extract_context(user_input_lower, target, module_info)
        
        # 5. Yapılacak aksiyonları belirle
        actions = self._determine_actions(intent, target, module_info, context)
        
        # 6. Güven skoru hesapla
        confidence = self._calculate_confidence(intent, target, module_info, actions)
        
        return ProcessedCommand(
            original_text=user_input,
            intent=intent,
            target=target,
            context=context,
            confidence=confidence,
            actions=actions
        )
    
    def _detect_intent(self, text: str) -> UserIntent:
        """Kullanıcı niyetini tespit et"""
        # Öncelikli: eski/önceki versiyonlarda arama
        if any(word in text for word in ['eski', 'önceki']) and any(word in text for word in ['versiyon', 'versiyonlar']):
            return UserIntent.SEARCH_FEATURE
        
        # "derin araştırma" pattern'i
        if 'araştırma' in text and any(word in text for word in ['eski', 'önceki', 'versiyon']):
            return UserIntent.SEARCH_FEATURE
        
        # Diğer arama/bulma
        if any(word in text for word in ['ara', 'tara', 'bul', 'search', 'find', 'nerede']):
            if any(word in text for word in ['eski', 'önceki']):
                return UserIntent.SEARCH_FEATURE
            return UserIntent.FIND_IMPLEMENTATION
        
        if any(word in text for word in ['analiz', 'incele', 'analyze', 'inspect']):
            return UserIntent.ANALYZE_CODE
        
        if any(word in text for word in ['geliştir', 'iyileştir', 'improve', 'enhance']):
            return UserIntent.IMPROVE_CODE
        
        # Varsayılan
        return UserIntent.SEARCH_FEATURE
    
    def _extract_target(self, text: str, intent: UserIntent) -> str:
        """Hedef özelliği/modülü çıkar"""
        # Önce özel terimleri kontrol et
        if 'kişisel enflasyon' in text:
            return 'kişisel enflasyon'
        if 'personal inflation' in text:
            return 'personal inflation'
        
        # "X bölümü" pattern'i
        bolum_match = re.search(r'(\w+\s*\w*)\s*bölüm', text)
        if bolum_match:
            return bolum_match.group(1).strip()
        
        # Pattern matching
        for pattern in self.command_patterns.get(intent, []):
            match = re.search(pattern, text)
            if match:
                target = match.group(1).strip()
                # Temizle
                target = target.replace('bilimi', '').replace('bilimii', '').replace('bölümü', '').replace('bölüm', '').strip()
                return target
        
        # Basit çıkarım
        words = text.split()
        
        # İlk anlamlı kelimeyi al
        skip_words = ['bunu', 'şunu', 'onu', 'bir', 'bu', 'şu', 'için', 'eski', 'versiyonları', 'tara', 'ile', 'ilgili']
        for word in words:
            if word not in skip_words and len(word) > 2:
                return word
        
        return text
    
    def _find_relevant_module(self, target: str) -> Dict[str, Any]:
        """İlgili modül bilgisini bul"""
        target_lower = target.lower()
        
        # Direkt eşleşme
        for key, info in self.project_structure.items():
            for feature in info['features']:
                if feature in target_lower or target_lower in feature:
                    return {
                        'category': key,
                        'file': info['main_file'],
                        'features': info['features']
                    }
        
        # Kısmi eşleşme
        if 'enflasyon' in target_lower or 'inflation' in target_lower:
            return {
                'category': 'inflation',
                'file': 'projects/kisiselenflasyon/inflation.py',
                'features': ['kişisel enflasyon', 'inflation', 'enflasyon']
            }
        
        # Varsayılan
        return {
            'category': 'unknown',
            'file': 'src/currencies_enhanced.py',
            'features': []
        }
    
    def _extract_context(self, text: str, target: str, module_info: Dict) -> Dict[str, Any]:
        """Bağlam bilgisi çıkar"""
        context = {
            'has_version_request': 'eski' in text or 'versiyon' in text or 'önceki' in text,
            'is_security_related': 'güvenlik' in text or 'security' in text,
            'is_performance_related': 'performans' in text or 'hız' in text,
            'module_info': module_info
        }
        
        # Versiyon aralığı
        version_match = re.search(r'v(\d+)-v(\d+)', text)
        if version_match:
            context['version_range'] = f"v{version_match.group(1)}-v{version_match.group(2)}"
        
        return context
    
    def _determine_actions(self, intent: UserIntent, target: str, module_info: Dict, context: Dict) -> List[Dict[str, Any]]:
        """Yapılacak aksiyonları belirle"""
        actions = []
        
        if intent == UserIntent.SEARCH_FEATURE:
            # 1. Arşivde ara
            if context.get('has_version_request'):
                # Özel durumlar için ayarlama
                if 'enflasyon' in target.lower() or 'inflation' in target.lower():
                    # Kişisel enflasyon için özel tarama - TAM İSMİ KULLAN
                    search_term = "kişisel enflasyon" if 'kişisel' in target.lower() else "inflation"
                    actions.append({
                        'type': 'scan_feature',
                        'command': f'scan-feature "{search_term}" projects/kisiselenflasyon/inflation.py all',
                        'description': f"Eski versiyonlarda '{target}' özelliğini ara"
                    })
                else:
                    actions.append({
                        'type': 'scan_feature',
                        'command': f"scan-feature {target} {module_info['file']} all",
                        'description': f"Eski versiyonlarda '{target}' özelliğini ara"
                    })
            
            # 2. Güncel projede kontrol
            actions.append({
                'type': 'check_current',
                'file': module_info['file'],
                'description': f"Güncel projede '{target}' kontrolü"
            })
            
            # 3. Agent analizi
            actions.append({
                'type': 'agent_analysis',
                'command': f"analyze {module_info['file']}",
                'agents': ['CODE_ANALYST'],
                'description': "Modül analizi"
            })
        
        elif intent == UserIntent.ANALYZE_CODE:
            # Multi-agent analiz
            agents = ['CODE_ANALYST']
            if context.get('is_security_related'):
                agents.append('SECURITY_AUDITOR')
            if context.get('is_performance_related'):
                agents.append('PERFORMANCE_OPTIMIZER')
            
            actions.append({
                'type': 'multi_agent_analysis',
                'command': f"multi-analyze {module_info['file']} {','.join(agents)}",
                'description': "Detaylı kod analizi"
            })
        
        return actions
    
    def _calculate_confidence(self, intent: UserIntent, target: str, module_info: Dict, actions: List) -> float:
        """Güven skoru hesapla"""
        score = 0.0
        
        # Niyet doğru tespit edildi
        if intent != UserIntent.SEARCH_FEATURE:  # Varsayılan değil
            score += 0.2
        else:
            # SEARCH_FEATURE ise ama açık belirtilmiş mi?
            if any(word in self.original_text.lower() for word in ['ara', 'tara', 'bul', 'search']):
                score += 0.15
        
        # Hedef açık ve anlamlı
        if target and target != self.original_text:
            score += 0.25
            if len(target.split()) > 1:  # Birden fazla kelime
                score += 0.1
        
        # Modül bulundu ve doğru
        if module_info['category'] != 'unknown':
            score += 0.25
            # Hedef ile modül uyumlu mu?
            if any(feature in target.lower() for feature in module_info['features']):
                score += 0.1
        
        # Aksiyonlar belirlendi ve mantıklı
        if actions:
            score += 0.15
        
        return min(score, 1.0)
    
    def execute_actions(self, processed_command: ProcessedCommand, session_manager) -> Dict[str, Any]:
        """Belirlenen aksiyonları çalıştır"""
        results = {
            'command': processed_command,
            'executed': [],
            'results': []
        }
        
        for action in processed_command.actions:
            if action['type'] == 'scan_feature':
                # scan-feature komutunu direkt çalıştır
                print(f"\n{Colors.GREEN}▶ Çalıştırılıyor: {action['command']}{Colors.RESET}")
                
                # Komutu parse et
                import re
                # "scan-feature "kişisel enflasyon" projects/kisiselenflasyon/inflation.py all" formatı
                match = re.search(r'scan-feature\s+"([^"]+)"\s+(\S+)\s+(\S+)', action['command'])
                if not match:
                    # Tırnaksız format dene
                    parts = action['command'].split()
                    if len(parts) >= 4:
                        feature = parts[1]
                        module = parts[2]
                        version_range = parts[3]
                    else:
                        continue
                else:
                    feature = match.group(1)
                    module = match.group(2)
                    version_range = match.group(3)
                
                # Direkt metodu çağır
                # Önce çalışma dizinini kontrol et
                import os
                cwd = os.getcwd()
                if 'unibos' not in cwd or not cwd.endswith('unibos'):
                    # Ana dizine geç
                    unibos_path = '/Users/berkhatirli/Desktop/unibos'
                    if os.path.exists(unibos_path):
                        os.chdir(unibos_path)
                        print(f"{Colors.DIM}Changed directory to: {unibos_path}{Colors.RESET}")
                
                session_manager._scan_feature_across_versions(feature, module, version_range)
                results['executed'].append(action)
            
            elif action['type'] == 'check_current':
                # Güncel dosyayı kontrol et
                file_path = Path(action['file'])
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if processed_command.target.lower() in content.lower():
                            print(f"✓ '{processed_command.target}' güncel projede mevcut!")
                            results['results'].append({
                                'type': 'found_in_current',
                                'file': str(file_path)
                            })
                
            elif action['type'] in ['agent_analysis', 'multi_agent_analysis']:
                # Agent komutunu çalıştır
                session_manager._process_interactive_command(action['command'])
                results['executed'].append(action)
        
        return results

# Export
__all__ = ['IntelligentCommandProcessor', 'UserIntent', 'ProcessedCommand']