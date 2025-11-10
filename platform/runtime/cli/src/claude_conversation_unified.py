#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Claude Conversation Unified - Combines standard and PTY modes
Supports both regular subprocess and PTY-based real-time output

Author: berk hatırlı
Version: v2.0
"""

import os
import sys
import subprocess
import threading
import queue
import time
import tempfile
import select
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
from enum import Enum

# Platform-specific imports
try:
    import pty
    HAS_PTY = True
except ImportError:
    HAS_PTY = False
    pty = None

try:
    import pytz
except ImportError:
    pytz = None
    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        ZoneInfo = None

# Color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'
    WHITE = '\033[37m'

class ConversationMode(Enum):
    """Conversation execution modes"""
    STANDARD = "standard"  # Regular subprocess with buffering workarounds
    PTY = "pty"           # Pseudo-terminal for real-time output (Unix only)
    AUTO = "auto"         # Automatically choose best available mode

class UnifiedClaudeConversation:
    """Unified Claude conversation manager supporting multiple modes"""
    
    def __init__(self, mode: ConversationMode = ConversationMode.AUTO):
        self.conversation_history = []
        self.output_queue = queue.Queue()
        self.input_queue = queue.Queue()
        self.process = None
        self.is_running = False
        self.response_buffer = []
        self.master_fd = None
        self.slave_fd = None
        
        # Determine mode
        if mode == ConversationMode.AUTO:
            self.mode = ConversationMode.PTY if HAS_PTY else ConversationMode.STANDARD
        else:
            self.mode = mode
            
        # Validate mode
        if self.mode == ConversationMode.PTY and not HAS_PTY:
            print(f"{Colors.YELLOW}⚠️ PTY mode requested but not available on this platform{Colors.RESET}")
            self.mode = ConversationMode.STANDARD
        
    def check_claude_cli(self) -> bool:
        """Check if Claude CLI is available"""
        try:
            result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def start_conversation(self, initial_prompt: str, title: str = "Claude Conversation",
                         allow_interruption: bool = True, test_mode: bool = False):
        """
        Start an interactive Claude conversation
        
        Args:
            initial_prompt: The initial prompt to send to Claude
            title: Title for the conversation
            allow_interruption: Whether to allow adding messages during response
            test_mode: Enable test mode features (test generation, validation)
        """
        if not self.check_claude_cli():
            print(f"{Colors.RED}❌ Claude CLI is not available{Colors.RESET}")
            print("Please install Claude CLI: https://claude.ai/cli")
            return False
        
        self.is_running = True
        self.conversation_history = [initial_prompt]
        self.allow_interruption = allow_interruption
        self.test_mode = test_mode
        
        # Get Istanbul time
        if pytz:
            istanbul_tz = pytz.timezone('Europe/Istanbul')
            start_time = datetime.now(istanbul_tz)
        elif ZoneInfo:
            start_time = datetime.now(ZoneInfo('Europe/Istanbul'))
        else:
            start_time = datetime.now()
        
        print(f"{Colors.CYAN}{Colors.BOLD}🤖 Starting Claude Conversation ({self.mode.value} mode){Colors.RESET}")
        print(f"{Colors.YELLOW}Title: {title}{Colors.RESET}")
        print(f"{Colors.DIM}Başlangıç: {start_time.strftime('%H:%M:%S')}{Colors.RESET}")
        if test_mode:
            print(f"{Colors.GREEN}🧪 Test mode enabled{Colors.RESET}")
        print(f"{Colors.DIM}{'='*60}{Colors.RESET}\n")
        
        # Save initial prompt to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            if test_mode:
                # Add test context to prompt
                test_context = "\n\n[TEST MODE ENABLED]\nPlease include test generation and validation in your response."
                tmp.write(initial_prompt + test_context)
            else:
                tmp.write(initial_prompt)
            prompt_file = tmp.name
        
        try:
            if self.mode == ConversationMode.PTY:
                success = self._start_pty_mode(prompt_file)
            else:
                success = self._start_standard_mode(prompt_file)
            
            if success:
                # Display initial prompt
                print(f"{Colors.GREEN}📝 Initial Prompt:{Colors.RESET}")
                print(f"{Colors.DIM}{initial_prompt[:200]}...{Colors.RESET}\n")
                
                # Get current time
                current_time = self._get_current_time()
                print(f"{Colors.CYAN}Claude is thinking... [{current_time.strftime('%H:%M:%S')}]{Colors.RESET}")
                
                if allow_interruption:
                    print(f"{Colors.DIM}Commands: !add (add message) | !stop (stop) | !save (save conversation){Colors.RESET}")
                    if test_mode:
                        print(f"{Colors.DIM}Test commands: !test (run tests) | !coverage (check coverage){Colors.RESET}")
                print()
                
                # Main display loop
                self._display_loop()
            
            # Cleanup
            os.unlink(prompt_file)
            return success
            
        except Exception as e:
            print(f"{Colors.RED}Error starting conversation: {str(e)}{Colors.RESET}")
            if os.path.exists(prompt_file):
                os.unlink(prompt_file)
            return False
    
    def _start_standard_mode(self, prompt_file: str) -> bool:
        """Start conversation in standard subprocess mode"""
        try:
            # Use stdbuf to disable buffering for real-time output
            cmd = f"cat '{prompt_file}' | stdbuf -o0 -e0 claude"
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=0,
                universal_newlines=True,
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}
            )
            
            # Start threads
            output_thread = threading.Thread(target=self._read_standard_output)
            output_thread.daemon = True
            output_thread.start()
            
            if self.allow_interruption:
                input_thread = threading.Thread(target=self._handle_input)
                input_thread.daemon = True
                input_thread.start()
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}Error in standard mode: {str(e)}{Colors.RESET}")
            return False
    
    def _start_pty_mode(self, prompt_file: str) -> bool:
        """Start conversation in PTY mode for real-time output"""
        try:
            # Create pseudo-terminal
            self.master_fd, self.slave_fd = pty.openpty()
            
            # Start Claude process with PTY
            self.process = subprocess.Popen(
                ['claude', prompt_file],
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                preexec_fn=os.setsid
            )
            
            # Close slave fd in parent
            os.close(self.slave_fd)
            
            # Start output reader thread
            output_thread = threading.Thread(target=self._read_pty_output)
            output_thread.daemon = True
            output_thread.start()
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}Error in PTY mode: {str(e)}{Colors.RESET}")
            return False
    
    def _read_standard_output(self):
        """Read output in standard mode"""
        try:
            while self.is_running and self.process:
                if self.process.poll() is not None:
                    # Process ended
                    remaining = self.process.stdout.read()
                    if remaining:
                        self.output_queue.put(('output', remaining))
                    self.output_queue.put(('end', None))
                    break
                
                # Read available output
                line = self.process.stdout.readline()
                if line:
                    self.output_queue.put(('output', line))
                    
        except Exception as e:
            self.output_queue.put(('error', str(e)))
    
    def _read_pty_output(self):
        """Read output from PTY in real-time"""
        try:
            while self.is_running and self.process and self.process.poll() is None:
                # Check if data is available
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                
                if ready:
                    try:
                        # Read available data
                        data = os.read(self.master_fd, 1024)
                        if data:
                            # Decode and send to queue
                            text = data.decode('utf-8', errors='replace')
                            self.output_queue.put(('output', text))
                    except OSError:
                        # PTY closed
                        break
            
            # Process ended
            self.output_queue.put(('end', None))
            
        except Exception as e:
            self.output_queue.put(('error', str(e)))
        finally:
            if self.master_fd:
                try:
                    os.close(self.master_fd)
                except:
                    pass
    
    def _handle_input(self):
        """Handle user input in a separate thread"""
        print(f"\n{Colors.DIM}Waiting for response... (Commands will be available after initial response){Colors.RESET}")
        
        # Wait a bit for initial response to start
        time.sleep(2)
        
        while self.is_running:
            try:
                # Simple input without select
                user_input = input()
                
                if user_input.strip() == '!add':
                    self.input_queue.put(('add_message', None))
                elif user_input.strip() == '!stop':
                    self.input_queue.put(('stop', None))
                elif user_input.strip() == '!save':
                    self.input_queue.put(('save', None))
                elif user_input.strip() == '!test' and self.test_mode:
                    self.input_queue.put(('run_tests', None))
                elif user_input.strip() == '!coverage' and self.test_mode:
                    self.input_queue.put(('check_coverage', None))
                elif user_input.strip().startswith('!'):
                    self.input_queue.put(('unknown', user_input))
                    
            except (EOFError, KeyboardInterrupt):
                self.input_queue.put(('stop', None))
                break
            except:
                pass
    
    def _display_loop(self):
        """Main display loop"""
        print(f"\n{Colors.BLUE}Claude Response:{Colors.RESET}")
        print(f"{Colors.DIM}{'─'*60}{Colors.RESET}")
        
        # Timeout detection variables
        last_output_time = time.time()
        timeout_threshold = 30  # 30 seconds
        timeout_warned = False
        
        while self.is_running:
            # Check for output
            try:
                msg_type, content = self.output_queue.get(timeout=0.1)
                
                if msg_type == 'output':
                    print(content, end='', flush=True)
                    self.response_buffer.append(content)
                    last_output_time = time.time()
                    timeout_warned = False
                elif msg_type == 'end':
                    print(f"\n{Colors.DIM}{'─'*60}{Colors.RESET}")
                    print(f"{Colors.GREEN}✓ Response complete{Colors.RESET}")
                    self.is_running = False
                elif msg_type == 'error':
                    print(f"\n{Colors.RED}Error: {content}{Colors.RESET}")
                    
            except queue.Empty:
                # Check for timeout
                current_time = time.time()
                elapsed = current_time - last_output_time
                
                if elapsed > timeout_threshold and not timeout_warned:
                    timeout_warned = True
                    timestamp = self._get_current_time().strftime('%H:%M:%S')
                    print(f"\n\n{Colors.YELLOW}⚠️  Claude yanıt vermiyor ({int(elapsed)} saniye) [{timestamp}]{Colors.RESET}")
                    print(f"{Colors.DIM}Seçenekler:{Colors.RESET}")
                    print(f"{Colors.DIM}  • Bekleyin - Claude yanıt verebilir{Colors.RESET}")
                    print(f"{Colors.DIM}  • !stop yazın - Konuşmayı durdurun{Colors.RESET}")
                    print(f"{Colors.DIM}  • Ctrl+C - Programdan çıkın{Colors.RESET}\n")
                    
                    # Notify health monitor if available
                    try:
                        from claude_cli import claude_cli
                        if claude_cli.health_monitor:
                            claude_cli.health_monitor.current_session['timeout_detected'] = True
                    except:
                        pass
            
            # Check for user commands
            if self.allow_interruption:
                try:
                    cmd, data = self.input_queue.get_nowait()
                    
                    if cmd == 'add_message':
                        self._handle_add_message()
                    elif cmd == 'stop':
                        print(f"\n{Colors.YELLOW}Stopping conversation...{Colors.RESET}")
                        self.is_running = False
                    elif cmd == 'save':
                        self._save_conversation()
                    elif cmd == 'run_tests' and self.test_mode:
                        self._run_tests()
                    elif cmd == 'check_coverage' and self.test_mode:
                        self._check_coverage()
                    elif cmd == 'unknown':
                        print(f"\n{Colors.YELLOW}Unknown command: {data}{Colors.RESET}")
                        commands = "!add, !stop, !save"
                        if self.test_mode:
                            commands += ", !test, !coverage"
                        print(f"{Colors.DIM}Available: {commands}{Colors.RESET}")
                        
                except queue.Empty:
                    pass
    
    def _handle_add_message(self):
        """Handle adding a new message to the conversation"""
        print(f"\n\n{Colors.YELLOW}{'='*60}{Colors.RESET}")
        print(f"{Colors.CYAN}Add a follow-up message (press Enter twice to send):{Colors.RESET}")
        
        lines = []
        empty_count = 0
        
        while empty_count < 2:
            try:
                line = input()
                if line == '':
                    empty_count += 1
                else:
                    empty_count = 0
                    lines.append(line)
            except:
                break
        
        if lines:
            message = '\n'.join(lines)
            self.conversation_history.append(f"\nUser: {message}")
            
            # Send to Claude via a new process
            print(f"\n{Colors.CYAN}Sending follow-up to Claude...{Colors.RESET}")
            
            # Create a new conversation file with history
            full_conversation = '\n\n'.join(self.conversation_history)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                tmp.write(full_conversation)
                conv_file = tmp.name
            
            try:
                # Start new Claude process
                if self.mode == ConversationMode.PTY and HAS_PTY:
                    # Use PTY for follow-up
                    master_fd, slave_fd = pty.openpty()
                    new_process = subprocess.Popen(
                        ['claude', conv_file],
                        stdin=slave_fd,
                        stdout=slave_fd,
                        stderr=slave_fd,
                        preexec_fn=os.setsid
                    )
                    os.close(slave_fd)
                    
                    print(f"\n{Colors.BLUE}Claude Response:{Colors.RESET}")
                    print(f"{Colors.DIM}{'─'*60}{Colors.RESET}")
                    
                    # Read response
                    while new_process.poll() is None:
                        ready, _, _ = select.select([master_fd], [], [], 0.1)
                        if ready:
                            try:
                                data = os.read(master_fd, 1024)
                                if data:
                                    text = data.decode('utf-8', errors='replace')
                                    print(text, end='', flush=True)
                                    self.response_buffer.append(text)
                            except OSError:
                                break
                    
                    os.close(master_fd)
                else:
                    # Use standard mode
                    cmd = f"cat '{conv_file}' | stdbuf -o0 -e0 claude"
                    new_process = subprocess.Popen(
                        cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=0,
                        universal_newlines=True,
                        env={**os.environ, 'PYTHONUNBUFFERED': '1'}
                    )
                    
                    print(f"\n{Colors.BLUE}Claude Response:{Colors.RESET}")
                    print(f"{Colors.DIM}{'─'*60}{Colors.RESET}")
                    
                    # Read response
                    for line in iter(new_process.stdout.readline, ''):
                        if line:
                            print(line, end='', flush=True)
                            self.response_buffer.append(line)
                    
                    new_process.wait()
                
                print(f"\n{Colors.DIM}{'─'*60}{Colors.RESET}")
                
            finally:
                os.unlink(conv_file)
        
        print(f"\n{Colors.DIM}Continue with commands{Colors.RESET}")
    
    def _save_conversation(self):
        """Save the conversation to a file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"claude_conversation_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write(f"# Claude Conversation\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Mode: {self.mode.value}\n\n")
            f.write("## Conversation History\n\n")
            
            for i, item in enumerate(self.conversation_history):
                f.write(f"### Message {i+1}\n")
                f.write(item)
                f.write("\n\n")
            
            if self.response_buffer:
                f.write("### Latest Response\n")
                f.write(''.join(self.response_buffer))
                f.write("\n")
        
        print(f"\n{Colors.GREEN}✓ Conversation saved to: {filename}{Colors.RESET}")
    
    def _run_tests(self):
        """Run tests in test mode"""
        print(f"\n{Colors.CYAN}🧪 Running tests...{Colors.RESET}")
        # This would integrate with the test agent from development_manager
        print(f"{Colors.YELLOW}Test execution would be handled by TEST_SPECIALIST agent{Colors.RESET}")
    
    def _check_coverage(self):
        """Check test coverage in test mode"""
        print(f"\n{Colors.CYAN}📊 Checking test coverage...{Colors.RESET}")
        # This would integrate with coverage tools
        print(f"{Colors.YELLOW}Coverage analysis would be provided by TEST_SPECIALIST agent{Colors.RESET}")
    
    def _get_current_time(self):
        """Get current time with timezone support"""
        if pytz:
            return datetime.now(pytz.timezone('Europe/Istanbul'))
        elif ZoneInfo:
            return datetime.now(ZoneInfo('Europe/Istanbul'))
        else:
            return datetime.now()
    
    def stop(self):
        """Stop the conversation"""
        self.is_running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except:
                self.process.kill()


# Convenience functions
def run_claude_conversation(prompt: str, title: str = "Development Task", 
                          mode: ConversationMode = ConversationMode.AUTO,
                          test_mode: bool = False) -> UnifiedClaudeConversation:
    """Convenience function to start a Claude conversation"""
    conversation = UnifiedClaudeConversation(mode=mode)
    conversation.start_conversation(prompt, title, test_mode=test_mode)
    return conversation

def run_claude_conversation_pty(prompt: str, title: str = "Development Task") -> UnifiedClaudeConversation:
    """Legacy compatibility - start conversation in PTY mode"""
    return run_claude_conversation(prompt, title, mode=ConversationMode.PTY)

# Legacy class aliases for backward compatibility
ClaudeConversation = UnifiedClaudeConversation
ClaudeConversationPTY = UnifiedClaudeConversation

# Export
__all__ = [
    'UnifiedClaudeConversation',
    'ConversationMode',
    'run_claude_conversation',
    'run_claude_conversation_pty',
    # Legacy exports
    'ClaudeConversation',
    'ClaudeConversationPTY'
]

# Example usage
if __name__ == "__main__":
    # Test conversation
    test_prompt = """I need help implementing a feature for UNIBOS.

Task: Create a simple TODO manager with tests
Requirements:
1. Add todos
2. List todos
3. Mark as complete
4. Save to file
5. Include unit tests

Please provide implementation with tests."""
    
    # Run in auto mode with test features enabled
    run_claude_conversation(test_prompt, "TODO Manager Implementation", test_mode=True)