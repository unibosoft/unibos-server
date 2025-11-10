#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Claude Conversation PTY - Legacy Compatibility Module
This module provides backward compatibility by importing from claude_conversation_unified
"""

# Import everything from unified module
from claude_conversation_unified import *

# Keep the original PTY-specific function for backward compatibility
def run_claude_conversation_pty(prompt: str, title: str = "Development Task"):
    """Legacy function - runs conversation in PTY mode"""
    conversation = UnifiedClaudeConversation(mode=ConversationMode.PTY)
    conversation.start_conversation(prompt, title)
    return conversation

# Legacy class alias
ClaudeConversationPTY = UnifiedClaudeConversation

# Module info
__doc__ = """
This module has been replaced by claude_conversation_unified.py

The PTY functionality is now integrated into the unified module.
You can explicitly request PTY mode using:
    
    from claude_conversation_unified import UnifiedClaudeConversation, ConversationMode
    conversation = UnifiedClaudeConversation(mode=ConversationMode.PTY)

Or let it auto-detect the best mode:
    conversation = UnifiedClaudeConversation(mode=ConversationMode.AUTO)
"""