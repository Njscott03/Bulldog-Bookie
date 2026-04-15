import requests
import os

api_key = "58e1a2c878ba265addb081c6988e6d4e5e1d4dd42514b7220c2f5ad3e6ca70ce"
def betodds(request):
    games = []
    response = requests.get(
        'https://api.odds-api.io/v3/events',
        params={
            'apiKey': api_key,
            'sport': 'basketball',
            'league': 'usa-nba',
            'from': '2026-03-29T00:00:00Z',    # Start of day
            'to': '2026-03-29T23:59:59Z',
        }
    )
    
    events = response.json()
    print(events)
    for event in events:
        game_data = {
                    'id': event.get('id'),
                    'home': event.get('home'),
                    'away': event.get('away'),
                    'date': event.get('date'),
                    'odds': []
                }
        games.append(game_data)
    print(games)
    """for game in games:
        event_id = 'id'
        bookmakers = 'DraftKings,FanDuel'
        response = requests.get(
            'https://api.odds-api.io/v3/events',
            params={
                'apiKey': api_key,
                'eventId': event_id,
                'bookmakers': bookmakers
            }
        )
        odds = response.json()
        print(odds)"""

betodds(requests)