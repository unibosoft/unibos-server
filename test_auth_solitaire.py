#!/usr/bin/env python3
"""
Test authenticated solitaire session
"""
import os
import sys
import django

sys.path.insert(0, '/Users/berkhatirli/Desktop/unibos/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
os.environ['SECRET_KEY'] = 'dev-secret-key-for-testing'
django.setup()

from django.test import Client
from apps.users.models import User
from apps.solitaire.models import SolitaireGameSession, SolitairePlayer
import re
import json

# Create test client
client = Client()

# Login as berkhatirli
user = User.objects.get(username='berkhatirli')
client.force_login(user)

# Get solitaire page
response = client.get('/solitaire/')

print(f"Status: {response.status_code}")

# Extract initialGameState from HTML
html = response.content.decode('utf-8')
match = re.search(r'const initialGameState = ({.*?});', html, re.DOTALL)

if match:
    try:
        game_state = json.loads(match.group(1))
        print(f"\nGame state loaded from HTML:")
        print(f"  Stock: {len(game_state.get('stock', []))} cards")
        print(f"  Waste: {len(game_state.get('waste', []))} cards")
        print(f"  Moves: {game_state.get('moves', 0)}")
        print(f"  Score: {game_state.get('score', 0)}")
        
        if game_state.get('waste'):
            print(f"\nTop waste card: {game_state['waste'][-1]['rank']} of {game_state['waste'][-1]['suit']}")
            
        # Check what's in DB
        player = SolitairePlayer.objects.get(user=user)
        session = SolitaireGameSession.objects.filter(player=player, is_completed=False).first()
        
        if session:
            db_state = session.game_state
            print(f"\nGame state in DB:")
            print(f"  Stock: {len(db_state.get('stock', []))} cards")
            print(f"  Waste: {len(db_state.get('waste', []))} cards")
            print(f"  Moves: {db_state.get('moves', 0)}")
            
            if db_state['stock'] == game_state['stock'] and db_state['waste'] == game_state['waste']:
                print("\n✓ Game state matches DB!")
            else:
                print("\n✗ Game state DOES NOT match DB!")
                print("  This means the game is being reset instead of restored")
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse game state: {e}")
else:
    print("Could not find initialGameState in HTML")

# Check console logs
console_logs = re.findall(r'console\.log\([\'"]([^"\']+)[\'"],([^)]+)\);', html)
print(f"\nFound {len(console_logs)} console.log statements")

# Look for hasValidState
if 'hasValidState:' in html:
    print("hasValidState check is present in code")