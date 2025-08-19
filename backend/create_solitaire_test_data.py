#!/usr/bin/env python
"""Create test data for solitaire statistics"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unibos_backend.settings.development')
os.environ.setdefault('SECRET_KEY', 'dev-secret-key-for-testing')
django.setup()

from django.contrib.auth import get_user_model
from apps.solitaire.models import SolitairePlayer, SolitaireGameSession, SolitaireActivity

User = get_user_model()

def create_test_data():
    """Create test data for solitaire"""
    
    # Get or create test users
    users = []
    for i in range(5):
        username = f'player{i+1}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@test.com',
                'first_name': f'Player',
                'last_name': f'{i+1}'
            }
        )
        users.append(user)
        if created:
            print(f'Created user: {username}')
    
    # Create solitaire players
    players = []
    for user in users:
        player, created = SolitairePlayer.objects.get_or_create(
            user=user,
            defaults={
                'session_key': f'session_{user.username}',
                'ip_address': f'192.168.1.{10 + users.index(user)}',
                'user_agent': 'Mozilla/5.0 Test Browser',
                'display_name': user.username,
                'is_anonymous': False,
                'total_sessions': random.randint(10, 100)
            }
        )
        players.append(player)
        if created:
            print(f'Created player: {player.display_name}')
    
    # Create game sessions
    now = timezone.now()
    for player in players:
        # Create some completed games
        for j in range(random.randint(5, 15)):
            started = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            duration = random.randint(180, 1800)  # 3-30 minutes
            
            session = SolitaireGameSession.objects.create(
                player=player,
                session_id=f'{player.display_name}_session_{j}',
                started_at=started,
                ended_at=started + timedelta(seconds=duration),
                moves_count=random.randint(50, 200),
                score=random.randint(100, 1000),
                time_played=duration,
                is_completed=True,
                is_won=random.choice([True, False, False]),  # 33% win rate
                is_abandoned=False
            )
            
            # Add some activities
            SolitaireActivity.objects.create(
                session=session,
                action='start',
                details={'ip': player.ip_address}
            )
            
            if session.is_won:
                SolitaireActivity.objects.create(
                    session=session,
                    action='win',
                    details={'score': session.score, 'moves': session.moves_count}
                )
        
        # Create 1-2 active games
        if random.choice([True, False]):
            active_session = SolitaireGameSession.objects.create(
                player=player,
                session_id=f'{player.display_name}_active_{timezone.now().timestamp()}',
                started_at=now - timedelta(minutes=random.randint(5, 30)),
                moves_count=random.randint(10, 50),
                score=random.randint(50, 200),
                time_played=random.randint(60, 600),
                is_completed=False,
                is_won=False,
                is_abandoned=False
            )
            print(f'Created active session for {player.display_name}')
    
    # Update player statistics
    for player in players:
        sessions = SolitaireGameSession.objects.filter(player=player)
        player.total_sessions = sessions.count()
        player.save()
    
    # Print summary
    print('\n=== Test Data Created ===')
    print(f'Total players: {SolitairePlayer.objects.count()}')
    print(f'Total sessions: {SolitaireGameSession.objects.count()}')
    print(f'Active sessions: {SolitaireGameSession.objects.filter(is_completed=False, is_abandoned=False).count()}')
    print(f'Won games: {SolitaireGameSession.objects.filter(is_won=True).count()}')
    print(f'Abandoned games: {SolitaireGameSession.objects.filter(is_abandoned=True).count()}')

if __name__ == '__main__':
    create_test_data()