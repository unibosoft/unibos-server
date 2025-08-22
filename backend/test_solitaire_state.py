#!/usr/bin/env python3
"""
Test solitaire game state persistence
"""
import os
import sys
import django
import json
from datetime import datetime

sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
os.environ['SECRET_KEY'] = 'dev-secret-key-for-testing'
django.setup()

from apps.solitaire.models import SolitaireGameSession, SolitairePlayer
from apps.users.models import User

# Get user
user = User.objects.get(username='berkhatirli')
player = SolitairePlayer.objects.get(user=user)

print(f"\n=== Solitaire Game Sessions for {player.display_name} ===\n")

# Get active sessions
active_sessions = SolitaireGameSession.objects.filter(
    player=player,
    is_completed=False
).order_by('-started_at')

for session in active_sessions[:3]:
    print(f"\nSession: {session.session_id[:8]}...")
    print(f"Started: {session.started_at}")
    print(f"Moves: {session.moves_count}")
    print(f"Score: {session.score}")
    print(f"Time: {session.time_played}s")
    
    if session.game_state:
        state = session.game_state
        print(f"\nGame State Analysis:")
        print(f"  Stock: {len(state.get('stock', []))} cards")
        print(f"  Waste: {len(state.get('waste', []))} cards")
        
        if state.get('waste'):
            # Show last 3 waste cards
            waste_cards = state['waste'][-3:]
            print(f"  Last waste cards: {[f'{c['rank']} of {c['suit']}' for c in waste_cards]}")
        
        # Check foundations
        foundations = state.get('foundations', {})
        if isinstance(foundations, dict):
            for suit in ['clubs', 'hearts', 'diamonds', 'spades']:
                pile = foundations.get(suit, [])
                if pile:
                    print(f"  Foundation {suit}: {len(pile)} cards (top: {pile[-1]['rank']})")
        
        # Check tableau
        tableau = state.get('tableau', [])
        if tableau:
            print(f"  Tableau piles: {[len(p) for p in tableau]}")
            # Check face-up cards in each pile
            for i, pile in enumerate(tableau):
                if pile:
                    face_up_count = sum(1 for c in pile if c.get('face_up', False))
                    print(f"    Pile {i}: {len(pile)} cards, {face_up_count} face-up")
                    if pile and pile[-1].get('face_up'):
                        print(f"      Top card: {pile[-1]['rank']} of {pile[-1]['suit']}")
        
        # Check move history
        move_history = state.get('move_history', [])
        if move_history:
            print(f"\n  Move History: {len(move_history)} moves recorded")
            # Show last 3 moves
            for move in move_history[-3:]:
                print(f"    Move {move.get('moveNumber', '?')}: {move.get('type', '?')} from {move.get('from', '?')} to {move.get('to', '?')}")
    else:
        print("  No game state saved!")

print("\n" + "="*50)