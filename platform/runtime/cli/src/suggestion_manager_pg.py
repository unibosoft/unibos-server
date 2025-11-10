#!/usr/bin/env python3
"""
💡 UNIBOS PostgreSQL Suggestion Manager
PostgreSQL tabanlı gelişmiş öneri yönetim sistemi
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import uuid

from sqlalchemy.orm import Session as SessionType
from sqlalchemy import and_, or_, func

# Database imports
from database.models import (
    Base, Suggestion, DevelopmentSession, Implementation, SuggestionPool,
    SuggestionStatus, SuggestionPriority, SuggestionCategory, SuggestionSource,
    create_tables
)
from database.db_manager import Session, DB_TYPE

# UNIBOS imports
from unibos_orchestrator_manager import get_main_orchestrator
try:
    from unibos_logger import logger, LogCategory
except ImportError:
    class logger:
        @staticmethod
        def info(msg, **kwargs): print(f"INFO: {msg}")
        @staticmethod
        def error(msg, **kwargs): print(f"ERROR: {msg}")
        @staticmethod
        def warning(msg, **kwargs): print(f"WARNING: {msg}")

class PostgreSQLSuggestionManager:
    """PostgreSQL tabanlı öneri yöneticisi"""
    
    def __init__(self):
        # Veritabanı oturumu
        self.session: SessionType = Session()
        
        # Tabloları oluştur (ilk çalıştırmada)
        try:
            create_tables()
        except Exception as e:
            logger.warning(f"Tables might already exist: {e}")
        
        # Legacy uyumluluk için json dosyası kontrolü
        self._migrate_from_json_if_exists()
    
    def _migrate_from_json_if_exists(self):
        """Eski JSON dosyasından verileri PostgreSQL'e taşı"""
        json_file = Path("data/suggestions.json")
        migration_flag = Path("data/.pg_migration_done")
        
        if json_file.exists() and not migration_flag.exists():
            try:
                logger.info("Migrating suggestions from JSON to PostgreSQL...")
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for sid, sdata in data.items():
                        # Mevcut öneriyi kontrol et
                        existing = self.session.query(Suggestion).filter_by(
                            title=sdata.get('text', sdata.get('title', ''))
                        ).first()
                        
                        if not existing:
                            # Yeni öneri oluştur
                            suggestion = Suggestion(
                                title=sdata.get('text', sdata.get('title', '')),
                                description=sdata.get('description', sdata.get('text', '')),
                                category=self._map_category(sdata.get('category', 'feature')),
                                priority=self._map_priority(sdata.get('priority', 'medium')),
                                status=self._map_status(sdata.get('status', 'pending')),
                                meta_data=sdata.get('metadata', {}),
                                implementation_plan=sdata.get('implementation_plan', []),
                                results=sdata.get('results', {}),
                                agent_assignments=sdata.get('agent_assignments', []),
                                created_at=datetime.fromisoformat(sdata['created_at']) if 'created_at' in sdata else datetime.utcnow()
                            )
                            self.session.add(suggestion)
                
                self.session.commit()
                
                # Migration flag oluştur
                migration_flag.parent.mkdir(parents=True, exist_ok=True)
                migration_flag.touch()
                logger.info(f"Migration completed. Migrated {len(data)} suggestions.")
                
            except Exception as e:
                logger.error(f"Error during migration: {e}")
                self.session.rollback()
    
    def _map_category(self, category: str) -> SuggestionCategory:
        """String kategoriyi enum'a çevir"""
        category_map = {
            'feature': SuggestionCategory.FEATURE,
            'bug_fix': SuggestionCategory.BUG_FIX,
            'performance': SuggestionCategory.PERFORMANCE,
            'security': SuggestionCategory.SECURITY,
            'ui_improvement': SuggestionCategory.UI_IMPROVEMENT,
            'refactoring': SuggestionCategory.REFACTORING,
            'documentation': SuggestionCategory.DOCUMENTATION,
            'feature_evolution': SuggestionCategory.FEATURE_EVOLUTION,
            'architecture': SuggestionCategory.ARCHITECTURE,
            'testing': SuggestionCategory.TESTING,
        }
        return category_map.get(category, SuggestionCategory.FEATURE)
    
    def _map_priority(self, priority: str) -> SuggestionPriority:
        """String önceliği enum'a çevir"""
        priority_map = {
            'low': SuggestionPriority.LOW,
            'medium': SuggestionPriority.MEDIUM,
            'high': SuggestionPriority.HIGH,
            'critical': SuggestionPriority.CRITICAL,
        }
        return priority_map.get(priority, SuggestionPriority.MEDIUM)
    
    def _map_status(self, status: str) -> SuggestionStatus:
        """String durumu enum'a çevir"""
        status_map = {
            'pending': SuggestionStatus.PENDING,
            'in_progress': SuggestionStatus.IN_PROGRESS,
            'completed': SuggestionStatus.COMPLETED,
            'rejected': SuggestionStatus.REJECTED,
            'failed': SuggestionStatus.FAILED,
            'archived': SuggestionStatus.ARCHIVED,
        }
        return status_map.get(status, SuggestionStatus.PENDING)
    
    def add_suggestion(self, title: str, description: str, category: str, 
                      priority: str = "medium", source: str = "auto",
                      metadata: Optional[Dict] = None) -> str:
        """Yeni öneri ekle"""
        try:
            suggestion = Suggestion(
                title=title,
                description=description,
                category=self._map_category(category),
                priority=self._map_priority(priority),
                source=SuggestionSource(source) if hasattr(SuggestionSource, source.upper()) else SuggestionSource.AUTO,
                meta_data=metadata or {}
            )
            
            # Agent orchestrator ile plan oluştur
            orchestrator = get_main_orchestrator()
            if orchestrator:
                # Öneri için uygun agent'ları belirle
                agents = self._determine_agents_for_suggestion(suggestion)
                suggestion.agent_assignments = agents
                
                # Implementasyon planı oluştur
                plan = self._create_implementation_plan(suggestion)
                suggestion.implementation_plan = plan
            
            self.session.add(suggestion)
            self.session.commit()
            
            logger.info(f"Suggestion added: {suggestion.id} - {title[:50]}...")
            return str(suggestion.id)
            
        except Exception as e:
            logger.error(f"Error adding suggestion: {e}")
            self.session.rollback()
            raise
    
    def add_to_pool(self, text: str, category: Optional[str] = None,
                   source: str = "auto", metadata: Optional[Dict] = None) -> str:
        """Öneri havuzuna ekle"""
        try:
            pool_item = SuggestionPool(
                text=text,
                category=category,
                source=source,
                meta_data=metadata or {}
            )
            
            self.session.add(pool_item)
            self.session.commit()
            
            logger.info(f"Added to suggestion pool: {text[:50]}...")
            return str(pool_item.id)
            
        except Exception as e:
            logger.error(f"Error adding to pool: {e}")
            self.session.rollback()
            raise
    
    def promote_from_pool(self, pool_id: str, title: Optional[str] = None,
                         description: Optional[str] = None) -> Optional[str]:
        """Havuzdan öneriyi aktif listeye taşı"""
        try:
            pool_item = self.session.query(SuggestionPool).filter_by(
                id=UUID(pool_id)
            ).first()
            
            if not pool_item or pool_item.is_promoted:
                return None
            
            # Öneri oluştur
            suggestion = Suggestion(
                title=title or pool_item.text[:100],
                description=description or pool_item.text,
                category=self._map_category(pool_item.category or 'feature'),
                source=SuggestionSource.AUTO,
                meta_data={
                    **pool_item.meta_data,
                    'promoted_from_pool': str(pool_item.id),
                    'pool_source': pool_item.source
                }
            )
            
            self.session.add(suggestion)
            
            # Pool item'ı güncelle
            pool_item.is_promoted = True
            pool_item.promoted_at = datetime.utcnow()
            pool_item.promoted_suggestion_id = suggestion.id
            
            self.session.commit()
            
            logger.info(f"Promoted from pool: {suggestion.id}")
            return str(suggestion.id)
            
        except Exception as e:
            logger.error(f"Error promoting from pool: {e}")
            self.session.rollback()
            return None
    
    def get_pool_items(self, source: Optional[str] = None, 
                      not_promoted: bool = True) -> List[Dict]:
        """Havuzdaki önerileri getir"""
        query = self.session.query(SuggestionPool)
        
        if source:
            query = query.filter_by(source=source)
        
        if not_promoted:
            query = query.filter_by(is_promoted=False)
        
        items = query.order_by(SuggestionPool.created_at.desc()).all()
        
        return [
            {
                'id': str(item.id),
                'text': item.text,
                'category': item.category,
                'source': item.source,
                'metadata': item.meta_data,
                'created_at': item.created_at.isoformat(),
                'difficulty_score': item.difficulty_score,
                'confidence_score': item.confidence_score,
            }
            for item in items
        ]
    
    def _determine_agents_for_suggestion(self, suggestion: Suggestion) -> List[str]:
        """Öneri için uygun agent'ları belirle"""
        category_agent_map = {
            SuggestionCategory.FEATURE: ["REFACTOR_SPECIALIST", "UI_IMPROVER"],
            SuggestionCategory.BUG_FIX: ["CODE_ANALYST", "REFACTOR_SPECIALIST"],
            SuggestionCategory.PERFORMANCE: ["PERFORMANCE_OPTIMIZER", "CODE_ANALYST"],
            SuggestionCategory.SECURITY: ["SECURITY_AUDITOR"],
            SuggestionCategory.UI_IMPROVEMENT: ["UI_IMPROVER", "CLAUDE_ENHANCER"],
            SuggestionCategory.REFACTORING: ["REFACTOR_SPECIALIST", "CODE_ANALYST"],
            SuggestionCategory.DOCUMENTATION: ["DOCUMENTATION_EXPERT"],
            SuggestionCategory.FEATURE_EVOLUTION: ["CODE_ANALYST", "REFACTOR_SPECIALIST", "UI_IMPROVER"],
            SuggestionCategory.ARCHITECTURE: ["CODE_ANALYST", "REFACTOR_SPECIALIST"],
            SuggestionCategory.TESTING: ["CODE_ANALYST", "SECURITY_AUDITOR"],
        }
        
        agents = category_agent_map.get(suggestion.category, ["CODE_ANALYST"])
        
        # Metadata'ya göre ek agent'lar
        if suggestion.meta_data.get('type') == 'UI_ENHANCEMENT':
            if "UI_IMPROVER" not in agents:
                agents.append("UI_IMPROVER")
        
        return agents
    
    def _create_implementation_plan(self, suggestion: Suggestion) -> List[str]:
        """Öneri için implementasyon planı oluştur"""
        plan = []
        
        # Temel adımlar
        module = suggestion.meta_data.get('module', 'main.py')
        plan.append(f"1. Analyze current implementation ({module})")
        plan.append(f"2. Review suggestion: {suggestion.title[:100]}")
        
        # Agent'lara göre adımlar ekle
        for i, agent in enumerate(suggestion.agent_assignments, 3):
            if agent == "CODE_ANALYST":
                plan.append(f"{i}. Code analysis and issue identification")
            elif agent == "REFACTOR_SPECIALIST":
                plan.append(f"{i}. Refactor and improve code structure")
            elif agent == "UI_IMPROVER":
                plan.append(f"{i}. Enhance UI/UX elements")
            elif agent == "PERFORMANCE_OPTIMIZER":
                plan.append(f"{i}. Optimize performance")
            elif agent == "SECURITY_AUDITOR":
                plan.append(f"{i}. Security audit and fixes")
        
        plan.append("X. Test and validate changes")
        plan.append("Y. Create commit with changes")
        
        return plan
    
    def execute_suggestion(self, suggestion_id: str) -> bool:
        """Öneriyi agent orchestrator üzerinden gerçekleştir"""
        try:
            suggestion = self.session.query(Suggestion).filter_by(
                id=UUID(suggestion_id)
            ).first()
            
            if not suggestion:
                logger.error(f"Suggestion not found: {suggestion_id}")
                return False
            
            # Zaten tamamlanmış veya devam eden mi kontrol et
            if suggestion.status in [SuggestionStatus.COMPLETED, SuggestionStatus.IN_PROGRESS]:
                logger.info(f"Suggestion already {suggestion.status.value}: {suggestion_id}")
                return False
            
            # Durumu güncelle
            suggestion.status = SuggestionStatus.IN_PROGRESS
            self.session.commit()
            
            # Agent orchestrator'ı al
            orchestrator = get_main_orchestrator()
            if not orchestrator:
                logger.error("Orchestrator not available")
                suggestion.status = SuggestionStatus.FAILED
                self.session.commit()
                return False
            
            # Her agent için görevi çalıştır
            for agent_name in suggestion.agent_assignments:
                logger.info(f"Executing with agent: {agent_name}")
                
                # Agent'a göre komut oluştur
                if suggestion.meta_data.get('module'):
                    module = suggestion.meta_data['module']
                    
                    # Agent'a göre uygun komutu belirle
                    if agent_name == "CODE_ANALYST":
                        result = orchestrator.analyze_module(module)
                    elif agent_name == "REFACTOR_SPECIALIST":
                        # Refactoring önerileri
                        from unibos_agent_system import AgentRole
                        agent = orchestrator.agents.get(AgentRole.REFACTOR_SPECIALIST)
                        if agent:
                            context = agent.analyze_codebase(module)
                            result = agent.generate_improvement_plan()
                    else:
                        # Diğer agent'lar için genel analiz
                        result = {"status": "analyzed"}
                    
                    # Sonuçları kaydet
                    if not suggestion.results:
                        suggestion.results = {}
                    suggestion.results[agent_name] = result
            
            # Başarılı tamamlandı
            suggestion.status = SuggestionStatus.COMPLETED
            suggestion.completed_at = datetime.utcnow()
            self.session.commit()
            
            logger.info(f"Suggestion completed: {suggestion_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error executing suggestion: {e}")
            if suggestion:
                suggestion.status = SuggestionStatus.FAILED
                if not suggestion.results:
                    suggestion.results = {}
                suggestion.results['error'] = str(e)
            self.session.commit()
            return False
    
    def get_suggestions(self, status: Optional[str] = None,
                       category: Optional[str] = None,
                       priority: Optional[str] = None,
                       limit: int = 100) -> List[Dict]:
        """Önerileri filtrele ve getir"""
        query = self.session.query(Suggestion)
        
        if status:
            query = query.filter_by(status=self._map_status(status))
        
        if category:
            query = query.filter_by(category=self._map_category(category))
        
        if priority:
            query = query.filter_by(priority=self._map_priority(priority))
        
        suggestions = query.order_by(
            Suggestion.priority.desc(),
            Suggestion.created_at.desc()
        ).limit(limit).all()
        
        return [s.to_dict() for s in suggestions]
    
    def get_pending_suggestions(self) -> List[Dict]:
        """Bekleyen önerileri getir"""
        return self.get_suggestions(status='pending')
    
    def get_suggestions_by_category(self, category: str) -> List[Dict]:
        """Kategoriye göre önerileri getir"""
        return self.get_suggestions(category=category)
    
    def update_suggestion_status(self, suggestion_id: str, status: str,
                               implementation: Optional[Dict] = None):
        """Öneri durumunu güncelle"""
        try:
            suggestion = self.session.query(Suggestion).filter_by(
                id=UUID(suggestion_id)
            ).first()
            
            if not suggestion:
                logger.error(f"Suggestion not found: {suggestion_id}")
                return False
            
            suggestion.status = self._map_status(status)
            suggestion.updated_at = datetime.utcnow()
            
            if status == 'completed':
                suggestion.completed_at = datetime.utcnow()
                
                # Implementation kaydı oluştur
                if implementation:
                    impl = Implementation(
                        suggestion_id=suggestion.id,
                        files_changed=implementation.get('files_changed', []),
                        lines_added=implementation.get('lines_added', 0),
                        lines_removed=implementation.get('lines_removed', 0),
                        commit_hash=implementation.get('commit_hash'),
                        commit_message=implementation.get('commit_message'),
                        tests_passed=implementation.get('tests_passed', True),
                        test_results=implementation.get('test_results', {})
                    )
                    self.session.add(impl)
            
            self.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating suggestion status: {e}")
            self.session.rollback()
            return False
    
    def get_suggestion_stats(self) -> Dict[str, Any]:
        """Öneri istatistiklerini getir"""
        try:
            total = self.session.query(func.count(Suggestion.id)).scalar()
            
            status_counts = dict(
                self.session.query(
                    Suggestion.status, func.count(Suggestion.id)
                ).group_by(Suggestion.status).all()
            )
            
            category_counts = dict(
                self.session.query(
                    Suggestion.category, func.count(Suggestion.id)
                ).group_by(Suggestion.category).all()
            )
            
            priority_counts = dict(
                self.session.query(
                    Suggestion.priority, func.count(Suggestion.id)
                ).group_by(Suggestion.priority).all()
            )
            
            # Pool istatistikleri
            pool_total = self.session.query(func.count(SuggestionPool.id)).scalar()
            pool_not_promoted = self.session.query(
                func.count(SuggestionPool.id)
            ).filter_by(is_promoted=False).scalar()
            
            return {
                'total': total,
                'status': {s.value: status_counts.get(s, 0) for s in SuggestionStatus},
                'category': {c.value: category_counts.get(c, 0) for c in SuggestionCategory},
                'priority': {p.value: priority_counts.get(p, 0) for p in SuggestionPriority},
                'pool': {
                    'total': pool_total,
                    'not_promoted': pool_not_promoted,
                    'promoted': pool_total - pool_not_promoted
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def create_development_session(self, suggestion_id: str, context: Optional[Dict] = None) -> str:
        """Geliştirme oturumu oluştur"""
        try:
            session = DevelopmentSession(
                suggestion_id=UUID(suggestion_id),
                context=context or {}
            )
            
            self.session.add(session)
            self.session.commit()
            
            return str(session.id)
            
        except Exception as e:
            logger.error(f"Error creating development session: {e}")
            self.session.rollback()
            raise
    
    def update_development_session(self, session_id: str, message: Dict,
                                 progress_notes: Optional[str] = None):
        """Geliştirme oturumunu güncelle"""
        try:
            dev_session = self.session.query(DevelopmentSession).filter_by(
                id=UUID(session_id)
            ).first()
            
            if not dev_session:
                return False
            
            dev_session.last_activity = datetime.utcnow()
            
            if not dev_session.messages:
                dev_session.messages = []
            dev_session.messages.append(message)
            
            if progress_notes:
                if not dev_session.progress_notes:
                    dev_session.progress_notes = []
                dev_session.progress_notes.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'note': progress_notes
                })
            
            self.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating development session: {e}")
            self.session.rollback()
            return False
    
    def get_resumable_sessions(self, days: int = 7) -> List[Dict]:
        """Devam edilebilir oturumları getir"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        sessions = self.session.query(DevelopmentSession).filter(
            and_(
                DevelopmentSession.status.in_(['active', 'paused']),
                DevelopmentSession.last_activity > cutoff
            )
        ).order_by(DevelopmentSession.last_activity.desc()).all()
        
        return [
            {
                'id': str(s.id),
                'suggestion_id': str(s.suggestion_id),
                'suggestion_title': s.suggestion.title if s.suggestion else 'Unknown',
                'started_at': s.started_at.isoformat(),
                'last_activity': s.last_activity.isoformat(),
                'status': s.status,
                'progress_notes': s.progress_notes,
            }
            for s in sessions
        ]
    
    def close(self):
        """Veritabanı bağlantısını kapat"""
        self.session.close()

# Global instance
pg_suggestion_manager = PostgreSQLSuggestionManager()

# Export
__all__ = ['PostgreSQLSuggestionManager', 'pg_suggestion_manager']