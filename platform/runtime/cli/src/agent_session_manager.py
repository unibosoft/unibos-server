#!/usr/bin/env python3
"""
🤝 UNIBOS Agent Session Manager
Ajanlarla sürekli iletişim ve komut yönetimi sistemi

Author: Berk Hatırlı
Version: v239
"""

import os
import sys
import json
import time
import queue
import threading
import glob
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

# UNIBOS logger
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from unibos_logger import logger, LogCategory, LogLevel
except ImportError:
    class logger:
        @staticmethod
        def info(msg, **kwargs): print(f"INFO: {msg}")
        @staticmethod
        def error(msg, **kwargs): print(f"ERROR: {msg}")
        @staticmethod
        def warning(msg, **kwargs): print(f"WARNING: {msg}")
        @staticmethod
        def debug(msg, **kwargs): pass

# Colors
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

class SessionState(Enum):
    """Oturum durumları"""
    IDLE = "idle"
    ACTIVE = "active"
    PROCESSING = "processing"
    WAITING_RESPONSE = "waiting_response"
    PAUSED = "paused"
    TERMINATED = "terminated"

class CommandType(Enum):
    """Komut tipleri"""
    ANALYZE = "analyze"
    ENHANCE = "enhance"
    REFACTOR = "refactor"
    OPTIMIZE = "optimize"
    SECURE = "secure"
    TEST = "test"
    DOCUMENT = "document"
    CUSTOM = "custom"

@dataclass
class AgentCommand:
    """Ajan komutu"""
    id: str
    agent_role: str
    command_type: CommandType
    module: str
    content: str
    priority: int = 5
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Optional[Any] = None

@dataclass
class AgentResponse:
    """Ajan yanıtı"""
    command_id: str
    agent_role: str
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time: float = 0.0
    success: bool = True
    error: Optional[str] = None

class AgentSession:
    """Tekil ajan oturumu"""
    
    def __init__(self, session_id: str, agent_role: str, agent_instance: Any):
        self.session_id = session_id
        self.agent_role = agent_role
        self.agent = agent_instance
        self.state = SessionState.IDLE
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.history: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_running = True
        self.worker_thread = None
        
    def start(self):
        """Oturumu başlat"""
        self.state = SessionState.ACTIVE
        self.worker_thread = threading.Thread(target=self._process_commands, daemon=True)
        self.worker_thread.start()
        logger.info(f"Agent session started: {self.agent_role}", category=LogCategory.CLAUDE)
        
    def stop(self):
        """Oturumu durdur"""
        self.is_running = False
        self.state = SessionState.TERMINATED
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info(f"Agent session stopped: {self.agent_role}", category=LogCategory.CLAUDE)
        
    def send_command(self, command: AgentCommand):
        """Komut gönder"""
        self.command_queue.put(command)
        self.last_activity = datetime.now()
        logger.debug(f"Command queued for {self.agent_role}: {command.id}", category=LogCategory.CLAUDE)
        
    def get_response(self, timeout: Optional[float] = None) -> Optional[AgentResponse]:
        """Yanıt al"""
        try:
            return self.response_queue.get(timeout=timeout)
        except queue.Empty:
            return None
            
    def _process_commands(self):
        """Komutları işle (worker thread)"""
        while self.is_running:
            try:
                # Komut al
                command = self.command_queue.get(timeout=1)
                self.state = SessionState.PROCESSING
                
                # Komutu işle
                start_time = time.time()
                try:
                    result = self._execute_command(command)
                    execution_time = time.time() - start_time
                    
                    # Yanıt oluştur
                    response = AgentResponse(
                        command_id=command.id,
                        agent_role=self.agent_role,
                        content=result,
                        execution_time=execution_time,
                        success=True
                    )
                    
                    # Komut durumunu güncelle
                    command.status = "completed"
                    command.result = result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    response = AgentResponse(
                        command_id=command.id,
                        agent_role=self.agent_role,
                        content=None,
                        execution_time=execution_time,
                        success=False,
                        error=str(e)
                    )
                    command.status = "failed"
                    logger.error(f"Command execution failed: {e}", category=LogCategory.CLAUDE)
                
                # Yanıtı kuyruğa ekle
                self.response_queue.put(response)
                
                # Geçmişe ekle
                self.history.append({
                    'command': command,
                    'response': response
                })
                
                self.state = SessionState.ACTIVE
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker thread error: {e}", category=LogCategory.CLAUDE)
                
    def _execute_command(self, command: AgentCommand) -> Any:
        """Komutu ajanla çalıştır"""
        # Analiz yap
        if command.command_type == CommandType.ANALYZE:
            context = self.agent.analyze_codebase(command.module)
            improvements = self.agent.generate_improvement_plan()
            return {
                'context': context,
                'improvements': improvements,
                'module': command.module
            }
            
        # İyileştirme yap
        elif command.command_type == CommandType.ENHANCE:
            context = self.agent.analyze_codebase(command.module)
            improvements = self.agent.generate_improvement_plan()
            # Burada Claude'a gönderim yapılabilir
            return {
                'improvements': improvements,
                'ready_for_claude': True
            }
            
        # Özel komut
        elif command.command_type == CommandType.CUSTOM:
            # Özel komut işleme
            return {
                'custom_result': f"Processed custom command: {command.content}"
            }
            
        else:
            return {
                'message': f"Command type {command.command_type} processed"
            }

class AgentSessionManager:
    """Çoklu ajan oturum yöneticisi"""
    
    def __init__(self, claude_cli):
        self.claude_cli = claude_cli
        self.sessions: Dict[str, AgentSession] = {}
        self.command_history: List[AgentCommand] = []
        self.response_handlers: Dict[str, Callable] = {}
        self.is_interactive = False
        self.current_session_id = None
        
        # Ana orchestrator'ı kullan
        from unibos_orchestrator_manager import get_main_orchestrator
        self.orchestrator = get_main_orchestrator(claude_cli)
        
        # Agent mapping - orchestrator'dan al
        self.available_agents = {}
            
    def create_session(self, agent_role: str) -> str:
        """Yeni ajan oturumu oluştur"""
        # Orchestrator'dan agent'ı al
        from unibos_agent_system import AgentRole
        
        # String'i AgentRole enum'a çevir
        agent_enum = None
        for role in AgentRole:
            if role.value == agent_role:
                agent_enum = role
                break
        
        if not agent_enum or agent_enum not in self.orchestrator.agents:
            raise ValueError(f"Unknown agent role: {agent_role}")
        
        # Gerçek agent'ı al
        agent = self.orchestrator.agents[agent_enum]
        
        session_id = f"{agent_role}_{int(time.time())}"
        
        # Oturum oluştur
        session = AgentSession(session_id, agent_role, agent)
        session.start()
        
        self.sessions[session_id] = session
        logger.info(f"Created session: {session_id}", category=LogCategory.CLAUDE)
        
        return session_id
        
    def send_command(self, session_id: str, command_type: CommandType, 
                    module: str, content: str = "", priority: int = 5) -> str:
        """Oturuma komut gönder"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
            
        # Komut oluştur
        command_id = f"cmd_{int(time.time() * 1000)}"
        command = AgentCommand(
            id=command_id,
            agent_role=session.agent_role,
            command_type=command_type,
            module=module,
            content=content,
            priority=priority
        )
        
        # Geçmişe ekle
        self.command_history.append(command)
        
        # Oturuma gönder
        session.send_command(command)
        
        return command_id
        
    def get_response(self, session_id: str, timeout: float = 30) -> Optional[AgentResponse]:
        """Oturumdan yanıt al"""
        session = self.sessions.get(session_id)
        if not session:
            return None
            
        return session.get_response(timeout)
        
    def broadcast_command(self, command_type: CommandType, module: str, 
                         content: str = "") -> Dict[str, str]:
        """Tüm aktif ajanlara komut gönder"""
        command_ids = {}
        
        for session_id, session in self.sessions.items():
            if session.state in [SessionState.ACTIVE, SessionState.IDLE]:
                cmd_id = self.send_command(session_id, command_type, module, content)
                command_ids[session_id] = cmd_id
                
        return command_ids
        
    def start_interactive_shell(self):
        """İnteraktif kabuk başlat"""
        self.is_interactive = True
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}🤖 UNIBOS Agent Interactive Shell{Colors.RESET}")
        print(f"{Colors.YELLOW}Multiple agents at your command{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
        
        # Hızlı başlangıç bilgisi
        print(f"{Colors.GREEN}Hızlı Başlangıç:{Colors.RESET}")
        print(f"  • 'help' yazarak tüm komutları görüntüleyin")
        print(f"  • 'nlp' yazarak doğal dil moduna geçin 🧠")
        print(f"  • 'create CODE_ANALYST' ile yeni bir ajan başlatın")
        print(f"  • 'analyze currencies_enhanced.py' ile modül analizi yapın")
        print(f"  • 'scan-feature kisisel_enflasyon currencies_enhanced.py' ile özellik taraması")
        print(f"  • 'multi-analyze currencies_enhanced.py' ile çoklu ajan analizi")
        print(f"  • 'exit' ile çıkış yapın\n")
        
        # Mevcut oturumları göster
        self._show_sessions()
        
        while self.is_interactive:
            try:
                # Prompt göster
                prompt = f"{Colors.GREEN}agent>{Colors.RESET} "
                if self.current_session_id:
                    session = self.sessions.get(self.current_session_id)
                    if session:
                        prompt = f"{Colors.BLUE}[{session.agent_role}]{Colors.GREEN}>{Colors.RESET} "
                
                # Komut al
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                    
                # Komutu işle
                self._process_interactive_command(user_input)
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Use 'exit' to quit{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.RESET}")
                
    def _process_interactive_command(self, command: str):
        """İnteraktif komutu işle"""
        parts = command.split()
        if not parts:
            return
            
        cmd = parts[0].lower()
        
        # Çıkış
        if cmd in ['exit', 'quit', 'q']:
            self.is_interactive = False
            print(f"{Colors.YELLOW}Exiting interactive shell...{Colors.RESET}")
            return
            
        # Yardım
        elif cmd in ['help', 'h', '?']:
            self._show_help()
            
        # Doğal dil modu
        elif cmd == 'nlp':
            self._start_nlp_mode()
            
        # Oturum oluştur
        elif cmd == 'create':
            if len(parts) < 2:
                print(f"{Colors.RED}Usage: create <agent_role>{Colors.RESET}")
                return
            role = parts[1].upper()
            try:
                from unibos_agent_system import AgentRole
                agent_role = AgentRole[role]
                session_id = self.create_session(agent_role.value)
                print(f"{Colors.GREEN}Created session: {session_id}{Colors.RESET}")
                self.current_session_id = session_id
            except KeyError:
                print(f"{Colors.RED}Unknown agent role: {role}{Colors.RESET}")
                self._show_available_agents()
            except Exception as e:
                print(f"{Colors.RED}Error creating session: {e}{Colors.RESET}")
                
        # Oturumları listele
        elif cmd in ['sessions', 'ls']:
            self._show_sessions()
            
        # Oturum seç
        elif cmd in ['use', 'select']:
            if len(parts) < 2:
                print(f"{Colors.RED}Usage: use <session_id>{Colors.RESET}")
                return
            session_id = parts[1]
            if session_id in self.sessions:
                self.current_session_id = session_id
                print(f"{Colors.GREEN}Switched to session: {session_id}{Colors.RESET}")
            else:
                print(f"{Colors.RED}Session not found: {session_id}{Colors.RESET}")
                
        # Analiz komutu
        elif cmd == 'analyze':
            if len(parts) < 2:
                print(f"{Colors.RED}Usage: analyze <module>{Colors.RESET}")
                return
            module = parts[1]
            self._send_current_command(CommandType.ANALYZE, module)
            
        # İyileştirme komutu
        elif cmd == 'enhance':
            if len(parts) < 2:
                print(f"{Colors.RED}Usage: enhance <module>{Colors.RESET}")
                return
            module = parts[1]
            self._send_current_command(CommandType.ENHANCE, module)
            
        # Yayın komutu (tüm ajanlara)
        elif cmd == 'broadcast':
            if len(parts) < 3:
                print(f"{Colors.RED}Usage: broadcast <command_type> <module>{Colors.RESET}")
                return
            cmd_type = parts[1].upper()
            module = parts[2]
            try:
                command_type = CommandType[cmd_type]
                cmd_ids = self.broadcast_command(command_type, module)
                print(f"{Colors.GREEN}Broadcast sent to {len(cmd_ids)} sessions{Colors.RESET}")
            except KeyError:
                print(f"{Colors.RED}Unknown command type: {cmd_type}{Colors.RESET}")
                
        # Geçmiş
        elif cmd == 'history':
            self._show_history()
            
        # Yanıtları kontrol et
        elif cmd == 'check':
            self._check_responses()
            
        # Temizle
        elif cmd in ['clear', 'cls']:
            os.system('clear' if os.name != 'nt' else 'cls')
            
        # Özellik tarama (versiyonlar arası)
        elif cmd == 'scan-feature':
            # Önce tırnak içindeki feature'ı kontrol et
            import re
            quoted_match = re.search(r'"([^"]+)"', command)
            if quoted_match:
                feature_name = quoted_match.group(1)
                # Komuttan tırnakları ve feature'ı çıkar
                remaining = command.replace(f'"{feature_name}"', '').strip()
                remaining_parts = remaining.split()
                module = remaining_parts[1] if len(remaining_parts) > 1 else "currencies_enhanced.py"
                version_range = remaining_parts[2] if len(remaining_parts) > 2 else "all"
            else:
                # Eski format
                if len(parts) < 2:
                    print(f"{Colors.RED}Usage: scan-feature <feature_name> [module] [version_range]{Colors.RESET}")
                    print(f"{Colors.DIM}Example: scan-feature kisisel_enflasyon currencies_enhanced.py v200-v242{Colors.RESET}")
                    return
                feature_name = parts[1]
                module = parts[2] if len(parts) > 2 else "currencies_enhanced.py"
                version_range = parts[3] if len(parts) > 3 else "all"
            
            self._scan_feature_across_versions(feature_name, module, version_range)
            
        # Çoklu ajan analizi
        elif cmd == 'multi-analyze':
            if len(parts) < 2:
                print(f"{Colors.RED}Usage: multi-analyze <module> [agents]{Colors.RESET}")
                print(f"{Colors.DIM}Example: multi-analyze currencies_enhanced.py CODE_ANALYST,UI_IMPROVER{Colors.RESET}")
                return
            module = parts[1]
            agents = parts[2].split(',') if len(parts) > 2 else ['CODE_ANALYST', 'REFACTOR_SPECIALIST', 'UI_IMPROVER']
            self._multi_agent_analysis(module, agents)
            
        # Akıllı komut analizi
        else:
            # Doğal dil komutlarını analiz et
            self._analyze_natural_command(command)
            
    def _send_current_command(self, command_type: CommandType, module: str):
        """Mevcut oturuma komut gönder"""
        if not self.current_session_id:
            print(f"{Colors.RED}No session selected. Use 'create' or 'use' first.{Colors.RESET}")
            return
            
        try:
            cmd_id = self.send_command(self.current_session_id, command_type, module)
            print(f"{Colors.GREEN}Command sent: {cmd_id}{Colors.RESET}")
            
            # Yanıt bekle
            print(f"{Colors.YELLOW}Waiting for response...{Colors.RESET}")
            response = self.get_response(self.current_session_id, timeout=30)
            
            if response:
                if response.success:
                    print(f"{Colors.GREEN}Response received in {response.execution_time:.2f}s{Colors.RESET}")
                    self._display_response(response)
                else:
                    print(f"{Colors.RED}Command failed: {response.error}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}No response received (timeout){Colors.RESET}")
                
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
            
    def _display_response(self, response: AgentResponse):
        """Yanıtı görüntüle"""
        print(f"\n{Colors.CYAN}{'─'*50}{Colors.RESET}")
        print(f"{Colors.BOLD}Agent: {response.agent_role}{Colors.RESET}")
        
        if isinstance(response.content, dict):
            # Context varsa
            if 'context' in response.content:
                context = response.content['context']
                print(f"\n{Colors.YELLOW}Files Analyzed:{Colors.RESET} {len(context.files_analyzed)}")
                print(f"{Colors.YELLOW}Improvement Areas:{Colors.RESET} {len(context.improvement_areas)}")
                
            # İyileştirmeler varsa
            if 'improvements' in response.content:
                improvements = response.content['improvements']
                print(f"\n{Colors.YELLOW}Improvements Found:{Colors.RESET}")
                for i, imp in enumerate(improvements[:5], 1):
                    print(f"{i}. {imp}")
                if len(improvements) > 5:
                    print(f"   ... and {len(improvements)-5} more")
                    
        else:
            print(response.content)
            
        print(f"{Colors.CYAN}{'─'*50}{Colors.RESET}\n")
        
    def _show_sessions(self):
        """Oturumları göster"""
        if not self.sessions:
            print(f"{Colors.YELLOW}No active sessions{Colors.RESET}")
            return
            
        print(f"\n{Colors.CYAN}Active Sessions:{Colors.RESET}")
        for session_id, session in self.sessions.items():
            marker = "→" if session_id == self.current_session_id else " "
            print(f"{marker} {Colors.GREEN}{session_id}{Colors.RESET} "
                  f"({session.agent_role}) - {session.state.value}")
                  
    def _show_help(self):
        """Yardım göster"""
        help_text = f"""
{Colors.CYAN}Available Commands:{Colors.RESET}

{Colors.YELLOW}Session Management:{Colors.RESET}
  create <role>     - Create new agent session
  use <session_id>  - Switch to session
  sessions/ls       - List active sessions
  
{Colors.YELLOW}Agent Commands:{Colors.RESET}
  analyze <module>          - Analyze module with current agent
  enhance <module>          - Generate enhancements
  broadcast <type> <module> - Send to all agents
  scan-feature <name> [range] - Scan feature across versions
  multi-analyze <module> [agents] - Multi-agent coordinated analysis
  
{Colors.YELLOW}Monitoring:{Colors.RESET}
  check            - Check for responses
  history          - Show command history
  
{Colors.YELLOW}Other:{Colors.RESET}
  nlp              - 🧠 Doğal dil moduna geç (Türkçe/İngilizce)
  help/h/?         - Show this help
  clear/cls        - Clear screen
  exit/quit/q      - Exit shell

{Colors.CYAN}Available Agent Roles:{Colors.RESET}
  CODE_ANALYST         - Kod analizi ve kalite değerlendirmesi
  REFACTOR_SPECIALIST  - Kod yeniden yapılandırma önerileri
  UI_IMPROVER          - Kullanıcı arayüzü iyileştirmeleri
  PERFORMANCE_OPTIMIZER - Performans optimizasyonu
  SECURITY_AUDITOR     - Güvenlik denetimi ve açık tespiti
  CLAUDE_ENHANCER      - Claude entegrasyonu geliştirmeleri

{Colors.CYAN}Örnek Kullanım:{Colors.RESET}
  agent> create CODE_ANALYST         # Yeni kod analiz ajanı oluştur
  agent> analyze main.py             # main.py modülünü analiz et
  agent> check                       # Analiz sonuçlarını kontrol et
  agent> enhance main.py             # İyileştirme önerileri al
  
{Colors.CYAN}Özellik Tarama:{Colors.RESET}
  agent> scan-feature kisisel_enflasyon currencies_enhanced.py  # Tüm versiyonlarda
  agent> scan-feature personal_inflation main.py v200-v242      # Belirli aralıkta
  
{Colors.CYAN}Çoklu Ajan Analizi:{Colors.RESET}
  agent> multi-analyze currencies_enhanced.py  # Varsayılan 3 ajanla
  agent> multi-analyze main.py CODE_ANALYST,SECURITY_AUDITOR,UI_IMPROVER
"""
        print(help_text)
        
    def _show_available_agents(self):
        """Mevcut ajanları göster"""
        print(f"\n{Colors.YELLOW}Available agents:{Colors.RESET}")
        from unibos_agent_system import AgentRole
        for role in AgentRole:
            if role in self.orchestrator.agents:
                capability = self.orchestrator.capabilities.get(role)
                if capability:
                    print(f"  - {role.name} ({role.value}) - {capability.description}")
                else:
                    print(f"  - {role.name} ({role.value})")
            
    def _show_history(self):
        """Komut geçmişini göster"""
        if not self.command_history:
            print(f"{Colors.YELLOW}No command history{Colors.RESET}")
            return
            
        print(f"\n{Colors.CYAN}Command History:{Colors.RESET}")
        for cmd in self.command_history[-10:]:
            status_color = Colors.GREEN if cmd.status == "completed" else Colors.YELLOW
            print(f"{cmd.timestamp.strftime('%H:%M:%S')} "
                  f"[{status_color}{cmd.status}{Colors.RESET}] "
                  f"{cmd.agent_role}: {cmd.command_type.value} {cmd.module}")
                  
    def _check_responses(self):
        """Bekleyen yanıtları kontrol et"""
        checked = 0
        for session_id, session in self.sessions.items():
            response = session.get_response(timeout=0.1)
            if response:
                print(f"\n{Colors.GREEN}Response from {session.agent_role}:{Colors.RESET}")
                self._display_response(response)
                checked += 1
                
        if checked == 0:
            print(f"{Colors.YELLOW}No pending responses{Colors.RESET}")
            
    def close_all_sessions(self):
        """Tüm oturumları kapat"""
        for session in self.sessions.values():
            session.stop()
        self.sessions.clear()
        logger.info("All agent sessions closed", category=LogCategory.CLAUDE)
    
    def _add_evolution_suggestions(self, evolution, module: str):
        """Evolution analizinden çıkan önerileri suggestion sistemine ekle"""
        try:
            # Mevcut claude_suggest sistemini kullan
            from claude_suggest import ClaudeSuggest, Priority
            suggest_system = ClaudeSuggest()
            
            if not evolution.improvements:
                return
                
            # Her iyileştirme için bir öneri oluştur
            for imp in evolution.improvements[:3]:  # İlk 3 öneri
                suggestion_title = f"[{imp['type']}] {evolution.feature_name}"
                suggestion_desc = imp['description']
                
                # Detaylı açıklama ekle
                if 'elements' in imp and imp['elements']:
                    suggestion_desc += f"\n\nÖrnekler:\n"
                    for elem in imp['elements'][:3]:
                        suggestion_desc += f"• {elem}\n"
                
                # Priority belirle
                priority_map = {
                    'high': Priority.HIGH,
                    'medium': Priority.MEDIUM,
                    'low': Priority.LOW,
                    'critical': Priority.CRITICAL
                }
                priority = priority_map.get(imp.get('priority', 'medium'), Priority.MEDIUM)
                
                # Claude suggest sistemine ekle
                try:
                    category_map = {
                        'UI_ENHANCEMENT': 'ui',
                        'NEW_FUNCTIONS': 'feature',
                        'DATA_STRUCTURES': 'refactor',
                        'PERFORMANCE': 'performance',
                        'SECURITY': 'security'
                    }
                    category = category_map.get(imp['type'], 'feature')
                    
                    # Tahmini süre belirle
                    estimated_hours = 2.0 if priority == Priority.HIGH else 1.0
                    
                    # Öneriyi ekle
                    suggest_system.add_suggestion(
                        title=suggestion_title,
                        description=suggestion_desc,
                        priority=priority,
                        category=category,
                        estimated_hours=estimated_hours
                    )
                    
                    print(f"{Colors.GREEN}✓ Suggestion added: {imp['type']}{Colors.RESET}")
                    
                except Exception as e:
                    print(f"{Colors.YELLOW}Could not add suggestion: {e}{Colors.RESET}")
                    
        except Exception as e:
            print(f"{Colors.RED}Error adding evolution suggestions: {e}{Colors.RESET}")
    
    def _scan_feature_across_versions(self, feature_name: str, module: str, version_range: str):
        """Belirli bir özelliği versiyonlar arası tara ve analiz et"""
        print(f"\n{Colors.CYAN}🔍 Feature Scanner: {feature_name}{Colors.RESET}")
        print(f"{Colors.YELLOW}Module: {module}{Colors.RESET}")
        print(f"{Colors.YELLOW}Version Range: {version_range}{Colors.RESET}")
        print(f"{Colors.CYAN}{'─'*60}{Colors.RESET}\n")
        
        # Çalışma dizinini her zaman kontrol et
        current_dir = os.getcwd()
        if not current_dir.endswith('unibos'):
            unibos_path = '/Users/berkhatirli/Desktop/unibos'
            if os.path.exists(unibos_path):
                os.chdir(unibos_path)
        
        # Özel durumlar için modül eşlemesi
        feature_module_mapping = {
            'kişisel enflasyon': 'projects/kisiselenflasyon/inflation.py',
            'kisisel_enflasyon': 'projects/kisiselenflasyon/inflation.py',
            'personal inflation': 'projects/kisiselenflasyon/inflation.py',
            'kişisel': 'projects/kisiselenflasyon/inflation.py'
        }
        
        # Feature'a göre modülü belirle
        for key, mapped_module in feature_module_mapping.items():
            if key in feature_name.lower():
                module = mapped_module
                print(f"{Colors.GREEN}Special module detected: {module}{Colors.RESET}")
                break
        
        # Versiyonları belirle
        module_name = module.replace('.py', '')
        
        # projects/ altındaki modüller için özel pattern
        if module.startswith('projects/'):
            # Sadece dosya adını al (inflation.py)
            filename = os.path.basename(module)
            # İki farklı pattern dene - eski ve yeni arşiv yapısı
            archive_patterns = [
                f"archive/versions/unibos_v*/projects/kisiselenflasyon/{filename}",
                f"archive/versions/unibos_v*/unibosoft*/projects/kisiselenflasyon/{filename}",
                f"archive/versions/unibos_v*/unibosoft*/unibosoft*/projects/kisiselenflasyon/{filename}"
            ]
        else:
            # Normal src/ altındaki modüller
            if version_range == "all" or version_range == "currencies_enhanced.py":
                # Tüm arşivleri tara (version_range yerine module geçmişse de)
                archive_pattern = f"archive/versions/unibos_v*/src/{module}"
            else:
                # Belirli aralık (örn: v200-v242)
                try:
                    if '-' in version_range:
                        start_v = int(version_range.split('-')[0].replace('v', ''))
                        end_v = int(version_range.split('-')[1].replace('v', ''))
                        # Versiyon aralığına göre filtrele
                        archive_pattern = f"archive/versions/unibos_v*/src/{module}"
                    else:
                        # Tek versiyon
                        archive_pattern = f"archive/versions/unibos_{version_range}*/src/{module}"
                except:
                    print(f"{Colors.RED}Invalid version range format. Use: v200-v242 or 'all'{Colors.RESET}")
                    return
            # Tek pattern için liste haline getir
            archive_patterns = [archive_pattern]
        
        # Dosyaları tara
        import glob
        all_files = []
        
        # Tüm pattern'leri dene
        for pattern in archive_patterns:
            files = glob.glob(pattern, recursive=True)
            all_files.extend(files)
        all_files = sorted(list(set(all_files)))  # Tekrarları kaldır
        
        # Versiyon aralığına göre filtrele
        version_files = []
        if version_range != "all" and '-' in version_range:
            try:
                start_v = int(version_range.split('-')[0].replace('v', ''))
                end_v = int(version_range.split('-')[1].replace('v', ''))
                
                for f in all_files:
                    # unibos_v217_20250719_0130 formatından versiyon numarasını çıkar
                    dirname = f.split('/')[-3]  # unibos_v217_20250719_0130
                    v_num = int(dirname.split('_')[1].replace('v', ''))
                    
                    if start_v <= v_num <= end_v:
                        version_files.append(f)
            except:
                version_files = all_files
        else:
            version_files = all_files
        
        print(f"{Colors.GREEN}Found {len(version_files)} version files to scan{Colors.RESET}\n")
        
        # CODE_ANALYST ajanı oluştur (eğer orchestrator varsa)
        if self.orchestrator:
            from unibos_agent_system import AgentRole
            code_analyst_role = AgentRole.CODE_ANALYST.value
            if code_analyst_role not in [s.agent_role for s in self.sessions.values()]:
                session_id = self.create_session(code_analyst_role)
            else:
                session_id = [sid for sid, s in self.sessions.items() if s.agent_role == code_analyst_role][0]
        
        # Feature implementasyonlarını topla
        feature_implementations = []
        
        for vfile in version_files[-10:]:  # Son 10 versiyon
            # Handle different archive structures
            path_parts = vfile.split('/')
            version = None
            v_num = None
            
            # Find the version folder (starts with unibos_v)
            for part in path_parts:
                if part.startswith('unibos_v') and len(part.split('_')) >= 2:
                    version = part
                    v_num = part.split('_')[1]  # v217
                    break
                    
            if not version:
                continue
            print(f"Scanning {Colors.BLUE}{v_num}{Colors.RESET}...", end='', flush=True)
            
            try:
                with open(vfile, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Feature'ı ara - daha akıllı arama
                search_terms = [feature_name.lower()]
                
                # Alternatif arama terimleri ekle
                if 'kişisel' in feature_name.lower() or 'kisisel' in feature_name.lower():
                    search_terms.extend(['personal', 'kisisel', 'kişisel', 'inflation', 'enflasyon'])
                elif 'inflation' in feature_name.lower():
                    search_terms.extend(['enflasyon', 'kişisel', 'kisisel', 'personal', 'inflation'])
                elif 'enflasyon' in feature_name.lower():
                    search_terms.extend(['inflation', 'kişisel', 'kisisel', 'personal', 'enflasyon'])
                
                found = False
                feature_lines = []
                
                for term in search_terms:
                    if term in content.lower():
                        found = True
                        # Implementasyon detaylarını çıkar
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if term in line.lower():
                                # Context için etrafındaki satırları da al
                                start = max(0, i-10)
                                end = min(len(lines), i+15)
                                context_lines = lines[start:end]
                                feature_lines.extend(context_lines)
                        break
                
                if found:
                    feature_implementations.append({
                        'version': version,
                        'file': vfile,
                        'lines': list(set(feature_lines))[:50],  # Unique lines, max 50
                        'search_terms': search_terms
                    })
                    print(f" {Colors.GREEN}✓ Found{Colors.RESET}")
                else:
                    print(f" {Colors.GRAY}✗ Not found{Colors.RESET}")
                    
            except Exception as e:
                print(f" {Colors.RED}✗ Error: {e}{Colors.RESET}")
        
        # Analiz sonuçlarını göster
        if feature_implementations:
            print(f"\n{Colors.CYAN}Feature Evolution Analysis:{Colors.RESET}")
            print(f"Feature '{feature_name}' found in {len(feature_implementations)} versions\n")
            
            # Versiyon listesi
            print(f"{Colors.YELLOW}Found in versions:{Colors.RESET}")
            for impl in feature_implementations[-5:]:  # Son 5 versiyon
                print(f"  • {impl['version']}")
            
            # En son implementasyonu analiz et
            latest = feature_implementations[-1]
            print(f"\n{Colors.YELLOW}Latest Implementation ({latest['version']}):{Colors.RESET}")
            print(f"File: {latest['file']}")
            print(f"Search terms used: {', '.join(latest.get('search_terms', [feature_name]))}")
            
            # Kod snippet'i göster
            print(f"\n{Colors.CYAN}Code Context:{Colors.RESET}")
            unique_lines = []
            for line in latest['lines']:
                line = line.strip()
                if line and line not in unique_lines and not line.startswith('#'):
                    unique_lines.append(line)
            
            for line in unique_lines[:15]:  # Max 15 satır
                if any(term in line.lower() for term in latest.get('search_terms', [feature_name.lower()])):
                    print(f"  {Colors.GREEN}→{Colors.RESET} {line}")
                else:
                    print(f"    {Colors.DIM}{line}{Colors.RESET}")
            
            # Agent ile analiz öner
            print(f"\n{Colors.GREEN}Recommended Next Steps:{Colors.RESET}")
            print(f"1. Analyze current implementation:")
            print(f"   analyze {module}")
            print(f"\n2. Multi-agent deep analysis:")
            print(f"   multi-analyze {module} CODE_ANALYST,UI_IMPROVER,REFACTOR_SPECIALIST")
            print(f"\n3. Generate enhancement suggestions:")
            print(f"   enhance {module}")
            
            # Feature evolution analysis
            try:
                from feature_evolution_analyzer import FeatureEvolutionAnalyzer
                analyzer = FeatureEvolutionAnalyzer()
                
                # Scan sonuçlarını hazırla
                scan_results = {
                    'version_files': version_files,
                    'feature_implementations': feature_implementations,
                    'feature_name': feature_name
                }
                
                # Evrim analizi yap
                evolution = analyzer.analyze_feature_evolution(feature_name, scan_results)
                
                # Detaylı rapor göster
                print(analyzer.create_detailed_report(evolution))
                
                # Entegrasyon kodu öner
                if evolution.best_implementation:
                    integration_code = analyzer.generate_integration_code(evolution, module)
                    if integration_code:
                        print(f"\n{Colors.GREEN}Integration Suggestions:{Colors.RESET}")
                        print(integration_code)
                
                # Suggestion sistemine önerileri ekle
                self._add_evolution_suggestions(evolution, module)
                
            except Exception as e:
                print(f"{Colors.RED}Evolution analysis error: {e}{Colors.RESET}")
            
            # Orchestrator'a otomatik analiz yaptır
            if hasattr(self, 'orchestrator') and self.orchestrator:
                print(f"\n{Colors.YELLOW}Running automated analysis...{Colors.RESET}")
                try:
                    # CODE_ANALYST ile hızlı analiz
                    from unibos_agent_system import AgentRole
                    agent = self.orchestrator.agents.get(AgentRole.CODE_ANALYST)
                    if agent:
                        # Güncel dosyayı analiz et
                        current_file = str(Path.cwd() / module)
                        if Path(current_file).exists():
                            context = agent.analyze_codebase(module)
                            
                            print(f"\n{Colors.CYAN}Quick Analysis Results:{Colors.RESET}")
                            print(f"Files analyzed: {len(context.files_analyzed)}")
                            print(f"Improvement areas: {len(context.improvement_areas)}")
                            
                            if context.improvement_areas:
                                print(f"\n{Colors.YELLOW}Key findings:{Colors.RESET}")
                                for area in context.improvement_areas[:5]:
                                    print(f"  • {area}")
                except Exception as e:
                    logger.error(f"Automated analysis failed: {e}", category=LogCategory.CLAUDE)
            
        else:
            print(f"\n{Colors.YELLOW}Feature '{feature_name}' not found in scanned versions{Colors.RESET}")
            
            # Güncel projede kontrol et
            print(f"\n{Colors.CYAN}Checking current project...{Colors.RESET}")
            current_path = Path.cwd() / module
            if current_path.exists():
                try:
                    with open(current_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if feature_name.lower() in content.lower() or any(term in content.lower() for term in ['inflation', 'enflasyon', 'kişisel', 'personal']):
                            print(f"{Colors.GREEN}✓ Feature found in current version!{Colors.RESET}")
                            print(f"\nFile: {current_path}")
                            
                            # Satırları göster
                            lines = content.split('\n')
                            found_lines = []
                            for i, line in enumerate(lines):
                                if feature_name.lower() in line.lower() or any(term in line.lower() for term in ['inflation', 'enflasyon', 'kişisel']):
                                    found_lines.append((i+1, line.strip()))
                            
                            if found_lines:
                                print(f"\n{Colors.YELLOW}Found at lines:{Colors.RESET}")
                                for line_no, line in found_lines[:10]:
                                    print(f"  Line {line_no}: {line}")
                            
                            print(f"\n{Colors.GREEN}Recommended actions:{Colors.RESET}")
                            print(f"1. Analyze the current module:")
                            print(f"   analyze {module}")
                            print(f"2. Run multi-agent analysis:")
                            print(f"   multi-analyze {module}")
                        else:
                            print(f"{Colors.RED}✗ Not found in current version either{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.RED}Error reading current file: {e}{Colors.RESET}")
            else:
                print(f"{Colors.RED}Current module not found: {module}{Colors.RESET}")
            
            print(f"\n{Colors.CYAN}Alternative suggestions:{Colors.RESET}")
            print(f"1. Try different search terms")
            print(f"2. Search in all Python files:")
            print(f"   grep -r '{feature_name}' projects/")
            print(f"3. List all inflation-related files:")
            print(f"   find . -name '*inflation*' -o -name '*enflasyon*'")
    
    def _multi_agent_analysis(self, module: str, agent_roles: List[str]):
        """Birden fazla ajanla koordineli analiz yap"""
        print(f"\n{Colors.CYAN}🤝 Multi-Agent Analysis{Colors.RESET}")
        print(f"{Colors.YELLOW}Module: {module}{Colors.RESET}")
        print(f"{Colors.YELLOW}Agents: {', '.join(agent_roles)}{Colors.RESET}")
        print(f"{Colors.CYAN}{'─'*60}{Colors.RESET}\n")
        
        # Ajanları oluştur/kontrol et
        from unibos_agent_system import AgentRole
        sessions = {}
        for role_name in agent_roles:
            try:
                # Agent role'ü validate et
                try:
                    agent_role = AgentRole[role_name]
                    role = agent_role.value
                except KeyError:
                    print(f"{Colors.RED}✗ Unknown agent role: {role_name}{Colors.RESET}")
                    continue
                
                # Mevcut oturum var mı kontrol et
                existing = [sid for sid, s in self.sessions.items() if s.agent_role == role]
                if existing:
                    sessions[role] = existing[0]
                    print(f"{Colors.GREEN}✓ Using existing {role} session{Colors.RESET}")
                else:
                    session_id = self.create_session(role)
                    sessions[role] = session_id
                    print(f"{Colors.GREEN}✓ Created {role} session{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}✗ Failed to create {role_name}: {e}{Colors.RESET}")
        
        if not sessions:
            print(f"{Colors.RED}No agents available for analysis{Colors.RESET}")
            return
        
        # Her ajana analiz komutu gönder
        print(f"\n{Colors.YELLOW}Sending analysis commands...{Colors.RESET}")
        command_ids = {}
        for role, session_id in sessions.items():
            cmd_id = self.send_command(session_id, CommandType.ANALYZE, module)
            command_ids[role] = cmd_id
            print(f"  → {role}: Command {cmd_id}")
        
        # Yanıtları topla
        print(f"\n{Colors.YELLOW}Collecting responses...{Colors.RESET}")
        responses = {}
        for role, session_id in sessions.items():
            print(f"  Waiting for {role}...", end='', flush=True)
            response = self.get_response(session_id, timeout=30)
            if response and response.success:
                responses[role] = response
                print(f" {Colors.GREEN}✓{Colors.RESET}")
            else:
                print(f" {Colors.RED}✗{Colors.RESET}")
        
        # Sonuçları birleştir ve göster
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Consolidated Analysis Results{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
        
        for role, response in responses.items():
            print(f"{Colors.YELLOW}━━━ {role} Analysis ━━━{Colors.RESET}")
            self._display_response(response)
        
        # Ortak öneriler
        if len(responses) > 1:
            print(f"\n{Colors.GREEN}Cross-Agent Insights:{Colors.RESET}")
            print(f"• {len(responses)} agents completed analysis")
            print(f"• Consider implementing suggestions that appear across multiple agents")
            print(f"• Use 'enhance {module}' with specific agent for detailed implementation")
    
    def _analyze_natural_command(self, command: str):
        """Doğal dil komutlarını analiz et ve uygun aksiyonu al"""
        command_lower = command.lower()
        
        # Özellik/fonksiyon anahtar kelimeleri
        feature_keywords = ['kişisel', 'enflasyon', 'döviz', 'menu', 'navigasyon', 'güvenlik', 
                          'performans', 'ui', 'arayüz', 'personal', 'inflation', 'currency']
        
        # Modül tahminleri
        module_mappings = {
            'kişisel enflasyon': 'currencies_enhanced.py',
            'personal inflation': 'currencies_enhanced.py',
            'kisisel_enflasyon': 'currencies_enhanced.py',
            'döviz': 'currencies_enhanced.py',
            'currency': 'currencies_enhanced.py',
            'menu': 'main.py',
            'navigasyon': 'main.py',
            'navigation': 'main.py',
            'git': 'git_manager.py',
            'screenshot': 'screenshot_manager.py',
            'claude': 'claude_cli.py',
            'agent': 'agent_session_manager.py'
        }
        
        # Aksiyon tahminleri
        action_keywords = {
            'tara': 'scan-feature',
            'scan': 'scan-feature',
            'ara': 'scan-feature',
            'search': 'scan-feature',
            'analiz': 'analyze',
            'analyze': 'analyze',
            'incele': 'analyze',
            'inspect': 'analyze',
            'geliştir': 'enhance',
            'enhance': 'enhance',
            'iyileştir': 'enhance',
            'improve': 'enhance'
        }
        
        # Modül tespit et
        detected_module = None
        detected_feature = None
        detected_action = None
        
        # Özellik tespiti
        for keyword in feature_keywords:
            if keyword in command_lower:
                detected_feature = keyword
                # İlgili modülü bul
                for key, module in module_mappings.items():
                    if keyword in key.lower():
                        detected_module = module
                        break
                break
        
        # Modül tespiti (eğer özellikten bulunamadıysa)
        if not detected_module:
            for key, module in module_mappings.items():
                if key in command_lower:
                    detected_module = module
                    detected_feature = key
                    break
        
        # Aksiyon tespiti
        for keyword, action in action_keywords.items():
            if keyword in command_lower:
                detected_action = action
                break
        
        # Varsayılan değerler
        if not detected_module:
            detected_module = 'currencies_enhanced.py'  # En çok kullanılan modül
        if not detected_action:
            detected_action = 'analyze'  # Varsayılan aksiyon
        
        # Önerilen komutu göster
        print(f"\n{Colors.YELLOW}Komut analizi:{Colors.RESET}")
        print(f"  Tespit edilen özellik: {detected_feature or 'Genel'}")
        print(f"  Tahmin edilen modül: {detected_module}")
        print(f"  Önerilen aksiyon: {detected_action}")
        
        # Kullanıcıya öneriler sun
        if detected_action == 'scan-feature' and detected_feature:
            suggested_cmd = f"scan-feature {detected_feature} {detected_module}"
            print(f"\n{Colors.GREEN}Önerilen komut:{Colors.RESET}")
            print(f"  {suggested_cmd}")
            print(f"\n{Colors.CYAN}Bu komutu çalıştırmak ister misiniz? (y/n):{Colors.RESET} ", end='')
            
            response = input().strip().lower()
            if response == 'y':
                self._process_interactive_command(suggested_cmd)
            else:
                print(f"{Colors.YELLOW}Alternatif komutlar:{Colors.RESET}")
                print(f"  • analyze {detected_module}")
                print(f"  • multi-analyze {detected_module}")
                print(f"  • enhance {detected_module}")
        
        elif detected_action in ['analyze', 'enhance']:
            # Hangi ajanların kullanılacağını belirle
            suggested_agents = []
            
            if 'güvenlik' in command_lower or 'security' in command_lower:
                suggested_agents.append('SECURITY_AUDITOR')
            if 'performans' in command_lower or 'performance' in command_lower:
                suggested_agents.append('PERFORMANCE_OPTIMIZER')
            if 'ui' in command_lower or 'arayüz' in command_lower:
                suggested_agents.append('UI_IMPROVER')
            if 'refactor' in command_lower or 'yeniden' in command_lower:
                suggested_agents.append('REFACTOR_SPECIALIST')
            
            # Varsayılan ajanlar
            if not suggested_agents:
                suggested_agents = ['CODE_ANALYST', 'REFACTOR_SPECIALIST']
            
            print(f"\n{Colors.GREEN}Önerilen komutlar:{Colors.RESET}")
            print(f"  1. {detected_action} {detected_module}")
            print(f"  2. multi-analyze {detected_module} {','.join(suggested_agents)}")
            print(f"\n{Colors.CYAN}Hangisini çalıştırmak istersiniz? (1/2):{Colors.RESET} ", end='')
            
            choice = input().strip()
            if choice == '1':
                # Tek ajan analizi için önce ajan oluştur
                if not self.current_session_id:
                    self._process_interactive_command(f"create {suggested_agents[0]}")
                self._process_interactive_command(f"{detected_action} {detected_module}")
            elif choice == '2':
                self._process_interactive_command(f"multi-analyze {detected_module} {','.join(suggested_agents)}")
        
        else:
            print(f"\n{Colors.RED}Komut anlaşılamadı: {command}{Colors.RESET}")
            print(f"{Colors.YELLOW}Örnekler:{Colors.RESET}")
            print(f"  • kişisel enflasyon özelliğini tara")
            print(f"  • döviz modülünü analiz et")
            print(f"  • güvenlik açısından git_manager'ı incele")
            print(f"  • performans optimizasyonu için main.py'i geliştir")
    
    def _start_nlp_mode(self):
        """Doğal dil modunu başlat"""
        try:
            from nlp_agent_orchestrator import NLPAgentOrchestrator
            
            # NLP orkestratörü oluştur
            nlp_orchestrator = NLPAgentOrchestrator(self)
            
            # Geçici olarak interaktif modu durdur
            self.is_interactive = False
            
            # NLP sohbet modunu başlat
            nlp_orchestrator.start_conversational_mode()
            
            # İnteraktif moda geri dön
            self.is_interactive = True
            
        except ImportError:
            print(f"{Colors.RED}NLP Agent Orchestrator not available{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error starting NLP mode: {e}{Colors.RESET}")
            self.is_interactive = True

# Export
__all__ = ['AgentSessionManager', 'AgentCommand', 'AgentResponse', 'CommandType', 'SessionState']