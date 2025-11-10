#!/usr/bin/env python3
"""
🧠 UNIBOS Claude NLP Processor
Claude API üzerinden gerçek doğal dil anlama

Bu sistem kullanıcı komutlarını Claude'a gönderip gerçek anlam çıkarımı yapar.
"""

import json
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path

class ClaudeNLPProcessor:
    """Claude üzerinden doğal dil işleme"""
    
    def __init__(self, claude_cli_path: Optional[str] = None):
        self.claude_cli = claude_cli_path or "claude"
        
    def understand_command(self, user_input: str, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """Kullanıcı komutunu Claude'a gönder ve anlamlandır"""
        
        prompt = f"""Kullanıcı UNIBOS projesi içinde şu komutu verdi: "{user_input}"

Proje bağlamı:
- Kişisel enflasyon modülü: projects/kisiselenflasyon/inflation.py
- Döviz modülü: src/currencies_enhanced.py
- Ana menü: src/main.py
- Git yönetimi: src/git_manager.py

Kullanıcının ne yapmak istediğini anla ve JSON formatında döndür:
{{
    "intent": "search_feature|analyze_code|improve_code|fix_issue",
    "target": "hedef özellik veya modül",
    "module_path": "tam dosya yolu",
    "version_scope": "current|archived|all",
    "specific_action": "yapılması gereken spesifik komut",
    "confidence": 0.0-1.0
}}

Örnek: Eğer kullanıcı "kişisel enflasyon özelliğini eski versiyonlarda ara" derse:
{{
    "intent": "search_feature",
    "target": "kişisel enflasyon",
    "module_path": "projects/kisiselenflasyon/inflation.py",
    "version_scope": "archived",
    "specific_action": "scan-feature \\"kişisel enflasyon\\" projects/kisiselenflasyon/inflation.py all",
    "confidence": 0.95
}}

Sadece JSON döndür, başka açıklama ekleme."""

        try:
            # Claude'a sor
            result = subprocess.run(
                [self.claude_cli, "-m", prompt],
                capture_output=True,
                text=True,
                check=True
            )
            
            # JSON'ı parse et
            response = json.loads(result.stdout.strip())
            return response
            
        except subprocess.CalledProcessError as e:
            print(f"Claude CLI error: {e}")
            # Fallback response
            return {
                "intent": "unknown",
                "target": user_input,
                "module_path": None,
                "version_scope": "current",
                "specific_action": None,
                "confidence": 0.0
            }
        except json.JSONDecodeError:
            print(f"Could not parse Claude response: {result.stdout}")
            return {
                "intent": "unknown",
                "target": user_input,
                "module_path": None,
                "version_scope": "current", 
                "specific_action": None,
                "confidence": 0.0
            }
    
    def generate_agent_plan(self, understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Claude'un anladığına göre ajan planı oluştur"""
        
        prompt = f"""Bu anlama göre hangi ajanları nasıl kullanmalıyım: {json.dumps(understanding, ensure_ascii=False)}

Mevcut ajanlar:
- CODE_ANALYST: Kod analizi
- REFACTOR_SPECIALIST: Kod iyileştirme
- UI_IMPROVER: UI geliştirme
- SECURITY_AUDITOR: Güvenlik kontrolü
- PERFORMANCE_OPTIMIZER: Performans optimizasyonu
- TEST_ENGINEER: Test yazma
- DOCUMENTATION_EXPERT: Dokümantasyon

JSON formatında döndür:
{{
    "primary_agent": "ana ajan",
    "supporting_agents": ["yardımcı ajanlar"],
    "execution_steps": [
        {{"step": 1, "agent": "ajan_adı", "command": "komut", "description": "açıklama"}}
    ]
}}"""

        try:
            result = subprocess.run(
                [self.claude_cli, "-m", prompt],
                capture_output=True,
                text=True,
                check=True
            )
            
            return json.loads(result.stdout.strip())
            
        except Exception as e:
            print(f"Error generating plan: {e}")
            # Basit fallback plan
            return {
                "primary_agent": "CODE_ANALYST",
                "supporting_agents": [],
                "execution_steps": [
                    {
                        "step": 1,
                        "agent": "CODE_ANALYST",
                        "command": understanding.get("specific_action", "analyze src/main.py"),
                        "description": "Analiz yap"
                    }
                ]
            }

# Export
__all__ = ['ClaudeNLPProcessor']