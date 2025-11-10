#!/usr/bin/env python3
"""
📊 UNIBOS Database Models
PostgreSQL veritabanı modelleri - Django uyumlu yapıda
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    create_engine, Column, String, Integer, Text, DateTime, 
    Boolean, Float, JSON, ForeignKey, Enum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import uuid

# Database manager'dan engine'i al
from .db_manager import ENGINE, DB_TYPE

# Base model
Base = declarative_base()

# UUID support for both databases
if DB_TYPE == "postgresql":
    from sqlalchemy.dialects.postgresql import UUID
    UUIDType = UUID(as_uuid=True)
else:
    # SQLite için String olarak UUID
    from sqlalchemy import String
    UUIDType = String(36)

# Enums
class SuggestionStatus(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    ARCHIVED = "archived"

class SuggestionPriority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SuggestionCategory(PyEnum):
    FEATURE = "feature"
    BUG_FIX = "bug_fix"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UI_IMPROVEMENT = "ui_improvement"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    FEATURE_EVOLUTION = "feature_evolution"
    ARCHITECTURE = "architecture"
    TESTING = "testing"

class SuggestionSource(PyEnum):
    MANUAL = "manual"
    AUTO = "auto"
    SCREENSHOT = "screenshot"
    FEATURE_EVOLUTION = "feature_evolution"
    USER = "user"
    AGENT = "agent"

# Models
class Suggestion(Base):
    """Öneri modeli - ana tablo"""
    __tablename__ = 'suggestions'
    
    id = Column(UUIDType, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Enum(SuggestionPriority), default=SuggestionPriority.MEDIUM)
    category = Column(Enum(SuggestionCategory), nullable=False)
    status = Column(Enum(SuggestionStatus), default=SuggestionStatus.PENDING)
    source = Column(Enum(SuggestionSource), default=SuggestionSource.AUTO)
    
    # Zaman damgaları
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # İlişkili veriler
    estimated_hours = Column(Float, default=1.0)
    actual_hours = Column(Float, nullable=True)
    
    # JSON alanlar
    meta_data = Column(JSON, default=dict)
    implementation_plan = Column(JSON, default=list)
    results = Column(JSON, default=dict)
    agent_assignments = Column(JSON, default=list)
    
    # Version tracking
    from_version = Column(String(20), nullable=True)  # Hangi versiyondan geldi
    implemented_version = Column(String(20), nullable=True)  # Hangi versiyonda uygulandı
    
    # İlişkiler
    sessions = relationship("DevelopmentSession", back_populates="suggestion", cascade="all, delete-orphan")
    implementations = relationship("Implementation", back_populates="suggestion", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_status_priority', 'status', 'priority'),
        Index('idx_category', 'category'),
        Index('idx_created_at', 'created_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Django serializer uyumlu dict çıktısı"""
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'category': self.category.value,
            'status': self.status.value,
            'source': self.source.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'metadata': self.meta_data,
            'implementation_plan': self.implementation_plan,
            'results': self.results,
            'agent_assignments': self.agent_assignments,
            'from_version': self.from_version,
            'implemented_version': self.implemented_version,
        }

class DevelopmentSession(Base):
    """Geliştirme oturumu modeli"""
    __tablename__ = 'development_sessions'
    
    id = Column(UUIDType, primary_key=True, default=lambda: str(uuid.uuid4()))
    suggestion_id = Column(UUIDType, ForeignKey('suggestions.id'), nullable=False)
    
    # Oturum bilgileri
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    
    status = Column(String(50), default='active')  # active, paused, completed, abandoned
    conversation_file = Column(String(255), nullable=True)
    
    # JSON alanlar
    context = Column(JSON, default=dict)
    progress_notes = Column(JSON, default=list)
    messages = Column(JSON, default=list)
    
    # İlişkiler
    suggestion = relationship("Suggestion", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_session_status', 'status'),
        Index('idx_last_activity', 'last_activity'),
    )

class Implementation(Base):
    """Uygulama detayları modeli"""
    __tablename__ = 'implementations'
    
    id = Column(UUIDType, primary_key=True, default=lambda: str(uuid.uuid4()))
    suggestion_id = Column(UUIDType, ForeignKey('suggestions.id'), nullable=False)
    
    # Uygulama detayları
    implemented_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    implemented_by = Column(String(100), default='system')
    
    # Değişiklik detayları
    files_changed = Column(JSON, default=list)
    lines_added = Column(Integer, default=0)
    lines_removed = Column(Integer, default=0)
    
    # Commit bilgileri
    commit_hash = Column(String(40), nullable=True)
    commit_message = Column(Text, nullable=True)
    
    # Test sonuçları
    tests_passed = Column(Boolean, default=True)
    test_results = Column(JSON, default=dict)
    
    # İlişkiler
    suggestion = relationship("Suggestion", back_populates="implementations")

class SuggestionPool(Base):
    """Öneri havuzu - henüz aktif olmayan öneriler"""
    __tablename__ = 'suggestion_pool'
    
    id = Column(UUIDType, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)
    source = Column(String(50), default='auto')
    
    # Analiz verileri
    difficulty_score = Column(Float, nullable=True)  # 1-10 arası zorluk
    confidence_score = Column(Float, nullable=True)  # 0-1 arası güven
    
    # Metadata
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    promoted_at = Column(DateTime, nullable=True)
    
    # Durum
    is_promoted = Column(Boolean, default=False)
    promoted_suggestion_id = Column(UUIDType, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_pool_source', 'source'),
        Index('idx_pool_promoted', 'is_promoted'),
    )

# Veritabanı tabloları oluşturma
def create_tables():
    """Tüm tabloları oluştur"""
    Base.metadata.create_all(ENGINE)

# Django migration uyumluluğu için
def get_django_models():
    """Django model tanımları için dict döndür"""
    return {
        'Suggestion': {
            'db_table': 'suggestions',
            'fields': {
                'id': 'UUIDField(primary_key=True, default=uuid.uuid4)',
                'title': 'CharField(max_length=255)',
                'description': 'TextField()',
                'priority': 'CharField(max_length=20, choices=...)',
                'category': 'CharField(max_length=50, choices=...)',
                'status': 'CharField(max_length=20, choices=...)',
                'source': 'CharField(max_length=50, choices=...)',
                'created_at': 'DateTimeField(auto_now_add=True)',
                'updated_at': 'DateTimeField(auto_now=True)',
                'completed_at': 'DateTimeField(null=True, blank=True)',
                'estimated_hours': 'FloatField(default=1.0)',
                'actual_hours': 'FloatField(null=True, blank=True)',
                'meta_data': 'JSONField(default=dict)',
                'implementation_plan': 'JSONField(default=list)',
                'results': 'JSONField(default=dict)',
                'agent_assignments': 'JSONField(default=list)',
                'from_version': 'CharField(max_length=20, null=True, blank=True)',
                'implemented_version': 'CharField(max_length=20, null=True, blank=True)',
            }
        },
        # Diğer modeller...
    }

if __name__ == "__main__":
    # Test için tabloları oluştur
    create_tables()
    print("Database tables created successfully!")