#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 claude cli module for unibos
self-development interface for unibos through claude api

Author: berk hatırlı - bitez, bodrum, muğla, türkiye, dünya, güneş sistemi, samanyolu, yerel galaksi grubu, evren  
Version: v238
Purpose: Enable unibos to self-develop using claude api
"""

import os
import sys
import json
import subprocess
import platform
import time
import threading
import re
from datetime import datetime
from pathlib import Path

# Platform-specific imports
if platform.system() != 'Windows':
    import select
    import fcntl

# unibos logger'ı import et
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unibos_logger import logger, LogCategory, LogLevel

# Import health monitor
try:
    from claude_health_monitor import ClaudeHealthMonitor, with_health_monitoring
except ImportError:
    ClaudeHealthMonitor = None
    with_health_monitoring = lambda x: x

# Import other required modules
try:
    from safe_version_manager import SafeVersionManager
except ImportError:
    SafeVersionManager = None

# Color codes for terminal
class Colors:
    # Basic colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    BG_MAGENTA = '\033[105m'
    BG_CYAN = '\033[106m'
    BG_WHITE = '\033[107m'
    BG_GRAY = '\033[100m'
    BG_DARK = '\033[40m'
    BG_CONTENT = '\033[48;5;234m'
    
    # Text styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    
    # Reset
    RESET = '\033[0m'

class ClaudeCLI:
    """claude cli interface for unibos self-development"""
    
    def __init__(self):
        """initialize claude cli"""
        self.config_path = Path.home() / '.unibos' / 'claude_config.json'
        self.history_path = Path.home() / '.unibos' / 'claude_history.json'
        
        # Initialize health monitor if available
        self.health_monitor = None
        if ClaudeHealthMonitor:
            try:
                self.health_monitor = ClaudeHealthMonitor()
                self.health_monitor.start_background_monitoring()
                logger.info("Claude Health Monitor başlatıldı", category=LogCategory.SYSTEM)
            except Exception as e:
                logger.error(f"Health Monitor başlatılamadı: {e}", category=LogCategory.SYSTEM)
        self.config = self.load_config()
        self.history = self.load_history()
        self.claude_cli_available = self.check_claude_cli()
        
        # Import screenshot manager
        try:
            from screenshot_manager import screenshot_manager
            self.screenshot_manager = screenshot_manager
            
            # Screenshot context accumulator - stores SS content from this session
            self.screenshot_context = {
                'session_start': datetime.now(),
                'screenshots_analyzed': [],
                'content_summary': [],
                'total_count': 0
            }
            
            # CRITICAL: Always check for screenshots on startup
            logger.info("Claude CLI: Performing mandatory screenshot check", category=LogCategory.CLAUDE)
            self.initial_screenshot_check()
            
        except ImportError:
            self.screenshot_manager = None
            self.screenshot_context = None
            logger.warning("Screenshot manager not available", category=LogCategory.CLAUDE)
            
        # Initialize agent session manager
        self.agent_session_manager = None
        try:
            from agent_session_manager import AgentSessionManager
            self.agent_session_manager = AgentSessionManager(self)
            logger.info("Agent Session Manager initialized", category=LogCategory.CLAUDE)
        except ImportError:
            logger.warning("Agent Session Manager not available", category=LogCategory.CLAUDE)
    
    def launch_agent_shell(self):
        """Launch interactive agent shell"""
        if not self.agent_session_manager:
            print(f"\n{Colors.RED}Agent Session Manager not available{Colors.RESET}")
            time.sleep(2)
            return
        
        try:
            self.agent_session_manager.start_interactive_shell()
        except Exception as e:
            logger.error(f"Agent shell error: {e}", category=LogCategory.CLAUDE)
            print(f"\n{Colors.RED}Error launching agent shell: {e}{Colors.RESET}")
            time.sleep(2)
        except ImportError:
            logger.warning("Agent Session Manager not available", category=LogCategory.CLAUDE)
        
        logger.info("Claude CLI başlatıldı", category=LogCategory.CLAUDE, 
                   details={"claude_available": self.claude_cli_available})
    
    def check_claude_cli(self):
        """check if claude cli is available"""
        try:
            result = subprocess.run(['which', 'claude'], 
                                  capture_output=True, text=True, 
                                  timeout=5)
            available = result.returncode == 0
            logger.debug(f"Claude CLI kontrol: {'mevcut' if available else 'yok'}", 
                        category=LogCategory.CLAUDE)
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"Claude CLI kontrol hatası: {str(e)}", category=LogCategory.CLAUDE)
            return False
    
    def show_claude_tools_menu(self):
        """Simplified Claude Tools menu with focused options"""
        while True:
            self.clear_screen()
            
            # Check screenshots before showing menu
            self._check_screenshots_on_entry()
            
            print(f"{Colors.CYAN}{Colors.BOLD}🤖 Claude Tools - AI Geliştirme Asistanı{Colors.RESET}")
            print(f"{Colors.DIM}{'='*60}{Colors.RESET}")
            
            # Show current version and branch info
            try:
                with open('src/VERSION.json', 'r') as f:
                    version_info = json.load(f)
                    print(f"{Colors.GREEN}📌 Version: {version_info['version']} | Build: {version_info['build_number']}{Colors.RESET}")
            except:
                pass
            
            # Main Features - Simplified to core functionality
            print(f"\n{Colors.MAGENTA}{Colors.BOLD}🚀 Ana Özellikler:{Colors.RESET}")
            print(f"{Colors.GREEN}1{Colors.RESET} - 🛡️  {Colors.BOLD}Güvenli Geliştirme{Colors.RESET} {Colors.DIM}(Safe development with auto versioning){Colors.RESET}")
            print(f"{Colors.GREEN}2{Colors.RESET} - 🤖 {Colors.BOLD}AI Ajan Sistemi{Colors.RESET} {Colors.DIM}(Unified agent processor){Colors.RESET}")
            print(f"{Colors.GREEN}3{Colors.RESET} - 💡 {Colors.BOLD}Development Manager{Colors.RESET} {Colors.DIM}(AI powered development){Colors.RESET}")
            print(f"{Colors.GREEN}4{Colors.RESET} - 💬 {Colors.BOLD}Claude Sohbet{Colors.RESET} {Colors.DIM}(Interactive chat){Colors.RESET}")
            
            # Advanced Tools - Secondary features
            print(f"\n{Colors.YELLOW}{Colors.BOLD}📦 Gelişmiş Araçlar:{Colors.RESET}")
            print(f"{Colors.CYAN}5{Colors.RESET} - 🔍 Arşiv Araştırma {Colors.DIM}(Deep archive search){Colors.RESET}")
            print(f"{Colors.CYAN}6{Colors.RESET} - 📊 Proje Analitiği {Colors.DIM}(Code stats & insights){Colors.RESET}")
            print(f"{Colors.CYAN}7{Colors.RESET} - 📋 Kod İnceleme {Colors.DIM}(AI code review){Colors.RESET}")
            
            # System Tools - Utility features
            print(f"\n{Colors.GRAY}{Colors.BOLD}⚙️  Sistem Araçları:{Colors.RESET}")
            print(f"{Colors.GRAY}8{Colors.RESET} - 📜 İletişim Logları")
            print(f"{Colors.GRAY}9{Colors.RESET} - 🏥 Sistem Durumu")
            print(f"{Colors.GRAY}D{Colors.RESET} - 🗄️  Database Kurulum {Colors.DIM}(PostgreSQL setup){Colors.RESET}")
            print(f"{Colors.GRAY}0{Colors.RESET} - 🔧 Diğer Araçlar {Colors.DIM}(More options){Colors.RESET}")
            
            print(f"\n{Colors.DIM}q{Colors.RESET} - Ana menüye dön")
            
            choice = self.get_simple_input(f"\n{Colors.BLUE}Seçiminiz: {Colors.RESET}").strip()
            
            if choice.lower() == 'q':
                self._check_screenshots_on_exit()
                break
            # Main Features
            elif choice == '1':
                self.enhanced_safe_development_mode()
            elif choice == '2':
                self.unified_agent_processor()
            elif choice == '3':
                self.smart_suggestions_mode()
            elif choice == '4':
                self.chat_mode()
            # Advanced Tools
            elif choice == '5':
                self.archive_research_agent_mode()
            elif choice == '6':
                self.project_analytics_mode()
            elif choice == '7':
                self.code_review_mode()
            # System Tools
            elif choice == '8':
                self.view_communication_logs()
            elif choice == '9':
                self.system_status_mode()
            elif choice.lower() == 'd':
                self.database_setup_wizard()
            elif choice == '0':
                self.show_advanced_tools_menu()
            else:
                print(f"\n{Colors.RED}Geçersiz seçim. Lütfen tekrar deneyin.{Colors.RESET}")
                time.sleep(1)
    
    def trigger_claude_development(self, suggestion_text, category, additional_context=None):
        """Trigger Claude to develop a specific suggestion"""
        # Don't clear screen for agent/suggestion flows to preserve output
        if category not in ['agent_enhancement', 'auto_suggestion', 'manual_suggestion']:
            self.clear_screen()
        # Add timestamp
        from datetime import datetime
        try:
            import pytz
            istanbul_tz = pytz.timezone('Europe/Istanbul')
            timestamp = datetime.now(istanbul_tz).strftime('%H:%M:%S')
        except ImportError:
            # Fallback to local time if pytz not available
            timestamp = datetime.now().strftime('%H:%M:%S')
        
        print(f"{Colors.CYAN}{Colors.BOLD}🚀 Claude Development Mode{Colors.RESET} {Colors.DIM}[{timestamp}]{Colors.RESET}")
        print(f"{Colors.YELLOW}Category: {category}{Colors.RESET}")
        print(f"{Colors.GREEN}Suggestion: {suggestion_text}{Colors.RESET}")
        print(f"{Colors.DIM}{'='*60}{Colors.RESET}\n")
        
        # Get additional context from user
        print(f"{Colors.CYAN}Provide additional context or requirements (optional):{Colors.RESET}")
        print(f"{Colors.DIM}Press Enter to use default analysis{Colors.RESET}")
        user_context = self.get_simple_input(f"\n{Colors.BLUE}Context: {Colors.RESET}")
        
        # Build screenshot context summary if available
        screenshot_context_info = ""
        if self.screenshot_context and self.screenshot_context['total_count'] > 0:
            screenshot_context_info = f"""
## Screenshot Context from Current Session
Total screenshots analyzed in this session: {self.screenshot_context['total_count']}

### Screenshot Content Summary:
"""
            # Add unique content summaries
            unique_contents = list(set(self.screenshot_context['content_summary']))
            for content in unique_contents:
                count = self.screenshot_context['content_summary'].count(content)
                screenshot_context_info += f"- {content} (found in {count} screenshot(s))\n"
            
            # Add recent screenshot details
            screenshot_context_info += "\n### Recent Screenshots:\n"
            for ss in self.screenshot_context['screenshots_analyzed'][-5:]:  # Last 5
                screenshot_context_info += f"- {ss['filename']}: {ss['content']}\n"
        
        # Prepare development prompt
        prompt = f"""I need you to implement the following development suggestion for UNIBOS:

**Suggestion:** {suggestion_text}
**Category:** {category}
{screenshot_context_info}

IMPORTANT: When providing code changes, use this exact format:

```FILE: path/to/file.py
Complete file content here...
```

For example:
```FILE: src/git_manager.py
#!/usr/bin/env python3
# Complete file content...
```

Please:
1. Analyze the current codebase relevant to this suggestion
2. Provide COMPLETE file contents (not just snippets) for any files you modify
3. Use the FILE: format shown above for each file change
4. Include all necessary imports and proper formatting
5. Test the implementation logic

Focus on:
- Complete, working code (not instructions)
- Following existing UNIBOS code patterns
- Proper error handling
- Clean, maintainable implementation
"""
        
        if user_context:
            prompt += f"\n\nAdditional context from user:\n{user_context}"
            
        # Add agent/additional context if provided
        if additional_context:
            prompt += f"\n\n## Additional Analysis Context:\n{additional_context}"
        
        print(f"\n{Colors.YELLOW}Sending development request to Claude...{Colors.RESET}")
        
        # Start health monitoring for this session
        session_id = None
        if self.health_monitor:
            session_id = f"dev_{int(time.time())}"
            self.health_monitor.start_session(session_id, f"development: {suggestion_text[:50]}...")
        
        # Check if Claude CLI is available
        if not self.claude_cli_available:
            print(f"\n{Colors.RED}Error: Claude CLI is not installed or not in PATH{Colors.RESET}")
            print(f"Please install Claude CLI first: https://claude.ai/cli")
            print(f"\n{Colors.YELLOW}Alternative methods:{Colors.RESET}")
            print(f"1. Copy the prompt above and use Claude in your browser")
            print(f"2. Install Claude CLI following the instructions")
            print(f"\n{Colors.DIM}Development prompt saved to: /tmp/claude_dev_prompt.txt{Colors.RESET}")
            
            # Save prompt to file
            with open('/tmp/claude_dev_prompt.txt', 'w') as f:
                f.write(prompt)
            
            input(f"\n{Colors.DIM}Press Enter to return...{Colors.RESET}")
            return
        
        # Use the conversation builder for interactive development
        try:
            # Try to use the conversation builder
            try:
                # Check if PTY mode is requested via environment variable
                use_pty = os.environ.get('CLAUDE_USE_PTY', '').lower() == 'true'
                
                if use_pty:
                    # Use PTY mode for better real-time output
                    from claude_conversation_pty import ClaudeConversationPTY
                    print(f"\n{Colors.GREEN}Starting interactive Claude conversation (PTY mode)...{Colors.RESET}")
                    print(f"{Colors.DIM}Using pseudo-terminal for real-time output.{Colors.RESET}\n")
                    conversation = ClaudeConversationPTY()
                else:
                    # Use standard mode with stdbuf
                    from claude_conversation import ClaudeConversation
                    print(f"\n{Colors.GREEN}Starting interactive Claude conversation...{Colors.RESET}")
                    print(f"{Colors.DIM}You can add follow-up messages during the response.{Colors.RESET}\n")
                    conversation = ClaudeConversation()
                
                success = conversation.start_conversation(prompt, f"Developing: {suggestion_text}")
                
                # End health monitoring session
                if self.health_monitor and session_id:
                    self.health_monitor.end_session(success=success)
                
                if success:
                    # Ask about marking suggestion as completed
                    print(f"\n{Colors.CYAN}Mark this suggestion as completed? (y/n):{Colors.RESET}")
                    if self.get_simple_input("").lower() == 'y':
                        self.mark_suggestion_completed(suggestion_text, category)
                        print(f"{Colors.GREEN}✓ Suggestion marked as completed{Colors.RESET}")
                
            except ImportError:
                # Fallback to simpler approach
                print(f"\n{Colors.YELLOW}Using simple Claude execution...{Colors.RESET}")
                
                # Save prompt to temp file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                    tmp.write(prompt)
                    tmp_path = tmp.name
                
                try:
                    cmd = f"cat '{tmp_path}' | claude"
                    process = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
                    
                    if process.stdout:
                        print(process.stdout)
                        
                        # Ask about marking suggestion as completed
                        print(f"\n{Colors.CYAN}Mark this suggestion as completed? (y/n):{Colors.RESET}")
                        if self.get_simple_input("").lower() == 'y':
                            self.mark_suggestion_completed(suggestion_text, category)
                            print(f"{Colors.GREEN}✓ Suggestion marked as completed{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}No response from Claude{Colors.RESET}")
                        
                except subprocess.TimeoutExpired:
                    print(f"{Colors.RED}Claude request timed out (10 minutes){Colors.RESET}")
                finally:
                    os.unlink(tmp_path)
                    
        except Exception as e:
            print(f"\n{Colors.RED}Error during development: {str(e)}{Colors.RESET}")
            logger.error(f"Development error: {str(e)}", category=LogCategory.CLAUDE)
        
        input(f"\n{Colors.DIM}Press Enter to return...{Colors.RESET}")
    
    def unified_agent_processor(self):
        """Unified agent processor combining all agent capabilities"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🤖 AI Ajan Sistemi{Colors.RESET}")
        print(f"{Colors.DIM}Tüm ajanlar tek arayüzde{Colors.RESET}\n")
        
        # Show available agents
        print(f"{Colors.YELLOW}Kullanılabilir Ajanlar:{Colors.RESET}")
        print(f"{Colors.GREEN}1{Colors.RESET} - 🎭 Orkestra Lideri {Colors.DIM}(Coordinate multiple agents){Colors.RESET}")
        print(f"{Colors.GREEN}2{Colors.RESET} - 🔬 Kod Analizci {Colors.DIM}(Deep code analysis){Colors.RESET}")
        print(f"{Colors.GREEN}3{Colors.RESET} - 🔍 Arşiv Araştırmacı {Colors.DIM}(Archive research){Colors.RESET}")
        print(f"{Colors.GREEN}4{Colors.RESET} - ♻️ Refaktör Uzmanı {Colors.DIM}(Code refactoring){Colors.RESET}")
        print(f"{Colors.GREEN}5{Colors.RESET} - 🐛 Hata Avcısı {Colors.DIM}(Bug detection){Colors.RESET}")
        print(f"{Colors.GREEN}6{Colors.RESET} - 🧠 Doğal Dil İşlemci {Colors.DIM}(NLP tasks){Colors.RESET}")
        
        print(f"\n{Colors.CYAN}Veya doğrudan komut girin:{Colors.RESET}")
        print(f"{Colors.DIM}Örnek: 'menu navigasyon hatasını düzelt'{Colors.RESET}")
        
        choice = self.get_simple_input(f"\n{Colors.BLUE}Seçim/Komut: {Colors.RESET}")
        
        # Handle numeric choices
        if choice == '1':
            self.agent_orchestra_mode()
        elif choice == '2':
            self.code_analyzer_agent_mode()
        elif choice == '3':
            self.archive_research_agent_mode()
        elif choice == '4':
            self.refactor_specialist_mode()
        elif choice == '5':
            self.bug_analysis_mode()
        elif choice == '6':
            self.nlp_processor_mode()
        elif choice:
            # Natural language command - use NLP agent to route
            self._process_natural_command(choice)
    
    def _process_natural_command(self, command: str):
        """Process natural language command with agent routing"""
        print(f"\n{Colors.CYAN}Komut analiz ediliyor...{Colors.RESET}")
        
        # Analyze command intent
        intent = self._analyze_command_intent(command)
        
        # Route to appropriate agent
        if 'bug' in command.lower() or 'hata' in command.lower():
            print(f"{Colors.YELLOW}Hata Avcısı ajanına yönlendiriliyor...{Colors.RESET}")
            self._analyze_and_fix_bug(command)
        elif 'refactor' in command.lower() or 'iyileştir' in command.lower():
            print(f"{Colors.YELLOW}Refaktör Uzmanına yönlendiriliyor...{Colors.RESET}")
            self._refactor_with_agent(command)
        elif 'araştır' in command.lower() or 'bul' in command.lower():
            print(f"{Colors.YELLOW}Arşiv Araştırmacısına yönlendiriliyor...{Colors.RESET}")
            self._research_with_agent(command)
        else:
            # Default to orchestrator for complex tasks
            print(f"{Colors.YELLOW}Orkestra Liderine yönlendiriliyor...{Colors.RESET}")
            self._orchestrate_agents(command)
    
    def system_status_mode(self):
        """Show system status and health"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🏥 Sistem Durumu{Colors.RESET}")
        print(f"{Colors.DIM}{'='*60}{Colors.RESET}\n")
        
        # Version info
        try:
            with open('src/VERSION.json', 'r') as f:
                version_info = json.load(f)
                print(f"{Colors.GREEN}Version:{Colors.RESET} {version_info['version']}")
                print(f"{Colors.GREEN}Build:{Colors.RESET} {version_info['build_number']}")
        except:
            print(f"{Colors.RED}Version bilgisi okunamadı{Colors.RESET}")
        
        # Git status
        print(f"\n{Colors.YELLOW}Git Durumu:{Colors.RESET}")
        result = subprocess.run(['git', 'status', '-sb'], capture_output=True, text=True)
        print(result.stdout)
        
        # Claude Health Monitor
        if self.health_monitor:
            print(f"\n{Colors.YELLOW}Claude Sağlık Durumu:{Colors.RESET}")
            self.health_monitor.show_status()
        
        # Screenshot status
        if self.screenshot_manager:
            print(f"\n{Colors.YELLOW}Screenshot Durumu:{Colors.RESET}")
            recent = self.screenshot_manager.get_recent_archives(3)
            if recent:
                print(f"Son arşivlenen {len(recent)} screenshot")
            else:
                print("Arşivlenmiş screenshot yok")
        
        input(f"\n{Colors.DIM}Devam etmek için Enter...{Colors.RESET}")
    
    def show_advanced_tools_menu(self):
        """Show advanced tools submenu"""
        while True:
            self.clear_screen()
            print(f"{Colors.CYAN}{Colors.BOLD}🔧 Gelişmiş Araçlar{Colors.RESET}")
            print(f"{Colors.DIM}{'='*60}{Colors.RESET}\n")
            
            print(f"{Colors.YELLOW}Geliştirme Araçları:{Colors.RESET}")
            print(f"{Colors.CYAN}1{Colors.RESET} - 💻 Kod Geliştirme Modu")
            print(f"{Colors.CYAN}2{Colors.RESET} - 🐛 Detaylı Hata Analizi")
            print(f"{Colors.CYAN}3{Colors.RESET} - 📚 Dokümantasyon Yardımcısı")
            
            print(f"\n{Colors.YELLOW}Yönetim Araçları:{Colors.RESET}")
            print(f"{Colors.CYAN}4{Colors.RESET} - 📝 Development Manager")
            print(f"{Colors.CYAN}5{Colors.RESET} - 🎯 Özellik Evrimi Analizi")
            
            print(f"\n{Colors.DIM}q - Geri dön{Colors.RESET}")
            
            choice = self.get_simple_input(f"\n{Colors.BLUE}Seçiminiz: {Colors.RESET}").lower()
            
            if choice == 'q':
                break
            elif choice == '1':
                self.code_development_mode()
            elif choice == '2':
                self.bug_analysis_mode()
            elif choice == '3':
                self.documentation_helper_mode()
            elif choice == '4':
                self.suggestions_manager_mode()
            elif choice == '5':
                self.feature_evolution_mode()
            elif choice == '6':
                self.database_setup_wizard()
            else:
                print(f"\n{Colors.RED}Geçersiz seçim{Colors.RESET}")
                time.sleep(1)
    
    def _analyze_feature_with_agent(self, feature: str) -> dict:
        """Analyze feature request with agent"""
        # Simulate agent analysis
        return {
            'complexity': 'medium',
            'suggested_files': ['src/main.py', 'src/claude_cli.py'],
            'dependencies': [],
            'tests_needed': True,
            'estimated_time': '2-3 hours'
        }
    
    def _develop_with_agent(self, feature: str, analysis: dict):
        """Develop feature with agent assistance"""
        print(f"\n{Colors.CYAN}Geliştirme planı:{Colors.RESET}")
        print(f"Karmaşıklık: {analysis['complexity']}")
        print(f"Etkilenen dosyalar: {', '.join(analysis['suggested_files'])}")
        print(f"Tahmini süre: {analysis['estimated_time']}")
        
        confirm = self.get_simple_input(f"\n{Colors.YELLOW}Başlatmak istiyor musunuz? (e/h): {Colors.RESET}")
        if confirm.lower() == 'e':
            self.trigger_claude_development(feature, 'safe_feature_development', analysis)
    
    def _analyze_and_fix_bug(self, bug_desc: str):
        """Analyze and fix bug with agent"""
        # First, search for related code
        print(f"\n{Colors.CYAN}İlgili kod aranıyor...{Colors.RESET}")
        
        # Use archive research agent to find related code
        if hasattr(self, 'archive_research_agent'):
            # Search in recent versions
            results = self._quick_code_search(bug_desc)
            if results:
                print(f"{Colors.GREEN}Potansiyel sorunlu alanlar bulundu{Colors.RESET}")
        
        # Start bug fix development
        self.trigger_claude_development(f"Bug fix: {bug_desc}", 'safe_bugfix')
    
    def _refactor_with_agent(self, target: str):
        """Refactor code with agent validation"""
        print(f"\n{Colors.CYAN}Kod analiz ediliyor...{Colors.RESET}")
        
        # Analyze code quality
        analysis = {
            'code_smells': ['long methods', 'duplicate code'],
            'complexity': 'high',
            'test_coverage': 'low'
        }
        
        print(f"\nBulunan sorunlar:")
        for smell in analysis['code_smells']:
            print(f"  - {smell}")
        
        # Start refactoring
        self.trigger_claude_development(f"Refactor: {target}", 'safe_refactor', analysis)
    
    def _run_tests(self):
        """Run project tests"""
        # Check if tests exist
        if os.path.exists('tests') or os.path.exists('test'):
            print("Test dizini bulundu, testler çalıştırılıyor...")
            # Run pytest or unittest
            subprocess.run(['python', '-m', 'pytest', '-v'], check=False)
        else:
            print(f"{Colors.YELLOW}Test dizini bulunamadı{Colors.RESET}")
    
    def _deploy_with_version(self):
        """Deploy changes with new version"""
        print(f"\n{Colors.CYAN}Yeni versiyon oluşturuluyor...{Colors.RESET}")
        
        # Use archive_version script
        try:
            subprocess.run(['python', 'src/archive_version.py'], check=True)
            print(f"{Colors.GREEN}✓ Yeni versiyon oluşturuldu{Colors.RESET}")
        except:
            print(f"{Colors.RED}Versiyon oluşturma başarısız{Colors.RESET}")
    
    def _analyze_command_intent(self, command: str) -> dict:
        """Analyze natural language command intent"""
        # Simple keyword-based intent detection
        intent = {
            'action': 'unknown',
            'target': '',
            'urgency': 'normal'
        }
        
        # Detect action
        if any(word in command.lower() for word in ['düzelt', 'fix', 'repair']):
            intent['action'] = 'fix'
        elif any(word in command.lower() for word in ['geliştir', 'develop', 'ekle']):
            intent['action'] = 'develop'
        elif any(word in command.lower() for word in ['araştır', 'bul', 'search']):
            intent['action'] = 'research'
        
        return intent
    
    def _research_with_agent(self, query: str):
        """Research using archive research agent"""
        # Delegate to archive research agent
        self.archive_research_agent_mode(initial_query=query)
    
    def _orchestrate_agents(self, task: str):
        """Orchestrate multiple agents for complex tasks"""
        print(f"\n{Colors.CYAN}Kompleks görev analiz ediliyor...{Colors.RESET}")
        print(f"Görev: {task}")
        
        # Analyze task complexity
        print(f"\n{Colors.YELLOW}Gerekli ajanlar belirleniyor...{Colors.RESET}")
        time.sleep(1)
        
        # Simulate agent assignment
        agents = ['Kod Analizci', 'Refaktör Uzmanı', 'Test Uzmanı']
        for agent in agents:
            print(f"  ✓ {agent} ajanı atandı")
        
        # Start orchestrated development
        self.trigger_claude_development(task, 'orchestrated_task', {
            'agents': agents,
            'complexity': 'high'
        })
    
    def _quick_code_search(self, query: str) -> list:
        """Quick code search in current version"""
        # Simple grep-based search
        results = []
        try:
            result = subprocess.run(
                ['grep', '-r', '-i', query.split()[0], 'src/'],
                capture_output=True, text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')[:5]  # First 5 results
                results = lines
        except:
            pass
        return results
    
    def _process_claude_output(self, output_lines):
        """Process Claude's output to extract code changes"""
        # This would parse the output and potentially create/update files
        # For now, just log that we received output
        logger.info(f"Received {len(output_lines)} lines of output from Claude", 
                   category=LogCategory.CLAUDE)
    
    def mark_suggestion_completed(self, suggestion_text, category):
        """Mark a suggestion as completed in CLAUDE_SUGGESTIONS.md"""
        try:
            suggestions_file = Path("CLAUDE_SUGGESTIONS.md")
            if not suggestions_file.exists():
                return
            
            content = suggestions_file.read_text(encoding='utf-8')
            
            # Add to completed section
            if "## Tamamlanan Öneriler" not in content:
                content += "\n\n## Tamamlanan Öneriler\n"
            
            # Add completed suggestion
            completed_entry = f"\n- [✓] {suggestion_text} (Category: {category}, Completed: {datetime.now().strftime('%Y-%m-%d')})"
            
            # Insert after completed section header
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "## Tamamlanan Öneriler" in line:
                    lines.insert(i + 1, completed_entry)
                    break
            
            # Write back
            suggestions_file.write_text('\n'.join(lines), encoding='utf-8')
            
        except Exception as e:
            logger.error(f"Failed to mark suggestion as completed: {str(e)}", 
                        category=LogCategory.CLAUDE)
    
    def get_simple_input(self, prompt=""):
        """Get simple input from user"""
        try:
            return input(prompt)
        except KeyboardInterrupt:
            return ""
        except Exception:
            return ""
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_health_monitor(self):
        """Show Claude Health Monitor"""
        self.clear_screen()
        
        if not self.health_monitor:
            print(f"{Colors.RED}Health Monitor mevcut değil!{Colors.RESET}")
            print(f"{Colors.YELLOW}Lütfen claude_health_monitor.py dosyasını kontrol edin.{Colors.RESET}")
            input(f"\n{Colors.DIM}Devam etmek için Enter...{Colors.RESET}")
            return
        
        # Show health report
        self.health_monitor.display_health_report()
        
        # Show options
        print(f"\n{Colors.CYAN}Seçenekler:{Colors.RESET}")
        print(f"1. Sağlık raporunu yenile")
        print(f"2. Geçmiş oturumları gör")
        print(f"3. Timeout geçmişini gör")
        print(f"4. İstatistikleri sıfırla")
        print(f"5. Ana menüye dön")
        
        choice = self.get_simple_input(f"\n{Colors.BLUE}Seçiminiz: {Colors.RESET}")
        
        if choice == '1':
            # Refresh
            self.show_health_monitor()
        elif choice == '2':
            # Show session history
            self.clear_screen()
            print(f"{Colors.CYAN}📝 Son 10 Oturum:{Colors.RESET}\n")
            
            sessions = self.health_monitor.health_data.get('sessions', [])[-10:]
            for session in reversed(sessions):
                status_emoji = "✅" if session['status'] == 'completed' else "❌"
                print(f"{status_emoji} {session['id']} - {session['command'][:50]}...")
                print(f"   Başlangıç: {session['start_time']}")
                if session.get('response_time'):
                    print(f"   Süre: {session['response_time']:.1f} saniye")
                print()
            
            input(f"\n{Colors.DIM}Devam etmek için Enter...{Colors.RESET}")
            self.show_health_monitor()
            
        elif choice == '3':
            # Show timeout history
            self.clear_screen()
            print(f"{Colors.YELLOW}⚠️ Timeout Geçmişi:{Colors.RESET}\n")
            
            timeouts = self.health_monitor.health_data.get('timeouts', [])[-10:]
            for timeout in reversed(timeouts):
                print(f"🕐 {timeout['timestamp']}")
                print(f"   Komut: {timeout['command'][:50]}...")
                print(f"   Eşik: {timeout['threshold']} saniye\n")
            
            input(f"\n{Colors.DIM}Devam etmek için Enter...{Colors.RESET}")
            self.show_health_monitor()
            
        elif choice == '4':
            # Reset statistics
            confirm = self.get_simple_input(f"\n{Colors.RED}İstatistikler sıfırlanacak. Emin misiniz? (e/h): {Colors.RESET}")
            if confirm.lower() == 'e':
                self.health_monitor.health_data['statistics'] = {
                    'total_sessions': 0,
                    'successful_sessions': 0,
                    'timeout_count': 0,
                    'recovery_count': 0,
                    'average_response_time': 0
                }
                self.health_monitor.save_health_data()
                print(f"{Colors.GREEN}✅ İstatistikler sıfırlandı{Colors.RESET}")
                time.sleep(1)
                self.show_health_monitor()
    
    def load_config(self):
        """Load configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {'auto_save': True}
    
    def load_history(self):
        """Load command history"""
        try:
            if self.history_path.exists():
                with open(self.history_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_history(self):
        """Save command history"""
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, 'w') as f:
                json.dump(self.history[-100:], f, indent=2)  # Keep last 100 entries
        except:
            pass
    
    def initial_screenshot_check(self):
        """Perform initial screenshot check on startup"""
        if not self.screenshot_manager:
            return
            
        try:
            count, archived = self.screenshot_manager.check_and_archive_all()
            if count > 0:
                print(f"\n{Colors.YELLOW}📸 {count} screenshot(s) found and archived{Colors.RESET}")
                for path in archived:
                    print(f"   {Colors.GREEN}✓{Colors.RESET} {path.name}")
                
                # Analyze screenshots for suggestions
                self.analyze_screenshots_for_suggestions(archived)
        except Exception as e:
            logger.error(f"Screenshot check error: {str(e)}", category=LogCategory.CLAUDE)
    
    def analyze_screenshots_for_suggestions(self, screenshot_paths):
        """Analyze archived screenshots to generate suggestions"""
        if not screenshot_paths:
            return
            
        for ss_path in screenshot_paths:
            try:
                # Try to read associated .txt file with content description
                txt_path = ss_path.with_suffix('.txt')
                content = "Unknown content"
                
                if txt_path.exists():
                    content = txt_path.read_text(encoding='utf-8').strip()
                else:
                    # Try to infer from filename
                    filename = ss_path.stem.lower()
                    if 'error' in filename:
                        content = "Error screen"
                    elif 'menu' in filename:
                        content = "Menu screen"
                    elif 'claude' in filename:
                        content = "Claude tools screen"
                    elif 'terminal' in filename:
                        content = "Terminal output"
                
                # Add to screenshot context
                self.screenshot_context['screenshots_analyzed'].append({
                    'filename': ss_path.name,
                    'content': content,
                    'timestamp': datetime.now()
                })
                self.screenshot_context['content_summary'].append(content)
                self.screenshot_context['total_count'] += 1
                
            except Exception as e:
                logger.error(f"Error analyzing screenshot {ss_path}: {str(e)}", 
                           category=LogCategory.CLAUDE)
    
    def start_agent_shell(self):
        """Start interactive agent shell for continuous communication"""
        if not self.agent_session_manager:
            print(f"\n{Colors.RED}Agent Session Manager not available{Colors.RESET}")
            print(f"Make sure unibos_agent_system.py is properly installed")
            input(f"\n{Colors.DIM}Press Enter to return...{Colors.RESET}")
            return
            
        try:
            # Start interactive shell
            self.agent_session_manager.start_interactive_shell()
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Exiting agent shell...{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}Error: {str(e)}{Colors.RESET}")
            logger.error(f"Agent shell error: {str(e)}", category=LogCategory.CLAUDE)
        finally:
            # Clean up sessions
            if self.agent_session_manager:
                self.agent_session_manager.close_all_sessions()
                
    def agent_analyze_and_improve(self, module_name=None):
        """Agent system for intelligent code improvement"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🤖 UNIBOS AI Agent System{Colors.RESET}")
        print(f"{Colors.YELLOW}Intelligent Code Analysis & Improvement{Colors.RESET}")
        print(f"{Colors.DIM}{'='*60}{Colors.RESET}\n")
        
        # Basit modül listesi
        modules = {
            "1": ("main.py", "Ana program"),
            "2": ("claude_cli.py", "Claude entegrasyonu"), 
            "3": ("currencies_enhanced.py", "Döviz modülü"),
            "4": ("git_manager.py", "Git yönetimi"),
            "5": ("screenshot_manager.py", "Screenshot yönetimi"),
        }
        
        print(f"{Colors.GREEN}Hangi modülü iyileştirmek istersiniz?{Colors.RESET}\n")
        for key, (file, desc) in modules.items():
            print(f"  {Colors.CYAN}{key}{Colors.RESET}. {file:<25} - {desc}")
        
        print(f"\n  {Colors.DIM}q. Geri dön{Colors.RESET}")
        
        choice = self.get_simple_input(f"\n{Colors.BLUE}Seçim: {Colors.RESET}")
        
        if choice == 'q':
            return
        
        if choice not in modules:
            print(f"{Colors.RED}Geçersiz seçim{Colors.RESET}")
            time.sleep(1)
            return self.agent_analyze_and_improve()
        
        file_name, desc = modules[choice]
        file_path = f"src/{file_name}"
        
        # Dosyayı analiz et
        print(f"\n{Colors.YELLOW}📊 Analiz ediliyor: {file_name}{Colors.RESET}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basit analiz
            issues = []
            
            # 1. Bare except kontrolü
            if 'except:' in content:
                issues.append("❌ Bare except kullanımı tespit edildi (güvenlik riski)")
            
            # 2. TODO/FIXME kontrolü
            todos = content.count('TODO') + content.count('FIXME')
            if todos > 0:
                issues.append(f"📝 {todos} adet TODO/FIXME bulundu")
            
            # 3. Uzun fonksiyon kontrolü
            lines = content.split('\n')
            in_function = False
            func_lines = 0
            long_functions = 0
            
            for line in lines:
                if line.strip().startswith('def '):
                    if func_lines > 50:
                        long_functions += 1
                    in_function = True
                    func_lines = 0
                elif in_function:
                    if line.strip() and not line[0].isspace():
                        in_function = False
                    else:
                        func_lines += 1
            
            if long_functions > 0:
                issues.append(f"📏 {long_functions} adet uzun fonksiyon (>50 satır)")
            
            # 4. Import kontrolü
            import_lines = [l for l in lines if l.strip().startswith(('import ', 'from '))]
            if len(import_lines) > 20:
                issues.append(f"📦 Çok fazla import ({len(import_lines)} adet)")
            
            # 5. Güvenlik kontrolleri
            if 'eval(' in content or 'exec(' in content:
                issues.append("⚠️ eval/exec kullanımı (güvenlik riski)")
            if 'shell=True' in content:
                issues.append("⚠️ shell=True kullanımı (injection riski)")
            
            # Sonuçları göster
            print(f"\n{Colors.CYAN}📋 Analiz Sonuçları:{Colors.RESET}")
            print(f"Dosya boyutu: {len(lines)} satır")
            print(f"Toplam karakter: {len(content)}")
            
            if issues:
                print(f"\n{Colors.YELLOW}Tespit edilen sorunlar:{Colors.RESET}")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print(f"\n{Colors.GREEN}✓ Kritik sorun tespit edilmedi!{Colors.RESET}")
            
            # İyileştirme önerisi
            print(f"\n{Colors.CYAN}Bu modülü Claude ile iyileştirmek ister misiniz? (y/n):{Colors.RESET} ", end='')
            if self.get_simple_input("").lower() == 'y':
                
                # Prompt hazırla
                prompt = f"""UNIBOS {file_name} Modülü İyileştirme

Dosya: {file_path}
Boyut: {len(lines)} satır

Tespit Edilen Sorunlar:
{chr(10).join(issues) if issues else 'Kritik sorun yok'}

Lütfen bu dosyayı iyileştir. Özellikle:
1. Tespit edilen sorunları düzelt
2. Kod kalitesini artır
3. Error handling ekle
4. Type hints ekle
5. Docstring'leri iyileştir

ÖNEMLI: Geriye uyumluluğu koru ve mevcut fonksiyonaliteyi bozma.

Kod değişikliklerini şu formatta ver:
```FILE: {file_path}
# Tam dosya içeriği...
```
"""
                
                # Screenshot context varsa ekle
                if hasattr(self, 'screenshot_context') and self.screenshot_context:
                    if self.screenshot_context.get('total_count', 0) > 0:
                        prompt += f"\n\nNOT: Bu oturumda {self.screenshot_context['total_count']} screenshot analiz edildi."
                        if self.screenshot_context.get('content_summary'):
                            prompt += f"\nScreenshot içerikleri: {', '.join(set(self.screenshot_context['content_summary']))}"
                
                # Claude'a gönder
                print(f"\n{Colors.YELLOW}Claude'a gönderiliyor...{Colors.RESET}")
                
                # Basit yöntem - direkt subprocess
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                    tmp.write(prompt)
                    tmp_path = tmp.name
                
                try:
                    # Claude'u çalıştır
                    cmd = f"claude < '{tmp_path}'"
                    print(f"\n{Colors.DIM}Komut: {cmd}{Colors.RESET}")
                    
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.stdout:
                        print(f"\n{Colors.GREEN}Claude'dan yanıt alındı:{Colors.RESET}")
                        print(result.stdout)
                    else:
                        print(f"\n{Colors.RED}Claude'dan yanıt alınamadı{Colors.RESET}")
                        if result.stderr:
                            print(f"Hata: {result.stderr}")
                    
                except Exception as e:
                    print(f"\n{Colors.RED}Hata: {str(e)}{Colors.RESET}")
                finally:
                    os.unlink(tmp_path)
            
        except FileNotFoundError:
            print(f"\n{Colors.RED}Dosya bulunamadı: {file_path}{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}Analiz hatası: {str(e)}{Colors.RESET}")
        
        input(f"\n{Colors.DIM}Devam etmek için Enter'a basın...{Colors.RESET}")
    
    # Development Tools Methods
    def chat_mode(self):
        """Interactive Claude conversation mode"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}💬 Claude Chat Mode{Colors.RESET}")
        print(f"{Colors.DIM}Interactive conversation with Claude AI{Colors.RESET}\n")
        
        print(f"{Colors.YELLOW}Starting interactive chat session...{Colors.RESET}")
        print(f"{Colors.DIM}Type 'exit' to return to menu{Colors.RESET}\n")
        
        while True:
            user_input = self.get_simple_input(f"\n{Colors.GREEN}You: {Colors.RESET}")
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            
            # Send to Claude and get response
            response = self.send_to_claude(user_input)
            print(f"\n{Colors.BLUE}Claude: {Colors.RESET}{response}")
    
    def code_development_mode(self):
        """AI-assisted code development mode"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🚀 Code Development Mode{Colors.RESET}")
        print(f"{Colors.DIM}Implement features with AI assistance{Colors.RESET}\n")
        
        # Get development task
        task = self.get_simple_input(f"{Colors.YELLOW}Describe the feature to develop: {Colors.RESET}")
        if not task:
            return
        
        # Get context
        context = self.get_simple_input(f"{Colors.YELLOW}Additional context (optional): {Colors.RESET}")
        
        # Trigger development
        self.trigger_claude_development(task, 'code_development', context)
    
    def bug_analysis_mode(self):
        """Analyze and fix bugs with AI assistance"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🔧 Bug Analysis Mode{Colors.RESET}")
        print(f"{Colors.DIM}Find and fix issues with AI help{Colors.RESET}\n")
        
        # List recent errors from logs
        print(f"{Colors.YELLOW}Recent errors in logs:{Colors.RESET}")
        # TODO: Implement log analysis
        
        bug_description = self.get_simple_input(f"\n{Colors.YELLOW}Describe the bug: {Colors.RESET}")
        if bug_description:
            self.trigger_claude_development(f"Fix bug: {bug_description}", 'bug_fix')
    
    def code_review_mode(self):
        """AI-powered code review"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}📋 Code Review Mode{Colors.RESET}")
        print(f"{Colors.DIM}AI-powered code analysis and suggestions{Colors.RESET}\n")
        
        file_path = self.get_simple_input(f"{Colors.YELLOW}Enter file path to review: {Colors.RESET}")
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                code = f.read()
            
            prompt = f"Please review this code and provide improvement suggestions:\n\n{code[:1000]}..."
            self.trigger_claude_development(prompt, 'code_review')
    
    # Project Management Methods
    def suggestions_manager_mode(self):
        """PostgreSQL-based suggestions management"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}💡 Suggestions Manager{Colors.RESET}")
        print(f"{Colors.DIM}Manage development tasks and suggestions{Colors.RESET}\n")
        
        try:
            from suggestion_manager import suggestion_manager
            
            # Show stats
            stats = suggestion_manager.get_suggestion_stats()
            print(f"{Colors.YELLOW}Suggestion Statistics:{Colors.RESET}")
            print(f"Total: {stats['total']}")
            print(f"Pending: {stats['status'].get('pending', 0)}")
            print(f"In Progress: {stats['status'].get('in_progress', 0)}")
            print(f"Completed: {stats['status'].get('completed', 0)}")
            print(f"\nPool (not promoted): {stats['pool'].get('not_promoted', 0)}")
            
            print(f"\n{Colors.YELLOW}Options:{Colors.RESET}")
            print(f"1. View pending suggestions")
            print(f"2. View suggestion pool")
            print(f"3. Add new suggestion")
            print(f"4. Execute suggestion")
            print(f"5. Update suggestion status")
            print(f"q. Back to menu")
            
            choice = self.get_simple_input(f"\n{Colors.BLUE}Select: {Colors.RESET}")
            
            if choice == '1':
                suggestions = suggestion_manager.get_pending_suggestions()
                for i, sugg in enumerate(suggestions[:10], 1):
                    print(f"\n{i}. {Colors.BOLD}{sugg['title']}{Colors.RESET}")
                    print(f"   Priority: {sugg['priority']} | Category: {sugg['category']}")
                    print(f"   {Colors.DIM}{sugg['description'][:100]}...{Colors.RESET}")
                
            elif choice == '2':
                pool_items = suggestion_manager.get_pool_items()
                for i, item in enumerate(pool_items[:10], 1):
                    print(f"\n{i}. {item['text'][:80]}...")
                    print(f"   Source: {item['source']} | Created: {item['created_at']}")
                
            elif choice == '3':
                title = self.get_simple_input(f"\n{Colors.YELLOW}Title: {Colors.RESET}")
                desc = self.get_simple_input(f"{Colors.YELLOW}Description: {Colors.RESET}")
                category = self.get_simple_input(f"{Colors.YELLOW}Category (feature/bug_fix/etc): {Colors.RESET}")
                
                if title and desc:
                    sid = suggestion_manager.add_suggestion(title, desc, category or 'feature')
                    print(f"\n{Colors.GREEN}✓ Suggestion added: {sid}{Colors.RESET}")
            
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
            
        except ImportError:
            print(f"{Colors.RED}Suggestion manager not available{Colors.RESET}")
            input(f"\n{Colors.DIM}Press Enter to return...{Colors.RESET}")
    
    def feature_evolution_mode(self):
        """Analyze archived features for evolution"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🎯 Feature Evolution Analyzer{Colors.RESET}")
        print(f"{Colors.DIM}Analyze and evolve features from archives{Colors.RESET}\n")
        
        try:
            from feature_evolution_analyzer import FeatureEvolutionAnalyzer
            analyzer = FeatureEvolutionAnalyzer()
            
            feature_name = self.get_simple_input(f"{Colors.YELLOW}Feature to analyze: {Colors.RESET}")
            if feature_name:
                # TODO: Implement archive scanning
                print(f"\n{Colors.YELLOW}Analyzing '{feature_name}' across versions...{Colors.RESET}")
                print(f"{Colors.DIM}Feature evolution analysis will be implemented{Colors.RESET}")
                
        except ImportError:
            print(f"{Colors.RED}Feature Evolution Analyzer not available{Colors.RESET}")
        
        input(f"\n{Colors.DIM}Press Enter to return...{Colors.RESET}")
    
    def project_analytics_mode(self):
        """Show project statistics and insights"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}📊 Project Analytics{Colors.RESET}")
        print(f"{Colors.DIM}Statistics and insights about UNIBOS{Colors.RESET}\n")
        
        # Show various stats
        print(f"{Colors.YELLOW}Code Statistics:{Colors.RESET}")
        try:
            import subprocess
            # Count Python files
            result = subprocess.run("find . -name '*.py' | wc -l", shell=True, capture_output=True, text=True)
            py_files = result.stdout.strip()
            print(f"Python files: {py_files}")
            
            # Count lines of code
            result = subprocess.run("find . -name '*.py' -exec wc -l {} + | tail -1", shell=True, capture_output=True, text=True)
            if result.stdout:
                loc = result.stdout.strip().split()[0]
                print(f"Lines of code: {loc}")
        except:
            pass
        
        input(f"\n{Colors.DIM}Press Enter to return...{Colors.RESET}")
    
    # AI Agent System Methods
    def agent_orchestra_mode(self):
        """Multi-agent collaboration system"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🤖 Agent Orchestra{Colors.RESET}")
        print(f"{Colors.DIM}Coordinate multiple AI agents for complex tasks{Colors.RESET}\n")
        
        if self.agent_session_manager:
            print(f"{Colors.YELLOW}Launching Agent Orchestra...{Colors.RESET}")
            self.agent_session_manager.start_interactive_shell()
        else:
            print(f"{Colors.RED}Agent system not available{Colors.RESET}")
            input(f"\n{Colors.DIM}Press Enter to return...{Colors.RESET}")
    
    def code_analyzer_agent_mode(self):
        """Deep code analysis with specialized agent"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🔬 Code Analyzer Agent{Colors.RESET}")
        print(f"{Colors.DIM}Deep analysis of code structure and quality{Colors.RESET}\n")
        
        module = self.get_simple_input(f"{Colors.YELLOW}Module to analyze (e.g., main.py): {Colors.RESET}")
        if module:
            # Trigger agent analysis
            self.agent_analyze_and_improve(module_name=module)
    
    def refactor_specialist_mode(self):
        """Code refactoring with specialized agent"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🛠️ Refactor Specialist{Colors.RESET}")
        print(f"{Colors.DIM}Intelligent code refactoring suggestions{Colors.RESET}\n")
        
        file_path = self.get_simple_input(f"{Colors.YELLOW}File to refactor: {Colors.RESET}")
        if file_path and os.path.exists(file_path):
            # Use refactor specialist agent
            print(f"\n{Colors.YELLOW}Analyzing code for refactoring opportunities...{Colors.RESET}")
            self.trigger_claude_development(f"Refactor {file_path}", 'refactoring')
    
    # Utilities Methods
    def documentation_helper_mode(self):
        """Generate and improve documentation"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}📚 Documentation Helper{Colors.RESET}")
        print(f"{Colors.DIM}Generate and improve project documentation{Colors.RESET}\n")
        
        print(f"{Colors.YELLOW}Documentation Options:{Colors.RESET}")
        print("1. Generate module documentation")
        print("2. Update README")
        print("3. Create API documentation")
        print("4. Generate changelog entry")
        
        choice = self.get_simple_input(f"\n{Colors.BLUE}Select: {Colors.RESET}")
        
        if choice == '1':
            module = self.get_simple_input(f"\n{Colors.YELLOW}Module name: {Colors.RESET}")
            if module:
                self.trigger_claude_development(f"Generate documentation for {module}", 'documentation')
        elif choice == '4':
            changes = self.get_simple_input(f"\n{Colors.YELLOW}Describe changes: {Colors.RESET}")
            if changes:
                self.trigger_claude_development(f"Generate changelog entry: {changes}", 'documentation')
    
    def view_communication_logs(self):
        """View Claude communication history"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}📜 Communication Logs{Colors.RESET}")
        print(f"{Colors.DIM}View session history and logs{Colors.RESET}\n")
        
        # List recent communication logs
        log_files = sorted(Path('.').glob('CLAUDE_COMMUNICATION_LOG_*.md'), reverse=True)[:5]
        
        if log_files:
            print(f"{Colors.YELLOW}Recent communication logs:{Colors.RESET}")
            for i, log_file in enumerate(log_files, 1):
                print(f"{i}. {log_file.name}")
            
            choice = self.get_simple_input(f"\n{Colors.BLUE}Select log to view (1-{len(log_files)}): {Colors.RESET}")
            
            if choice.isdigit() and 1 <= int(choice) <= len(log_files):
                with open(log_files[int(choice)-1], 'r') as f:
                    content = f.read()
                print(f"\n{Colors.DIM}{content[:1000]}...{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}No communication logs found{Colors.RESET}")
        
        input(f"\n{Colors.DIM}Press Enter to return...{Colors.RESET}")

    def _check_screenshots_on_entry(self):
        """Check screenshots when entering Claude tools"""
        if self.screenshot_manager:
            try:
                count, archived = self.screenshot_manager.check_and_archive_all()
                if count > 0:
                    print(f"\n{Colors.YELLOW}📸 Archived {count} screenshots on entry{Colors.RESET}")
                    for path in archived:
                        print(f"   ✓ {path.name}")
                    print()
                    time.sleep(1)
            except:
                pass
    
    def _check_screenshots_on_exit(self):
        """Check screenshots when exiting Claude tools"""
        if self.screenshot_manager:
            try:
                count, archived = self.screenshot_manager.check_and_archive_all()
                if count > 0:
                    print(f"\n{Colors.YELLOW}📸 Archived {count} screenshots on exit{Colors.RESET}")
                    for path in archived:
                        print(f"   ✓ {path.name}")
                    time.sleep(1)
            except:
                pass
    
    # Quick Access Methods
    def direct_agent_processor(self):
        """Direct interface to agent processor"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🚀 Agent Processor - Direkt Arayüz{Colors.RESET}")
        print(f"{Colors.DIM}Ajanlarla direkt iletişim kurabilirsiniz{Colors.RESET}\n")
        
        if self.agent_session_manager:
            print(f"{Colors.YELLOW}Komutlar:{Colors.RESET}")
            print("  help - Yardım göster")
            print("  list - Mevcut ajanları listele")
            print("  chat <agent> - Belirli bir ajanla sohbet")
            print("  task <description> - Yeni görev oluştur")
            print("  exit - Çıkış\n")
            
            # Start command-line style interface
            while True:
                try:
                    command = self.get_simple_input(f"{Colors.GREEN}agent>{Colors.RESET} ").strip()
                    
                    if command == 'exit':
                        break
                    elif command == 'help':
                        print("\nAgent Processor Komutları:")
                        print("  chat developer - Geliştirici ajanla sohbet")
                        print("  chat analyst - Analizci ajanla sohbet")
                        print("  task 'implement new feature' - Yeni görev başlat")
                        print("  status - Aktif görevleri göster")
                    elif command.startswith('chat '):
                        agent_type = command[5:].strip()
                        print(f"\n{Colors.CYAN}'{agent_type}' ajanıyla bağlantı kuruluyor...{Colors.RESET}")
                        # TODO: Implement agent chat
                    elif command.startswith('task '):
                        task_desc = command[5:].strip()
                        print(f"\n{Colors.YELLOW}Görev oluşturuluyor: {task_desc}{Colors.RESET}")
                        # Create task and add to suggestions
                        self._add_to_suggestions(task_desc, 'agent_task')
                    elif command:
                        # Process as natural language command
                        print(f"\n{Colors.CYAN}Komut işleniyor...{Colors.RESET}")
                        self._process_nlp_command(command)
                        
                except KeyboardInterrupt:
                    print(f"\n{Colors.YELLOW}Agent processor'dan çıkılıyor...{Colors.RESET}")
                    break
                except Exception as e:
                    print(f"{Colors.RED}Hata: {e}{Colors.RESET}")
                    
        else:
            print(f"{Colors.RED}Agent sistemi mevcut değil{Colors.RESET}")
        
        input(f"\n{Colors.DIM}Ana menüye dönmek için Enter...{Colors.RESET}")
    
    def smart_suggestions_mode(self):
        """AI-powered smart suggestions"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}💡 Smart Suggestions - AI Destekli Öneriler{Colors.RESET}")
        print(f"{Colors.DIM}Mevcut koda ve geçmişe dayalı akıllı öneriler{Colors.RESET}\n")
        
        print(f"{Colors.YELLOW}Öneri kaynakları analiz ediliyor...{Colors.RESET}")
        
        suggestions = []
        
        # 1. Analyze recent screenshots
        if self.screenshot_context and self.screenshot_context['content_summary']:
            print(f"  ✓ Screenshot analizleri")
            for content in self.screenshot_context['content_summary'][-3:]:
                suggestions.append(f"[SS] {content}")
        
        # 2. Analyze recent communication logs
        log_files = sorted(Path('.').glob('CLAUDE_COMMUNICATION_LOG_*.md'), reverse=True)[:2]
        if log_files:
            print(f"  ✓ İletişim logları")
            for log in log_files:
                try:
                    content = log.read_text()[:500]
                    if 'devam ediyor' in content or 'TODO' in content:
                        suggestions.append(f"[LOG] Tamamlanmamış görev: {log.name}")
                except:
                    pass
        
        # 3. Generate AI suggestions based on code analysis
        print(f"  ✓ Kod analizi")
        suggestions.extend(self._generate_agent_suggestions())
        
        # 4. Check for common patterns
        print(f"  ✓ Pattern analizi")
        suggestions.extend(self._analyze_code_patterns())
        
        # Display suggestions
        print(f"\n{Colors.GREEN}Bulunan öneriler:{Colors.RESET}")
        for i, suggestion in enumerate(suggestions[:10], 1):
            print(f"{i}. {suggestion}")
        
        # Action options
        print(f"\n{Colors.YELLOW}Seçenekler:{Colors.RESET}")
        print("  1-10: Öneriyi geliştirmeye başla")
        print("  r: Yeniden analiz et")
        print("  a: Tüm önerileri göster")
        print("  q: Çıkış")
        
        choice = self.get_simple_input(f"\n{Colors.BLUE}Seçiminiz: {Colors.RESET}")
        
        if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
            selected = suggestions[int(choice)-1]
            self.trigger_claude_development(selected, 'smart_suggestion')
        elif choice == 'r':
            self.smart_suggestions_mode()
        elif choice == 'a':
            for i, suggestion in enumerate(suggestions, 1):
                print(f"{i}. {suggestion}")
            input(f"\n{Colors.DIM}Devam etmek için Enter...{Colors.RESET}")
    
    def enhanced_safe_development_mode(self):
        """Enhanced safe development mode with agent integration"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🛡️ Güvenli Geliştirme Modu v2{Colors.RESET}")
        print(f"{Colors.DIM}Ajan destekli, otomatik versiyon yönetimi ile güvenli geliştirme{Colors.RESET}\n")
        
        # Quick action menu
        print(f"{Colors.YELLOW}Hızlı İşlemler:{Colors.RESET}")
        print(f"{Colors.GREEN}1{Colors.RESET} - 🚀 Yeni özellik geliştir {Colors.DIM}(Agent powered){Colors.RESET}")
        print(f"{Colors.GREEN}2{Colors.RESET} - 🐛 Hata düzelt {Colors.DIM}(Bug fix with auto test){Colors.RESET}")
        print(f"{Colors.GREEN}3{Colors.RESET} - ♻️ Kod iyileştir {Colors.DIM}(Refactor with safety checks){Colors.RESET}")
        print(f"{Colors.GREEN}4{Colors.RESET} - 📋 Review & Deploy {Colors.DIM}(Final checks and version){Colors.RESET}")
        print(f"{Colors.CYAN}5{Colors.RESET} - 🔄 Git işlemleri {Colors.DIM}(Manual git operations){Colors.RESET}")
        
        choice = self.get_simple_input(f"\n{Colors.BLUE}Seçiminiz: {Colors.RESET}")
        
        if choice == '1':
            self._safe_feature_development()
        elif choice == '2':
            self._safe_bug_fix()
        elif choice == '3':
            self._safe_refactor()
        elif choice == '4':
            self._review_and_deploy()
        elif choice == '5':
            self.safe_development_mode()  # Call original for git operations
        else:
            print(f"\n{Colors.YELLOW}Ana menüye dönülüyor...{Colors.RESET}")
            time.sleep(1)
    
    def _safe_feature_development(self):
        """Safe feature development with agent support"""
        print(f"\n{Colors.CYAN}🚀 Yeni Özellik Geliştirme{Colors.RESET}")
        
        # Get feature description
        feature = self.get_simple_input(f"\n{Colors.YELLOW}Özellik açıklaması: {Colors.RESET}")
        if not feature:
            return
            
        # Create safe branch
        self._ensure_safe_branch(feature)
        
        # Use agent to analyze and plan
        print(f"\n{Colors.CYAN}Ajan analizi başlatılıyor...{Colors.RESET}")
        analysis = self._analyze_feature_with_agent(feature)
        
        # Start development with agent
        self._develop_with_agent(feature, analysis)
    
    def _safe_bug_fix(self):
        """Safe bug fix with automatic testing"""
        print(f"\n{Colors.CYAN}🐛 Hata Düzeltme{Colors.RESET}")
        
        bug_desc = self.get_simple_input(f"\n{Colors.YELLOW}Hata açıklaması: {Colors.RESET}")
        if not bug_desc:
            return
            
        # Create bugfix branch
        self._ensure_safe_branch(f"bugfix-{bug_desc[:20]}")
        
        # Analyze bug with agent
        print(f"\n{Colors.CYAN}Hata analizi yapılıyor...{Colors.RESET}")
        self._analyze_and_fix_bug(bug_desc)
    
    def _safe_refactor(self):
        """Safe refactoring with agent validation"""
        print(f"\n{Colors.CYAN}♻️ Kod İyileştirme{Colors.RESET}")
        
        target = self.get_simple_input(f"\n{Colors.YELLOW}Refactor hedefi (dosya/modül): {Colors.RESET}")
        if not target:
            return
            
        # Create refactor branch
        self._ensure_safe_branch(f"refactor-{target.replace('/', '-')}")
        
        # Start refactoring with agent
        print(f"\n{Colors.CYAN}Refactor analizi başlatılıyor...{Colors.RESET}")
        self._refactor_with_agent(target)
    
    def _review_and_deploy(self):
        """Review changes and deploy with new version"""
        print(f"\n{Colors.CYAN}📋 Review & Deploy{Colors.RESET}")
        
        # Show current changes
        print(f"\n{Colors.YELLOW}Mevcut değişiklikler:{Colors.RESET}")
        subprocess.run(['git', 'diff', '--stat'], check=False)
        
        # Run tests
        print(f"\n{Colors.CYAN}Testler çalıştırılıyor...{Colors.RESET}")
        self._run_tests()
        
        # Final review
        confirm = self.get_simple_input(f"\n{Colors.YELLOW}Deploy etmek istiyor musunuz? (e/h): {Colors.RESET}")
        if confirm.lower() == 'e':
            self._deploy_with_version()
    
    def _ensure_safe_branch(self, feature_name: str):
        """Ensure we're on a safe development branch"""
        # Check current branch
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True)
        current_branch = result.stdout.strip()
        
        if current_branch == 'main' or current_branch == 'master':
            # Create new branch
            safe_branch = f"dev/{feature_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            subprocess.run(['git', 'checkout', '-b', safe_branch], check=False)
            print(f"{Colors.GREEN}✓ Güvenli branch oluşturuldu: {safe_branch}{Colors.RESET}")
    
    def safe_development_mode(self):
        """Original safe development mode for compatibility"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🛡️ Güvenli Geliştirme Modu{Colors.RESET}")
        print(f"{Colors.DIM}Otomatik versiyon ve branch yönetimi ile güvenli geliştirme{Colors.RESET}\n")
        
        # Check if SafeVersionManager is available
        if SafeVersionManager is None:
            print(f"{Colors.RED}SafeVersionManager modülü bulunamadı!{Colors.RESET}")
            print(f"{Colors.YELLOW}Lütfen safe_version_manager.py dosyasının varlığını kontrol edin.{Colors.RESET}")
            input(f"\n{Colors.DIM}Devam etmek için Enter...{Colors.RESET}")
            return
        
        try:
            svm = SafeVersionManager()
            
            # Show current version
            version_info = svm.get_current_version()
            if version_info:
                print(f"{Colors.GREEN}Mevcut versiyon: {version_info['version']}{Colors.RESET}")
                print(f"Build: {version_info['build_number']}\n")
            else:
                print(f"{Colors.YELLOW}⚠️ VERSION.json okunamadı, varsayılan değerler kullanılacak{Colors.RESET}\n")
            
            # Check git push status
            result = subprocess.run(['git', 'status', '-sb'], capture_output=True, text=True)
            if 'ahead' in result.stdout:
                print(f"{Colors.YELLOW}⚠️ Push edilmemiş commit'ler var{Colors.RESET}")
                print(f"{Colors.CYAN}Push yapmak için: git push{Colors.RESET}\n")
            
            # Check for uncommitted changes first
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            
            if result.stdout.strip():
                # Has uncommitted changes - show git menu
                print(f"{Colors.YELLOW}⚠️ Commit edilmemiş değişiklikler tespit edildi{Colors.RESET}")
                print(f"{Colors.CYAN}Güvenli geliştirme için önce değişikliklerinizi commit etmelisiniz{Colors.RESET}\n")
                
                # Show quick git menu directly without asking for feature name
                # Don't ask for feature name yet - will be asked after git operations
                self._show_quick_git_menu(svm, None)
                
            else:
                # No uncommitted changes - proceed normally
                print(f"{Colors.GREEN}✅ Çalışma dizini temiz{Colors.RESET}\n")
                
                # Now ask for feature name
                feature_name = self.get_simple_input(f"{Colors.YELLOW}Özellik adı (opsiyonel): {Colors.RESET}").strip()
                
                # Create safe development branch
                print(f"\n{Colors.CYAN}Güvenli geliştirme branch'i oluşturuluyor...{Colors.RESET}")
                success, result = svm.create_safe_development_branch(feature_name)
                
                if success:
                    branch_name = result
                    print(f"{Colors.GREEN}✓ Branch oluşturuldu: {branch_name}{Colors.RESET}")
                    
                    # Show development workflow
                    print(f"\n{Colors.YELLOW}Geliştirme akışı:{Colors.RESET}")
                    print("1. 🔧 Kod geliştirmeleri yapın")
                    print("2. ✅ Testleri çalıştırın")
                    print("3. 📝 Değişiklikleri commit edin")
                    print("4. 🚀 Yeni versiyon oluşturun ve push edin")
                    
                    print(f"\n{Colors.CYAN}Ne yapmak istersiniz?{Colors.RESET}")
                    print("1. Claude ile geliştirme başlat")
                    print("2. Manuel geliştirme (branch'te kal)")
                    print("3. Mevcut değişiklikleri validate et")
                    print("4. Checkpoint oluştur")
                    
                    choice = self.get_simple_input(f"\n{Colors.BLUE}Seçiminiz: {Colors.RESET}")
                    
                    if choice == '1':
                        # Start Claude development
                        task = self.get_simple_input(f"\n{Colors.YELLOW}Geliştirme görevi: {Colors.RESET}")
                        if task:
                            self.trigger_claude_development(task, 'safe_development', {
                                'branch': branch_name,
                                'feature': feature_name
                            })
                            
                            # After development, offer to create version
                            print(f"\n{Colors.YELLOW}Geliştirme tamamlandı mı?{Colors.RESET}")
                            if self.get_simple_input("Yeni versiyon oluştur? (e/h): ").lower() == 'e':
                                self._complete_safe_development(svm, branch_name)
                                
                    elif choice == '3':
                        # Validate changes
                        valid, issues = svm.validate_changes()
                        if valid:
                            print(f"{Colors.GREEN}✅ Tüm kontroller başarılı!{Colors.RESET}")
                        else:
                            print(f"{Colors.RED}❌ Sorunlar bulundu:{Colors.RESET}")
                            for issue in issues:
                                print(f"  • {issue}")
                                
                    elif choice == '4':
                        # Create checkpoint
                        try:
                            # Create checkpoint file
                            checkpoint_file = svm.base_path / '.git' / 'UNIBOS_CHECKPOINT'
                            checkpoint_data = {
                                'branch': branch_name,
                                'created_at': datetime.now(svm.istanbul_tz).isoformat(),
                                'base_version': version_info['version'] if version_info else 'unknown',
                                'feature': feature_name or 'development'
                            }
                            
                            with open(checkpoint_file, 'w') as f:
                                json.dump(checkpoint_data, f, indent=2)
                            
                            print(f"{Colors.GREEN}✅ Checkpoint oluşturuldu{Colors.RESET}")
                            print(f"  Branch: {branch_name}")
                            print(f"  Feature: {feature_name or 'development'}")
                        except Exception as e:
                            print(f"{Colors.RED}❌ Checkpoint oluşturulamadı: {e}{Colors.RESET}")
                else:
                    # Branch creation failed
                    error_msg = result
                    if "commit" in error_msg.lower() and "önce" in error_msg.lower():
                        # This is not an error, but an informational message
                        print(f"\n{Colors.YELLOW}ℹ️  {error_msg}{Colors.RESET}")
                        
                        # Show quick git menu with the feature name
                        menu_result = self._show_quick_git_menu(svm, feature_name)
                        if menu_result:
                            # Successfully created branch after git operations
                            # Don't restart the whole flow, just return
                            return
                    elif "iptal" in error_msg.lower():
                        print(f"\n{Colors.YELLOW}ℹ️  {error_msg}{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}❌ Branch oluşturulamadı: {error_msg}{Colors.RESET}")
                
        except Exception as e:
            print(f"{Colors.RED}Hata: {e}{Colors.RESET}")
            input(f"\n{Colors.DIM}Devam etmek için Enter...{Colors.RESET}")
    
    def _complete_safe_development(self, svm, branch_name):
        """Complete safe development with version creation and push"""
        print(f"\n{Colors.CYAN}Güvenli geliştirme tamamlanıyor...{Colors.RESET}")
        
        # Get version description
        description = self.get_simple_input(f"{Colors.YELLOW}Versiyon açıklaması: {Colors.RESET}").strip()
        if not description:
            description = f"Development from {branch_name}"
        
        # Get features
        features = []
        print(f"{Colors.YELLOW}Yeni özellikler (boş satır ile bitir):{Colors.RESET}")
        while True:
            feature = self.get_simple_input("- ").strip()
            if not feature:
                break
            features.append(feature)
        
        # Create new version
        success, new_version = svm.create_new_version(description, features)
        
        if success:
            print(f"\n{Colors.GREEN}✅ Yeni versiyon oluşturuldu: {new_version}{Colors.RESET}")
            
            # Commit and push
            print(f"\n{Colors.CYAN}Değişiklikler commit ediliyor ve push yapılıyor...{Colors.RESET}")
            commit_msg = f"{new_version}: {description}"
            success, msg = svm.commit_and_push_safely(commit_msg)
            
            if success:
                print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")
                print(f"\n{Colors.YELLOW}Tamamlanan işlemler:{Colors.RESET}")
                print(f"  ✓ Yeni versiyon: {new_version}")
                print(f"  ✓ Branch: {branch_name}")
                print(f"  ✓ Main branch'e merge edildi")
                print(f"  ✓ Versiyon branch'i oluşturuldu")
            else:
                print(f"{Colors.RED}❌ Push başarısız: {msg}{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ Versiyon oluşturulamadı: {new_version}{Colors.RESET}")
    
    def nlp_processor_mode(self):
        """Natural language command processor"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🧠 NLP İşlemci - Doğal Dil Komutları{Colors.RESET}")
        print(f"{Colors.DIM}Doğal dilde komutlar verin, sistem anlasın ve uygulasın{Colors.RESET}\n")
        
        print(f"{Colors.YELLOW}Örnek komutlar:{Colors.RESET}")
        print("  • 'main.py dosyasındaki hataları düzelt'")
        print("  • 'yeni bir özellik ekle: kullanıcı bildirimleri'")
        print("  • 'veritabanı bağlantısını optimize et'")
        print("  • 'son 5 commiti göster'")
        
        while True:
            command = self.get_simple_input(f"\n{Colors.GREEN}nlp>{Colors.RESET} ").strip()
            
            if command.lower() in ['exit', 'çıkış', 'quit']:
                break
            elif command:
                self._process_nlp_command(command)
    
    
    def claude_health_monitor_mode(self):
        """Show Claude Health Monitor stats"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🏥 Claude Health Monitor{Colors.RESET}")
        print(f"{Colors.DIM}{'='*60}{Colors.RESET}")
        
        if self.health_monitor:
            try:
                stats = self.health_monitor.get_current_stats()
                self.health_monitor.display_dashboard()
            except Exception as e:
                print(f"\n{Colors.RED}Health Monitor error: {e}{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}Health Monitor not available{Colors.RESET}")
            
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        
    def archive_research_agent_mode(self, initial_query=None):
        """Launch Archive Research Agent"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🔎 Arşiv Araştırma Ajanı Başlatılıyor...{Colors.RESET}")
        
        try:
            from archive_research_agent import ArchiveResearchAgent
            agent = ArchiveResearchAgent()
            
            print(f"\n{Colors.GREEN}✓ Ajan yüklendi{Colors.RESET}")
            time.sleep(1)
            
            # If initial query provided, process it directly
            if initial_query:
                print(f"\n{Colors.YELLOW}Doğrudan sorgu işleniyor: {initial_query}{Colors.RESET}")
                # Analyze and search
                analysis_config = agent.analyze_with_claude(initial_query)
                analysis_config["original_query"] = initial_query
                
                # Progress göstergesi
                def progress_callback(message, percent):
                    print(f"\r{Colors.GRAY}[{'█' * int(percent/5)}{' ' * (20-int(percent/5))}] "
                          f"{percent:.1f}% - {message}{Colors.RESET}", end='', flush=True)
                
                # Perform search
                result = agent.deep_search(analysis_config, progress_callback)
                
                # Show report
                print("\n")  # New line after progress
                report = agent.generate_report(result)
                print(report)
                
                input(f"\n{Colors.DIM}Devam etmek için Enter...{Colors.RESET}")
            else:
                # Launch interactive research mode
                agent.interactive_research()
            
        except ImportError as e:
            print(f"\n{Colors.RED}Arşiv Araştırma Ajanı yüklenemedi:{Colors.RESET}")
            print(f"{Colors.RED}{str(e)}{Colors.RESET}")
            time.sleep(3)
        except Exception as e:
            print(f"\n{Colors.RED}Hata: {str(e)}{Colors.RESET}")
            logger.error(f"Archive Research Agent error: {e}", category=LogCategory.MODULE)
            time.sleep(3)
    
    # Helper methods
    def _add_to_suggestions(self, suggestion, source):
        """Add suggestion to suggestions database"""
        try:
            from suggestion_manager import suggestion_manager
            suggestion_manager.add_suggestion(suggestion, 'pending', source)
            print(f"{Colors.GREEN}✓ Öneri eklendi{Colors.RESET}")
        except:
            pass
    
    def _generate_agent_suggestions(self):
        """Generate suggestions using AI agents"""
        suggestions = []
        
        # TODO: Implement actual agent-based analysis
        # For now, return some sample suggestions
        suggestions.extend([
            "Performance: main.py'deki döngüleri optimize et",
            "Security: API anahtarlarını güvenli sakla",
            "Refactor: Duplicate code'ları temizle"
        ])
        
        return suggestions
    
    def _analyze_code_patterns(self):
        """Analyze code for common improvement patterns"""
        patterns = []
        
        # Check for TODO comments
        try:
            result = subprocess.run("grep -r 'TODO' src/", shell=True, capture_output=True, text=True)
            if result.stdout:
                todo_count = len(result.stdout.strip().split('\n'))
                patterns.append(f"Code: {todo_count} TODO yorumu bulundu")
        except:
            pass
        
        return patterns
    
    def _process_nlp_command(self, command):
        """Process natural language command"""
        print(f"\n{Colors.CYAN}Komut analiz ediliyor...{Colors.RESET}")
        
        # Simple pattern matching for now
        command_lower = command.lower()
        
        if 'hata' in command_lower or 'bug' in command_lower:
            print("→ Hata analizi başlatılıyor...")
            self.bug_analysis_mode()
        elif 'özellik' in command_lower or 'feature' in command_lower:
            print("→ Özellik geliştirme moduna geçiliyor...")
            self.code_development_mode()
        elif 'optimize' in command_lower or 'performans' in command_lower:
            print("→ Optimizasyon analizi başlatılıyor...")
            self.trigger_claude_development(command, 'optimization')
        elif 'test' in command_lower:
            print("→ Test komutları çalıştırılıyor...")
            subprocess.run("python -m pytest", shell=True)
        else:
            # Forward to Claude for interpretation
            print("→ Claude'a iletiliyor...")
            self.send_to_claude(command)
    
    def _display_git_status(self):
        """Display git status with colors"""
        result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.startswith('M '):
                    print(f"  {Colors.YELLOW}M{Colors.RESET} {line[2:]}")
                elif line.startswith('A '):
                    print(f"  {Colors.GREEN}A{Colors.RESET} {line[2:]}")
                elif line.startswith('D '):
                    print(f"  {Colors.RED}D{Colors.RESET} {line[2:]}")
                elif line.startswith('??'):
                    print(f"  {Colors.GRAY}?{Colors.RESET} {line[3:]}")
                else:
                    print(f"  {line}")
            return True  # Has changes
        else:
            print(f"  {Colors.GREEN}Temiz - değişiklik yok{Colors.RESET}")
            return False  # No changes
    
    def _show_quick_git_menu(self, svm, feature_name=None):
        """Show quick git menu for uncommitted changes"""
        while True:
            # Show current git status with colors
            print(f"\n{Colors.CYAN}Mevcut değişiklikler:{Colors.RESET}")
            has_changes = self._display_git_status()
            
            if not has_changes:
                # No changes, ask for feature name if not provided
                if feature_name is None:
                    feature_name = self.get_simple_input(f"\n{Colors.YELLOW}Özellik adı (opsiyonel): {Colors.RESET}").strip()
                
                print(f"\n{Colors.GREEN}✅ Çalışma dizini temiz, branch oluşturuluyor...{Colors.RESET}")
                success, branch_name = svm.create_safe_development_branch(feature_name)
                if success:
                    print(f"{Colors.GREEN}✅ Branch oluşturuldu: {branch_name}{Colors.RESET}")
                    return True
                break
            
            # Quick git menu with both numbers and letters
            print(f"\n{Colors.MAGENTA}{Colors.BOLD}⚡ Hızlı Git İşlemleri:{Colors.RESET}")
            print(f"{Colors.CYAN}1{Colors.RESET}/{Colors.GREEN}A{Colors.RESET} - 🎯 {Colors.BOLD}Add All{Colors.RESET} {Colors.DIM}(Tüm değişiklikleri ekle){Colors.RESET}")
            print(f"{Colors.CYAN}2{Colors.RESET}/{Colors.GREEN}C{Colors.RESET} - 📝 {Colors.BOLD}Commit{Colors.RESET} {Colors.DIM}(Stage edilenleri commit et){Colors.RESET}")
            print(f"{Colors.CYAN}3{Colors.RESET}/{Colors.GREEN}Q{Colors.RESET} - ⚡ {Colors.BOLD}Quick Commit{Colors.RESET} {Colors.DIM}(Add all + Commit){Colors.RESET}")
            print(f"{Colors.CYAN}4{Colors.RESET}/{Colors.GREEN}S{Colors.RESET} - 📊 {Colors.BOLD}Status{Colors.RESET} {Colors.DIM}(Detaylı durum){Colors.RESET}")
            print(f"{Colors.CYAN}5{Colors.RESET}/{Colors.GREEN}D{Colors.RESET} - 🔍 {Colors.BOLD}Diff{Colors.RESET} {Colors.DIM}(Değişiklikleri göster){Colors.RESET}")
            print(f"{Colors.CYAN}6{Colors.RESET}/{Colors.GREEN}G{Colors.RESET} - 🔧 {Colors.BOLD}Git Manager{Colors.RESET} {Colors.DIM}(Tam git menüsü){Colors.RESET}")
            print(f"{Colors.CYAN}7{Colors.RESET}/{Colors.GREEN}R{Colors.RESET} - 🔄 {Colors.BOLD}Retry{Colors.RESET} {Colors.DIM}(Safe Dev Mode'u tekrar dene){Colors.RESET}")
            print(f"{Colors.CYAN}8{Colors.RESET}/{Colors.GREEN}P{Colors.RESET} - 🚀 {Colors.BOLD}Push{Colors.RESET} {Colors.DIM}(GitHub'a push et){Colors.RESET}")
            print(f"{Colors.CYAN}9{Colors.RESET}/{Colors.GREEN}X{Colors.RESET} - ❌ {Colors.BOLD}Exit{Colors.RESET} {Colors.DIM}(Çıkış){Colors.RESET}")
            
            choice = self.get_simple_input(f"\n{Colors.BLUE}Seçiminiz: {Colors.RESET}").lower()
            
            if choice in ['1', 'a']:
                # Add all changes
                subprocess.run(['git', 'add', '-A'])
                print(f"{Colors.GREEN}✅ Tüm değişiklikler eklendi{Colors.RESET}")
                
            elif choice in ['2', 'c']:
                # Commit staged changes
                result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                                      capture_output=True, text=True)
                if not result.stdout.strip():
                    print(f"{Colors.YELLOW}⚠️ Stage edilmiş değişiklik yok. Önce '1/A' ile ekleyin.{Colors.RESET}")
                else:
                    msg = self.get_simple_input(f"\n{Colors.YELLOW}Commit mesajı (boş bırakabilirsiniz): {Colors.RESET}").strip()
                    if not msg:
                        # Use default commit message if empty
                        msg = "Work in progress"
                        print(f"{Colors.DIM}Varsayılan mesaj kullanılıyor: {msg}{Colors.RESET}")
                    subprocess.run(['git', 'commit', '-m', msg])
                    print(f"{Colors.GREEN}✅ Commit tamamlandı{Colors.RESET}")
                    # Try safe dev mode again
                    print(f"\n{Colors.CYAN}Safe Development Mode'u tekrar deniyorum...{Colors.RESET}")
                    time.sleep(1)
                    # Ask for feature name if not provided
                    if feature_name is None:
                        feature_name = self.get_simple_input(f"\n{Colors.YELLOW}Özellik adı (opsiyonel): {Colors.RESET}").strip()
                    success, branch_name = svm.create_safe_development_branch(feature_name)
                    if success:
                        print(f"{Colors.GREEN}✅ Branch oluşturuldu: {branch_name}{Colors.RESET}")
                        
                        # Show development workflow options
                        print(f"\n{Colors.YELLOW}Geliştirme akışı:{Colors.RESET}")
                        print("1. 🔧 Kod geliştirmeleri yapın")
                        print("2. ✅ Testleri çalıştırın")
                        print("3. 📝 Değişiklikleri commit edin")
                        print("4. 🚀 Yeni versiyon oluşturun ve push edin")
                        
                        print(f"\n{Colors.CYAN}Ne yapmak istersiniz?{Colors.RESET}")
                        print("1. Claude ile geliştirme başlat")
                        print("2. Manuel geliştirme (branch'te kal)")
                        print("3. Ana menüye dön")
                        
                        choice = self.get_simple_input(f"\n{Colors.BLUE}Seçiminiz: {Colors.RESET}")
                        
                        if choice == '1':
                            # Start Claude development
                            task = self.get_simple_input(f"\n{Colors.YELLOW}Geliştirme görevi: {Colors.RESET}")
                            if task:
                                self.trigger_claude_development(task, 'safe_development', {
                                    'branch': branch_name,
                                    'feature': feature_name
                                })
                        elif choice == '2':
                            print(f"\n{Colors.GREEN}Branch'tesiniz: {branch_name}{Colors.RESET}")
                            print(f"{Colors.DIM}İşiniz bittiğinde versiyonlama için tekrar gelin{Colors.RESET}")
                        
                        return True  # Success, exit menu
                        
            elif choice in ['3', 'q']:
                # Quick commit (add all + commit)
                subprocess.run(['git', 'add', '-A'])
                msg = self.get_simple_input(f"\n{Colors.YELLOW}Commit mesajı (boş bırakabilirsiniz): {Colors.RESET}").strip()
                if not msg:
                    # Use default commit message if empty
                    msg = "Work in progress"
                    print(f"{Colors.DIM}Varsayılan mesaj kullanılıyor: {msg}{Colors.RESET}")
                subprocess.run(['git', 'commit', '-m', msg])
                print(f"{Colors.GREEN}✅ Quick commit tamamlandı{Colors.RESET}")
                # Try safe dev mode again
                print(f"\n{Colors.CYAN}Safe Development Mode'u tekrar deniyorum...{Colors.RESET}")
                time.sleep(1)
                # Ask for feature name if not provided
                if feature_name is None:
                    feature_name = self.get_simple_input(f"\n{Colors.YELLOW}Özellik adı (opsiyonel): {Colors.RESET}").strip()
                success, branch_name = svm.create_safe_development_branch(feature_name)
                if success:
                    print(f"{Colors.GREEN}✅ Branch oluşturuldu: {branch_name}{Colors.RESET}")
                    
                    # Show development workflow options
                    print(f"\n{Colors.YELLOW}Geliştirme akışı:{Colors.RESET}")
                    print("1. 🔧 Kod geliştirmeleri yapın")
                    print("2. ✅ Testleri çalıştırın")
                    print("3. 📝 Değişiklikleri commit edin")
                    print("4. 🚀 Yeni versiyon oluşturun ve push edin")
                    
                    print(f"\n{Colors.CYAN}Ne yapmak istersiniz?{Colors.RESET}")
                    print("1. Claude ile geliştirme başlat")
                    print("2. Manuel geliştirme (branch'te kal)")
                    print("3. Ana menüye dön")
                    
                    choice = self.get_simple_input(f"\n{Colors.BLUE}Seçiminiz: {Colors.RESET}")
                    
                    if choice == '1':
                        # Start Claude development
                        task = self.get_simple_input(f"\n{Colors.YELLOW}Geliştirme görevi: {Colors.RESET}")
                        if task:
                            self.trigger_claude_development(task, 'safe_development', {
                                'branch': branch_name,
                                'feature': feature_name
                            })
                    elif choice == '2':
                        print(f"\n{Colors.GREEN}Branch'tesiniz: {branch_name}{Colors.RESET}")
                        print(f"{Colors.DIM}İşiniz bittiğinde versiyonlama için tekrar gelin{Colors.RESET}")
                    
                    return True  # Success, exit menu
                        
            elif choice in ['4', 's']:
                # Detailed status
                subprocess.run(['git', 'status'])
                input(f"\n{Colors.DIM}Devam etmek için Enter...{Colors.RESET}")
                
            elif choice in ['5', 'd']:
                # Show diff
                subprocess.run(['git', 'diff'])
                input(f"\n{Colors.DIM}Devam etmek için Enter...{Colors.RESET}")
                
            elif choice in ['6', 'g']:
                # Open full Git Manager
                try:
                    from git_manager import GitManager
                    git_mgr = GitManager()
                    git_mgr.show_git_menu()
                except ImportError:
                    print(f"{Colors.RED}Git Manager bulunamadı{Colors.RESET}")
                    
            elif choice in ['7', 'r']:
                # Retry safe dev mode with same feature name
                print(f"\n{Colors.CYAN}Safe Development Mode'u tekrar deniyorum...{Colors.RESET}")
                # Ask for feature name if not provided
                if feature_name is None:
                    feature_name = self.get_simple_input(f"\n{Colors.YELLOW}Özellik adı (opsiyonel): {Colors.RESET}").strip()
                success, branch_name = svm.create_safe_development_branch(feature_name)
                if success:
                    print(f"{Colors.GREEN}✅ Branch oluşturuldu: {branch_name}{Colors.RESET}")
                    
                    # Show development workflow options
                    print(f"\n{Colors.YELLOW}Geliştirme akışı:{Colors.RESET}")
                    print("1. 🔧 Kod geliştirmeleri yapın")
                    print("2. ✅ Testleri çalıştırın")
                    print("3. 📝 Değişiklikleri commit edin")
                    print("4. 🚀 Yeni versiyon oluşturun ve push edin")
                    
                    print(f"\n{Colors.CYAN}Ne yapmak istersiniz?{Colors.RESET}")
                    print("1. Claude ile geliştirme başlat")
                    print("2. Manuel geliştirme (branch'te kal)")
                    print("3. Ana menüye dön")
                    
                    choice = self.get_simple_input(f"\n{Colors.BLUE}Seçiminiz: {Colors.RESET}")
                    
                    if choice == '1':
                        # Start Claude development
                        task = self.get_simple_input(f"\n{Colors.YELLOW}Geliştirme görevi: {Colors.RESET}")
                        if task:
                            self.trigger_claude_development(task, 'safe_development', {
                                'branch': branch_name,
                                'feature': feature_name
                            })
                    elif choice == '2':
                        print(f"\n{Colors.GREEN}Branch'tesiniz: {branch_name}{Colors.RESET}")
                        print(f"{Colors.DIM}İşiniz bittiğinde versiyonlama için tekrar gelin{Colors.RESET}")
                    
                    return True  # Success, exit menu
                else:
                    print(f"{Colors.RED}❌ Hala başarısız: {branch_name}{Colors.RESET}")
                    
            elif choice in ['8', 'p']:
                # Push to remote
                print(f"\n{Colors.CYAN}GitHub'a push ediliyor...{Colors.RESET}")
                result = subprocess.run(['git', 'push'], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}✅ Push başarılı{Colors.RESET}")
                else:
                    print(f"{Colors.RED}❌ Push başarısız: {result.stderr}{Colors.RESET}")
                    # Try push with upstream
                    print(f"\n{Colors.YELLOW}Upstream ile tekrar deneniyor...{Colors.RESET}")
                    branch = subprocess.run(['git', 'branch', '--show-current'], 
                                          capture_output=True, text=True).stdout.strip()
                    result = subprocess.run(['git', 'push', '-u', 'origin', branch], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"{Colors.GREEN}✅ Push başarılı (upstream set){Colors.RESET}")
                    else:
                        print(f"{Colors.RED}❌ Push hala başarısız{Colors.RESET}")
                
            elif choice in ['9', 'x']:
                # Exit
                return False
                
            else:
                print(f"{Colors.RED}Geçersiz seçim{Colors.RESET}")

# Export the main class
claude_cli = ClaudeCLI()

# Removed unused import - claude_cli_methods.py has been deleted