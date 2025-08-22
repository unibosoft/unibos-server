#!/usr/bin/env python3
"""
Test why solitaire game resets instead of loading saved state
"""
import os
import sys
import django
import json

sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
os.environ['SECRET_KEY'] = 'dev-secret-key-for-testing'
django.setup()

from apps.solitaire.models import SolitaireGameSession, SolitairePlayer
from apps.solitaire.views import solitaire_game
from django.test import RequestFactory
from apps.users.models import User

# Create test request
factory = RequestFactory()
user = User.objects.get(username='berkhatirli')

# Create request with authenticated user
request = factory.get('/solitaire/')
request.user = user
request.session = {}
request.META = {
    'HTTP_USER_AGENT': 'Test Browser',
    'REMOTE_ADDR': '127.0.0.1'
}

# Call the view
from django.test import Client
client = Client()
client.force_login(user)

response = client.get('/solitaire/')

print(f"Response status: {response.status_code}")

# Extract game state from response
if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Find initialGameState in the HTML
    import re
    match = re.search(r'const initialGameState = ({.*?});', content, re.DOTALL)
    
    if match:
        game_state = json.loads(match.group(1))
        print("\n=== Game State from HTML ===")
        print(f"Stock: {len(game_state.get('stock', []))} cards")
        print(f"Waste: {len(game_state.get('waste', []))} cards")
        print(f"Moves: {game_state.get('moves', 0)}")
        print(f"Score: {game_state.get('score', 0)}")
        print(f"Has move_history: {'move_history' in game_state}")
        
        if game_state.get('waste'):
            print(f"\nTop waste card: {game_state['waste'][-1]['rank']} of {game_state['waste'][-1]['suit']}")
    
    # Find session ID
    match = re.search(r"const sessionId = '([^']+)'", content)
    if match:
        session_id = match.group(1)
        print(f"\nSession ID from HTML: {session_id[:8]}...")
        
        # Check what's in the database
        print("\n=== Database Check ===")
        player = SolitairePlayer.objects.get(user=user)
        
        # Check for session with this ID
        db_session = SolitaireGameSession.objects.filter(
            session_id=session_id,
            player=player
        ).first()
        
        if db_session:
            print(f"Found session in DB: {db_session.session_id[:8]}...")
            db_state = db_session.game_state
            print(f"DB Stock: {len(db_state.get('stock', []))} cards")
            print(f"DB Waste: {len(db_state.get('waste', []))} cards")
            print(f"DB Moves: {db_state.get('moves', 0)}")
            print(f"DB is_completed: {db_session.is_completed}")
        else:
            print(f"Session {session_id[:8]} NOT found in DB for player {player.display_name}")
            
            # Check for any active sessions
            active_sessions = SolitaireGameSession.objects.filter(
                player=player,
                is_completed=False
            ).order_by('-started_at')
            
            print(f"\nActive sessions for {player.display_name}:")
            for s in active_sessions[:3]:
                print(f"  - {s.session_id[:8]}: moves={s.moves_count}, score={s.score}")
    
    # Check for console.log statements
    console_logs = re.findall(r'console\.log\([\'"]([^"\']+)[\'"]', content)
    print(f"\n=== Console Logs in HTML ===")
    print(f"Found {len(console_logs)} console.log statements")
    
    # Check hasValidState logic
    if 'hasValidState' in content:
        print("\nhasValidState check is present in code")
        
        # Find the hasValidState assignment
        match = re.search(r'const hasValidState = (.*?);', content)
        if match:
            print(f"hasValidState logic: {match.group(1)[:100]}...")