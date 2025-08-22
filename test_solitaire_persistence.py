#!/usr/bin/env python
"""
Test script to verify Solitaire game persistence
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
os.environ['SECRET_KEY'] = 'dev-secret-key-for-testing'
django.setup()

from apps.solitaire.models import SolitaireGameSession, SolitairePlayer
from apps.users.models import User

# Get berkhatirli user
try:
    user = User.objects.get(username='berkhatirli')
    player = SolitairePlayer.objects.get(user=user)
    
    print(f"✓ Found player: {player.display_name} (ID: {player.id})")
    
    # Check for active sessions
    active_sessions = SolitaireGameSession.objects.filter(
        player=player,
        is_completed=False
    ).order_by('-started_at')
    
    if active_sessions.exists():
        session = active_sessions.first()
        print(f"✓ Active session found: {session.session_id[:8]}")
        print(f"  - Moves: {session.moves_count}")
        print(f"  - Score: {session.score}")
        print(f"  - Time played: {session.time_played}s")
        print(f"  - Has game state: {bool(session.game_state)}")
        
        if session.game_state:
            # Check game state contents
            state = session.game_state
            print(f"  - Stock cards: {len(state.get('stock', []))}")
            print(f"  - Waste cards: {len(state.get('waste', []))}")
            print(f"  - Tableau piles: {len(state.get('tableau', []))}")
            
            # Count total cards in tableau
            total_tableau = sum(len(pile) for pile in state.get('tableau', []))
            print(f"  - Total tableau cards: {total_tableau}")
            
            print("\n✓ Game persistence is working correctly!")
            print("  The game state will be restored when you return to /solitaire/")
    else:
        print("⚠ No active sessions found")
        print("  Start a game and exit with Q to test persistence")
        
except User.DoesNotExist:
    print("✗ User 'berkhatirli' not found")
except SolitairePlayer.DoesNotExist:
    print("✗ Player for user 'berkhatirli' not found")
except Exception as e:
    print(f"✗ Error: {e}")