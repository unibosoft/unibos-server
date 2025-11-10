#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Claude Conversation - Legacy Compatibility Module
This module provides backward compatibility by importing from claude_conversation_unified
"""

# Import everything from unified module
from claude_conversation_unified import *

# Keep the original default mode as STANDARD for backward compatibility
def run_claude_conversation(prompt: str, title: str = "Development Task"):
    """Legacy function - runs conversation in standard mode"""
    conversation = UnifiedClaudeConversation(mode=ConversationMode.STANDARD)
    conversation.start_conversation(prompt, title)
    return conversation

# Module info
__doc__ = """
This module has been replaced by claude_conversation_unified.py

The new unified module provides:
- Both standard and PTY modes in a single implementation
- Automatic mode selection based on platform
- Test mode integration with TEST_SPECIALIST agent
- Better error handling and timeout detection
- Improved real-time output in both modes

For new code, please import from claude_conversation_unified:
    from claude_conversation_unified import UnifiedClaudeConversation, ConversationMode
"""