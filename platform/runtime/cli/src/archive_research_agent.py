#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Archive Research Agent - v251
Derin arşiv araştırması ve kod evrim analizi yapan ajan

Author: berk hatırlı
Version: v251
Purpose: Eski versiyonlardaki işlevleri araştırıp raporlayan AI ajanı
"""

import os
import sys
import json
import re
import ast
import difflib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict
import threading
import time
import queue
import subprocess
import tempfile
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unibos_logger import logger, LogCategory, LogLevel
# Remove claude_cli import for now, implement local solution

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

@dataclass
class CodeEvolution:
    """Kod evrim bilgisi"""
    function_name: str
    first_seen_version: str
    last_seen_version: str
    total_versions: int
    changes: List[Dict[str, Any]] = field(default_factory=list)
    complexity_trend: str = ""  # "increasing", "decreasing", "stable"
    
@dataclass
class FeatureHistory:
    """Özellik geçmişi"""
    feature_name: str
    description: str
    introduced_version: str
    removed_version: Optional[str] = None
    related_files: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
@dataclass
class ResearchResult:
    """Araştırma sonucu"""
    query: str
    timestamp: datetime
    total_versions_analyzed: int
    total_files_scanned: int
    findings: List[Dict[str, Any]] = field(default_factory=list)
    code_evolutions: List[CodeEvolution] = field(default_factory=list)
    feature_history: List[FeatureHistory] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
class ArchiveResearchAgent:
    """Arşiv araştırma ajanı"""
    
    def __init__(self):
        """Initialize agent"""
        self.base_path = Path("/Users/berkhatirli/Desktop/unibos")
        self.archive_path = self.base_path / "archive" / "versions"
        self.results_cache = {}
        self.current_version = self._get_current_version()
        self.analysis_thread = None
        self.is_analyzing = False
        
        logger.info("Archive Research Agent initialized", category=LogCategory.MODULE)
    
    def _get_current_version(self) -> str:
        """Mevcut versiyonu al"""
        try:
            version_file = self.base_path / "src" / "VERSION.json"
            if version_file.exists():
                import json
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', 'v256')
            return 'v256'
        except:
            return 'v256'
        
    def _execute_claude_command(self, prompt: str) -> Dict[str, Any]:
        """Execute Claude command locally"""
        try:
            # Try subprocess with claude CLI
            import subprocess
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                temp_file = f.name
                
            try:
                result = subprocess.run(
                    ['claude', '-m', 'claude-3-sonnet-20240229', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # Try to parse as JSON
                    try:
                        return json.loads(result.stdout)
                    except:
                        # Return as text
                        return {"raw_response": result.stdout}
                        
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            logger.error(f"Claude execution failed: {e}", category=LogCategory.MODULE)
            
        # Return None if failed
        return None
        
    def analyze_with_claude(self, user_query: str) -> Dict[str, Any]:
        """Kullanıcı sorgusunu Claude ile analiz et"""
        print(f"\n{Colors.CYAN}🤖 Claude ile sorgu analizi yapılıyor...{Colors.RESET}")
        
        prompt = f"""
Kullanıcı şu konuda araştırma istiyor: "{user_query}"

Bu bir WEB ARAYÜZÜ GELİŞTİRME araştırması. Kullanıcı eski versiyonlardaki web özelliklerini bulup, yeni bir Django web arayüzü oluşturmak istiyor.

Araştırma için:
1. Web/Django ile ilgili anahtar kelimeler: urls.py, views.py, models.py, templates, static, settings.py, wsgi.py, manage.py
2. HTML template dosyaları: *.html, base.html, index.html
3. Web framework özellikleri: flask, django, fastapi, werkzeug, jinja2
4. Frontend özellikleri: css, javascript, bootstrap, htmx
5. Database bağlantıları: postgres, sqlite, mysql

ODAKLAN:
- Web sunucu yapılandırmaları
- URL routing sistemleri  
- Template engine kullanımları
- Form işleme metodları
- Authentication sistemleri
- API endpoint'leri
- Frontend-backend entegrasyonu

Yanıtını JSON formatında ver:
{{
    "keywords": ["urls", "views", "models", "template", "django"],
    "file_patterns": ["CHANGELOG.md", "CLAUDE*.md", "VERSION.json", "*.py", "*.html", "*.css", "*.js", "*urls.py", "*views.py", "*models.py", "*settings.py"],
    "version_range": {{"start": "v001", "end": "{self.current_version}"}},
    "focus_modules": ["web", "django", "projects", "kisiselenflasyon"],
    "analysis_strategy": "Django web arayüzü bileşenlerini ve template sistemlerini araştır"
}}
"""
        
        try:
            response = self._execute_claude_command(prompt)
            if isinstance(response, dict):
                return response
            else:
                # Fallback
                return {
                    "keywords": self._extract_keywords(user_query),
                    "file_patterns": ["*.py", "*.md", "*.json"],
                    "version_range": {"start": "v001", "end": "v250"},
                    "focus_modules": ["main", "currencies", "recaria", "birlikteyiz", "kisiselenflasyon"],
                    "analysis_strategy": "Tüm versiyonlarda kapsamlı arama"
                }
        except Exception as e:
            logger.error(f"Claude analysis failed: {e}", category=LogCategory.MODULE)
            return self._fallback_analysis(user_query)
            
    def _extract_keywords(self, query: str) -> List[str]:
        """Sorgudan anahtar kelimeleri çıkar"""
        # Daha akıllı keyword extraction
        stop_words = {
            "ve", "veya", "için", "ile", "bir", "bu", "şu", "o", "da", "de", "ki", "mi", 
            "eski", "yeni", "farklı", "güzel", "iyi", "ilgili", "detaylı", "tüm", "bazı",
            "yap", "et", "ol", "bul", "ver", "al", "gel", "git", "var", "yok",
            "versiyonlarda", "versiyonları", "özellikleri", "özellikler",
            "şimdilik", "sadece", "ana", "ile", "gibi", "aynı", "devam"
        }
        
        # Önemli teknik terimler
        important_terms = ["web", "arayüz", "django", "postgres", "postgresql", "cli", "ui", 
                          "interface", "template", "view", "model", "kisiselenflasyon", "kişisel enflasyon"]
        
        # Query'yi küçük harfe çevir ve noktalama işaretlerini temizle
        query_clean = query.lower().replace(',', ' ').replace('.', ' ').replace('!', ' ').replace('?', ' ')
        words = query_clean.split()
        
        # Önce önemli terimleri bul
        keywords = []
        for term in important_terms:
            if term in query_clean:
                keywords.append(term)
        
        # Sonra diğer anlamlı kelimeleri ekle
        for word in words:
            if len(word) > 3 and word not in stop_words and word not in keywords:
                # Fiil çekimlerini temizle
                if not any(word.endswith(suffix) for suffix in ["mış", "miş", "muş", "müş", "dık", "dik", "tık", "tik"]):
                    keywords.append(word)
                    if len(keywords) >= 5:  # Max 5 keyword
                        break
        
        return keywords[:5]
        
    def _fallback_analysis(self, query: str) -> Dict[str, Any]:
        """Claude olmadığında fallback analiz"""
        keywords = self._extract_keywords(query)
        
        # Web/Django özel kelimeleri kontrol et
        web_keywords = ["web", "django", "template", "html", "views", "urls", "models", "arayüz", "ui", "interface"]
        query_lower = query.lower()
        
        # Her zaman CHANGELOG ve CLAUDE dosyalarını dahil et
        essential_patterns = ["CHANGELOG.md", "CLAUDE*.md", "VERSION.json"]
        
        # Eğer web/Django ile ilgiliyse, keywords zaten extract edilmiş olacak
        # Ama emin olmak için kontrol edelim
        if any(wk in query_lower for wk in web_keywords):
            # Web araması için özel dosya pattern'leri
            file_patterns = essential_patterns + [
                "*.py", "*.html", "*.md", "*urls.py", "*views.py", "*models.py",
                "*web*.py", "*django*.py", "*template*.html", "**/web/**", "**/django/**"
            ]
            # Eğer keywords'de web terimleri yoksa ekle
            if not any(k in keywords for k in ["web", "django", "arayüz"]):
                keywords = ["web", "django", "arayüz"] + keywords[:2]
        else:
            file_patterns = essential_patterns + ["*.py", "*.md"]
            
        return {
            "keywords": keywords[:5],  # Max 5 keyword
            "file_patterns": file_patterns,
            "version_range": {"start": "v001", "end": self.current_version},
            "focus_modules": ["kisiselenflasyon", "web", "django", "main", "projects"],
            "analysis_strategy": f"'{', '.join(keywords[:3])}' anahtar kelimeleriyle web odaklı arama"
        }
        
    def deep_search(self, analysis_config: Dict[str, Any], progress_callback=None) -> ResearchResult:
        """Derin arşiv araştırması yap"""
        result = ResearchResult(
            query=analysis_config.get("original_query", ""),
            timestamp=datetime.now(),
            total_versions_analyzed=0,
            total_files_scanned=0
        )
        
        keywords = analysis_config.get("keywords", [])
        file_patterns = analysis_config.get("file_patterns", ["*.py"])
        version_range = analysis_config.get("version_range", {})
        focus_modules = analysis_config.get("focus_modules", [])
        
        # Version dizinlerini tara
        version_dirs = sorted([d for d in self.archive_path.iterdir() if d.is_dir()])
        
        # Version filtreleme
        if version_range:
            start_v = version_range.get("start", "v001")
            end_v = version_range.get("end", "v999")
            version_dirs = [d for d in version_dirs if self._version_in_range(d.name, start_v, end_v)]
        
        total_versions = len(version_dirs)
        
        for idx, version_dir in enumerate(version_dirs):
            if progress_callback:
                progress = (idx + 1) / total_versions * 100
                progress_callback(f"Analyzing {version_dir.name}", progress)
                
            self._analyze_version(version_dir, keywords, file_patterns, focus_modules, result, progress_callback)
            result.total_versions_analyzed += 1
            
        # Kod evrimlerini analiz et
        self._analyze_code_evolution(result)
        
        # Önerileri oluştur
        self._generate_recommendations(result)
        
        return result
        
    def _version_in_range(self, version_name: str, start: str, end: str) -> bool:
        """Versiyon aralıkta mı kontrol et"""
        try:
            # Extract version number
            v_match = re.search(r'v(\d+)', version_name)
            if not v_match:
                return False
                
            v_num = int(v_match.group(1))
            start_num = int(re.search(r'v(\d+)', start).group(1))
            end_num = int(re.search(r'v(\d+)', end).group(1))
            
            return start_num <= v_num <= end_num
        except:
            return False
            
    def _analyze_version(self, version_dir: Path, keywords: List[str], 
                        file_patterns: List[str], focus_modules: List[str], 
                        result: ResearchResult, progress_callback=None):
        """Bir versiyonu analiz et"""
        for pattern in file_patterns:
            for file_path in version_dir.rglob(pattern):
                if file_path.is_file():
                    result.total_files_scanned += 1
                    self._analyze_file(file_path, keywords, focus_modules, result, version_dir.name, progress_callback)
                    
    def _analyze_file(self, file_path: Path, keywords: List[str], 
                     focus_modules: List[str], result: ResearchResult, version: str, progress_callback=None):
        """Bir dosyayı analiz et"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Önemli dosyaları her zaman analiz et
            file_name = file_path.name
            is_important_file = (
                file_name == "CHANGELOG.md" or 
                file_name.startswith("CLAUDE") and file_name.endswith(".md") or
                file_name == "VERSION.json"
            )
            
            # Dosya yolu kontrolü - sadece ilgili dosyaları analiz et
            file_str = str(file_path).lower()
            if not is_important_file and \
               not any(module in file_str for module in focus_modules) and \
               not any(pattern in file_str for pattern in ["web", "django", "template", "views", "urls"]):
                return
            
            # CHANGELOG için özel parsing
            if file_name == "CHANGELOG.md" and any(kw in content.lower() for kw in keywords):
                # Version başlıklarını bul
                lines = content.splitlines()
                for idx, line in enumerate(lines):
                    if line.startswith("## ") and any(kw.lower() in line.lower() for kw in keywords):
                        # Version bölümünü al
                        context_lines = []
                        for i in range(idx, min(idx + 20, len(lines))):
                            if i > idx and lines[i].startswith("## "):
                                break
                            context_lines.append(lines[i])
                        
                        finding = {
                            "version": version,
                            "file": str(file_path.relative_to(self.base_path)),
                            "keyword": "changelog_entry",
                            "line_number": idx + 1,
                            "context": '\n'.join(context_lines[:10]),  # İlk 10 satır
                            "type": "changelog_match"
                        }
                        result.findings.append(finding)
                        file_findings += 1
                        
                        if len(result.findings) >= 1000:
                            return
            
            # Normal keyword araması - her dosyada max 5 bulgu
            if not is_important_file or file_findings < 5:
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        # Context çıkar
                        lines = content.splitlines()
                        for idx, line in enumerate(lines):
                            if keyword.lower() in line.lower() and file_findings < 5:
                                context_start = max(0, idx - 2)
                                context_end = min(len(lines), idx + 3)
                                context = '\n'.join(lines[context_start:context_end])
                                
                                finding = {
                                    "version": version,
                                    "file": str(file_path.relative_to(self.base_path)),
                                    "keyword": keyword,
                                    "line_number": idx + 1,
                                    "context": context,
                                    "type": "keyword_match"
                                }
                                result.findings.append(finding)
                                file_findings += 1
                                
                                # Toplam bulgu limiti
                                if len(result.findings) >= 1000:
                                    return
                            
            # Python dosyası ise AST analizi
            if file_path.suffix == '.py':
                self._analyze_python_ast(file_path, content, version, result)
                
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}", category=LogCategory.MODULE)
            
    def _analyze_python_ast(self, file_path: Path, content: str, version: str, result: ResearchResult):
        """Python AST analizi yap"""
        try:
            # Django/web ile ilgili dosyalara odaklan
            file_str = str(file_path).lower()
            if not any(pattern in file_str for pattern in ["web", "django", "views", "urls", "models", "kisiselenflasyon"]):
                return
                
            tree = ast.parse(content)
            
            # Django/web ile ilgili fonksiyon ve sınıfları bul
            web_patterns = ["view", "View", "template", "render", "response", "request", 
                          "url", "path", "route", "model", "Model", "form", "Form"]
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Web/Django ile ilgili fonksiyonlara odaklan
                    if any(pattern in node.name for pattern in web_patterns):
                        finding = {
                            "version": version,
                            "file": str(file_path.relative_to(self.base_path)),
                            "function": node.name,
                            "line_number": node.lineno,
                            "type": "function_definition",
                            "docstring": ast.get_docstring(node)
                        }
                        result.findings.append(finding)
                        
                        # Bulgu limiti kontrolü
                        if len(result.findings) >= 1000:
                            if progress_callback:
                                progress_callback(f"1000 bulgu limitine ulaşıldı", 100)
                            return
                    
                elif isinstance(node, ast.ClassDef):
                    # Web/Django ile ilgili sınıflara odaklan
                    if any(pattern in node.name for pattern in web_patterns):
                        finding = {
                            "version": version,
                            "file": str(file_path.relative_to(self.base_path)),
                            "class": node.name,
                            "line_number": node.lineno,
                            "type": "class_definition",
                            "docstring": ast.get_docstring(node)
                        }
                        result.findings.append(finding)
                        
                        # Bulgu limiti kontrolü
                        if len(result.findings) >= 1000:
                            if progress_callback:
                                progress_callback(f"1000 bulgu limitine ulaşıldı", 100)
                            return
                    
        except Exception:
            # AST parse edilemezse sessizce geç
            pass
            
    def _analyze_code_evolution(self, result: ResearchResult):
        """Kod evrimini analiz et"""
        # Fonksiyonları grupla
        function_versions = defaultdict(list)
        
        for finding in result.findings:
            if finding["type"] == "function_definition":
                func_name = finding["function"]
                function_versions[func_name].append({
                    "version": finding["version"],
                    "file": finding["file"],
                    "docstring": finding.get("docstring", "")
                })
                
        # Evrim analizi
        for func_name, versions in function_versions.items():
            if len(versions) > 1:
                evolution = CodeEvolution(
                    function_name=func_name,
                    first_seen_version=versions[0]["version"],
                    last_seen_version=versions[-1]["version"],
                    total_versions=len(versions),
                    changes=versions
                )
                
                # Complexity trend analizi (basit)
                if len(versions) > 5:
                    evolution.complexity_trend = "evolving"
                else:
                    evolution.complexity_trend = "stable"
                    
                result.code_evolutions.append(evolution)
                
    def _generate_recommendations(self, result: ResearchResult):
        """Araştırma sonuçlarına göre öneriler oluştur"""
        # En çok değişen fonksiyonlar
        if result.code_evolutions:
            most_evolved = max(result.code_evolutions, key=lambda x: x.total_versions)
            result.recommendations.append(
                f"'{most_evolved.function_name}' fonksiyonu {most_evolved.total_versions} "
                f"versiyonda değişmiş. Detaylı incelemeye değer."
            )
            
        # Kaldırılan özellikler
        removed_features = [f for f in result.feature_history if f.removed_version]
        if removed_features:
            result.recommendations.append(
                f"{len(removed_features)} özellik kaldırılmış. "
                "Bunları yeniden implemente etmek faydalı olabilir."
            )
            
        # Versiyon önerileri
        if result.total_versions_analyzed > 50:
            result.recommendations.append(
                "Çok sayıda versiyon analiz edildi. "
                "Daha spesifik bir arama kriteri kullanmayı düşünün."
            )
            
    def save_report_to_file(self, result: ResearchResult) -> str:
        """Araştırma raporunu dosyaya kaydet"""
        # reports dizini oluştur
        reports_dir = self.base_path / "reports" / "archive_research"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Dosya adını oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', result.query)[:50]
        filename = f"research_{timestamp}_{query_slug}.md"
        filepath = reports_dir / filename
        
        # Detaylı rapor oluştur
        full_report = self._generate_full_report(result)
        
        # Dosyaya yaz
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        return str(filepath)
    
    def _generate_full_report(self, result: ResearchResult) -> str:
        """Detaylı rapor oluştur"""
        report = []
        report.append(f"# 🔍 Arşiv Araştırma Raporu")
        report.append(f"\n**Tarih:** {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Sorgu:** {result.query}")
        report.append(f"**Analiz Edilen Versiyon Sayısı:** {result.total_versions_analyzed}")
        report.append(f"**Taranan Dosya Sayısı:** {result.total_files_scanned}")
        report.append(f"**Toplam Bulgu:** {len(result.findings)}")
        
        # Kod Evrimi Bölümü
        if result.code_evolutions:
            report.append(f"\n## 🔄 Kod Evrimi Analizi")
            report.append(f"\n### Sorgudaki '{result.query}' ile İlgili Fonksiyon Değişimleri:\n")
            
            # Sorguyla ilgili evrimleri filtrele
            query_keywords = [kw.lower() for kw in result.query.split() if len(kw) > 2]
            relevant_evolutions = []
            
            for evolution in result.code_evolutions:
                # Fonksiyon adı veya docstring'de sorgu kelimelerini ara
                is_relevant = False
                func_name_lower = evolution.function_name.lower()
                
                # Direkt fonksiyon adında arama
                for keyword in query_keywords:
                    if keyword in func_name_lower:
                        is_relevant = True
                        break
                
                # Docstring'lerde arama
                if not is_relevant and evolution.changes:
                    for change in evolution.changes:
                        if change.get('docstring'):
                            docstring_lower = change['docstring'].lower()
                            for keyword in query_keywords:
                                if keyword in docstring_lower:
                                    is_relevant = True
                                    break
                        if is_relevant:
                            break
                
                if is_relevant:
                    relevant_evolutions.append(evolution)
            
            # Eğer sorguyla ilgili evrim bulunamazsa, en çok değişen fonksiyonları göster
            if not relevant_evolutions and result.code_evolutions:
                report.append(f"*Sorguyla doğrudan ilgili fonksiyon değişimi bulunamadı.*")
                report.append(f"*En çok değişen fonksiyonlar:*\n")
                relevant_evolutions = sorted(result.code_evolutions, 
                                           key=lambda x: x.total_versions, 
                                           reverse=True)[:5]
            
            for evolution in relevant_evolutions:
                report.append(f"#### {evolution.function_name}")
                report.append(f"- **İlk Görülme:** {evolution.first_seen_version}")
                report.append(f"- **Son Görülme:** {evolution.last_seen_version}")
                report.append(f"- **Toplam Değişim:** {evolution.total_versions} versiyon")
                report.append(f"- **Karmaşıklık Trendi:** {evolution.complexity_trend}")
                
                # Sorguyla ilgili değişimleri vurgula
                relevant_changes = []
                for change in evolution.changes:
                    change_text = f"  - {change['version']}: {change['file']}"
                    if change.get('docstring'):
                        docstring_lower = change['docstring'].lower()
                        for keyword in query_keywords:
                            if keyword in docstring_lower:
                                change_text += f" **['{keyword}' içeriyor]**"
                                break
                        change_text += f"\n    > {change['docstring']}"
                    relevant_changes.append(change_text)
                
                # Değişim detayları
                if relevant_changes:
                    report.append(f"\n**Versiyon Geçmişi:**")
                    for change_text in relevant_changes:
                        report.append(change_text)
                report.append("")
        
        # Detaylı Bulgular
        if result.findings:
            report.append(f"\n## 📌 Detaylı Bulgular")
            
            # Keyword matches
            keyword_matches = [f for f in result.findings if f["type"] == "keyword_match"]
            if keyword_matches:
                report.append(f"\n### Anahtar Kelime Eşleşmeleri ({len(keyword_matches)} adet):\n")
                for i, match in enumerate(keyword_matches, 1):
                    report.append(f"**{i}. {match['version']} - {match['file']}:{match['line_number']}**")
                    report.append(f"   - Keyword: `{match['keyword']}`")
                    report.append(f"   - Context:")
                    report.append(f"```")
                    report.append(match['context'])
                    report.append(f"```\n")
        
        # Öneriler
        if result.recommendations:
            report.append(f"\n## 💡 Öneriler")
            for i, rec in enumerate(result.recommendations, 1):
                report.append(f"{i}. {rec}")
        
        return "\n".join(report)
    
    def generate_report(self, result: ResearchResult) -> str:
        """Araştırma raporunu oluştur (ekran için kısa versiyon)"""
        report = []
        report.append(f"\n{Colors.BOLD}🔍 Arşiv Araştırma Raporu{Colors.RESET}")
        report.append(f"{Colors.GRAY}{'='*60}{Colors.RESET}")
        report.append(f"📅 Tarih: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"🔎 Sorgu: {result.query}")
        report.append(f"📊 Analiz Edilen Versiyon: {result.total_versions_analyzed}")
        report.append(f"📄 Taranan Dosya: {result.total_files_scanned}")
        report.append(f"🎯 Toplam Bulgu: {len(result.findings)}")
        
        # Önemli bulgular
        if result.findings:
            report.append(f"\n{Colors.YELLOW}📌 Önemli Bulgular:{Colors.RESET}")
            
            # Changelog matches
            changelog_matches = [f for f in result.findings if f["type"] == "changelog_match"]
            if changelog_matches:
                report.append(f"\n  {Colors.MAGENTA}📋 CHANGELOG Bulguları:{Colors.RESET}")
                for match in changelog_matches[:3]:  # İlk 3 sonuç
                    report.append(f"  • {match['version']} - {match['file']}")
                    context_preview = match['context'].split('\n')[0][:80] + "..."
                    report.append(f"    {Colors.GRAY}{context_preview}{Colors.RESET}")
            
            # Keyword matches
            keyword_matches = [f for f in result.findings if f["type"] == "keyword_match"]
            if keyword_matches:
                report.append(f"\n  {Colors.CYAN}Anahtar Kelime Eşleşmeleri:{Colors.RESET}")
                for match in keyword_matches[:5]:  # İlk 5 sonuç
                    report.append(f"  • {match['version']} - {match['file']}:{match['line_number']}")
                    report.append(f"    Keyword: {Colors.GREEN}{match['keyword']}{Colors.RESET}")
                    
        # Kod evrimi
        if result.code_evolutions:
            report.append(f"\n{Colors.YELLOW}🔄 Kod Evrimi:{Colors.RESET}")
            for evolution in result.code_evolutions[:5]:
                report.append(f"  • {Colors.CYAN}{evolution.function_name}{Colors.RESET}")
                report.append(f"    İlk görülme: {evolution.first_seen_version}")
                report.append(f"    Son görülme: {evolution.last_seen_version}")
                report.append(f"    Değişim sayısı: {evolution.total_versions}")
                
        # Öneriler
        if result.recommendations:
            report.append(f"\n{Colors.YELLOW}💡 Öneriler:{Colors.RESET}")
            for rec in result.recommendations:
                report.append(f"  • {rec}")
                
        return "\n".join(report)
        
    def interactive_research(self):
        """İnteraktif araştırma modu - Claude CLI ile"""
        print(f"\n{Colors.BOLD}🔍 Arşiv Araştırma Ajanı - Claude Powered{Colors.RESET}")
        print(f"{Colors.GRAY}Çıkmak için 'q' yazın{Colors.RESET}\n")
        
        # İlk araştırma
        query = input(f"{Colors.CYAN}Araştırma konusu: {Colors.RESET}").strip()
        
        if query and query.lower() != 'q':
            # Claude'a arşiv araştırma isteği gönder
            # _research_with_claude içinde _interactive_session çağrılacak
            # ve oradan çıkış yapılmadıkça program devam etmeyecek
            self._research_with_claude(query)
    
    def _research_with_claude(self, query: str):
        """Claude CLI ile arşiv araştırması yap"""
        print(f"\n{Colors.YELLOW}🤖 Claude ile arşiv araştırması başlatılıyor...{Colors.RESET}")
        
        # Arşiv dizin listesini al
        archive_dirs = []
        if self.archive_path.exists():
            archive_dirs = [d.name for d in sorted(self.archive_path.iterdir()) if d.is_dir()]
        
        prompt = f"""
Kullanıcının isteği: "{query}"

UNIBOS projesinin arşivinde {len(archive_dirs)} versiyon mevcut.
Son versiyonlar: {', '.join(archive_dirs[-20:])}

Bu bir ARŞİV ARAŞTIRMA ve GELİŞTİRME görevidir. Kullanıcının isteğini analiz et ve:

1. İstekle ilgili eski versiyonlardaki özellikleri tespit et
2. En iyi implementasyonları ve çözümleri bul
3. Modern teknolojilerle güncellenmiş öneriler oluştur
4. Her öneri için detaylı uygulama planı hazırla

ARAŞTIRMA ALANLARI:
- Modül yapıları ve organizasyon
- API tasarımları ve endpoint'ler
- Veritabanı şemaları ve modeller
- UI/UX çözümleri ve arayüz tasarımları
- Algoritma ve veri yapıları
- Test stratejileri ve best practice'ler
- Güvenlik implementasyonları
- Performans optimizasyonları

ÖNERİ FORMATI:
## 🚀 [Ana Başlık - Kullanıcının İsteğine Göre]

### 1. [Öneri Başlığı]
**Açıklama:** Ne yapılacak ve neden
**Adımlar:**
1. İlk adım (komutla birlikte)
2. İkinci adım (kod örneğiyle)
3. Üçüncü adım
...

**Örnek Kod:**
```[uygun dil]
# Örnek implementasyon
```

**Notlar:** Dikkat edilmesi gerekenler

---

Kullanıcının isteğine göre EN AZ 5, EN FAZLA 10 pratik öneri oluştur.
Her öneri UYGULANMAYA HAZIR olmalı.
"""
        
        suggestions = []  # Önerileri sakla
        claude_output = ""  # Claude çıktısını sakla
        
        try:
            # Claude'a gönder
            import tempfile
            import subprocess
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                temp_file = f.name
            
            try:
                # Claude CLI çağrısı - gerçek zamanlı output için subprocess.Popen kullan
                print(f"{Colors.CYAN}Claude düşünüyor...{Colors.RESET}")
                print(f"{Colors.DIM}{'─'*60}{Colors.RESET}")
                
                # Claude CLI çağrısı - farklı yöntemler dene
                # Önce basit subprocess.run ile dene
                print(f"{Colors.YELLOW}⚠️  Not: Claude çıktısı tamamlandıktan sonra gösterilecek{Colors.RESET}\n")
                
                # Method 1: Direct execution with real-time output
                try:
                    # Use os.system for real output
                    cmd = f"claude '@{temp_file}'"
                    print(f"{Colors.DIM}Executing: {cmd}{Colors.RESET}\n")
                    
                    # os.system shows output in real-time
                    exit_code = os.system(cmd)
                    
                    if exit_code == 0:
                        claude_output = "[Output shown above]"
                        suggestions = []  # Will need to parse manually
                    else:
                        raise Exception(f"Claude exited with code {exit_code}")
                        
                except Exception as e:
                    print(f"\n{Colors.YELLOW}Method 1 failed, trying alternative...{Colors.RESET}")
                    
                    # Method 2: Try with unbuffered output
                    process = subprocess.Popen(
                        ['claude', '@' + temp_file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,  # Combine streams
                        text=True,
                        bufsize=0,  # Unbuffered
                        universal_newlines=True,
                        env={**os.environ, 'PYTHONUNBUFFERED': '1'}  # Force unbuffered
                    )
                
                    # Alternative method output handling
                    claude_output = ""
                    output_lines = []
                    
                    # Read output line by line
                    while True:
                        line = process.stdout.readline()
                        if not line and process.poll() is not None:
                            break
                        if line:
                            print(line, end='', flush=True)
                            claude_output += line
                            output_lines.append(line)
                    
                    # Check return code
                    if process.returncode == 0:
                        print(f"\n{Colors.DIM}{'─'*60}{Colors.RESET}")
                        print(f"\n{Colors.GREEN}✅ Claude analizi tamamlandı{Colors.RESET}")
                        
                        # Save suggestions
                        suggestions = self._save_claude_suggestions(claude_output, query)
                        
                        if suggestions:
                            print(f"\n{Colors.CYAN}📋 Oluşturulan Öneriler:{Colors.RESET}")
                            for i, suggestion in enumerate(suggestions, 1):
                                print(f"{Colors.YELLOW}{i}.{Colors.RESET} {suggestion['title']}")
                            print(f"\n{Colors.GRAY}Öneri numarasını yazarak direkt geliştirmeye başlayabilirsiniz.{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}❌ Claude hatası (kod: {process.returncode}){Colors.RESET}")
                    
            finally:
                import os
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}⏱️ Claude timeout (120 saniye){Colors.RESET}")
            print(f"{Colors.YELLOW}💡 İpucu: Daha spesifik bir soru sormayı deneyin{Colors.RESET}")
            
            # Timeout durumunda da interaktif oturumu başlat
            self._handle_timeout_interactive(query)
            return
            
        except Exception as e:
            print(f"{Colors.RED}❌ Hata: {e}{Colors.RESET}")
            # Hata durumunda yeni araştırma seçeneği sun
            self._handle_error_interactive(query)
            return
        
        # İnteraktif input alanı - sadece başarılı durumda
        if claude_output:
            self._interactive_session(claude_output, suggestions, query)
        else:
            # Claude çıktısı yoksa bile interaktif mod
            self._handle_no_output_interactive(query)
    
    def _save_claude_suggestions(self, claude_output: str, original_query: str):
        """Claude'un önerilerini PostgreSQL'e kaydet ve listeyi döndür"""
        suggestions_list = []
        try:
            from suggestion_manager_pg import PostgreSQLSuggestionManager
            manager = PostgreSQLSuggestionManager()
            
            # Basit parsing - önerileri bul
            lines = claude_output.split('\n')
            current_suggestion = None
            suggestions_saved = 0
            
            for line in lines:
                # Öneri başlığı tespiti - numaralı başlıkları da kontrol et
                if (line.startswith('### ') and line[4:].strip()) or \
                   (line.strip() and line.split('.', 1)[0].strip().isdigit() and line.startswith('### ')):
                    if current_suggestion:
                        # Önceki öneriyi kaydet
                        self._save_single_suggestion(manager, current_suggestion, original_query)
                        suggestions_list.append(current_suggestion)
                        suggestions_saved += 1
                    
                    # Başlıktan numarayı temizle
                    title = line[4:].strip()
                    if title and title.split('.', 1)[0].strip().isdigit():
                        title = title.split('.', 1)[1].strip()
                    
                    current_suggestion = {
                        'title': title,
                        'description': '',
                        'steps': []
                    }
                elif current_suggestion and line.strip():
                    if line.startswith('**Açıklama:**'):
                        current_suggestion['description'] = line[13:].strip()
                    elif line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                        current_suggestion['steps'].append(line.strip())
            
            # Son öneriyi kaydet
            if current_suggestion:
                self._save_single_suggestion(manager, current_suggestion, original_query)
                suggestions_list.append(current_suggestion)
                suggestions_saved += 1
            
            if suggestions_saved > 0:
                print(f"\n{Colors.GREEN}✅ {suggestions_saved} öneri PostgreSQL'e kaydedildi{Colors.RESET}")
                
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Öneriler kaydedilemedi: {e}{Colors.RESET}")
        
        return suggestions_list
    
    def _save_single_suggestion(self, manager, suggestion, original_query):
        """Tek bir öneriyi kaydet"""
        full_description = suggestion['description']
        if suggestion['steps']:
            full_description += "\n\nAdımlar:\n" + "\n".join(suggestion['steps'])
        
        manager.add_suggestion(
            title=suggestion['title'][:255],  # PostgreSQL limit
            description=full_description,
            category='feature',
            priority='high',
            source='claude_archive_research',
            metadata={
                'original_query': original_query,
                'from_claude': True,
                'implementation_ready': True
            }
        )

    def _create_suggestions_from_research(self, result: ResearchResult):
        """Araştırma sonuçlarından web arayüzü geliştirme önerileri oluştur"""
        try:
            from suggestion_manager_pg import PostgreSQLSuggestionManager
            
            print(f"\n{Colors.CYAN}📝 Web arayüzü geliştirme önerileri oluşturuluyor...{Colors.RESET}")
            
            manager = PostgreSQLSuggestionManager()
            suggestions_created = 0
            created_suggestions = []
            
            # Web framework kullanımını tespit et
            web_frameworks = {
                'django': {'count': 0, 'versions': []},
                'flask': {'count': 0, 'versions': []},
                'fastapi': {'count': 0, 'versions': []}
            }
            
            # Template engine kullanımını tespit et
            template_engines = {
                'jinja2': 0,
                'django_templates': 0,
                'mako': 0
            }
            
            # Web özellikleri tespit et
            web_features = {
                'authentication': False,
                'api_endpoints': False,
                'database_models': False,
                'forms': False,
                'ajax': False,
                'bootstrap': False,
                'htmx': False
            }
            
            # Bulguları analiz et
            for finding in result.findings:
                file_path = finding.get('file', '').lower()
                context = finding.get('context', '').lower()
                
                # Framework tespiti
                if 'django' in file_path or 'django' in context:
                    web_frameworks['django']['count'] += 1
                    web_frameworks['django']['versions'].append(finding.get('version', ''))
                elif 'flask' in file_path or 'flask' in context:
                    web_frameworks['flask']['count'] += 1
                    web_frameworks['flask']['versions'].append(finding.get('version', ''))
                    
                # Özellik tespiti
                if 'login' in context or 'authenticate' in context:
                    web_features['authentication'] = True
                if 'api' in file_path or 'endpoint' in context:
                    web_features['api_endpoints'] = True
                if 'models.py' in file_path:
                    web_features['database_models'] = True
                if 'forms.py' in file_path or 'form' in context:
                    web_features['forms'] = True
                if 'ajax' in context or 'fetch' in context:
                    web_features['ajax'] = True
                if 'bootstrap' in context:
                    web_features['bootstrap'] = True
                if 'htmx' in context:
                    web_features['htmx'] = True
            
            # 1. Django projesi kurulum önerisi
            if web_frameworks['django']['count'] > 0 or 'django' in result.query.lower():
                title = "Django projesi kurulumu ve temel yapılandırma"
                description = (
                    "1. Django projesi oluştur: django-admin startproject unibos_web\n"
                    "2. Kişisel enflasyon app'i oluştur: python manage.py startapp kisiselenflasyon\n"
                    "3. PostgreSQL veritabanı bağlantısını yapılandır (settings.py)\n"
                    "4. Static ve media dosya yapılandırması\n"
                    "5. URL routing sistemi kurulumu"
                )
                
                suggestion_id = manager.add_suggestion(
                    title=title,
                    description=description,
                    category='feature',
                    priority='high',
                    source='archive_research',
                    metadata={
                        'query': result.query,
                        'implementation_steps': True,
                        'report_file': getattr(result, 'report_file', ''),
                        'framework': 'django'
                    }
                )
                if suggestion_id:
                    suggestions_created += 1
                    created_suggestions.append({
                        'title': title,
                        'description': description,
                        'category': 'feature',
                        'priority': 'high'
                    })
            
            # 2. Kişisel enflasyon modülü Django uyarlaması
            title = "Kişisel enflasyon modülünü Django web app olarak uyarla"
            description = (
                "1. models.py: User, Category, Product, PriceEntry modellerini oluştur\n"
                "2. views.py: CategoryListView, ProductCreateView, PriceEntryView oluştur\n"
                "3. forms.py: ProductForm, PriceEntryForm, CategoryForm oluştur\n"
                "4. templates/kisiselenflasyon/: base.html, dashboard.html, product_form.html\n"
                "5. CLI'daki hesaplama mantığını Django service layer'a taşı"
            )
            
            suggestion_id = manager.add_suggestion(
                title=title,
                description=description,
                category='feature',
                priority='high',
                source='archive_research',
                metadata={
                    'module': 'kisiselenflasyon',
                    'implementation_steps': True,
                    'report_file': getattr(result, 'report_file', '')
                }
            )
            if suggestion_id:
                suggestions_created += 1
                created_suggestions.append({
                    'title': title,
                    'description': description,
                    'category': 'feature',
                    'priority': 'high'
                })
            
            # 3. PostgreSQL veritabanı entegrasyonu
            title = "PostgreSQL veritabanı şeması ve migration'ları oluştur"
            description = (
                "1. settings.py'de DATABASES konfigürasyonu (PostgreSQL)\n"
                "2. Kullanıcı tablosu: django.contrib.auth.User kullan\n"
                "3. Kategori tablosu: parent-child ilişkisi için MPTT kullan\n"
                "4. Ürün tablosu: kategori foreign key, fiyat history için ayrı tablo\n"
                "5. Initial migration ve seed data scripti hazırla"
            )
            
            suggestion_id = manager.add_suggestion(
                title=title,
                description=description,
                category='feature',
                priority='high',
                source='archive_research',
                metadata={
                    'database': 'postgresql',
                    'implementation_steps': True,
                    'report_file': getattr(result, 'report_file', '')
                }
            )
            if suggestion_id:
                suggestions_created += 1
                created_suggestions.append({
                    'title': title,
                    'description': description,
                    'category': 'feature',
                    'priority': 'high'
                })
            
            # 4. CLI benzeri web arayüzü tasarımı
            title = "Terminal görünümlü modern web arayüzü tasarla"
            description = (
                "1. Static CSS: terminal.css - monospace font, dark theme, neon yeşil text\n"
                "2. JavaScript: terminal-emulator.js - komut satırı simülasyonu\n"
                "3. HTMX entegrasyonu: Sayfa yenileme olmadan dinamik içerik\n"
                "4. ASCII art header ve menü sistemini web'e uyarla\n"
                "5. Keyboard shortcut'ları web için implement et (1,2,3 tuşları menü seçimi)"
            )
            
            suggestion_id = manager.add_suggestion(
                title=title,
                description=description,
                category='feature',
                priority='medium',
                source='archive_research',
                metadata={
                    'ui_design': 'terminal_style',
                    'implementation_steps': True,
                    'report_file': getattr(result, 'report_file', '')
                }
            )
            if suggestion_id:
                suggestions_created += 1
                created_suggestions.append({
                    'title': title,
                    'description': description,
                    'category': 'feature',
                    'priority': 'medium'
                })
            
            # 5. Authentication sistemi
            if web_features['authentication'] or 'kullanıcı' in result.query.lower():
                title = "Django authentication sistemi kurulumu"
                description = (
                    "1. django.contrib.auth entegrasyonu\n"
                    "2. Login/Logout view'ları ve template'leri\n"
                    "3. User registration formu ve email doğrulama\n"
                    "4. Password reset flow implementasyonu\n"
                    "5. User dashboard ve profil sayfaları"
                )
                
                suggestion_id = manager.add_suggestion(
                    title=title,
                    description=description,
                    category='feature',
                    priority='high',
                    source='archive_research',
                    metadata={
                        'security': 'authentication',
                        'implementation_steps': True,
                        'report_file': getattr(result, 'report_file', '')
                    }
                )
                if suggestion_id:
                    suggestions_created += 1
                    created_suggestions.append({
                        'title': title,
                        'description': description,
                        'category': 'feature',
                        'priority': 'high'
                    })
            
            if suggestions_created > 0:
                print(f"{Colors.GREEN}✓ {suggestions_created} adet öneri oluşturuldu{Colors.RESET}")
                print(f"{Colors.GRAY}  (Ajan yapısı kullanılarak oluşturuldu){Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}ℹ️  Bu araştırmadan öneri oluşturulmadı{Colors.RESET}")
            
            return created_suggestions
                
        except ImportError:
            print(f"{Colors.YELLOW}⚠️  PostgreSQL öneri sistemi kullanılamıyor{Colors.RESET}")
            return []
        except Exception as e:
            print(f"{Colors.RED}✗ Öneri oluşturma hatası: {e}{Colors.RESET}")
            return []
    
    def _interactive_session(self, claude_output: str, suggestions: List[Dict], original_query: str):
        """Claude çıktısı sonrası interaktif oturum"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}💬 İnteraktif Mod Aktif{Colors.RESET}")
        print(f"{Colors.GRAY}Claude'un çıktısına göre yeni mesajlar gönderebilirsiniz.{Colors.RESET}")
        print(f"{Colors.GRAY}Komutlar: [1-{len(suggestions)}] öneri seç | 'q' çıkış | 'r' tekrar araştır{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        while True:
            # İnput alanı
            user_input = input(f"\n{Colors.BLUE}📝 Mesajınız: {Colors.RESET}").strip()
            
            if not user_input:
                continue
                
            # Çıkış
            if user_input.lower() == 'q':
                print(f"\n{Colors.YELLOW}İnteraktif moddan çıkılıyor...{Colors.RESET}")
                break
                
            # Tekrar araştır
            elif user_input.lower() == 'r':
                new_query = input(f"\n{Colors.CYAN}Yeni araştırma konusu: {Colors.RESET}").strip()
                if new_query:
                    self._research_with_claude(new_query)
                break
                
            # Numara ile öneri seçimi
            elif user_input.isdigit():
                idx = int(user_input) - 1
                if 0 <= idx < len(suggestions):
                    selected = suggestions[idx]
                    print(f"\n{Colors.GREEN}✅ Seçilen öneri: {selected['title']}{Colors.RESET}")
                    
                    # Claude ile geliştirmeye başla
                    self._develop_suggestion_with_claude(selected, original_query)
                else:
                    print(f"{Colors.RED}❌ Geçersiz öneri numarası{Colors.RESET}")
                    
            # Claude'a ek soru/yorum gönder
            else:
                self._send_followup_to_claude(user_input, claude_output, original_query)
    
    def _develop_suggestion_with_claude(self, suggestion: Dict, original_query: str):
        """Seçilen öneriyi Claude ile geliştir"""
        print(f"\n{Colors.YELLOW}🚀 Claude ile geliştirme başlatılıyor...{Colors.RESET}")
        
        prompt = f"""
Kullanıcı şu öneriyi seçti ve uygulamak istiyor:

**Öneri:** {suggestion['title']}
**Açıklama:** {suggestion['description']}

Orijinal araştırma konusu: "{original_query}"

Bu öneriyi UNIBOS projesinde adım adım uygula:
1. Gerekli dosyaları oluştur/güncelle
2. Kod örneklerini ver
3. Test senaryolarını hazırla
4. Deployment adımlarını açıkla

Her adımı detaylı açıkla ve direkt uygulanabilir kod ver.
"""
        
        try:
            import tempfile
            import subprocess
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                temp_file = f.name
            
            try:
                # Claude CLI ile geliştirme - gerçek zamanlı output
                print(f"\n{Colors.CYAN}Claude geliştirme yapıyor...{Colors.RESET}")
                print(f"{Colors.DIM}{'─'*60}{Colors.RESET}")
                
                process = subprocess.Popen(
                    ['claude', '@' + temp_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Gerçek zamanlı output göster
                development_output = ""
                output_queue = queue.Queue()
                
                def read_dev_output(pipe, pipe_name):
                    for line in iter(pipe.readline, ''):
                        if line:
                            output_queue.put((pipe_name, line))
                    pipe.close()
                
                # Thread'leri başlat
                stdout_thread = threading.Thread(target=read_dev_output, args=(process.stdout, 'stdout'))
                stderr_thread = threading.Thread(target=read_dev_output, args=(process.stderr, 'stderr'))
                stdout_thread.daemon = True
                stderr_thread.daemon = True
                stdout_thread.start()
                stderr_thread.start()
                
                # Timeout için zamanlayıcı
                start_time = time.time()
                timeout = 300  # 5 dakika
                
                # Output'u gerçek zamanlı göster
                while True:
                    # Process bitmiş mi kontrol et
                    if process.poll() is not None:
                        break
                        
                    # Timeout kontrolü
                    if time.time() - start_time > timeout:
                        process.terminate()
                        print(f"\n{Colors.RED}⏱️ Geliştirme timeout (5 dakika){Colors.RESET}")
                        break
                    
                    # Queue'dan output al
                    try:
                        pipe_name, line = output_queue.get(timeout=0.1)
                        if pipe_name == 'stdout':
                            print(line, end='', flush=True)
                            development_output += line
                        elif pipe_name == 'stderr':
                            print(f"{Colors.RED}Error: {line}{Colors.RESET}", end='', flush=True)
                    except queue.Empty:
                        continue
                
                # Thread'lerin bitmesini bekle
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)
                
                if process.returncode == 0:
                    print(f"\n{Colors.DIM}{'─'*60}{Colors.RESET}")
                    print(f"\n{Colors.GREEN}✅ Geliştirme tamamlandı{Colors.RESET}")
                    
                    # Geliştirme sonrası seçenekler
                    print(f"\n{Colors.YELLOW}Ne yapmak istersiniz?{Colors.RESET}")
                    print(f"  1. Başka bir öneri seç")
                    print(f"  2. Bu geliştirmeyi kaydet")
                    print(f"  3. Yeni araştırma yap")
                    print(f"  q. Çıkış")
                    
                    action = input(f"\n{Colors.CYAN}Seçiminiz: {Colors.RESET}").strip()
                    
                    if action == '2':
                        # Geliştirmeyi kaydet
                        self._save_development_to_file(suggestion['title'], development_output)
                else:
                    print(f"{Colors.RED}❌ Claude hatası: {result.stderr}{Colors.RESET}")
                    
            finally:
                import os
                os.unlink(temp_file)
                
        except Exception as e:
            print(f"{Colors.RED}❌ Hata: {e}{Colors.RESET}")
    
    def _send_followup_to_claude(self, message: str, previous_output: str, original_query: str):
        """Claude'a takip sorusu/yorumu gönder"""
        print(f"\n{Colors.YELLOW}🤔 Claude'a iletiliyor...{Colors.RESET}")
        
        prompt = f"""
Önceki araştırma konusu: "{original_query}"

Kullanıcı senin önceki yanıtınla ilgili şunu söylüyor:
"{message}"

Önceki yanıtını göz önünde bulundurarak kullanıcının yeni sorusuna/yorumuna yanıt ver.
Eğer daha spesifik öneriler istiyorsa, daha detaylı öneriler sun.
Eğer bir konuda açıklama istiyorsa, detaylı açıkla.
"""
        
        try:
            import tempfile
            import subprocess
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                temp_file = f.name
            
            try:
                result = subprocess.run(
                    ['claude', '@' + temp_file],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    print(f"\n{Colors.GREEN}Claude yanıtı:{Colors.RESET}\n")
                    print(result.stdout)
                else:
                    print(f"{Colors.RED}❌ Claude hatası: {result.stderr}{Colors.RESET}")
                    
            finally:
                import os
                os.unlink(temp_file)
                
        except Exception as e:
            print(f"{Colors.RED}❌ Hata: {e}{Colors.RESET}")
    
    def _save_development_to_file(self, title: str, content: str):
        """Geliştirmeyi dosyaya kaydet"""
        try:
            # Reports dizini oluştur
            reports_dir = self.base_path / "reports" / "developments"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Dosya adı
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
            filename = f"dev_{timestamp}_{safe_title}.md"
            filepath = reports_dir / filename
            
            # İçeriği kaydet
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Geliştirme: {title}\n\n")
                f.write(f"**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("## Claude Geliştirme Detayları\n\n")
                f.write(content)
            
            print(f"\n{Colors.GREEN}✅ Geliştirme kaydedildi: {filename}{Colors.RESET}")
            
        except Exception as e:
            print(f"{Colors.RED}❌ Kayıt hatası: {e}{Colors.RESET}")
    
    def _handle_timeout_interactive(self, original_query: str):
        """Timeout durumunda interaktif seçenekler"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}⏱️ Zaman Aşımı - Ne yapmak istersiniz?{Colors.RESET}")
        print(f"{Colors.GRAY}1. Daha kısa/spesifik bir soru sor{Colors.RESET}")
        print(f"{Colors.GRAY}2. Farklı bir konu araştır{Colors.RESET}")
        print(f"{Colors.GRAY}3. Çıkış{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        choice = input(f"\n{Colors.BLUE}Seçiminiz (1/2/3): {Colors.RESET}").strip()
        
        if choice == '1':
            print(f"\n{Colors.GRAY}Orijinal soru: {original_query}{Colors.RESET}")
            new_query = input(f"{Colors.CYAN}Daha spesifik sorunuz: {Colors.RESET}").strip()
            if new_query:
                self._research_with_claude(new_query)
        elif choice == '2':
            new_query = input(f"{Colors.CYAN}Yeni araştırma konusu: {Colors.RESET}").strip()
            if new_query:
                self._research_with_claude(new_query)
        # choice == '3' veya başka: çıkış
    
    def _handle_error_interactive(self, original_query: str):
        """Hata durumunda interaktif seçenekler"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}❌ Hata Oluştu - Ne yapmak istersiniz?{Colors.RESET}")
        print(f"{Colors.GRAY}1. Tekrar dene{Colors.RESET}")
        print(f"{Colors.GRAY}2. Farklı bir konu araştır{Colors.RESET}")
        print(f"{Colors.GRAY}3. Çıkış{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        choice = input(f"\n{Colors.BLUE}Seçiminiz (1/2/3): {Colors.RESET}").strip()
        
        if choice == '1':
            self._research_with_claude(original_query)
        elif choice == '2':
            new_query = input(f"{Colors.CYAN}Yeni araştırma konusu: {Colors.RESET}").strip()
            if new_query:
                self._research_with_claude(new_query)
        # choice == '3' veya başka: çıkış
    
    def _handle_no_output_interactive(self, original_query: str):
        """Claude çıktısı olmadığında interaktif seçenekler"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}⚠️ Claude'dan yanıt alınamadı{Colors.RESET}")
        print(f"{Colors.GRAY}1. Tekrar dene{Colors.RESET}")
        print(f"{Colors.GRAY}2. Farklı bir konu araştır{Colors.RESET}")
        print(f"{Colors.GRAY}3. Çıkış{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        choice = input(f"\n{Colors.BLUE}Seçiminiz (1/2/3): {Colors.RESET}").strip()
        
        if choice == '1':
            self._research_with_claude(original_query)
        elif choice == '2':
            new_query = input(f"{Colors.CYAN}Yeni araştırma konusu: {Colors.RESET}").strip()
            if new_query:
                self._research_with_claude(new_query)
        # choice == '3' veya başka: çıkış


def main():
    """Test için ana fonksiyon"""
    agent = ArchiveResearchAgent()
    agent.interactive_research()


if __name__ == "__main__":
    main()