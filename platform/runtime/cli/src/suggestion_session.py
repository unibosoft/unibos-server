#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Suggestion Session Manager - Persistent development sessions
Tracks and resumes interrupted development sessions

Author: berk hatırlı
Version: v1.0
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, asdict
from enum import Enum

class SessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

@dataclass
class DevelopmentSession:
    suggestion_id: int
    suggestion_title: str
    started_at: datetime
    last_activity: datetime
    status: SessionStatus
    conversation_file: Optional[str] = None
    context: Optional[Dict] = None
    progress_notes: Optional[str] = None
    
    def to_dict(self):
        data = asdict(self)
        data['started_at'] = self.started_at.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data):
        data['started_at'] = datetime.fromisoformat(data['started_at'])
        data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        data['status'] = SessionStatus(data['status'])
        return cls(**data)

class SuggestionSessionManager:
    """Manages persistent development sessions"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.session_dir = db_path.parent / 'sessions'
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.active_session_file = self.session_dir / 'active_session.json'
    
    def create_session(self, suggestion_id: int, suggestion_title: str, 
                      initial_prompt: str) -> DevelopmentSession:
        """Create a new development session"""
        now = datetime.now()
        conversation_file = f"conversation_{suggestion_id}_{now.strftime('%Y%m%d_%H%M%S')}.json"
        
        session = DevelopmentSession(
            suggestion_id=suggestion_id,
            suggestion_title=suggestion_title,
            started_at=now,
            last_activity=now,
            status=SessionStatus.ACTIVE,
            conversation_file=conversation_file,
            context={'initial_prompt': initial_prompt}
        )
        
        # Save session to database
        self._save_to_db(session)
        
        # Mark as active session
        self._save_active_session(session)
        
        # Initialize conversation file
        conversation_path = self.session_dir / conversation_file
        with open(conversation_path, 'w') as f:
            json.dump({
                'suggestion_id': suggestion_id,
                'title': suggestion_title,
                'started_at': now.isoformat(),
                'messages': [
                    {
                        'role': 'user',
                        'content': initial_prompt,
                        'timestamp': now.isoformat()
                    }
                ]
            }, f, indent=2)
        
        return session
    
    def update_session(self, suggestion_id: int, message: Dict, 
                      progress_notes: Optional[str] = None):
        """Update session with new activity"""
        session = self.get_active_session()
        if not session or session.suggestion_id != suggestion_id:
            return
        
        session.last_activity = datetime.now()
        if progress_notes:
            session.progress_notes = progress_notes
        
        # Update conversation file
        if session.conversation_file:
            conversation_path = self.session_dir / session.conversation_file
            if conversation_path.exists():
                with open(conversation_path, 'r') as f:
                    data = json.load(f)
                
                data['messages'].append({
                    **message,
                    'timestamp': datetime.now().isoformat()
                })
                
                with open(conversation_path, 'w') as f:
                    json.dump(data, f, indent=2)
        
        # Update database
        self._update_db(session)
        self._save_active_session(session)
    
    def get_active_session(self) -> Optional[DevelopmentSession]:
        """Get current active session"""
        if not self.active_session_file.exists():
            return None
        
        try:
            with open(self.active_session_file, 'r') as f:
                data = json.load(f)
            return DevelopmentSession.from_dict(data)
        except:
            return None
    
    def pause_session(self, suggestion_id: int):
        """Pause a session (e.g., on Claude timeout or user interrupt)"""
        session = self.get_active_session()
        if session and session.suggestion_id == suggestion_id:
            session.status = SessionStatus.PAUSED
            session.last_activity = datetime.now()
            self._update_db(session)
            self._save_active_session(session)
    
    def complete_session(self, suggestion_id: int):
        """Mark session as completed"""
        session = self.get_active_session()
        if session and session.suggestion_id == suggestion_id:
            session.status = SessionStatus.COMPLETED
            session.last_activity = datetime.now()
            self._update_db(session)
            
            # Remove active session file
            if self.active_session_file.exists():
                self.active_session_file.unlink()
    
    def abandon_session(self, suggestion_id: int):
        """Abandon a session"""
        session = self.get_active_session()
        if session and session.suggestion_id == suggestion_id:
            session.status = SessionStatus.ABANDONED
            session.last_activity = datetime.now()
            self._update_db(session)
            
            # Remove active session file
            if self.active_session_file.exists():
                self.active_session_file.unlink()
    
    def get_resumable_sessions(self) -> List[DevelopmentSession]:
        """Get all sessions that can be resumed"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, s.title as suggestion_title
            FROM active_sessions a
            JOIN suggestions s ON a.suggestion_id = s.id
            WHERE a.status IN ('active', 'paused')
            AND datetime(a.last_activity) > datetime('now', '-7 days')
            ORDER BY a.last_activity DESC
        ''')
        
        sessions = []
        for row in cursor.fetchall():
            session_data = {
                'suggestion_id': row['suggestion_id'],
                'suggestion_title': row['suggestion_title'],
                'started_at': row['started_at'],
                'last_activity': row['last_activity'],
                'status': row['status'],
                'conversation_file': row['conversation_file'],
                'context': json.loads(row['context']) if row['context'] else None,
                'progress_notes': row['progress_notes']
            }
            sessions.append(DevelopmentSession.from_dict(session_data))
        
        conn.close()
        return sessions
    
    def get_session_conversation(self, session: DevelopmentSession) -> Optional[Dict]:
        """Get conversation history for a session"""
        if not session.conversation_file:
            return None
        
        conversation_path = self.session_dir / session.conversation_file
        if not conversation_path.exists():
            return None
        
        with open(conversation_path, 'r') as f:
            return json.load(f)
    
    def _save_to_db(self, session: DevelopmentSession):
        """Save session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO active_sessions 
            (suggestion_id, started_at, last_activity, status, 
             conversation_file, context, progress_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.suggestion_id,
            session.started_at.isoformat(),
            session.last_activity.isoformat(),
            session.status.value,
            session.conversation_file,
            json.dumps(session.context) if session.context else None,
            session.progress_notes
        ))
        
        conn.commit()
        conn.close()
    
    def _update_db(self, session: DevelopmentSession):
        """Update session in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE active_sessions 
            SET last_activity = ?, status = ?, progress_notes = ?
            WHERE suggestion_id = ?
        ''', (
            session.last_activity.isoformat(),
            session.status.value,
            session.progress_notes,
            session.suggestion_id
        ))
        
        conn.commit()
        conn.close()
    
    def _save_active_session(self, session: DevelopmentSession):
        """Save session as the active session"""
        with open(self.active_session_file, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)