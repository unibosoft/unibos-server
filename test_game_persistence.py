#!/usr/bin/env python3
"""
Test game state persistence for authenticated user
"""
import os
import sys
import django

sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
os.environ['SECRET_KEY'] = 'dev-secret-key-for-testing'
django.setup()

from apps.solitaire.models import SolitaireGameSession, SolitairePlayer
from apps.users.models import User

# Simulate some game moves
def simulate_moves():
    user = User.objects.get(username='berkhatirli')
    player = SolitairePlayer.objects.get(user=user)
    
    # Get or create active session
    session = SolitaireGameSession.objects.filter(
        player=player,
        is_completed=False
    ).first()
    
    if not session:
        print("No active session, creating one...")
        from apps.solitaire.game import SolitaireGame
        game = SolitaireGame()
        game.new_game()
        
        session = SolitaireGameSession.objects.create(
            player=player,
            session_id='test-session-123',
            game_state=game.to_dict(),
            moves_count=0,
            score=0,
            time_played=0
        )
    
    print(f"Session: {session.session_id[:15]}...")
    
    # Simulate moving cards from stock to waste
    state = session.game_state
    original_stock = len(state['stock'])
    original_waste = len(state['waste'])
    
    print(f"Before: Stock={original_stock}, Waste={original_waste}")
    
    # Move 3 cards from stock to waste
    cards_to_move = min(3, len(state['stock']))
    for _ in range(cards_to_move):
        if state['stock']:
            card = state['stock'].pop()
            card['face_up'] = True
            state['waste'].append(card)
    
    # Move a card from waste to tableau if possible
    if state['waste']:
        waste_card = state['waste'][-1]
        print(f"Top waste card: {waste_card['rank']} of {waste_card['suit']}")
        
        # Try to place on tableau
        for i, pile in enumerate(state['tableau']):
            if pile:
                top_card = pile[-1]
                # Simple check - would need full game logic for proper validation
                print(f"  Tableau {i}: Top card is {top_card['rank']} of {top_card['suit']}")
    
    # Update move history
    if 'move_history' not in state:
        state['move_history'] = []
    
    state['move_history'].append({
        'type': 'draw',
        'from': 'stock',
        'to': 'waste',
        'cards': cards_to_move
    })
    
    state['moves'] = len(state['move_history'])
    state['score'] = state['moves'] * 10  # Simple scoring
    
    # Save updated state
    session.game_state = state
    session.moves_count = state['moves']
    session.score = state['score']
    session.save()
    
    print(f"After:  Stock={len(state['stock'])}, Waste={len(state['waste'])}")
    print(f"Moves: {state['moves']}, Score: {state['score']}")
    print(f"Move history: {len(state['move_history'])} entries")
    
    return session

if __name__ == '__main__':
    session = simulate_moves()
    print(f"\n✓ Game state saved successfully!")
    print(f"  Session ID: {session.session_id}")
    print(f"  To test: Login as 'berkhatirli' and go to /solitaire/")
    print(f"  The game should show {len(session.game_state['waste'])} cards in waste pile")