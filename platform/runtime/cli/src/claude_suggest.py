#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Claude Suggest - Modern suggestion-based development system
A clean, efficient development assistant for UNIBOS

Author: berk hatırlı
Version: v1.0
"""

import os
import sys
import json
import subprocess
import time
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Import session manager
try:
    from suggestion_session import SuggestionSessionManager, SessionStatus
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    SESSION_MANAGER_AVAILABLE = False

# Import agent system
try:
    from unibos_agent_system import UNIBOSAgent, UNIBOSAgentOrchestrator, AgentRole
    AGENT_SYSTEM_AVAILABLE = True
except ImportError:
    AGENT_SYSTEM_AVAILABLE = False
    print(f"[DEBUG] Agent system not available - create unibos_agent_system.py in src/")

# Color codes for terminal
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    ORANGE = '\033[38;5;208m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

class Priority(Enum):
    LOW = "🟢"
    MEDIUM = "🟡"
    HIGH = "🟠"
    CRITICAL = "🔴"

class Status(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Suggestion:
    id: int
    title: str
    description: str
    priority: Priority
    category: str
    estimated_hours: float
    created_at: datetime
    status: Status = Status.PENDING
    completed_at: Optional[datetime] = None
    implementation: Optional[str] = None
    
    def to_dict(self):
        data = asdict(self)
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data

class ClaudeSuggest:
    """Modern suggestion-based development system"""
    
    def __init__(self):
        self.db_path = Path.home() / '.unibos' / 'suggestions.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        self.claude_available = self.check_claude_cli()
        
        # Initialize session manager if available
        if SESSION_MANAGER_AVAILABLE:
            self.session_manager = SuggestionSessionManager(self.db_path)
            self.check_resumable_sessions()
        else:
            self.session_manager = None
        
        # Initialize agent system if available
        if AGENT_SYSTEM_AVAILABLE:
            self.agent_orchestrator = UNIBOSAgentOrchestrator(self)
            print(f"{Colors.DIM}[DEBUG] Agent system initialized{Colors.RESET}")
        else:
            self.agent_orchestrator = None
        
        # Debug: Show DB path
        # print(f"[DEBUG] Using database: {self.db_path}")
        
    def init_database(self):
        """Initialize SQLite database for suggestions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                estimated_hours REAL NOT NULL,
                created_at TIMESTAMP NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                completed_at TIMESTAMP,
                implementation TEXT
            )
        ''')
        
        # Add active_sessions table for session tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                suggestion_id INTEGER NOT NULL,
                started_at TIMESTAMP NOT NULL,
                last_activity TIMESTAMP NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                conversation_file TEXT,
                context TEXT,
                progress_notes TEXT,
                FOREIGN KEY (suggestion_id) REFERENCES suggestions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_claude_cli(self) -> bool:
        """Check if Claude CLI is available"""
        try:
            result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def check_resumable_sessions(self):
        """Check for sessions that can be resumed"""
        if not self.session_manager:
            return
        
        sessions = self.session_manager.get_resumable_sessions()
        if sessions:
            print(f"\n{Colors.YELLOW}📌 Resumable development sessions found:{Colors.RESET}")
            for i, session in enumerate(sessions[:3], 1):
                time_diff = datetime.now() - session.last_activity
                hours_ago = time_diff.total_seconds() / 3600
                
                print(f"\n{i}. {Colors.BOLD}{session.suggestion_title}{Colors.RESET}")
                print(f"   Status: {session.status.value}")
                print(f"   Last activity: {hours_ago:.1f} hours ago")
                if session.progress_notes:
                    print(f"   Progress: {session.progress_notes[:50]}...")
            
            print(f"\n{Colors.CYAN}Resume a session? (1-{len(sessions[:3])}/n):{Colors.RESET} ", end='', flush=True)
            choice = input().strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(sessions[:3]):
                session = sessions[int(choice) - 1]
                self.resume_development_session(session)
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Show application header"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔════════════════════════════════════════════╗")
        print("║        🎯 CLAUDE SUGGEST v1.0              ║")
        print("║    Modern Development Assistant            ║")
        print("╚════════════════════════════════════════════╝")
        print(f"{Colors.RESET}\n")
    
    def analyze_codebase(self) -> List[Dict]:
        """Analyze codebase and generate suggestions"""
        print(f"{Colors.YELLOW}🔍 Analyzing codebase...{Colors.RESET}")
        
        suggestions = []
        
        # Quick analysis of common improvement areas
        checks = [
            ("Error Handling", "find . -name '*.py' -exec grep -l 'except:' {} \\; | wc -l"),
            ("TODO Comments", "find . -name '*.py' -exec grep -l 'TODO\\|FIXME' {} \\; | wc -l"),
            ("Long Functions", "find . -name '*.py' -exec grep -E '^def .{40,}' {} \\; | wc -l"),
            ("Missing Docstrings", "find . -name '*.py' -exec grep -l '^def.*:$' {} \\; | wc -l"),
        ]
        
        for check_name, command in checks:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                count = int(result.stdout.strip())
                if count > 0:
                    suggestions.append({
                        'title': f"Improve {check_name}",
                        'description': f"Found {count} files that need {check_name.lower()} improvements",
                        'priority': Priority.MEDIUM if count < 10 else Priority.HIGH,
                        'category': 'code_quality',
                        'estimated_hours': min(count * 0.5, 8)
                    })
            except:
                pass
        
        # Add some smart suggestions based on project structure
        if Path('src').exists():
            suggestions.extend([
                {
                    'title': "Add Unit Tests",
                    'description': "Implement comprehensive unit tests for core modules",
                    'priority': Priority.HIGH,
                    'category': 'testing',
                    'estimated_hours': 4
                },
                {
                    'title': "Performance Optimization",
                    'description': "Profile and optimize slow functions",
                    'priority': Priority.MEDIUM,
                    'category': 'performance',
                    'estimated_hours': 3
                },
                {
                    'title': "API Documentation",
                    'description': "Generate and improve API documentation",
                    'priority': Priority.LOW,
                    'category': 'documentation',
                    'estimated_hours': 2
                }
            ])
        
        return suggestions
    
    def agent_analyze_module(self):
        """AI Agent module analysis and improvement"""
        self.show_header()
        print(f"{Colors.ORANGE}{Colors.BOLD}🤖 UNIBOS AI Agent System{Colors.RESET}")
        print(f"{Colors.YELLOW}Intelligent Code Analysis & Improvement{Colors.RESET}")
        print(f"{Colors.DIM}{'='*50}{Colors.RESET}\n")
        
        if not AGENT_SYSTEM_AVAILABLE:
            print(f"{Colors.RED}❌ Agent system not available{Colors.RESET}")
            print(f"Please ensure unibos_agent_system.py is in the src/ directory")
            input("\nPress Enter to return...")
            return
        
        # Module selection
        modules = {
            "1": ("main", "Ana program (main.py)"),
            "2": ("claude", "Claude entegrasyonu"),
            "3": ("currencies", "Döviz modülü"),
            "4": ("recaria", "Recaria oyunu"),
            "5": ("birlikteyiz", "Mesh network"),
            "6": ("git", "Git yönetimi"),
            "7": ("all", "Tüm proje analizi"),
        }
        
        print(f"{Colors.GREEN}Select module to analyze and improve:{Colors.RESET}\n")
        for key, (module, desc) in modules.items():
            print(f"  {Colors.CYAN}{key}{Colors.RESET}. {module:<15} - {desc}")
        
        print(f"\n  {Colors.DIM}q. Return to main menu{Colors.RESET}")
        
        choice = input(f"\n{Colors.BLUE}Choice: {Colors.RESET}")
        
        if choice == 'q':
            return
        
        if choice not in modules:
            print(f"{Colors.RED}Invalid choice{Colors.RESET}")
            time.sleep(1)
            return
        
        module_name, desc = modules[choice]
        
        # Perform agent analysis
        print(f"\n{Colors.YELLOW}🤖 Starting AI agent analysis...{Colors.RESET}")
        print(f"{Colors.CYAN}Module: {module_name}{Colors.RESET}")
        print(f"{Colors.DIM}This may take a moment...{Colors.RESET}\n")
        
        try:
            # Let agent analyze the module
            analysis = self.agent_orchestrator.analyze_module(module_name)
            
            # Display results
            print(f"\n{Colors.GREEN}✅ Analysis Complete!{Colors.RESET}\n")
            
            total_issues = 0
            for agent_role, data in analysis['analyses'].items():
                if data['issues_found'] > 0:
                    print(f"{Colors.YELLOW}{agent_role.replace('_', ' ').title()}:{Colors.RESET}")
                    print(f"  Files analyzed: {data['files_analyzed']}")
                    print(f"  Issues found: {data['issues_found']}")
                    total_issues += data['issues_found']
                    
                    # Show top 3 issues
                    for imp in data['improvements'][:3]:
                        if isinstance(imp, dict):
                            # Handle different improvement formats
                            if 'file' in imp:
                                print(f"    • {imp.get('file', 'Unknown')}: {imp.get('issue', imp.get('vulnerability', 'Issue'))}")
                            elif 'area' in imp:
                                print(f"    • {imp.get('area', 'Unknown')}: {imp.get('suggestion', 'Improvement needed')}")
                            else:
                                print(f"    • {imp}")
                        else:
                            print(f"    • {imp}")
                    print()
            
            if total_issues == 0:
                print(f"{Colors.GREEN}No critical issues found! Code is in good shape.{Colors.RESET}")
            else:
                # Ask if user wants to create a suggestion for improvements
                print(f"\n{Colors.CYAN}Would you like to:{Colors.RESET}")
                print("1. Create a suggestion for these improvements")
                print("2. Start immediate development with Claude")
                print("3. View detailed report")
                print("0. Return to menu")
                
                action = input(f"\n{Colors.BLUE}Choice: {Colors.RESET}")
                
                if action == '1':
                    # Create suggestion from analysis
                    title = f"AI Agent improvements for {module_name} module"
                    description = f"Agent analysis found {total_issues} issues across multiple categories"
                    
                    suggestion_id = self.add_suggestion(
                        title, description, Priority.HIGH, 
                        'agent_analysis', total_issues * 0.5
                    )
                    print(f"\n{Colors.GREEN}✅ Suggestion created (ID: {suggestion_id}){Colors.RESET}")
                    
                elif action == '2':
                    # Direct development with Claude
                    print(f"\n{Colors.YELLOW}🚀 Starting Claude development...{Colors.RESET}")
                    prompt = self.agent_orchestrator.generate_enhancement_prompt(analysis)
                    
                    # Create temporary suggestion for tracking
                    title = f"AI Agent improvements for {module_name} module"
                    suggestion = Suggestion(
                        id=0, title=title, 
                        description=f"Direct development from agent analysis",
                        priority=Priority.HIGH, category='agent_analysis',
                        estimated_hours=total_issues * 0.5,
                        created_at=datetime.now()
                    )
                    
                    # Send to Claude for development
                    self._develop_with_claude(suggestion, prompt)
                    
                elif action == '3':
                    # Show detailed report
                    print(f"\n{Colors.CYAN}Detailed Analysis Report:{Colors.RESET}")
                    print(json.dumps(analysis, indent=2))
                    input("\nPress Enter to continue...")
                    
        except Exception as e:
            print(f"{Colors.RED}Error during analysis: {str(e)}{Colors.RESET}")
            import traceback
            traceback.print_exc()
        
        input("\nPress Enter to return...")
    
    def _develop_with_claude(self, suggestion: Suggestion, custom_prompt: Optional[str] = None):
        """Internal method to develop with Claude using a custom prompt"""
        if not self.claude_available:
            print(f"{Colors.RED}❌ Claude CLI is not available{Colors.RESET}")
            return
        
        prompt = custom_prompt or f"""I need you to implement the following development task for UNIBOS:

**Task**: {suggestion.title}
**Description**: {suggestion.description}
**Category**: {suggestion.category}
**Estimated Time**: {suggestion.estimated_hours} hours

Please:
1. Analyze the current codebase
2. Implement the required changes
3. Follow UNIBOS coding standards
4. Include proper error handling
5. Add necessary tests if applicable

Provide the implementation with clear explanations of changes made."""
        
        print(f"\n{Colors.YELLOW}📡 Sending to Claude...{Colors.RESET}\n")
        
        try:
            from claude_conversation import ClaudeConversation
            
            print(f"{Colors.CYAN}Starting interactive Claude conversation...{Colors.RESET}")
            print(f"{Colors.DIM}You can add follow-up messages during the response.{Colors.RESET}\n")
            
            conversation = ClaudeConversation()
            conversation.start_conversation(prompt, f"Developing: {suggestion.title}")
            
            print(f"\n{Colors.GREEN}Development session completed!{Colors.RESET}")
            
        except Exception as e:
            print(f"{Colors.RED}Error during development: {str(e)}{Colors.RESET}")
    
    def add_suggestion(self, title: str, description: str, priority: Priority, 
                      category: str, estimated_hours: float) -> int:
        """Add a new suggestion to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO suggestions (title, description, priority, category, 
                                   estimated_hours, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, priority.value, category, estimated_hours, 
              datetime.now(), Status.PENDING.value))
        
        suggestion_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return suggestion_id
    
    def get_suggestions(self, status: Optional[Status] = None) -> List[Suggestion]:
        """Get suggestions from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM suggestions WHERE status = ? ORDER BY created_at DESC', 
                          (status.value,))
        else:
            cursor.execute('SELECT * FROM suggestions ORDER BY created_at DESC')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Debug: Print number of rows found
        # print(f"[DEBUG] Found {len(rows)} suggestions with status={status.value if status else 'all'}")
        
        suggestions = []
        for row in rows:
            suggestions.append(Suggestion(
                id=row['id'],
                title=row['title'],
                description=row['description'],
                priority=Priority(row['priority']),
                category=row['category'],
                estimated_hours=row['estimated_hours'],
                created_at=datetime.fromisoformat(row['created_at']),
                status=Status(row['status']),
                completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                implementation=row['implementation']
            ))
        
        return suggestions
    
    def update_suggestion_status(self, suggestion_id: int, status: Status, 
                               implementation: Optional[str] = None):
        """Update suggestion status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status == Status.COMPLETED:
            cursor.execute('''
                UPDATE suggestions 
                SET status = ?, completed_at = ?, implementation = ?
                WHERE id = ?
            ''', (status.value, datetime.now(), implementation, suggestion_id))
        else:
            cursor.execute('''
                UPDATE suggestions 
                SET status = ?
                WHERE id = ?
            ''', (status.value, suggestion_id))
        
        conn.commit()
        conn.close()
    
    def develop_suggestion(self, suggestion: Suggestion):
        """Develop a suggestion using Claude CLI"""
        self.show_header()
        
        print(f"{Colors.BOLD}🚀 Developing: {suggestion.title}{Colors.RESET}")
        print(f"{Colors.DIM}{'='*50}{Colors.RESET}\n")
        
        print(f"{suggestion.priority.value} Priority: {suggestion.priority.name}")
        print(f"📁 Category: {suggestion.category}")
        print(f"⏱️  Estimated: {suggestion.estimated_hours} hours")
        print(f"\n{Colors.CYAN}Description:{Colors.RESET}")
        print(f"{suggestion.description}\n")
        
        if not self.claude_available:
            print(f"{Colors.RED}❌ Claude CLI is not available{Colors.RESET}")
            print("Please install Claude CLI: https://claude.ai/cli")
            input("\nPress Enter to return...")
            return
        
        # Update status to in progress
        self.update_suggestion_status(suggestion.id, Status.IN_PROGRESS)
        
        # Create session if session manager is available
        if self.session_manager:
            session = self.session_manager.create_session(
                suggestion.id, suggestion.title, ""
            )
            print(f"{Colors.DIM}📝 Session created and will be saved for resume capability{Colors.RESET}\n")
        
        # Develop with Claude
        self._develop_with_claude(suggestion)
        
        # Ask if implementation was successful
        print(f"\n{Colors.YELLOW}{'='*50}{Colors.RESET}")
        response = input(f"\n{Colors.CYAN}Was the implementation successful? (y/n): {Colors.RESET}")
        
        if response.lower() == 'y':
            # Get implementation notes
            print(f"\n{Colors.CYAN}Brief summary of changes (optional):{Colors.RESET}")
            summary = input("> ")
            
            implementation_notes = f"Completed via interactive conversation\n"
            if summary:
                implementation_notes += f"Summary: {summary}\n"
            
            self.update_suggestion_status(suggestion.id, Status.COMPLETED, implementation_notes)
            print(f"{Colors.GREEN}✅ Marked as completed!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⏸️  Suggestion remains in progress{Colors.RESET}")
        
        input("\nPress Enter to continue...")
    
    def show_suggestions_menu(self):
        """Show suggestions menu"""
        while True:
            self.show_header()
            
            # Get all suggestions first to debug
            all_suggestions = self.get_suggestions()
            pending_suggestions = self.get_suggestions(Status.PENDING)
            
            # Debug info
            if not pending_suggestions and all_suggestions:
                print(f"{Colors.DIM}[DEBUG] Found {len(all_suggestions)} total suggestions but 0 pending{Colors.RESET}")
                print(f"{Colors.DIM}[DEBUG] Suggestion statuses: {[s.status.value for s in all_suggestions[:5]]}{Colors.RESET}\n")
            
            suggestions = pending_suggestions
            
            if suggestions:
                print(f"{Colors.BOLD}📋 Pending Suggestions:{Colors.RESET}\n")
                
                for i, suggestion in enumerate(suggestions[:10], 1):
                    print(f"{i:2d}. {suggestion.priority.value} {suggestion.title}")
                    print(f"    {Colors.DIM}{suggestion.description[:60]}...{Colors.RESET}")
                    print(f"    {Colors.DIM}Category: {suggestion.category} | "
                          f"Time: {suggestion.estimated_hours}h{Colors.RESET}\n")
                
                if len(suggestions) > 10:
                    print(f"{Colors.DIM}... and {len(suggestions) - 10} more{Colors.RESET}\n")
            else:
                print(f"{Colors.DIM}No pending suggestions{Colors.RESET}\n")
            
            print(f"{Colors.BOLD}Actions:{Colors.RESET}")
            print("1. 🔍 Analyze codebase for suggestions")
            print("2. ➕ Add manual suggestion")
            print("3. 🚀 Develop a suggestion")
            print("4. 📊 View completed suggestions")
            
            # Add agent option if available
            if AGENT_SYSTEM_AVAILABLE:
                print(f"5. {Colors.ORANGE}🤖 AI Agent Analysis (NEW!){Colors.RESET}")
                option_offset = 1
            else:
                option_offset = 0
            
            # Add resume option if session manager is available
            if self.session_manager:
                sessions = self.session_manager.get_resumable_sessions()
                if sessions:
                    print(f"{5 + option_offset}. 🔄 Resume development session ({len(sessions)} available)")
                    print(f"{6 + option_offset}. 🗑️  Clear all suggestions")
                else:
                    print(f"{5 + option_offset}. 🗑️  Clear all suggestions")
            else:
                print(f"{5 + option_offset}. 🗑️  Clear all suggestions")
            
            print("0. 🚪 Exit")
            
            choice = input(f"\n{Colors.CYAN}Select an option: {Colors.RESET}")
            
            if choice == '1':
                self.analyze_and_add_suggestions()
            elif choice == '2':
                self.add_manual_suggestion()
            elif choice == '3':
                self.select_and_develop()
            elif choice == '4':
                self.show_completed_suggestions()
            elif choice == '5' and AGENT_SYSTEM_AVAILABLE:
                self.agent_analyze_module()
            elif choice == str(5 + option_offset):
                # Check if this is resume or clear
                if self.session_manager:
                    sessions = self.session_manager.get_resumable_sessions()
                    if sessions:
                        self.show_resumable_sessions()
                    else:
                        self.clear_suggestions()
                else:
                    self.clear_suggestions()
            elif choice == str(6 + option_offset) and self.session_manager:
                # This is clear suggestions if resume option is shown
                sessions = self.session_manager.get_resumable_sessions()
                if sessions:
                    self.clear_suggestions()
            elif choice == '0':
                break
            else:
                print(f"{Colors.RED}Invalid option{Colors.RESET}")
                time.sleep(1)
    
    def analyze_and_add_suggestions(self):
        """Analyze codebase and add suggestions"""
        self.show_header()
        
        suggestions = self.analyze_codebase()
        
        if suggestions:
            print(f"\n{Colors.GREEN}✅ Found {len(suggestions)} suggestions:{Colors.RESET}\n")
            
            for suggestion in suggestions:
                suggestion_id = self.add_suggestion(
                    suggestion['title'],
                    suggestion['description'],
                    suggestion['priority'],
                    suggestion['category'],
                    suggestion['estimated_hours']
                )
                print(f"  • Added: {suggestion['title']}")
            
            print(f"\n{Colors.GREEN}✅ All suggestions added to database{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}No new suggestions found{Colors.RESET}")
        
        input("\nPress Enter to continue...")
    
    def add_manual_suggestion(self):
        """Add a manual suggestion"""
        self.show_header()
        print(f"{Colors.BOLD}➕ Add Manual Suggestion{Colors.RESET}\n")
        
        title = input(f"{Colors.CYAN}Title: {Colors.RESET}")
        if not title:
            return
        
        description = input(f"{Colors.CYAN}Description: {Colors.RESET}")
        if not description:
            return
        
        print(f"\n{Colors.CYAN}Priority:{Colors.RESET}")
        print("1. 🟢 Low")
        print("2. 🟡 Medium")
        print("3. 🟠 High")
        print("4. 🔴 Critical")
        
        priority_choice = input(f"\n{Colors.CYAN}Select priority (1-4): {Colors.RESET}")
        priority_map = {'1': Priority.LOW, '2': Priority.MEDIUM, 
                        '3': Priority.HIGH, '4': Priority.CRITICAL}
        priority = priority_map.get(priority_choice, Priority.MEDIUM)
        
        category = input(f"\n{Colors.CYAN}Category (e.g., feature, bug, performance): {Colors.RESET}")
        if not category:
            category = "general"
        
        try:
            hours = float(input(f"{Colors.CYAN}Estimated hours: {Colors.RESET}"))
        except:
            hours = 2.0
        
        suggestion_id = self.add_suggestion(title, description, priority, category, hours)
        print(f"\n{Colors.GREEN}✅ Suggestion added (ID: {suggestion_id}){Colors.RESET}")
        
        input("\nPress Enter to continue...")
    
    def select_and_develop(self):
        """Select a suggestion to develop"""
        suggestions = self.get_suggestions(Status.PENDING)
        
        if not suggestions:
            print(f"{Colors.YELLOW}No pending suggestions{Colors.RESET}")
            input("\nPress Enter to continue...")
            return
        
        self.show_header()
        print(f"{Colors.BOLD}🚀 Select Suggestion to Develop{Colors.RESET}\n")
        
        for i, suggestion in enumerate(suggestions[:10], 1):
            print(f"{i:2d}. {suggestion.priority.value} {suggestion.title}")
        
        try:
            choice = int(input(f"\n{Colors.CYAN}Select suggestion (1-{min(10, len(suggestions))}): {Colors.RESET}"))
            if 1 <= choice <= min(10, len(suggestions)):
                self.develop_suggestion(suggestions[choice - 1])
            else:
                print(f"{Colors.RED}Invalid selection{Colors.RESET}")
                time.sleep(1)
        except:
            print(f"{Colors.RED}Invalid input{Colors.RESET}")
            time.sleep(1)
    
    def show_completed_suggestions(self):
        """Show completed suggestions"""
        self.show_header()
        print(f"{Colors.BOLD}✅ Completed Suggestions{Colors.RESET}\n")
        
        suggestions = self.get_suggestions(Status.COMPLETED)
        
        if suggestions:
            for suggestion in suggestions[:20]:
                print(f"• {suggestion.title}")
                print(f"  {Colors.DIM}Completed: {suggestion.completed_at.strftime('%Y-%m-%d %H:%M')}{Colors.RESET}")
                print()
        else:
            print(f"{Colors.DIM}No completed suggestions{Colors.RESET}")
        
        input("\nPress Enter to continue...")
    
    def clear_suggestions(self):
        """Clear all suggestions"""
        confirm = input(f"\n{Colors.RED}Are you sure you want to clear all suggestions? (yes/no): {Colors.RESET}")
        
        if confirm.lower() == 'yes':
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM suggestions')
            conn.commit()
            conn.close()
            print(f"{Colors.GREEN}✅ All suggestions cleared{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}Cancelled{Colors.RESET}")
        
        input("\nPress Enter to continue...")
    
    def show_resumable_sessions(self):
        """Show resumable development sessions"""
        self.show_header()
        print(f"{Colors.BOLD}🔄 Resumable Development Sessions{Colors.RESET}\n")
        
        sessions = self.session_manager.get_resumable_sessions()
        
        if not sessions:
            print(f"{Colors.DIM}No resumable sessions{Colors.RESET}")
            input("\nPress Enter to continue...")
            return
        
        for i, session in enumerate(sessions, 1):
            time_diff = datetime.now() - session.last_activity
            hours_ago = time_diff.total_seconds() / 3600
            
            print(f"{i}. {Colors.BOLD}{session.suggestion_title}{Colors.RESET}")
            print(f"   Status: {session.status.value}")
            print(f"   Started: {session.started_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Last activity: {hours_ago:.1f} hours ago")
            if session.progress_notes:
                print(f"   Progress: {session.progress_notes[:80]}...")
            print()
        
        print("0. 🚪 Back to main menu")
        
        choice = input(f"\n{Colors.CYAN}Select session to resume (1-{len(sessions)}/0): {Colors.RESET}")
        
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(sessions):
                self.resume_development_session(sessions[idx - 1])
            elif idx == 0:
                return
            else:
                print(f"{Colors.RED}Invalid selection{Colors.RESET}")
                time.sleep(1)
    
    def resume_development_session(self, session):
        """Resume a paused development session"""
        self.show_header()
        
        print(f"{Colors.BOLD}🔄 Resuming: {session.suggestion_title}{Colors.RESET}")
        print(f"{Colors.DIM}{'='*50}{Colors.RESET}\n")
        
        # Get suggestion details
        suggestion = None
        suggestions = self.get_suggestions()
        for s in suggestions:
            if s.id == session.suggestion_id:
                suggestion = s
                break
        
        if not suggestion:
            print(f"{Colors.RED}❌ Suggestion not found{Colors.RESET}")
            input("\nPress Enter to continue...")
            return
        
        print(f"{suggestion.priority.value} Priority: {suggestion.priority.name}")
        print(f"📁 Category: {suggestion.category}")
        print(f"⏱️  Estimated: {suggestion.estimated_hours} hours")
        
        # Show conversation history
        conversation_data = self.session_manager.get_session_conversation(session)
        if conversation_data and 'messages' in conversation_data:
            print(f"\n{Colors.CYAN}Previous conversation ({len(conversation_data['messages'])} messages):{Colors.RESET}")
            for msg in conversation_data['messages'][-3:]:  # Show last 3 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                if len(content) > 100:
                    content = content[:100] + "..."
                print(f"  {role}: {content}")
        
        print(f"\n{Colors.YELLOW}Continue development? (y/n):{Colors.RESET} ", end='', flush=True)
        if input().lower() == 'y':
            # Continue with the conversation
            try:
                from claude_conversation import ClaudeConversation
                
                print(f"\n{Colors.CYAN}Resuming Claude conversation...{Colors.RESET}")
                
                # Prepare context prompt
                context_prompt = f"""Continue developing the following task:

**Task**: {suggestion.title}
**Description**: {suggestion.description}

You were previously working on this task. Please continue from where you left off.
Previous progress notes: {session.progress_notes or 'No notes available'}"""
                
                conversation = ClaudeConversation()
                conversation.start_conversation(context_prompt, f"Resuming: {suggestion.title}")
                
                # Update session
                if self.session_manager:
                    self.session_manager.update_session(
                        session.suggestion_id,
                        {'role': 'system', 'content': 'Session resumed'},
                        progress_notes="Session resumed after pause"
                    )
                
                # After conversation ends
                print(f"\n{Colors.GREEN}Development session completed!{Colors.RESET}")
                
                # Ask if implementation was successful
                print(f"\n{Colors.YELLOW}{'='*50}{Colors.RESET}")
                response = input(f"\n{Colors.CYAN}Was the implementation successful? (y/n): {Colors.RESET}")
                
                if response.lower() == 'y':
                    self.update_suggestion_status(suggestion.id, Status.COMPLETED, "Completed after resume")
                    if self.session_manager:
                        self.session_manager.complete_session(session.suggestion_id)
                    print(f"{Colors.GREEN}✅ Marked as completed!{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}⏸️  Suggestion remains in progress{Colors.RESET}")
                    if self.session_manager:
                        self.session_manager.pause_session(session.suggestion_id)
                        
            except Exception as e:
                print(f"{Colors.RED}Error resuming session: {str(e)}{Colors.RESET}")
                if self.session_manager:
                    self.session_manager.pause_session(session.suggestion_id)
        else:
            print(f"{Colors.YELLOW}Session not resumed{Colors.RESET}")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Run the main application"""
        self.show_suggestions_menu()
        print(f"\n{Colors.CYAN}Thank you for using Claude Suggest!{Colors.RESET}")


# CLI entry point
if __name__ == "__main__":
    app = ClaudeSuggest()
    app.run()