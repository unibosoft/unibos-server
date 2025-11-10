#!/usr/bin/env python3
"""
UNIBOS Claude Agent System
Mevcut claude_cli.py ile entegre çalışan çoklu ajan sistemi
"""

import os
import sys
import json
import subprocess
import tempfile
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path

# UNIBOS logger entegrasyonu
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

# Colors from main.py
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
    ORANGE = "\033[38;5;208m"
    BG_ORANGE = "\033[48;5;208m"
    BG_CONTENT = "\033[48;5;236m"

# Agent rolleri
class AgentRole(Enum):
    ORCHESTRATOR = "orchestrator"
    CODE_ANALYST = "code_analyst"
    REFACTOR_SPECIALIST = "refactor_specialist"
    UI_IMPROVER = "ui_improver"
    PERFORMANCE_OPTIMIZER = "performance_optimizer"
    SECURITY_AUDITOR = "security_auditor"
    TEST_ENGINEER = "test_engineer"
    DOCUMENTATION_EXPERT = "documentation_expert"
    INTEGRATION_SPECIALIST = "integration_specialist"
    CLAUDE_ENHANCER = "claude_enhancer"

@dataclass
class AgentCapability:
    """Ajan yetenekleri"""
    role: AgentRole
    name: str
    description: str
    specialties: List[str]
    can_modify_files: bool = True
    requires_confirmation: bool = True

@dataclass
class CodeContext:
    """Kod analiz bağlamı"""
    files_analyzed: Dict[str, str] = field(default_factory=dict)
    module_structure: Dict[str, List[str]] = field(default_factory=dict)
    improvement_areas: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    current_version: str = ""
    screenshot_context: Dict[str, Any] = field(default_factory=dict)

class UNIBOSAgent:
    """Temel ajan sınıfı"""
    
    def __init__(self, role: AgentRole, capability: AgentCapability):
        self.role = role
        self.capability = capability
        self.base_path = Path("/Users/berkhatirli/Desktop/unibos")
        self.context = CodeContext()
        self.claude_files = self._load_claude_files()
        
        # KRITIK: Her ajan başladığında screenshot kontrolü yap
        self._check_and_archive_screenshots()
        
    def _load_claude_files(self) -> Dict[str, str]:
        """CLAUDE dosyalarını yükle"""
        claude_files = {}
        patterns = ["CLAUDE*.md", "README.md", "LLM_COMPREHENSIVE_GUIDE.md"]
        
        for pattern in patterns:
            for file_path in self.base_path.glob(pattern):
                try:
                    claude_files[file_path.name] = file_path.read_text(encoding='utf-8')
                except Exception as e:
                    logger.warning(f"Could not load {file_path}: {e}")
        
        return claude_files
    
    def _check_and_archive_screenshots(self):
        """KRITIK: Screenshot kontrolü ve arşivleme - HER ZAMAN YAPILMALI"""
        try:
            from screenshot_manager import screenshot_manager
            
            logger.info(f"{self.capability.name} checking for screenshots...", 
                       category=LogCategory.SYSTEM)
            
            count, archived = screenshot_manager.check_and_archive_all()
            
            if count > 0:
                logger.success(f"{self.capability.name} archived {count} screenshots", 
                              category=LogCategory.SYSTEM)
                
                # Context'e ekle
                self.context.screenshot_context['auto_archived'] = count
                self.context.screenshot_context['archived_files'] = [str(p) for p in archived]
                
                # İyileştirme önerisi ekle
                self.context.improvement_areas.insert(0, 
                    f"CRITICAL: {count} screenshots were found and archived. " +
                    "Always check for screenshots at the start of every session!")
                    
        except Exception as e:
            logger.error(f"Screenshot check failed: {e}", category=LogCategory.SYSTEM)
            # Hata olsa bile devam et ama uyar
            self.context.improvement_areas.insert(0,
                "WARNING: Screenshot check failed! Manual check required.")
    
    def analyze_codebase(self, target_module: Optional[str] = None) -> CodeContext:
        """Kod tabanını analiz et"""
        logger.info(f"{self.capability.name} analyzing codebase...")
        
        # Screenshot analizi yap
        self._analyze_screenshots()
        
        # Versiyon bilgisini al
        try:
            version_file = self.base_path / "src" / "VERSION.json"
            if version_file.exists():
                with open(version_file, 'r') as f:
                    version_data = json.load(f)
                    self.context.current_version = version_data.get('version', 'unknown')
        except:
            self.context.current_version = 'unknown'
        
        # Modül yapısını analiz et
        if target_module:
            self._analyze_specific_module(target_module)
        else:
            self._analyze_full_structure()
        
        return self.context
    
    def _analyze_specific_module(self, module_name: str):
        """Belirli bir modülü analiz et"""
        module_paths = {
            'claude': ['src/claude_cli.py', 'src/claude_tool_v2.py', 'src/claude_conversation.py'],
            'main': ['src/main.py'],
            'currencies': ['src/currencies_enhanced.py', 'projects/currencies/'],
            'recaria': ['projects/recaria/'],
            'birlikteyiz': ['projects/birlikteyiz/'],
            'git': ['src/git_manager.py']
        }
        
        paths = module_paths.get(module_name, [])
        for path_str in paths:
            path = self.base_path / path_str
            if path.exists():
                if path.is_file():
                    self.context.files_analyzed[str(path)] = self._analyze_file(path)
                elif path.is_dir():
                    for py_file in path.rglob("*.py"):
                        self.context.files_analyzed[str(py_file)] = self._analyze_file(py_file)
    
    def _analyze_file(self, file_path: Path) -> str:
        """Dosyayı analiz et"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Basit analiz - import'ları bul
            imports = []
            for line in content.split('\n'):
                if line.strip().startswith(('import ', 'from ')):
                    imports.append(line.strip())
            
            # Dependencies'e ekle
            self.context.dependencies[str(file_path)] = imports
            
            # İyileştirme alanlarını tespit et
            if 'TODO' in content or 'FIXME' in content:
                self.context.improvement_areas.append(f"{file_path}: Contains TODO/FIXME")
            
            if len(content.split('\n')) > 500:
                self.context.improvement_areas.append(f"{file_path}: Large file (>500 lines)")
            
            return content[:1000]  # İlk 1000 karakter
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return ""
    
    def _analyze_full_structure(self):
        """Tüm proje yapısını analiz et"""
        # src/ dizini
        src_path = self.base_path / "src"
        if src_path.exists():
            for py_file in src_path.glob("*.py"):
                self.context.files_analyzed[str(py_file)] = self._analyze_file(py_file)
        
        # projects/ dizini
        projects_path = self.base_path / "projects"
        if projects_path.exists():
            for module_dir in projects_path.iterdir():
                if module_dir.is_dir():
                    module_files = []
                    for py_file in module_dir.rglob("*.py"):
                        module_files.append(str(py_file.relative_to(self.base_path)))
                    self.context.module_structure[module_dir.name] = module_files
    
    def _analyze_screenshots(self):
        """Screenshot'ları detaylı analiz et"""
        logger.info(f"{self.capability.name} analyzing screenshots...")
        
        # Screenshot manager'ı import et
        try:
            from screenshot_manager import screenshot_manager
            
            # Ana dizindeki screenshot'ları kontrol et
            screenshots = list(self.base_path.glob("*.png")) + list(self.base_path.glob("*.jpg"))
            screenshots.extend(list(self.base_path.glob("*.jpeg")) + list(self.base_path.glob("*.PNG")))
            screenshots.extend(list(self.base_path.glob("*.JPG")) + list(self.base_path.glob("*.JPEG")))
            
            if screenshots:
                self.context.screenshot_context['found_screenshots'] = []
                self.context.screenshot_context['analysis_time'] = datetime.now().isoformat()
                
                for ss in screenshots:
                    # Her screenshot'ı analiz et
                    analysis = {
                        'path': str(ss),
                        'name': ss.name,
                        'size': ss.stat().st_size,
                        'modified': datetime.fromtimestamp(ss.stat().st_mtime).isoformat(),
                        'content_analysis': self._analyze_screenshot_content(ss)
                    }
                    self.context.screenshot_context['found_screenshots'].append(analysis)
                    
                    # İyileştirme alanına ekle
                    self.context.improvement_areas.append(
                        f"Screenshot found: {ss.name} - Should be archived"
                    )
                
                # Arşivle
                logger.info(f"Archiving {len(screenshots)} screenshots...")
                count, archived = screenshot_manager.check_and_archive_all()
                self.context.screenshot_context['archived_count'] = count
                self.context.screenshot_context['archived_paths'] = [str(p) for p in archived]
            else:
                self.context.screenshot_context['message'] = "No screenshots found in main directory"
                
        except Exception as e:
            logger.error(f"Screenshot analysis error: {e}")
            self.context.screenshot_context['error'] = str(e)
    
    def _analyze_screenshot_content(self, screenshot_path: Path) -> Dict[str, Any]:
        """Screenshot içeriğini analiz et"""
        try:
            # Dosya adından bilgi çıkar
            name = screenshot_path.name.lower()
            content_hints = []
            
            # Pattern matching
            if 'error' in name or 'hata' in name:
                content_hints.append('error_screenshot')
            if 'menu' in name or 'menü' in name:
                content_hints.append('menu_screenshot')
            if 'bug' in name:
                content_hints.append('bug_report')
            if 'feature' in name or 'özellik' in name:
                content_hints.append('feature_request')
            if 'ui' in name or 'interface' in name:
                content_hints.append('ui_element')
            if 'code' in name or 'kod' in name:
                content_hints.append('code_snippet')
            
            # Tarih bilgisi varsa çıkar
            date_pattern = r'(\d{4}[_-]?\d{2}[_-]?\d{2}|\d{2}[_-]?\d{2}[_-]?\d{4})'
            date_match = re.search(date_pattern, name)
            if date_match:
                content_hints.append(f'dated_{date_match.group()}')
            
            return {
                'content_hints': content_hints,
                'requires_manual_review': True,
                'priority': 'high' if any(h in ['error_screenshot', 'bug_report'] for h in content_hints) else 'normal'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_improvement_plan(self) -> List[Dict[str, Any]]:
        """İyileştirme planı oluştur - Adım adım yaklaşım"""
        improvements = []
        
        # Screenshot bazlı iyileştirmeler öncelikli
        if self.context.screenshot_context.get('found_screenshots'):
            improvements.append({
                'step': 1,
                'category': 'screenshot_management',
                'priority': 'critical',
                'action': 'Archive screenshots immediately',
                'details': f"Found {len(self.context.screenshot_context['found_screenshots'])} screenshots that need archiving",
                'implementation': 'Use screenshot_manager.check_and_archive_all()'
            })
        
        # Role göre özel iyileştirmeler
        if self.role == AgentRole.CODE_ANALYST:
            improvements.extend(self._analyze_code_quality_stepwise())
        elif self.role == AgentRole.UI_IMPROVER:
            improvements.extend(self._analyze_ui_improvements_stepwise())
        elif self.role == AgentRole.PERFORMANCE_OPTIMIZER:
            improvements.extend(self._analyze_performance_stepwise())
        elif self.role == AgentRole.SECURITY_AUDITOR:
            improvements.extend(self._analyze_security_stepwise())
        elif self.role == AgentRole.CLAUDE_ENHANCER:
            improvements.extend(self._analyze_claude_enhancements_stepwise())
        
        # Adımları sırala
        improvements.sort(key=lambda x: (x.get('priority', 'normal') != 'critical', x.get('step', 999)))
        
        return improvements
    
    def _analyze_code_quality_stepwise(self) -> List[Dict[str, Any]]:
        """Kod kalitesi analizi - Adım adım"""
        issues = []
        step_counter = 2  # 1 screenshot için ayrıldı
        
        # Adım 1: Kritik güvenlik sorunları
        for file_path, content in self.context.files_analyzed.items():
            if 'eval(' in content or 'exec(' in content:
                issues.append({
                    'step': step_counter,
                    'category': 'security',
                    'file': file_path,
                    'issue': 'Dangerous eval/exec usage',
                    'severity': 'critical',
                    'priority': 'critical',
                    'suggestion': 'Replace with safer alternatives',
                    'implementation_steps': [
                        '1. Identify the exact usage context',
                        '2. Replace eval() with ast.literal_eval() for literals',
                        '3. Use getattr() for dynamic attribute access',
                        '4. Implement proper input validation'
                    ]
                })
                step_counter += 1
        
        # Adım 2: Exception handling
        for file_path, content in self.context.files_analyzed.items():
            if 'except:' in content:
                issues.append({
                    'step': step_counter,
                    'category': 'error_handling',
                    'file': file_path,
                    'issue': 'Bare except clause found',
                    'severity': 'medium',
                    'priority': 'high',
                    'suggestion': 'Use specific exception types',
                    'implementation_steps': [
                        '1. Analyze what exceptions can occur',
                        '2. Replace with specific exceptions (e.g., ValueError, IOError)',
                        '3. Add proper logging for exceptions',
                        '4. Ensure critical errors are re-raised'
                    ]
                })
                step_counter += 1
        
        # Adım 3: TODO/FIXME items
        for area in self.context.improvement_areas:
            if 'TODO' in area or 'FIXME' in area:
                issues.append({
                    'step': step_counter,
                    'category': 'technical_debt',
                    'issue': area,
                    'severity': 'low',
                    'priority': 'normal',
                    'suggestion': 'Address TODO/FIXME items',
                    'implementation_steps': [
                        '1. Review the TODO/FIXME context',
                        '2. Prioritize based on impact',
                        '3. Implement solution',
                        '4. Test thoroughly'
                    ]
                })
                step_counter += 1
        
        return issues
    
    def _analyze_ui_improvements_stepwise(self) -> List[Dict[str, Any]]:
        """UI iyileştirmeleri - Adım adım"""
        improvements = []
        step_counter = 2
        
        # Screenshot'lardan UI ipuçları
        if self.context.screenshot_context.get('found_screenshots'):
            ui_screenshots = [ss for ss in self.context.screenshot_context['found_screenshots'] 
                            if any(hint in ss.get('content_analysis', {}).get('content_hints', []) 
                                  for hint in ['menu_screenshot', 'ui_element'])]
            
            if ui_screenshots:
                improvements.append({
                    'step': step_counter,
                    'category': 'ui_analysis',
                    'priority': 'high',
                    'issue': f'Found {len(ui_screenshots)} UI-related screenshots',
                    'suggestion': 'Analyze screenshots for UI improvement opportunities',
                    'implementation_steps': [
                        '1. Review each UI screenshot',
                        '2. Identify usability issues',
                        '3. Document improvement suggestions',
                        '4. Prioritize based on user impact'
                    ],
                    'related_files': [ss['name'] for ss in ui_screenshots]
                })
                step_counter += 1
        
        # main.py UI kontrolleri
        main_file = str(self.base_path / "src" / "main.py")
        if main_file in self.context.files_analyzed:
            content = self.context.files_analyzed[main_file]
            
            # Renk tutarlılığı
            if 'Colors.' in content:
                improvements.append({
                    'step': step_counter,
                    'category': 'ui_consistency',
                    'area': 'Color consistency',
                    'suggestion': 'Ensure all UI elements use consistent color scheme',
                    'priority': 'medium',
                    'implementation_steps': [
                        '1. Audit all color usage in the codebase',
                        '2. Create a color palette mapping',
                        '3. Replace hardcoded colors with palette references',
                        '4. Test visual consistency across all menus'
                    ]
                })
                step_counter += 1
            
            # Menu navigasyonu
            if 'menu' in content.lower():
                improvements.append({
                    'step': step_counter,
                    'category': 'ui_navigation',
                    'area': 'Menu navigation',
                    'suggestion': 'Improve menu navigation experience',
                    'priority': 'high',
                    'implementation_steps': [
                        '1. Add keyboard shortcuts for common actions',
                        '2. Implement breadcrumb navigation',
                        '3. Add menu state persistence',
                        '4. Improve menu transition animations'
                    ]
                })
                step_counter += 1
        
        return improvements
    
    def _analyze_performance_stepwise(self) -> List[Dict[str, Any]]:
        """Performans analizi - Adım adım"""
        issues = []
        step_counter = 2
        
        # Import optimizasyonu
        for file_path, imports in self.context.dependencies.items():
            import_count = len([i for i in imports if i.startswith('import') or i.startswith('from')])
            if import_count > 20:
                issues.append({
                    'step': step_counter,
                    'category': 'import_optimization',
                    'file': file_path,
                    'issue': f'Too many imports ({import_count})',
                    'severity': 'medium',
                    'priority': 'medium',
                    'suggestion': 'Optimize imports for better startup performance',
                    'implementation_steps': [
                        '1. Identify unused imports with pylint/flake8',
                        '2. Group related imports',
                        '3. Implement lazy imports for heavy modules',
                        '4. Consider splitting large modules'
                    ],
                    'metrics': {
                        'current_imports': import_count,
                        'target_imports': 15
                    }
                })
                step_counter += 1
        
        # Büyük dosya analizi
        for file_path, content in self.context.files_analyzed.items():
            file_size = len(content)
            if file_size > 500 * 80:  # ~500 satır * 80 karakter
                issues.append({
                    'step': step_counter,
                    'category': 'file_size_optimization',
                    'file': file_path,
                    'issue': f'Large file detected ({file_size} chars)',
                    'severity': 'low',
                    'priority': 'normal',
                    'suggestion': 'Consider splitting into smaller modules',
                    'implementation_steps': [
                        '1. Identify logical boundaries in the code',
                        '2. Extract related functions into separate modules',
                        '3. Create proper module hierarchy',
                        '4. Update imports across the codebase'
                    ]
                })
                step_counter += 1
        
        return issues
    
    def _analyze_security_stepwise(self) -> List[Dict[str, Any]]:
        """Güvenlik analizi - Adım adım"""
        vulnerabilities = []
        step_counter = 2
        
        for file_path, content in self.context.files_analyzed.items():
            # Shell injection riski
            if 'shell=True' in content:
                vulnerabilities.append({
                    'step': step_counter,
                    'category': 'security_vulnerability',
                    'file': file_path,
                    'vulnerability': 'Shell injection risk',
                    'risk': 'critical',
                    'priority': 'critical',
                    'suggestion': 'Remove shell=True from subprocess calls',
                    'implementation_steps': [
                        '1. Locate all subprocess calls with shell=True',
                        '2. Convert command strings to argument lists',
                        '3. Use shlex.split() for complex commands',
                        '4. Test all modified subprocess calls'
                    ],
                    'example_fix': 'subprocess.run(["ls", "-la"], capture_output=True)'
                })
                step_counter += 1
            
            # Pickle güvenlik riski
            if 'pickle.' in content:
                vulnerabilities.append({
                    'step': step_counter,
                    'category': 'security_vulnerability',
                    'file': file_path,
                    'vulnerability': 'Pickle usage detected',
                    'risk': 'high',
                    'priority': 'high',
                    'suggestion': 'Replace pickle with JSON for serialization',
                    'implementation_steps': [
                        '1. Identify what data is being pickled',
                        '2. Convert data structures to JSON-compatible format',
                        '3. Replace pickle.dump/load with json.dump/load',
                        '4. Add data validation for deserialized content'
                    ]
                })
                step_counter += 1
            
            # Hassas bilgi kontrolü
            sensitive_patterns = ['password', 'api_key', 'secret', 'token']
            for pattern in sensitive_patterns:
                if pattern in content.lower():
                    vulnerabilities.append({
                        'step': step_counter,
                        'category': 'sensitive_data',
                        'file': file_path,
                        'vulnerability': f'Potential sensitive data: {pattern}',
                        'risk': 'medium',
                        'priority': 'high',
                        'suggestion': 'Ensure sensitive data is properly handled',
                        'implementation_steps': [
                            '1. Check if sensitive data is hardcoded',
                            '2. Move to environment variables or secure config',
                            '3. Add proper encryption if needed',
                            '4. Implement secure key management'
                        ]
                    })
                    step_counter += 1
                    break
        
        return vulnerabilities
    
    def _analyze_claude_enhancements_stepwise(self) -> List[Dict[str, Any]]:
        """Claude entegrasyon iyileştirmeleri - Adım adım"""
        enhancements = []
        step_counter = 2
        
        # Screenshot context kullanımı
        enhancements.append({
            'step': step_counter,
            'category': 'claude_integration',
            'feature': 'Screenshot Context Enhancement',
            'priority': 'high',
            'suggestion': 'Improve screenshot context usage in Claude prompts',
            'implementation_steps': [
                '1. Extract meaningful context from screenshots',
                '2. Include screenshot analysis in prompts',
                '3. Track screenshot-driven improvements',
                '4. Build screenshot-to-action mapping'
            ]
        })
        step_counter += 1
        
        # Agent koordinasyonu
        enhancements.append({
            'step': step_counter,
            'category': 'agent_coordination',
            'feature': 'Multi-Agent Task Distribution',
            'priority': 'medium',
            'suggestion': 'Implement intelligent task distribution among agents',
            'implementation_steps': [
                '1. Analyze task complexity and agent capabilities',
                '2. Create task-to-agent mapping logic',
                '3. Implement parallel agent execution',
                '4. Add result aggregation mechanism'
            ]
        })
        step_counter += 1
        
        # Prompt engineering
        enhancements.append({
            'step': step_counter,
            'category': 'prompt_optimization',
            'feature': 'Dynamic Prompt Generation',
            'priority': 'medium',
            'suggestion': 'Create context-aware dynamic prompts',
            'implementation_steps': [
                '1. Build prompt templates for different scenarios',
                '2. Include relevant code context automatically',
                '3. Add success metrics to prompts',
                '4. Implement prompt effectiveness tracking'
            ]
        })
        
        return enhancements

class UNIBOSAgentOrchestrator:
    """Agent koordinatörü - Claude CLI ile entegre"""
    
    def __init__(self, claude_cli):
        self.claude_cli = claude_cli
        self.agents = self._initialize_agents()
        self.capabilities = self._define_capabilities()
        
    def _define_capabilities(self) -> Dict[AgentRole, AgentCapability]:
        """Agent yeteneklerini tanımla"""
        return {
            AgentRole.CODE_ANALYST: AgentCapability(
                role=AgentRole.CODE_ANALYST,
                name="Code Analyst",
                description="Kod kalitesi ve yapı analizi",
                specialties=["code quality", "structure analysis", "dependency mapping"]
            ),
            AgentRole.REFACTOR_SPECIALIST: AgentCapability(
                role=AgentRole.REFACTOR_SPECIALIST,
                name="Refactor Specialist",
                description="Kod yeniden yapılandırma",
                specialties=["refactoring", "clean code", "design patterns"]
            ),
            AgentRole.UI_IMPROVER: AgentCapability(
                role=AgentRole.UI_IMPROVER,
                name="UI Improver",
                description="Terminal UI/UX iyileştirmeleri",
                specialties=["terminal ui", "user experience", "navigation"]
            ),
            AgentRole.PERFORMANCE_OPTIMIZER: AgentCapability(
                role=AgentRole.PERFORMANCE_OPTIMIZER,
                name="Performance Optimizer",
                description="Performans optimizasyonu",
                specialties=["optimization", "caching", "async operations"]
            ),
            AgentRole.SECURITY_AUDITOR: AgentCapability(
                role=AgentRole.SECURITY_AUDITOR,
                name="Security Auditor",
                description="Güvenlik denetimi",
                specialties=["security", "vulnerability scanning", "best practices"]
            ),
            AgentRole.CLAUDE_ENHANCER: AgentCapability(
                role=AgentRole.CLAUDE_ENHANCER,
                name="Claude Enhancer",
                description="Claude entegrasyonu iyileştirme",
                specialties=["claude integration", "ai features", "prompt engineering"]
            )
        }
    
    def _initialize_agents(self) -> Dict[AgentRole, UNIBOSAgent]:
        """Ajanları başlat"""
        agents = {}
        for role, capability in self._define_capabilities().items():
            agents[role] = UNIBOSAgent(role, capability)
        return agents
    
    def analyze_module(self, module_name: str) -> Dict[str, Any]:
        """Belirli bir modülü analiz et"""
        logger.info(f"Analyzing module: {module_name}")
        
        results = {
            'module': module_name,
            'timestamp': datetime.now().isoformat(),
            'analyses': {},
            'recommendations': []
        }
        
        # Her ajan modülü analiz etsin
        for role, agent in self.agents.items():
            if role in [AgentRole.CODE_ANALYST, AgentRole.UI_IMPROVER, AgentRole.PERFORMANCE_OPTIMIZER]:
                context = agent.analyze_codebase(module_name)
                improvements = agent.generate_improvement_plan()
                
                results['analyses'][role.value] = {
                    'files_analyzed': len(context.files_analyzed),
                    'issues_found': len(improvements),
                    'improvements': improvements
                }
        
        return results
    
    def process_natural_language_command(self, user_command: str) -> Dict[str, Any]:
        """Doğal dil komutunu işle ve uygun ajanları çalıştır"""
        logger.info(f"Processing NL command: {user_command}")
        
        result = {
            'command': user_command,
            'understanding': {},
            'actions': [],
            'results': {}
        }
        
        # Komut analizi için CODE_ANALYST'i kullan
        analyst = self.agents.get(AgentRole.CODE_ANALYST)
        if analyst:
            # Basit pattern matching ile intent çıkar
            if any(word in user_command.lower() for word in ['ara', 'tara', 'search', 'find']):
                if any(word in user_command.lower() for word in ['eski', 'önceki', 'versiyon', 'previous']):
                    result['understanding'] = {
                        'intent': 'search_in_versions',
                        'target': self._extract_target(user_command)
                    }
                    result['actions'].append({
                        'type': 'scan_feature',
                        'description': 'Eski versiyonlarda özellik tarama'
                    })
        
        return result
    
    def _extract_target(self, text: str) -> str:
        """Metinden hedef özelliği çıkar"""
        # Basit extraction - geliştirilmeli
        if 'kişisel enflasyon' in text.lower():
            return 'kişisel enflasyon'
        if 'personal inflation' in text.lower():
            return 'personal inflation'
        
        # İlk anlamlı kelimeyi döndür
        words = text.split()
        for word in words:
            if len(word) > 3 and word not in ['için', 'eski', 'yeni', 'versiyonlarda']:
                return word
        return text
    
    def generate_enhancement_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """Claude için iyileştirme promptu oluştur"""
        prompt = f"""UNIBOS Module Enhancement Request

Module: {analysis_results['module']}
Version: {self.agents[AgentRole.CODE_ANALYST].context.current_version}

## Analysis Results:
"""
        
        for agent_role, data in analysis_results['analyses'].items():
            prompt += f"\n### {agent_role.replace('_', ' ').title()}:\n"
            prompt += f"Files analyzed: {data['files_analyzed']}\n"
            prompt += f"Issues found: {data['issues_found']}\n"
            
            if data['improvements']:
                prompt += "\nKey findings:\n"
                for imp in data['improvements'][:5]:  # İlk 5 öneri
                    prompt += f"- {imp}\n"
        
        prompt += """
## Task:
Please provide code improvements for the identified issues. Use the following format:

```FILE: path/to/file.py
Complete improved file content...
```

Focus on:
1. Maintaining backward compatibility
2. Following UNIBOS coding standards
3. Improving without breaking existing functionality
4. Adding proper error handling and logging
"""
        
        return prompt
    
    def generate_detailed_enhancement_prompt(self, analysis_results: Dict[str, Any], 
                                           all_improvements: List[Dict[str, Any]]) -> str:
        """Detaylı geliştirme promptu oluştur"""
        prompt = f"""UNIBOS Agent-Driven Enhancement

Module: {analysis_results['module']}
Version: {self.agents[AgentRole.CODE_ANALYST].context.current_version}
Total Improvements: {len(all_improvements)}

## Prioritized Improvements:
"""
        
        # Priority'ye göre grupla
        by_priority = {}
        for imp in all_improvements:
            priority = imp.get('priority', 'normal') if isinstance(imp, dict) else 'normal'
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(imp)
        
        # Priority sırasına göre yazdır
        for priority in ['critical', 'high', 'medium', 'normal', 'low']:
            if priority in by_priority and by_priority[priority]:
                prompt += f"\n### {priority.upper()} Priority ({len(by_priority[priority])} items):\n"
                for imp in by_priority[priority][:3]:  # Her priority'den max 3
                    if isinstance(imp, dict):
                        prompt += f"\n- **{imp.get('suggestion', 'Improvement')}**"
                        if 'file' in imp:
                            prompt += f"\n  - File: `{imp['file']}`"
                        if 'category' in imp:
                            prompt += f"\n  - Category: {imp['category']}"
                        if 'implementation_steps' in imp:
                            prompt += "\n  - Implementation:"
                            for step in imp['implementation_steps']:
                                prompt += f"\n    {step}"
                    else:
                        prompt += f"\n- {imp}"
                prompt += "\n"
        
        # Screenshot context varsa ekle
        if hasattr(self.agents[AgentRole.CODE_ANALYST], 'context') and \
           self.agents[AgentRole.CODE_ANALYST].context.screenshot_context.get('found_screenshots'):
            prompt += "\n## Screenshot Context:\n"
            ss_context = self.agents[AgentRole.CODE_ANALYST].context.screenshot_context
            prompt += f"Found {len(ss_context['found_screenshots'])} screenshots that need attention.\n"
            for ss in ss_context['found_screenshots'][:3]:
                prompt += f"- {ss['name']}: {ss.get('content_analysis', {}).get('priority', 'normal')} priority\n"
        
        prompt += """
## Implementation Guidelines:

1. **Step-by-Step Approach**: Implement improvements incrementally
2. **Testing**: Include test cases for critical changes
3. **Documentation**: Update docstrings and comments
4. **Error Handling**: Add proper try-except blocks
5. **Logging**: Use the unibos_logger for important operations
6. **Version**: Update VERSION.json after implementation

## Expected Output Format:

For each improvement:
1. Explain what you're fixing
2. Show the code changes
3. Explain the benefits

Use this format:
```python
# FILE: path/to/file.py
# CHANGE: Description of what's being fixed

[Updated code here]
```
"""
        
        return prompt
    
    def trigger_enhancement(self, module_name: str, auto_proceed: bool = False):
        """Modül iyileştirmesini tetikle"""
        print(f"\n{Colors.CYAN}🤖 UNIBOS Agent System - Module Enhancement{Colors.RESET}")
        print(f"{Colors.YELLOW}Target Module: {module_name}{Colors.RESET}")
        print(f"{Colors.DIM}{'='*60}{Colors.RESET}\n")
        
        # Analiz yap
        print(f"{Colors.GREEN}Step 1: Analyzing module...{Colors.RESET}")
        analysis = self.analyze_module(module_name)
        
        # Tüm iyileştirmeleri topla
        all_improvements = []
        total_issues = 0
        
        # Sonuçları göster
        print(f"\n{Colors.CYAN}Analysis Results:{Colors.RESET}")
        for agent_role, data in analysis['analyses'].items():
            print(f"\n{Colors.YELLOW}{agent_role}:{Colors.RESET}")
            print(f"  Files analyzed: {data['files_analyzed']}")
            print(f"  Issues found: {data['issues_found']}")
            
            total_issues += data['issues_found']
            
            if data['improvements']:
                all_improvements.extend(data['improvements'])
                print(f"  Top issues:")
                for imp in data['improvements'][:3]:
                    # Detaylı gösterim
                    if isinstance(imp, dict):
                        print(f"    - [{imp.get('priority', 'normal').upper()}] {imp.get('suggestion', imp)}")
                        if 'file' in imp:
                            print(f"      File: {imp['file']}")
                    else:
                        print(f"    - {imp}")
        
        # Hiç sorun bulunamadıysa özel işlem
        if total_issues == 0:
            print(f"\n{Colors.GREEN}✓ No critical issues found.{Colors.RESET}")
            print(f"{Colors.YELLOW}However, I'll perform a deeper analysis...{Colors.RESET}")
            
            # Force olarak bazı iyileştirmeler ekle
            forced_improvements = [
                {
                    'priority': 'medium',
                    'suggestion': 'Code documentation review',
                    'category': 'documentation',
                    'implementation_steps': [
                        'Review all functions for proper docstrings',
                        'Add type hints where missing',
                        'Update module-level documentation'
                    ]
                },
                {
                    'priority': 'low',
                    'suggestion': 'Code style consistency check',
                    'category': 'style',
                    'implementation_steps': [
                        'Apply consistent formatting',
                        'Review naming conventions',
                        'Check import organization'
                    ]
                }
            ]
            all_improvements.extend(forced_improvements)
            analysis['forced_analysis'] = True
        
        # Kullanıcı onayı (auto_proceed değilse)
        if not auto_proceed:
            print(f"\n{Colors.CYAN}Found {len(all_improvements)} improvement opportunities.{Colors.RESET}")
            print(f"{Colors.CYAN}Proceed with enhancement? (y/n):{Colors.RESET} ", end='')
            if input().lower() != 'y':
                print(f"{Colors.YELLOW}Enhancement cancelled.{Colors.RESET}")
                return
        
        # Gelişmiş prompt oluştur
        print(f"\n{Colors.GREEN}Step 2: Generating enhancement prompt...{Colors.RESET}")
        prompt = self.generate_detailed_enhancement_prompt(analysis, all_improvements)
        
        # Development version check
        use_dev_version = True  # Always use dev version for safety
        
        if use_dev_version:
            print(f"\n{Colors.YELLOW}Creating development version for safe modifications...{Colors.RESET}")
            
            try:
                from development_version_manager import dev_version_manager
                
                # Create development version
                dev_path = dev_version_manager.create_development_version(
                    f"Agent enhancement for {module_name} module"
                )
                
                if dev_path:
                    print(f"{Colors.GREEN}✓ Development version created: {dev_path.name}{Colors.RESET}")
                    print(f"{Colors.CYAN}All changes will be made in the development version.{Colors.RESET}")
                    print(f"{Colors.CYAN}You can test it later with: ./launch_dev.sh{Colors.RESET}\n")
                    
                    # Add dev path to prompt
                    prompt = f"""IMPORTANT: Make all changes in the development version at:
{dev_path}

Do NOT modify the main codebase.

""" + prompt
                else:
                    print(f"{Colors.YELLOW}Warning: Could not create dev version, using main codebase{Colors.RESET}")
                    
            except ImportError:
                print(f"{Colors.YELLOW}Development version manager not available{Colors.RESET}")
        
        # Claude'a gönder
        print(f"\n{Colors.GREEN}Step 3: Sending to Claude...{Colors.RESET}")
        
        # Detaylı suggestion text oluştur
        suggestion_text = f"""Module: {module_name}

Improvements found ({len(all_improvements)} total):
"""
        
        # Priority'ye göre sırala
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'normal': 3, 'low': 4}
        sorted_improvements = sorted(all_improvements, 
                                   key=lambda x: priority_order.get(x.get('priority', 'normal'), 3))
        
        for i, imp in enumerate(sorted_improvements[:10], 1):
            if isinstance(imp, dict):
                suggestion_text += f"\n{i}. [{imp.get('priority', 'normal').upper()}] {imp.get('suggestion', str(imp))}"
                if 'file' in imp:
                    suggestion_text += f"\n   File: {imp['file']}"
                if 'implementation_steps' in imp:
                    suggestion_text += "\n   Steps:"
                    for step in imp['implementation_steps'][:2]:
                        suggestion_text += f"\n   - {step}"
            else:
                suggestion_text += f"\n{i}. {imp}"
        
        # Mevcut claude_cli'nin trigger_claude_development metodunu kullan
        self.claude_cli.trigger_claude_development(
            suggestion_text,
            "agent_enhancement",
            additional_context=prompt
        )

# Claude CLI'ya agent desteği ekle
def add_agent_support_to_claude_cli(claude_cli_instance):
    """Mevcut Claude CLI'ya agent desteği ekle"""
    
    # Orchestrator'ı ekle
    claude_cli_instance.agent_orchestrator = UNIBOSAgentOrchestrator(claude_cli_instance)
    
    # Yeni metod ekle
    def show_agent_menu(self):
        """Show agent enhancement menu"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🤖 UNIBOS Agent System{Colors.RESET}")
        print(f"{Colors.YELLOW}AI-Powered Code Enhancement{Colors.RESET}")
        print(f"{Colors.DIM}{'='*60}{Colors.RESET}\n")
        
        # Modül seçenekleri
        modules = [
            ("1", "main", "Ana program (main.py)"),
            ("2", "claude", "Claude entegrasyonu"),
            ("3", "currencies", "Döviz modülü"),
            ("4", "recaria", "Recaria oyunu"),
            ("5", "birlikteyiz", "Mesh network"),
            ("6", "git", "Git yönetimi"),
            ("7", "all", "Tüm proje analizi"),
        ]
        
        print(f"{Colors.GREEN}Select module to enhance:{Colors.RESET}\n")
        for key, module, desc in modules:
            print(f"  {Colors.CYAN}{key}{Colors.RESET}. {module:<15} - {desc}")
        
        print(f"\n  {Colors.DIM}q. Return to Claude tools{Colors.RESET}")
        
        choice = self.get_simple_input(f"\n{Colors.BLUE}Choice: {Colors.RESET}")
        
        module_map = {
            "1": "main",
            "2": "claude", 
            "3": "currencies",
            "4": "recaria",
            "5": "birlikteyiz",
            "6": "git",
            "7": "all"
        }
        
        if choice in module_map:
            self.agent_orchestrator.trigger_enhancement(module_map[choice])
        elif choice.lower() != 'q':
            print(f"{Colors.RED}Invalid choice{Colors.RESET}")
            time.sleep(1)
            return self.show_agent_menu()
    
    # Metodu instance'a bağla
    import types
    claude_cli_instance.show_agent_menu = types.MethodType(show_agent_menu, claude_cli_instance)
    
    logger.info("Agent support added to Claude CLI", category=LogCategory.CLAUDE)
    
    return claude_cli_instance

# Export for integration
__all__ = ['UNIBOSAgent', 'UNIBOSAgentOrchestrator', 'add_agent_support_to_claude_cli']
