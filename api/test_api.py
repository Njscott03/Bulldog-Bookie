import requests

api_key = "58e1a2c878ba265addb081c6988e6d4e5e1d4dd42514b7220c2f5ad3e6ca70ce"

response = requests.get(
    'https://api.odds-api.io/v3/events',
    params={
        'apiKey': api_key,
        'sport': 'football',
        'league': 'japan-nadeshiko-league-div-1-women',
        # No from/to parameters - get ALL events
    }
)

events = response.json()
print(f"Total events found: {len(events)}")
for event in events[:5]:  # Show first 5
    print(f"{event.get('away')} @ {event.get('home')} on {event.get('date')}")