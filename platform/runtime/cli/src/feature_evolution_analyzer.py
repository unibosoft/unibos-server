#!/usr/bin/env python3
"""
🔬 UNIBOS Feature Evolution Analyzer
Arşivlenen versiyonlardan en ileri özellikleri çıkarıp analiz eden sistem

Bu modül eski versiyonlardaki özellikleri analiz edip güncel versiyona
entegre edilebilecek en iyi implementasyonları belirler.
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import difflib

# UNIBOS imports
try:
    from unibos_logger import logger, LogCategory, LogLevel
except ImportError:
    class logger:
        @staticmethod
        def info(msg, **kwargs): print(f"INFO: {msg}")
        @staticmethod
        def error(msg, **kwargs): print(f"ERROR: {msg}")

# PostgreSQL Suggestion Manager import
try:
    from suggestion_manager_pg import pg_suggestion_manager
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logger.warning("PostgreSQL suggestion manager not available")

# Renkler
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    RED = "\033[31m"
    DIM = "\033[2m"

@dataclass
class FeatureImplementation:
    """Bir özelliğin implementasyon detayları"""
    version: str
    file_path: str
    code_snippet: str
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    ui_elements: List[str] = field(default_factory=list)
    data_structures: List[str] = field(default_factory=list)

@dataclass 
class FeatureEvolution:
    """Bir özelliğin evrim analizi"""
    feature_name: str
    implementations: List[FeatureImplementation]
    best_implementation: Optional[FeatureImplementation] = None
    improvements: List[Dict[str, Any]] = field(default_factory=list)
    migration_plan: List[str] = field(default_factory=list)

class FeatureEvolutionAnalyzer:
    """Özellik evrim analizörü"""
    
    def __init__(self):
        self.current_version = self._get_current_version()
        self.suggestion_manager = pg_suggestion_manager if POSTGRES_AVAILABLE else None
        
    def _get_current_version(self) -> str:
        """Güncel versiyon numarasını al"""
        try:
            version_file = Path("src/VERSION.json")
            if version_file.exists():
                with open(version_file, 'r') as f:
                    data = json.load(f)
                    return data.get('version', 'v242')
        except:
            pass
        return 'v242'
    
    def analyze_feature_evolution(self, feature_name: str, scan_results: Dict[str, Any]) -> FeatureEvolution:
        """Özellik evrimini analiz et"""
        print(f"\n{Colors.CYAN}🔬 Feature Evolution Analysis: {feature_name}{Colors.RESET}")
        print(f"{Colors.CYAN}{'─'*60}{Colors.RESET}\n")
        
        evolution = FeatureEvolution(
            feature_name=feature_name,
            implementations=[]
        )
        
        # Scan sonuçlarından implementasyonları çıkar
        version_files = scan_results.get('version_files', [])
        if not version_files and 'feature_implementations' in scan_results:
            # feature_implementations listesinden dosya yollarını çıkar
            for impl_data in scan_results['feature_implementations']:
                if isinstance(impl_data, dict) and 'file' in impl_data:
                    version_files.append(impl_data['file'])
                elif isinstance(impl_data, str):
                    # Eğer direkt dosya yolu ise
                    version_files.append(impl_data)
        
        # Her dosya için implementasyon analizi yap
        for version_file in version_files[:10]:  # İlk 10 versiyon
            try:
                impl = self._analyze_implementation(version_file, feature_name)
                if impl:
                    evolution.implementations.append(impl)
            except Exception as e:
                print(f"{Colors.DIM}Error analyzing {version_file}: {e}{Colors.RESET}")
        
        # En iyi implementasyonu belirle
        if evolution.implementations:
            evolution.best_implementation = self._find_best_implementation(evolution.implementations)
            
        # İyileştirmeleri belirle
        evolution.improvements = self._identify_improvements(evolution)
        
        # Migrasyon planı oluştur
        evolution.migration_plan = self._create_migration_plan(evolution)
        
        return evolution
    
    def _analyze_implementation(self, file_path: str, feature_name: str) -> Optional[FeatureImplementation]:
        """Bir implementasyonu analiz et"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Versiyon bilgisini çıkar
            path_parts = file_path.split('/')
            version = None
            for part in path_parts:
                if part.startswith('unibos_v'):
                    version = part.split('_')[1]  # v234
                    break
            
            if not version:
                return None
            
            impl = FeatureImplementation(
                version=version,
                file_path=file_path,
                code_snippet=""
            )
            
            # AST analizi
            try:
                tree = ast.parse(content)
                
                # Fonksiyonları bul
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        impl.functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        impl.classes.append(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            impl.imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            impl.imports.append(f"{node.module}")
            except:
                pass
            
            # UI elementlerini bul
            ui_patterns = [
                r'print\s*\(\s*["\']([^"\']+)["\']',
                r'input\s*\(\s*["\']([^"\']+)["\']',
                r'═+|─+|╔+|╚+|║+',  # Box drawing
                r'[📊🎯💰📈📉⚡]'  # Emojiler
            ]
            
            for pattern in ui_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    impl.ui_elements.extend(matches[:5])  # İlk 5 örnek
            
            # Veri yapılarını bul
            data_patterns = [
                r'(\w+)\s*=\s*\{[^}]+\}',  # Dict
                r'(\w+)\s*=\s*\[[^\]]+\]',  # List
                r'class\s+(\w+)',  # Class
                r'dataclass.*class\s+(\w+)'  # Dataclass
            ]
            
            for pattern in data_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    impl.data_structures.extend(matches[:3])
            
            # Özellik ile ilgili kod parçasını bul
            lines = content.split('\n')
            feature_lines = []
            for i, line in enumerate(lines):
                if feature_name.lower() in line.lower():
                    # Context için etrafındaki satırları al
                    start = max(0, i-5)
                    end = min(len(lines), i+6)
                    feature_lines.extend(lines[start:end])
            
            impl.code_snippet = '\n'.join(feature_lines[:20])  # İlk 20 satır
            
            # Karmaşıklık skoru hesapla
            impl.complexity_score = self._calculate_complexity(impl)
            
            return impl
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None
    
    def _calculate_complexity(self, impl: FeatureImplementation) -> float:
        """Implementasyon karmaşıklığını hesapla"""
        score = 0.0
        
        # Fonksiyon sayısı
        score += len(impl.functions) * 0.1
        
        # Class sayısı
        score += len(impl.classes) * 0.2
        
        # Import sayısı
        score += len(impl.imports) * 0.05
        
        # UI zenginliği
        score += len(impl.ui_elements) * 0.15
        
        # Veri yapıları
        score += len(impl.data_structures) * 0.1
        
        return min(score, 10.0)  # Max 10 puan
    
    def _find_best_implementation(self, implementations: List[FeatureImplementation]) -> FeatureImplementation:
        """En iyi implementasyonu bul"""
        # Skorlama kriterleri
        scored_impls = []
        
        for impl in implementations:
            score = 0.0
            
            # Karmaşıklık skoru
            score += impl.complexity_score * 2
            
            # Yenilik (daha yeni versiyonlar daha yüksek skor)
            version_num = int(impl.version.replace('v', ''))
            score += (version_num / 100) * 3
            
            # UI zenginliği
            if impl.ui_elements:
                score += min(len(impl.ui_elements), 10) * 0.5
            
            # Fonksiyon çeşitliliği
            score += min(len(impl.functions), 10) * 0.3
            
            scored_impls.append((score, impl))
        
        # En yüksek skorlu implementasyonu döndür
        scored_impls.sort(key=lambda x: x[0], reverse=True)
        return scored_impls[0][1] if scored_impls else implementations[0]
    
    def _identify_improvements(self, evolution: FeatureEvolution) -> List[Dict[str, Any]]:
        """İyileştirmeleri belirle"""
        improvements = []
        
        if not evolution.best_implementation:
            return improvements
        
        best = evolution.best_implementation
        
        # UI iyileştirmeleri
        if best.ui_elements:
            improvements.append({
                'type': 'UI_ENHANCEMENT',
                'description': 'Gelişmiş UI elementleri bulundu',
                'elements': best.ui_elements[:5],
                'priority': 'high'
            })
        
        # Yeni fonksiyonlar
        unique_functions = set()
        for impl in evolution.implementations:
            unique_functions.update(impl.functions)
        
        if unique_functions:
            improvements.append({
                'type': 'NEW_FUNCTIONS',
                'description': f'{len(unique_functions)} benzersiz fonksiyon bulundu',
                'functions': list(unique_functions)[:10],
                'priority': 'medium'
            })
        
        # Veri yapıları
        if best.data_structures:
            improvements.append({
                'type': 'DATA_STRUCTURES',
                'description': 'Gelişmiş veri yapıları kullanımı',
                'structures': best.data_structures,
                'priority': 'medium'
            })
        
        return improvements
    
    def _create_migration_plan(self, evolution: FeatureEvolution) -> List[str]:
        """Migrasyon planı oluştur"""
        plan = []
        
        if not evolution.best_implementation:
            return plan
        
        plan.append(f"1. En iyi implementasyon: {evolution.best_implementation.version}")
        plan.append(f"2. Dosya: {evolution.best_implementation.file_path}")
        
        if evolution.improvements:
            plan.append("3. Uygulanacak iyileştirmeler:")
            for i, imp in enumerate(evolution.improvements, 1):
                plan.append(f"   {i}. {imp['type']}: {imp['description']}")
        
        plan.append("4. Entegrasyon adımları:")
        plan.append("   - Mevcut kodu yedekle")
        plan.append("   - Yeni özellikleri test ortamında dene")
        plan.append("   - UI elementlerini entegre et")
        plan.append("   - Fonksiyonları birleştir")
        plan.append("   - Test ve doğrulama")
        
        return plan
    
    def generate_integration_code(self, evolution: FeatureEvolution, current_file: str) -> str:
        """Entegrasyon kodu oluştur"""
        if not evolution.best_implementation:
            return ""
        
        print(f"\n{Colors.GREEN}📝 Generating Integration Code{Colors.RESET}")
        print(f"{Colors.DIM}Best version: {evolution.best_implementation.version}{Colors.RESET}")
        
        # Mevcut dosyayı oku
        current_content = ""
        if os.path.exists(current_file):
            with open(current_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
        
        # Entegrasyon önerileri
        suggestions = []
        
        # UI elementleri
        if evolution.best_implementation.ui_elements:
            ui_code = "\n# Enhanced UI Elements from " + evolution.best_implementation.version + "\n"
            for elem in evolution.best_implementation.ui_elements[:3]:
                if elem not in current_content:
                    ui_code += f"# Consider adding: {elem}\n"
            suggestions.append(ui_code)
        
        # Yeni fonksiyonlar
        new_functions = []
        for func in evolution.best_implementation.functions:
            if func not in current_content:
                new_functions.append(func)
        
        if new_functions:
            func_code = f"\n# New functions from {evolution.best_implementation.version}:\n"
            func_code += f"# Functions to integrate: {', '.join(new_functions[:5])}\n"
            suggestions.append(func_code)
        
        return '\n'.join(suggestions)
    
    def create_detailed_report(self, evolution: FeatureEvolution) -> str:
        """Detaylı rapor oluştur"""
        report = []
        report.append(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        report.append(f"{Colors.BOLD}Feature Evolution Report: {evolution.feature_name}{Colors.RESET}")
        report.append(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
        
        # Özet
        report.append(f"{Colors.YELLOW}Summary:{Colors.RESET}")
        report.append(f"Total implementations analyzed: {len(evolution.implementations)}")
        if evolution.best_implementation:
            report.append(f"Best implementation: {evolution.best_implementation.version}")
            report.append(f"Complexity score: {evolution.best_implementation.complexity_score:.2f}")
        
        # İyileştirmeler
        if evolution.improvements:
            report.append(f"\n{Colors.YELLOW}Identified Improvements:{Colors.RESET}")
            for imp in evolution.improvements:
                report.append(f"• {imp['type']}: {imp['description']}")
                if 'elements' in imp:
                    for elem in imp['elements'][:3]:
                        report.append(f"  - {elem}")
        
        # Migrasyon planı
        if evolution.migration_plan:
            report.append(f"\n{Colors.YELLOW}Migration Plan:{Colors.RESET}")
            for step in evolution.migration_plan:
                report.append(step)
        
        # Kod snippet
        if evolution.best_implementation and evolution.best_implementation.code_snippet:
            report.append(f"\n{Colors.YELLOW}Best Implementation Preview:{Colors.RESET}")
            report.append(f"{Colors.DIM}{evolution.best_implementation.code_snippet}{Colors.RESET}")
        
        return '\n'.join(report)
    
    def create_suggestions_from_evolution(self, evolution: FeatureEvolution) -> List[str]:
        """Evolution analizinden suggestion'lar oluştur"""
        suggestions_created = []
        
        if not self.suggestion_manager:
            logger.warning("Suggestion manager not available, cannot create suggestions")
            return suggestions_created
        
        # Her improvement için suggestion oluştur
        for imp in evolution.improvements:
            try:
                # Öneri metni oluştur
                title = f"{evolution.feature_name} - {imp['type']}"
                description = f"{imp['description']}\n"
                
                if 'elements' in imp:
                    description += "\nÖğeler:\n"
                    for elem in imp['elements']:
                        description += f"- {elem}\n"
                
                if 'functions' in imp:
                    description += "\nFonksiyonlar:\n"
                    for func in imp['functions']:
                        description += f"- {func}\n"
                
                # Metadata oluştur
                metadata = {
                    'feature_name': evolution.feature_name,
                    'improvement_type': imp['type'],
                    'source_version': evolution.best_implementation.version if evolution.best_implementation else None,
                    'source_file': evolution.best_implementation.file_path if evolution.best_implementation else None,
                    'priority_level': imp.get('priority', 'medium'),
                }
                
                # Kategori belirle
                category_map = {
                    'UI_ENHANCEMENT': 'ui_improvement',
                    'NEW_FUNCTIONS': 'feature',
                    'DATA_STRUCTURES': 'architecture',
                    'PERFORMANCE': 'performance',
                    'SECURITY': 'security',
                }
                category = category_map.get(imp['type'], 'feature_evolution')
                
                # Suggestion'ı ekle
                suggestion_id = self.suggestion_manager.add_suggestion(
                    title=title,
                    description=description,
                    category=category,
                    priority=imp.get('priority', 'medium'),
                    source='feature_evolution',
                    metadata=metadata
                )
                
                suggestions_created.append(suggestion_id)
                logger.info(f"Created suggestion: {title} (ID: {suggestion_id})")
                
            except Exception as e:
                logger.error(f"Error creating suggestion: {e}")
        
        # Genel evolution suggestion'ı oluştur
        if evolution.best_implementation and len(evolution.implementations) > 1:
            try:
                title = f"Complete {evolution.feature_name} Evolution Implementation"
                description = f"Implement the best version of {evolution.feature_name} from {evolution.best_implementation.version}\n\n"
                description += "Migration Plan:\n"
                for step in evolution.migration_plan:
                    description += f"{step}\n"
                
                metadata = {
                    'feature_name': evolution.feature_name,
                    'best_version': evolution.best_implementation.version,
                    'total_implementations': len(evolution.implementations),
                    'complexity_score': evolution.best_implementation.complexity_score,
                    'migration_required': True,
                }
                
                suggestion_id = self.suggestion_manager.add_suggestion(
                    title=title,
                    description=description,
                    category='feature_evolution',
                    priority='high',
                    source='feature_evolution',
                    metadata=metadata
                )
                
                suggestions_created.append(suggestion_id)
                logger.info(f"Created main evolution suggestion: {title}")
                
            except Exception as e:
                logger.error(f"Error creating main suggestion: {e}")
        
        return suggestions_created
    
    def add_to_suggestion_pool(self, text: str, metadata: Optional[Dict] = None) -> Optional[str]:
        """Öneri havuzuna ekle"""
        if not self.suggestion_manager:
            return None
        
        try:
            pool_id = self.suggestion_manager.add_to_pool(
                text=text,
                category='feature_evolution',
                source='feature_evolution',
                metadata=metadata or {}
            )
            return pool_id
        except Exception as e:
            logger.error(f"Error adding to pool: {e}")
            return None

# Export
__all__ = ['FeatureEvolutionAnalyzer', 'FeatureEvolution', 'FeatureImplementation']