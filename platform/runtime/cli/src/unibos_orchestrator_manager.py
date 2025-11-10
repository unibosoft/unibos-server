#!/usr/bin/env python3
"""
🎯 UNIBOS Orchestrator Manager
Ana orchestrator yönetimi ve singleton pattern

Bu modül tüm sistemde tek bir orchestrator instance'ı kullanılmasını sağlar.
"""

from typing import Optional
from unibos_agent_system import UNIBOSAgentOrchestrator

class OrchestratorManager:
    """Singleton orchestrator yöneticisi"""
    _instance: Optional['OrchestratorManager'] = None
    _orchestrator: Optional[UNIBOSAgentOrchestrator] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, claude_cli=None):
        """Orchestrator'ı başlat"""
        if self._orchestrator is None:
            self._orchestrator = UNIBOSAgentOrchestrator(claude_cli)
        return self._orchestrator
    
    def get_orchestrator(self) -> Optional[UNIBOSAgentOrchestrator]:
        """Mevcut orchestrator'ı getir"""
        return self._orchestrator
    
    def reset(self):
        """Orchestrator'ı sıfırla"""
        self._orchestrator = None

# Global instance
orchestrator_manager = OrchestratorManager()

def get_main_orchestrator(claude_cli=None) -> UNIBOSAgentOrchestrator:
    """Ana orchestrator'ı getir veya oluştur"""
    return orchestrator_manager.initialize(claude_cli)

# Export
__all__ = ['OrchestratorManager', 'orchestrator_manager', 'get_main_orchestrator']