#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AI Builder - Intelligent Development Platform
Simplified and enhanced AI-powered development interface

Author: berk hatırlı
Version: v1.0
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unibos_logger import logger, LogCategory, LogLevel

# Color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    
    # Backgrounds
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_GRAY = '\033[100m'
    BG_DARK = '\033[48;5;234m'

class AIBuilder:
    """AI Builder - Simplified intelligent development interface"""
    
    def __init__(self):
        self.base_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.current_session = None
        self.development_history = []
        self.active_agents = {}
        
        # Try to import database manager
        try:
            from suggestion_manager_pg import PostgreSQLSuggestionManager
            self.db_manager = PostgreSQLSuggestionManager()
        except:
            self.db_manager = None
            
        logger.info("AI Builder initialized", category=LogCategory.MODULE)
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def show_header(self):
        """Show AI Builder header"""
        self.clear_screen()
        cols = os.get_terminal_size().columns
        
        print(f"\n{Colors.CYAN}{'═' * cols}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}🤖 ai builder{Colors.RESET} - intelligent development platform".center(cols))
        print(f"{Colors.DIM}powered by claude ai{Colors.RESET}".center(cols))
        print(f"{Colors.CYAN}{'═' * cols}{Colors.RESET}\n")
    
    def show_main_menu(self):
        """Show simplified main menu"""
        menu_items = [
            ("1", "🚀 new development", "start a new ai-powered development session"),
            ("2", "📋 my developments", "view and continue previous developments"),
            ("3", "🔍 smart search", "search codebase with ai assistance"),
            ("4", "🧠 active agents", "manage ai agents"),
            ("5", "📊 analytics", "development insights and statistics"),
            ("6", "⚙️  settings", "configure ai builder"),
            ("q", "🚪 exit", "return to main menu")
        ]
        
        print(f"{Colors.BOLD}main menu:{Colors.RESET}\n")
        
        for key, title, desc in menu_items:
            print(f"  {Colors.CYAN}[{key}]{Colors.RESET} {title}")
            print(f"      {Colors.DIM}{desc}{Colors.RESET}\n")
        
        return input(f"{Colors.YELLOW}select option: {Colors.RESET}").strip().lower()
    
    def new_development(self):
        """Start new development session"""
        self.show_header()
        print(f"{Colors.BOLD}🚀 new development session{Colors.RESET}\n")
        
        # Development type selection
        print(f"{Colors.CYAN}what would you like to develop?{Colors.RESET}\n")
        
        dev_types = [
            ("1", "feature", "add new functionality"),
            ("2", "fix", "fix bugs or issues"),
            ("3", "refactor", "improve existing code"),
            ("4", "documentation", "create or update docs"),
            ("5", "custom", "describe your own task")
        ]
        
        for key, title, desc in dev_types:
            print(f"  [{key}] {Colors.GREEN}{title}{Colors.RESET} - {Colors.DIM}{desc}{Colors.RESET}")
        
        print()
        choice = input(f"{Colors.YELLOW}select type [1-5]: {Colors.RESET}").strip()
        
        if choice not in ["1", "2", "3", "4", "5"]:
            return
        
        dev_type = dev_types[int(choice) - 1][1]
        
        # Get description
        print(f"\n{Colors.CYAN}describe what you want to {dev_type.lower()}:{Colors.RESET}")
        description = input(f"{Colors.DIM}> {Colors.RESET}").strip()
        
        if not description:
            return
        
        # Start development with AI
        self._start_ai_development(dev_type, description)
    
    def _start_ai_development(self, dev_type: str, description: str):
        """Start AI-powered development"""
        print(f"\n{Colors.YELLOW}🤖 AI is analyzing your request...{Colors.RESET}")
        
        # Create development session
        session_id = self._create_session(dev_type, description)
        
        # Use appropriate agent
        if dev_type == "Feature":
            self._use_feature_agent(description, session_id)
        elif dev_type == "Fix":
            self._use_fix_agent(description, session_id)
        elif dev_type == "Refactor":
            self._use_refactor_agent(description, session_id)
        elif dev_type == "Documentation":
            self._use_doc_agent(description, session_id)
        else:
            self._use_general_agent(description, session_id)
    
    def _create_session(self, dev_type: str, description: str) -> str:
        """Create development session in database"""
        if self.db_manager:
            try:
                from database.models import DevelopmentSession, Suggestion, SuggestionCategory, SuggestionSource
                
                # Create a suggestion first
                category_map = {
                    "feature": SuggestionCategory.FEATURE,
                    "fix": SuggestionCategory.BUG_FIX,
                    "refactor": SuggestionCategory.REFACTORING,
                    "documentation": SuggestionCategory.DOCUMENTATION,
                    "custom": SuggestionCategory.FEATURE
                }
                
                suggestion = Suggestion(
                    title=f"{dev_type}: {description[:50]}...",
                    description=description,
                    category=category_map.get(dev_type.lower(), SuggestionCategory.FEATURE),
                    source=SuggestionSource.USER
                )
                self.db_manager.session.add(suggestion)
                self.db_manager.session.commit()
                
                # Create development session
                session = DevelopmentSession(
                    suggestion_id=suggestion.id,
                    status='active',
                    context={'dev_type': dev_type, 'description': description}
                )
                self.db_manager.session.add(session)
                self.db_manager.session.commit()
                
                return str(session.id)
            except Exception as e:
                logger.error(f"Failed to create session: {e}", category=LogCategory.DATABASE)
        
        # Fallback to timestamp-based ID
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _use_feature_agent(self, description: str, session_id: str):
        """Use feature development agent"""
        print(f"\n{Colors.GREEN}✅ Feature Development Agent activated{Colors.RESET}")
        print(f"{Colors.DIM}session id: {session_id}{Colors.RESET}\n")
        
        # Prepare prompt for Claude
        prompt = f"""I need to implement a new feature for UNIBOS:

**Feature Request:** {description}

Please:
1. Analyze the request and break it down into steps
2. Check existing codebase for related functionality
3. Suggest implementation approach
4. Write the necessary code
5. Add appropriate tests
6. Update documentation

Provide a complete, production-ready implementation."""

        # Execute with Claude
        self._execute_with_claude(prompt, session_id)
    
    def _use_fix_agent(self, description: str, session_id: str):
        """Use bug fix agent"""
        print(f"\n{Colors.YELLOW}🐛 Bug Fix Agent activated{Colors.RESET}")
        print(f"{Colors.DIM}session id: {session_id}{Colors.RESET}\n")
        
        prompt = f"""I need to fix an issue in UNIBOS:

**Issue Description:** {description}

Please:
1. Analyze the issue
2. Identify the root cause
3. Find affected files
4. Implement the fix
5. Test the solution
6. Ensure no regressions

Provide a complete fix with explanations."""

        self._execute_with_claude(prompt, session_id)
    
    def _use_refactor_agent(self, description: str, session_id: str):
        """Use refactoring agent"""
        print(f"\n{Colors.BLUE}♻️  Refactoring Agent activated{Colors.RESET}")
        print(f"{Colors.DIM}session id: {session_id}{Colors.RESET}\n")
        
        prompt = f"""I need to refactor code in UNIBOS:

**Refactoring Goal:** {description}

Please:
1. Analyze current implementation
2. Identify improvement opportunities
3. Plan refactoring approach
4. Implement changes incrementally
5. Ensure backward compatibility
6. Update tests and docs

Provide clean, maintainable code."""

        self._execute_with_claude(prompt, session_id)
    
    def _use_doc_agent(self, description: str, session_id: str):
        """Use documentation agent"""
        print(f"\n{Colors.MAGENTA}📚 Documentation Agent activated{Colors.RESET}")
        print(f"{Colors.DIM}session id: {session_id}{Colors.RESET}\n")
        
        prompt = f"""I need documentation for UNIBOS:

**Documentation Need:** {description}

Please:
1. Analyze what needs to be documented
2. Follow project documentation standards
3. Create clear, comprehensive docs
4. Add code examples where appropriate
5. Update relevant README files
6. Ensure accuracy

Provide professional documentation."""

        self._execute_with_claude(prompt, session_id)
    
    def _use_general_agent(self, description: str, session_id: str):
        """Use general purpose agent"""
        print(f"\n{Colors.CYAN}🎯 General Agent activated{Colors.RESET}")
        print(f"{Colors.DIM}session id: {session_id}{Colors.RESET}\n")
        
        prompt = f"""I need help with UNIBOS development:

**Request:** {description}

Please analyze this request and provide appropriate assistance.
Consider the project structure, coding standards, and best practices."""

        self._execute_with_claude(prompt, session_id)
    
    def _execute_with_claude(self, prompt: str, session_id: str):
        """Execute development with Claude"""
        try:
            # Check for Claude conversation module
            use_pty = os.environ.get('CLAUDE_USE_PTY', '').lower() == 'true'
            
            if use_pty:
                from claude_conversation_pty import ClaudeConversationPTY
                conversation = ClaudeConversationPTY()
            else:
                from claude_conversation import ClaudeConversation
                conversation = ClaudeConversation()
            
            print(f"{Colors.CYAN}Starting AI development session...{Colors.RESET}\n")
            
            # Start conversation
            success = conversation.start_conversation(
                prompt, 
                f"Development Session {session_id}"
            )
            
            if success:
                self._save_session_results(session_id, conversation.response_buffer)
                print(f"\n{Colors.GREEN}✅ Development session completed{Colors.RESET}")
                
                # Run tests after development
                print(f"\n{Colors.YELLOW}🧪 Running automated tests...{Colors.RESET}")
                test_passed = self._run_tests()
                
                # Offer to continue or finish
                print(f"\n{Colors.YELLOW}options:{Colors.RESET}")
                print(f"  [1] Continue with follow-up")
                if test_passed:
                    print(f"  [2] Mark as complete and prepare for version delivery")
                else:
                    print(f"  [2] Fix test failures and retry")
                print(f"  [3] Save and exit")
                print(f"  [4] Run tests again")
                
                choice = input(f"\n{Colors.CYAN}select option: {Colors.RESET}").strip()
                
                if choice == "1":
                    # Continue development
                    follow_up = input(f"\n{Colors.CYAN}Follow-up request: {Colors.RESET}").strip()
                    if follow_up:
                        self._execute_with_claude(follow_up, session_id)
                elif choice == "2":
                    if test_passed:
                        self._mark_session_complete(session_id)
                    else:
                        # Fix test failures
                        print(f"\n{Colors.YELLOW}Let me fix the test failures...{Colors.RESET}")
                        fix_prompt = f"The following tests failed. Please fix them:\n\n{self._get_test_failures()}"
                        self._execute_with_claude(fix_prompt, session_id)
                elif choice == "4":
                    # Run tests again
                    self._run_tests()
                    # Show options again
                    self._execute_with_claude("", session_id)  # Empty prompt to show options
            else:
                print(f"{Colors.RED}❌ Development session failed{Colors.RESET}")
                
        except ImportError:
            print(f"{Colors.RED}Claude conversation module not found{Colors.RESET}")
            print(f"{Colors.YELLOW}Please ensure Claude CLI is installed{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
            logger.error(f"Claude execution failed: {e}", category=LogCategory.MODULE)
    
    def _save_session_results(self, session_id: str, results: List[str]):
        """Save session results to database"""
        if self.db_manager and results:
            try:
                from database.models import Implementation, DevelopmentSession
                
                # Get session to find suggestion
                session = self.db_manager.session.query(DevelopmentSession).filter_by(id=session_id).first()
                if not session or not session.suggestion:
                    return
                
                # Join results
                content = ''.join(results)
                
                # Update session messages
                if not session.messages:
                    session.messages = []
                session.messages.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'result',
                    'content': content[:1000]  # Store first 1000 chars
                })
                
                # Create implementation record
                impl = Implementation(
                    suggestion_id=session.suggestion.id,
                    implemented_by='ai_builder',
                    commit_message=f"AI Builder implementation for: {session.suggestion.title}"
                )
                self.db_manager.session.add(impl)
                self.db_manager.session.commit()
                
                logger.info(f"Session {session_id} results saved", category=LogCategory.DATABASE)
            except Exception as e:
                logger.error(f"Failed to save results: {e}", category=LogCategory.DATABASE)
    
    def _run_tests(self) -> bool:
        """Run automated tests"""
        try:
            from test_agent import TestAgent
            
            # Initialize test agent
            self.test_agent = TestAgent()
            
            # Run all tests
            success, results = self.test_agent.run_all_tests(verbose=False)
            
            # Store results for later use
            self.last_test_results = results
            
            return success
            
        except ImportError:
            print(f"{Colors.YELLOW}⚠️  Test agent not available{Colors.RESET}")
            logger.warning("Test agent module not found", category=LogCategory.MODULE)
            return True  # Allow to continue without tests
        except Exception as e:
            print(f"{Colors.RED}❌ Test execution failed: {e}{Colors.RESET}")
            logger.error(f"Test execution error: {e}", category=LogCategory.MODULE)
            return False
    
    def _get_test_failures(self) -> str:
        """Get test failure details"""
        if not hasattr(self, 'last_test_results') or not self.last_test_results:
            return "No test results available"
        
        failures = []
        for result in self.last_test_results:
            if not result['success'] and result['critical']:
                failures.append(f"- {result['name']}: {result['message']}")
        
        if not failures:
            return "No critical test failures"
        
        return "\n".join(failures)
    
    def _mark_session_complete(self, session_id: str):
        """Mark session as complete"""
        if self.db_manager:
            try:
                from database.models import DevelopmentSession, SuggestionStatus
                session = self.db_manager.session.query(DevelopmentSession).filter_by(id=session_id).first()
                if session:
                    session.status = 'completed'
                    session.ended_at = datetime.utcnow()
                    # Also update the suggestion status
                    if session.suggestion:
                        session.suggestion.status = SuggestionStatus.COMPLETED
                        session.suggestion.completed_at = datetime.utcnow()
                    self.db_manager.session.commit()
                    print(f"{Colors.GREEN}✅ Session marked as complete{Colors.RESET}")
            except Exception as e:
                logger.error(f"Failed to update session: {e}", category=LogCategory.DATABASE)
    
    def my_developments(self):
        """Show development history"""
        self.show_header()
        print(f"{Colors.BOLD}📋 My Developments{Colors.RESET}\n")
        
        if self.db_manager:
            try:
                from database.models import DevelopmentSession
                
                # Get recent sessions with their suggestions
                sessions = self.db_manager.session.query(DevelopmentSession)\
                    .order_by(DevelopmentSession.started_at.desc())\
                    .limit(10)\
                    .all()
                
                if not sessions:
                    print(f"{Colors.YELLOW}No development sessions found{Colors.RESET}")
                    input(f"\n{Colors.DIM}press enter to continue...{Colors.RESET}")
                    return
                
                print(f"{Colors.CYAN}recent development sessions:{Colors.RESET}\n")
                
                for i, session in enumerate(sessions, 1):
                    status_color = Colors.GREEN if session.status == 'completed' else Colors.YELLOW
                    # Get title from suggestion or context
                    title = "Untitled Session"
                    if session.suggestion and session.suggestion.title:
                        title = session.suggestion.title
                    elif session.context and 'description' in session.context:
                        title = session.context['description'][:50] + "..."
                    
                    print(f"  [{i}] {title}")
                    print(f"      {Colors.DIM}Status: {status_color}{session.status}{Colors.RESET}")
                    print(f"      {Colors.DIM}Started: {session.started_at.strftime('%Y-%m-%d %H:%M')}{Colors.RESET}")
                    print()
                
                # Selection
                choice = input(f"{Colors.YELLOW}select session to view [1-{len(sessions)}] or 'q' to go back: {Colors.RESET}").strip()
                
                if choice.isdigit() and 1 <= int(choice) <= len(sessions):
                    self._view_session_details(sessions[int(choice) - 1])
                    
            except Exception as e:
                print(f"{Colors.RED}Error loading sessions: {e}{Colors.RESET}")
                logger.error(f"Failed to load sessions: {e}", category=LogCategory.DATABASE)
        else:
            print(f"{Colors.YELLOW}Database not available{Colors.RESET}")
            
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
    
    def _view_session_details(self, session):
        """View session details"""
        self.clear_screen()
        print(f"\n{Colors.BOLD}📄 session details{Colors.RESET}\n")
        
        # Get details from suggestion or context
        title = "Untitled Session"
        description = "No description available"
        dev_type = "unknown"
        
        if session.suggestion:
            title = session.suggestion.title
            description = session.suggestion.description
            dev_type = session.suggestion.category.value
        elif session.context:
            title = session.context.get('description', 'Untitled')[:50] + "..."
            description = session.context.get('description', 'No description')
            dev_type = session.context.get('dev_type', 'unknown')
        
        print(f"{Colors.CYAN}Title:{Colors.RESET} {title}")
        print(f"{Colors.CYAN}Type:{Colors.RESET} {dev_type}")
        print(f"{Colors.CYAN}Status:{Colors.RESET} {session.status}")
        print(f"{Colors.CYAN}Description:{Colors.RESET}\n{description}\n")
        
        # Show implementations from suggestion
        if session.suggestion and session.suggestion.implementations:
            print(f"{Colors.BOLD}Implementations:{Colors.RESET}\n")
            for impl in session.suggestion.implementations:
                print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")
                # Implementation model doesn't have content field, show files changed instead
                print(f"Implemented at: {impl.implemented_at}")
                print(f"Files changed: {', '.join(impl.files_changed) if impl.files_changed else 'None'}")
                print(f"Lines: +{impl.lines_added} -{impl.lines_removed}")
                print()
        
        # Options
        print(f"\n{Colors.YELLOW}Options:{Colors.RESET}")
        print(f"  [1] Continue development")
        print(f"  [2] Export to file")
        print(f"  [3] Go back")
        
        choice = input(f"\n{Colors.CYAN}Select option: {Colors.RESET}").strip()
        
        if choice == "1" and session.status != 'completed':
            # Continue development
            follow_up = input(f"\n{Colors.CYAN}Continue with: {Colors.RESET}").strip()
            if follow_up:
                self._execute_with_claude(follow_up, str(session.id))
        elif choice == "2":
            # Export to file
            self._export_session(session)
    
    def _export_session(self, session):
        """Export session to file"""
        filename = f"development_{session.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.base_path / "exports" / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Get details from suggestion or context
            title = "Untitled Session"
            description = "No description"
            dev_type = "unknown"
            
            if session.suggestion:
                title = session.suggestion.title
                description = session.suggestion.description
                dev_type = session.suggestion.category.value
            elif session.context:
                title = session.context.get('description', 'Untitled')[:50] + "..."
                description = session.context.get('description', 'No description')
                dev_type = session.context.get('dev_type', 'unknown')
            
            f.write(f"# Development Session: {title}\n\n")
            f.write(f"**Type:** {dev_type}\n")
            f.write(f"**Status:** {session.status}\n")
            f.write(f"**Started:** {session.started_at}\n\n")
            f.write(f"## Description\n\n{description}\n\n")
            
            if session.messages:
                f.write("## Session Messages\n\n")
                for msg in session.messages:
                    f.write(f"### {msg.get('timestamp', 'Unknown time')}\n")
                    f.write(f"Type: {msg.get('type', 'unknown')}\n\n")
                    f.write(f"{msg.get('content', '')}\n\n")
        
        print(f"\n{Colors.GREEN}✅ Exported to: {filename}{Colors.RESET}")
        input(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")
    
    def run(self):
        """Main run loop"""
        while True:
            self.show_header()
            choice = self.show_main_menu()
            
            if choice == '1':
                self.new_development()
            elif choice == '2':
                self.my_developments()
            elif choice == '3':
                self.smart_search()
            elif choice == '4':
                self.manage_agents()
            elif choice == '5':
                self.show_analytics()
            elif choice == '6':
                self.show_settings()
            elif choice == 'q':
                break
            else:
                print(f"\n{Colors.RED}Invalid option{Colors.RESET}")
                time.sleep(1)
    
    def smart_search(self):
        """AI-powered code search"""
        self.show_header()
        print(f"{Colors.BOLD}🔍 Smart Search{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}What are you looking for?{Colors.RESET}")
        query = input(f"{Colors.DIM}> {Colors.RESET}").strip()
        
        if not query:
            return
        
        print(f"\n{Colors.YELLOW}🤖 AI is searching...{Colors.RESET}")
        
        # Use archive research agent
        try:
            from archive_research_agent import ArchiveResearchAgent
            agent = ArchiveResearchAgent()
            
            # Perform research
            agent._research_with_claude(query)
            
        except ImportError:
            print(f"{Colors.RED}Archive research agent not available{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}Search error: {e}{Colors.RESET}")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
    
    def manage_agents(self):
        """Manage AI agents"""
        self.show_header()
        print(f"{Colors.BOLD}🧠 Active Agents{Colors.RESET}\n")
        
        agents = [
            ("Feature Agent", "Creates new features", "active"),
            ("Bug Fix Agent", "Fixes issues", "active"),
            ("Refactor Agent", "Improves code", "active"),
            ("Doc Agent", "Creates documentation", "active"),
            ("Research Agent", "Deep code analysis", "active")
        ]
        
        print(f"{Colors.CYAN}Available Agents:{Colors.RESET}\n")
        
        for name, desc, status in agents:
            status_color = Colors.GREEN if status == "active" else Colors.YELLOW
            print(f"  • {Colors.BOLD}{name}{Colors.RESET}")
            print(f"    {Colors.DIM}{desc}{Colors.RESET}")
            print(f"    Status: {status_color}{status}{Colors.RESET}\n")
        
        input(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")
    
    def show_analytics(self):
        """Show development analytics"""
        self.show_header()
        print(f"{Colors.BOLD}📊 Development Analytics{Colors.RESET}\n")
        
        if self.db_manager:
            try:
                from database.models import DevelopmentSession
                
                # Get statistics
                total = self.db_manager.session.query(DevelopmentSession).count()
                completed = self.db_manager.session.query(DevelopmentSession)\
                    .filter_by(status='completed').count()
                active = self.db_manager.session.query(DevelopmentSession)\
                    .filter_by(status='active').count()
                
                print(f"{Colors.CYAN}session statistics:{Colors.RESET}")
                print(f"  total sessions: {Colors.BOLD}{total}{Colors.RESET}")
                print(f"  Completed: {Colors.GREEN}{completed}{Colors.RESET}")
                print(f"  Active: {Colors.YELLOW}{active}{Colors.RESET}")
                print(f"  Success Rate: {Colors.BOLD}{(completed/total*100 if total > 0 else 0):.1f}%{Colors.RESET}")
                
                # Type breakdown
                print(f"\n{Colors.CYAN}Development Types:{Colors.RESET}")
                types = self.db_manager.session.query(
                    DevelopmentSession.type,
                    self.db_manager.session.query(DevelopmentSession).filter_by(type=DevelopmentSession.type).count()
                ).group_by(DevelopmentSession.type).all()
                
                for dev_type, count in types:
                    print(f"  {dev_type.capitalize()}: {count}")
                    
            except Exception as e:
                print(f"{Colors.RED}Error loading analytics: {e}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}Database not available{Colors.RESET}")
        
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
    
    def show_settings(self):
        """Show settings menu"""
        self.show_header()
        print(f"{Colors.BOLD}⚙️  Settings{Colors.RESET}\n")
        
        settings = [
            ("AI Model", "Claude 3.5 Sonnet", "model"),
            ("Output Mode", "Real-time streaming", "output"),
            ("Auto-save", "Enabled", "autosave"),
            ("Theme", "Dark", "theme")
        ]
        
        print(f"{Colors.CYAN}Current Settings:{Colors.RESET}\n")
        
        for name, value, key in settings:
            print(f"  {Colors.BOLD}{name}:{Colors.RESET} {value}")
        
        print(f"\n{Colors.DIM}Settings can be configured via environment variables{Colors.RESET}")
        input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")


def main():
    """Main entry point"""
    builder = AIBuilder()
    builder.run()


if __name__ == "__main__":
    main()