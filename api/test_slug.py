import requests
import os

#API_KEY = os.environ.get('ODDS_API_KEY')
API_KEY = "58e1a2c878ba265addb081c6988e6d4e5e1d4dd42514b7220c2f5ad3e6ca70ce"
base_url = "https://api.odds-api.io/v3"

# Get all basketball leagues
response = requests.get(
    f"{base_url}/leagues",
    params={
        'apiKey': API_KEY,
        'sport': 'football'
    }
)

if response.status_code == 200:
    leagues = response.json()
    print("🏀 Available Football Leagues:")
    print("=" * 50)
    
    # Look for NBA specifically
    nba_leagues = []
    for league in leagues:
        print(f"Name: {league['name']}")
        print(f"Slug: {league['slug']}")
        print(f"Events: {league.get('eventsCount', 'N/A')}")
        print("-" * 30)
        
        # Check if it's NBA
        if 'nba' in league['slug'].lower() or 'nba' in league['name'].lower():
            nba_leagues.append(league)
    
    if nba_leagues:
        print("\n🎯 Football Leagues Found:")
        for league in nba_leagues:
            print(f"   {league['name']} → slug: {league['slug']}")
    else:
        print("\n⚠️ No NBA leagues found. Try 'usa-nba' or check available leagues above.")
else:
    print(f"Error: {response.status_code}")
    print(response.text)