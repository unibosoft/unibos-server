#!/usr/bin/env python3
"""
🧠 UNIBOS NLP Agent Orchestrator
Doğal dil tabanlı akıllı görev dağıtım sistemi

Bu sistem kullanıcının doğal dildeki isteklerini anlar ve uygun ajanlara
otomatik olarak görev dağıtımı yapar.

Author: Berk Hatırlı
Version: v242
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# UNIBOS imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unibos_agent_system import AgentRole
from agent_session_manager import AgentSessionManager, CommandType
from intelligent_command_processor import IntelligentCommandProcessor, UserIntent
try:
    from unibos_logger import logger, LogCategory, LogLevel
except ImportError:
    # Fallback logger
    class logger:
        @staticmethod
        def info(msg, **kwargs): print(f"INFO: {msg}")
        @staticmethod
        def error(msg, **kwargs): print(f"ERROR: {msg}")
        @staticmethod
        def warning(msg, **kwargs): print(f"WARNING: {msg}")
        @staticmethod
        def debug(msg, **kwargs): pass

# Renkler
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

class IntentType(Enum):
    """Kullanıcı niyeti türleri"""
    ANALYZE = "analyze"          # Analiz et, incele, bak
    SEARCH = "search"           # Ara, tara, bul
    IMPROVE = "improve"         # Geliştir, iyileştir, optimize et
    FIX = "fix"                # Düzelt, çöz, tamir et
    CREATE = "create"          # Oluştur, ekle, yeni
    EXPLAIN = "explain"        # Açıkla, anlat, göster
    REVIEW = "review"          # Gözden geçir, kontrol et
    SECURITY = "security"      # Güvenlik kontrolü
    PERFORMANCE = "performance" # Performans analizi
    DOCUMENT = "document"      # Dokümantasyon

@dataclass
class ParsedIntent:
    """Anlamlandırılmış kullanıcı niyeti"""
    raw_text: str
    intent_type: IntentType
    target_module: Optional[str] = None
    target_feature: Optional[str] = None
    suggested_agents: List[AgentRole] = field(default_factory=list)
    confidence: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    
class NLPAgentOrchestrator:
    """Doğal dil tabanlı ajan orkestratörü"""
    
    def __init__(self, session_manager: AgentSessionManager):
        self.session_manager = session_manager
        self.intelligent_processor = IntelligentCommandProcessor()
        
        # Ana orchestrator'ı al
        from unibos_orchestrator_manager import get_main_orchestrator
        self.main_orchestrator = get_main_orchestrator()
    
    def _get_intent_description(self, intent: UserIntent) -> str:
        """Niyet açıklaması"""
        descriptions = {
            UserIntent.SEARCH_FEATURE: "Eski versiyonlarda özellik arama",
            UserIntent.ANALYZE_CODE: "Kod analizi",
            UserIntent.FIND_IMPLEMENTATION: "İmplementasyon bulma",
            UserIntent.COMPARE_VERSIONS: "Versiyon karşılaştırma",
            UserIntent.IMPROVE_CODE: "Kod iyileştirme",
            UserIntent.FIX_ISSUE: "Sorun çözme"
        }
        return descriptions.get(intent, "Bilinmeyen işlem")
    
    def _get_confidence_bar(self, confidence: float) -> str:
        """Güven seviyesi görseli"""
        filled = int(confidence * 10)
        empty = 10 - filled
        bar = '█' * filled + '░' * empty
        percent = int(confidence * 100)
        
        if confidence >= 0.8:
            color = Colors.GREEN
        elif confidence >= 0.5:
            color = Colors.YELLOW
        else:
            color = Colors.RED
            
        return f"{color}[{bar}] {percent}%{Colors.RESET}"
        
        # Türkçe-İngilizce anahtar kelime eşlemeleri
        self.intent_keywords = {
            IntentType.ANALYZE: [
                'analiz', 'incele', 'bak', 'kontrol et', 'göster',
                'analyze', 'inspect', 'check', 'examine', 'review'
            ],
            IntentType.SEARCH: [
                'ara', 'tara', 'bul', 'nerede', 'hangi',
                'search', 'scan', 'find', 'locate', 'where'
            ],
            IntentType.IMPROVE: [
                'geliştir', 'iyileştir', 'optimize', 'güzelleştir', 'düzenle',
                'improve', 'enhance', 'optimize', 'refactor', 'upgrade'
            ],
            IntentType.FIX: [
                'düzelt', 'çöz', 'tamir', 'hata', 'sorun',
                'fix', 'solve', 'repair', 'bug', 'issue'
            ],
            IntentType.CREATE: [
                'oluştur', 'ekle', 'yeni', 'yarat', 'başlat',
                'create', 'add', 'new', 'generate', 'make'
            ],
            IntentType.EXPLAIN: [
                'açıkla', 'anlat', 'göster', 'ne yapar', 'nasıl',
                'explain', 'describe', 'show', 'what does', 'how'
            ],
            IntentType.SECURITY: [
                'güvenlik', 'güvenli', 'açık', 'zafiyet', 'tehdit',
                'security', 'secure', 'vulnerability', 'threat', 'risk'
            ],
            IntentType.PERFORMANCE: [
                'performans', 'hız', 'yavaş', 'optimize', 'verim',
                'performance', 'speed', 'slow', 'optimize', 'efficiency'
            ]
        }
        
        # Özellik/modül eşlemeleri
        self.feature_module_map = {
            # Döviz özellikleri
            'kişisel enflasyon': 'currencies_enhanced.py',
            'kisisel_enflasyon': 'currencies_enhanced.py',
            'personal inflation': 'currencies_enhanced.py',
            'döviz': 'currencies_enhanced.py',
            'currency': 'currencies_enhanced.py',
            'kur': 'currencies_enhanced.py',
            'exchange': 'currencies_enhanced.py',
            
            # Ana menü
            'menü': 'main.py',
            'menu': 'main.py',
            'navigasyon': 'main.py',
            'navigation': 'main.py',
            'ana ekran': 'main.py',
            'main screen': 'main.py',
            
            # Git işlemleri
            'git': 'git_manager.py',
            'commit': 'git_manager.py',
            'versiyon': 'git_manager.py',
            'version': 'git_manager.py',
            
            # Screenshot
            'ekran görüntüsü': 'screenshot_manager.py',
            'screenshot': 'screenshot_manager.py',
            'ss': 'screenshot_manager.py',
            
            # Claude entegrasyonu
            'claude': 'claude_cli.py',
            'ai': 'claude_cli.py',
            'yapay zeka': 'claude_cli.py',
            
            # Ajan sistemi
            'ajan': 'agent_session_manager.py',
            'agent': 'agent_session_manager.py'
        }
        
        # Ajan-görev eşlemeleri
        self.intent_agent_map = {
            IntentType.ANALYZE: [AgentRole.CODE_ANALYST],
            IntentType.SEARCH: [AgentRole.CODE_ANALYST],
            IntentType.IMPROVE: [AgentRole.REFACTOR_SPECIALIST, AgentRole.UI_IMPROVER],
            IntentType.FIX: [AgentRole.CODE_ANALYST, AgentRole.REFACTOR_SPECIALIST],
            IntentType.CREATE: [AgentRole.REFACTOR_SPECIALIST],
            IntentType.EXPLAIN: [AgentRole.DOCUMENTATION_EXPERT],
            IntentType.SECURITY: [AgentRole.SECURITY_AUDITOR],
            IntentType.PERFORMANCE: [AgentRole.PERFORMANCE_OPTIMIZER],
            IntentType.REVIEW: [AgentRole.CODE_ANALYST, AgentRole.SECURITY_AUDITOR],
            IntentType.DOCUMENT: [AgentRole.DOCUMENTATION_EXPERT]
        }
    
    def parse_natural_language(self, text: str) -> ParsedIntent:
        """Doğal dil metnini anlamlandır"""
        text_lower = text.lower()
        
        # Niyet tespiti
        intent_type = self._detect_intent(text_lower)
        
        # Modül/özellik tespiti
        target_module, target_feature = self._detect_target(text_lower)
        
        # Uygun ajanları belirle
        suggested_agents = self._suggest_agents(intent_type, text_lower)
        
        # Güven skoru hesapla
        confidence = self._calculate_confidence(intent_type, target_module, suggested_agents)
        
        # Ek bağlam bilgisi
        context = self._extract_context(text_lower)
        
        return ParsedIntent(
            raw_text=text,
            intent_type=intent_type,
            target_module=target_module,
            target_feature=target_feature,
            suggested_agents=suggested_agents,
            confidence=confidence,
            context=context
        )
    
    def _detect_intent(self, text: str) -> IntentType:
        """Metinden kullanıcı niyetini tespit et"""
        intent_scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            # En yüksek skora sahip niyeti döndür
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        
        # Varsayılan niyet
        return IntentType.ANALYZE
    
    def _detect_target(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Hedef modül ve özelliği tespit et"""
        target_module = None
        target_feature = None
        
        # Özellik/modül eşlemelerini kontrol et
        for feature, module in self.feature_module_map.items():
            if feature in text:
                target_module = module
                target_feature = feature
                break
        
        # Direkt modül adı geçiyor mu kontrol et
        if not target_module:
            modules = ['main.py', 'currencies_enhanced.py', 'git_manager.py', 
                      'screenshot_manager.py', 'claude_cli.py', 'agent_session_manager.py']
            for module in modules:
                if module.replace('.py', '') in text or module in text:
                    target_module = module
                    break
        
        return target_module, target_feature
    
    def _suggest_agents(self, intent: IntentType, text: str) -> List[AgentRole]:
        """Niyet ve metne göre uygun ajanları öner"""
        agents = list(self.intent_agent_map.get(intent, [AgentRole.CODE_ANALYST]))
        
        # Özel durumlar için ek ajanlar
        if 'güvenlik' in text or 'security' in text:
            if AgentRole.SECURITY_AUDITOR not in agents:
                agents.append(AgentRole.SECURITY_AUDITOR)
        
        if 'performans' in text or 'performance' in text or 'yavaş' in text:
            if AgentRole.PERFORMANCE_OPTIMIZER not in agents:
                agents.append(AgentRole.PERFORMANCE_OPTIMIZER)
        
        if 'ui' in text or 'arayüz' in text or 'görünüm' in text:
            if AgentRole.UI_IMPROVER not in agents:
                agents.append(AgentRole.UI_IMPROVER)
        
        if 'test' in text:
            if AgentRole.TEST_ENGINEER not in agents:
                agents.append(AgentRole.TEST_ENGINEER)
        
        return agents
    
    def _calculate_confidence(self, intent: IntentType, module: Optional[str], 
                            agents: List[AgentRole]) -> float:
        """Güven skoru hesapla (0.0-1.0)"""
        score = 0.0
        
        # Niyet tespit edildi
        if intent != IntentType.ANALYZE:  # ANALYZE varsayılan
            score += 0.3
        
        # Hedef modül tespit edildi
        if module:
            score += 0.4
        
        # Uygun ajanlar belirlendi
        if agents:
            score += 0.3
        
        return min(score, 1.0)
    
    def _extract_context(self, text: str) -> Dict[str, Any]:
        """Metinden ek bağlam bilgisi çıkar"""
        context = {}
        
        # Versiyon aralığı
        version_match = re.search(r'v(\d+)-v(\d+)', text)
        if version_match:
            context['version_range'] = f"v{version_match.group(1)}-v{version_match.group(2)}"
        
        # Aciliyet
        if any(word in text for word in ['acil', 'hemen', 'urgent', 'immediately']):
            context['priority'] = 'high'
        
        # Detay seviyesi
        if any(word in text for word in ['detaylı', 'ayrıntılı', 'detailed', 'comprehensive']):
            context['detail_level'] = 'high'
        
        return context
    
    def execute_intent(self, parsed_intent: ParsedIntent) -> Dict[str, Any]:
        """Anlamlandırılmış niyeti çalıştır"""
        results = {
            'intent': parsed_intent,
            'executed_commands': [],
            'agent_responses': {},
            'success': False
        }
        
        print(f"\n{Colors.CYAN}🧠 NLP Agent Orchestrator{Colors.RESET}")
        print(f"{Colors.YELLOW}Anladığım: {parsed_intent.intent_type.value}{Colors.RESET}")
        
        if parsed_intent.target_module:
            print(f"{Colors.YELLOW}Hedef: {parsed_intent.target_module}{Colors.RESET}")
        
        if parsed_intent.target_feature:
            print(f"{Colors.YELLOW}Özellik: {parsed_intent.target_feature}{Colors.RESET}")
        
        print(f"{Colors.YELLOW}Güven: {parsed_intent.confidence:.0%}{Colors.RESET}")
        print(f"{Colors.YELLOW}Önerilen ajanlar: {', '.join(a.value for a in parsed_intent.suggested_agents)}{Colors.RESET}")
        
        # Onay al
        print(f"\n{Colors.CYAN}Bu analiz doğru mu? (e/h):{Colors.RESET} ", end='')
        response = input().strip().lower()
        
        if response != 'e':
            print(f"{Colors.YELLOW}İsteğinizi daha açık ifade edebilir misiniz?{Colors.RESET}")
            return results
        
        # Görevleri çalıştır
        if parsed_intent.intent_type == IntentType.SEARCH and parsed_intent.target_feature:
            # Özellik tarama
            module = parsed_intent.target_module or 'currencies_enhanced.py'
            version_range = parsed_intent.context.get('version_range', 'all')
            
            # Özel durumlar için düzeltme
            if 'kişisel enflasyon' in parsed_intent.target_feature.lower():
                # Doğrudan inflation.py'yi hedefle
                cmd = f"scan-feature inflation projects/kisiselenflasyon/inflation.py {version_range}"
            else:
                cmd = f"scan-feature {parsed_intent.target_feature} {module} {version_range}"
            
            print(f"\n{Colors.GREEN}Çalıştırılıyor: {cmd}{Colors.RESET}")
            self.session_manager._process_interactive_command(cmd)
            results['executed_commands'].append(cmd)
            
        elif parsed_intent.intent_type in [IntentType.ANALYZE, IntentType.IMPROVE, IntentType.REVIEW]:
            # Çoklu ajan analizi
            if parsed_intent.target_module and len(parsed_intent.suggested_agents) > 1:
                agents_str = ','.join(a.name for a in parsed_intent.suggested_agents)
                cmd = f"multi-analyze {parsed_intent.target_module} {agents_str}"
                print(f"\n{Colors.GREEN}Çalıştırılıyor: {cmd}{Colors.RESET}")
                self.session_manager._process_interactive_command(cmd)
                results['executed_commands'].append(cmd)
            
            # Tek ajan analizi
            elif parsed_intent.target_module:
                for agent in parsed_intent.suggested_agents:
                    # Ajan oluştur
                    create_cmd = f"create {agent.name}"
                    self.session_manager._process_interactive_command(create_cmd)
                    
                    # Analiz yap
                    action = 'enhance' if parsed_intent.intent_type == IntentType.IMPROVE else 'analyze'
                    cmd = f"{action} {parsed_intent.target_module}"
                    print(f"\n{Colors.GREEN}Çalıştırılıyor: {cmd}{Colors.RESET}")
                    self.session_manager._process_interactive_command(cmd)
                    results['executed_commands'].append(cmd)
        
        results['success'] = len(results['executed_commands']) > 0
        return results
    
    def start_conversational_mode(self):
        """Sohbet modunu başlat"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}🧠 UNIBOS Doğal Dil Modu{Colors.RESET}")
        print(f"{Colors.YELLOW}Ne yapmamı istersiniz?{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
        
        print(f"{Colors.GREEN}Örnekler:{Colors.RESET}")
        print(f"  • Kişisel enflasyon özelliğini eski versiyonlarda ara")
        print(f"  • Döviz modülünü güvenlik açısından incele")
        print(f"  • Ana menüdeki navigasyon sorunlarını düzelt")
        print(f"  • Git manager'ın performansını optimize et")
        print(f"  • Claude entegrasyonunu geliştir\n")
        
        while True:
            try:
                # Kullanıcı girişi
                user_input = input(f"{Colors.GREEN}Siz>{Colors.RESET} ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['çık', 'exit', 'quit', 'q']:
                    print(f"{Colors.YELLOW}Doğal dil modundan çıkılıyor...{Colors.RESET}")
                    break
                
                # Önce ana orchestrator ile dene
                if self.main_orchestrator:
                    orch_result = self.main_orchestrator.process_natural_language_command(user_input)
                    if orch_result['understanding']:
                        print(f"\n{Colors.CYAN}Anladığım:{Colors.RESET} {orch_result['understanding'].get('target', user_input)}")
                        print(f"{Colors.GREEN}Ana orchestrator üzerinden işleniyor...{Colors.RESET}")
                        
                        # Orchestrator'ın belirlediği aksiyonları çalıştır
                        for action in orch_result['actions']:
                            if action['type'] == 'scan_feature':
                                target = orch_result['understanding']['target']
                                
                                # Çalışma dizinini kontrol et
                                import os
                                current_dir = os.getcwd()
                                if not current_dir.endswith('unibos'):
                                    unibos_path = '/Users/berkhatirli/Desktop/unibos'
                                    if os.path.exists(unibos_path):
                                        os.chdir(unibos_path)
                                        print(f"{Colors.DIM}Working directory changed to: {unibos_path}{Colors.RESET}")
                                
                                self.session_manager._scan_feature_across_versions(
                                    target, 
                                    'projects/kisiselenflasyon/inflation.py', 
                                    'all'
                                )
                        continue
                
                # Fallback: intelligent processor
                processed_cmd = self.intelligent_processor.process_command(user_input)
                
                # Basit ve direkt gösterim
                print(f"\n{Colors.CYAN}Anladığım:{Colors.RESET} {processed_cmd.target}")
                
                # Güven çok düşükse direkt hata ver
                if processed_cmd.confidence < 0.4:
                    print(f"{Colors.YELLOW}Tam olarak ne demek istediğinizi anlayamadım.{Colors.RESET}")
                    print(f"{Colors.DIM}Örnek: 'kişisel enflasyon özelliğini eski versiyonlarda ara'{Colors.RESET}")
                    continue
                
                # Orta güvende onay iste (sadece güven skorunu göster)
                if processed_cmd.confidence < 0.7:
                    print(f"Güven: {self._get_confidence_bar(processed_cmd.confidence)}")
                    print(f"\n{Colors.YELLOW}Devam edeyim mi? (e/h):{Colors.RESET} ", end='')
                    confirm = input().strip().lower()
                    if confirm != 'e':
                        continue
                
                # Direkt çalıştır - fazla detay gösterme
                self.intelligent_processor.execute_actions(processed_cmd, self.session_manager)
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}İptal edildi{Colors.RESET}")
            except Exception as e:
                print(f"\n{Colors.RED}Hata: {e}{Colors.RESET}")

# Export
__all__ = ['NLPAgentOrchestrator', 'IntentType', 'ParsedIntent']