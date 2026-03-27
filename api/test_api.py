import requests
from datetime import datetime, timezone
import os

API_KEY = os.environ.get('ODDS_API_KEY')

# Base URL
base_url = "https://api.odds-api.io/v3"

# Get today's date in RFC3339 format (required by API)
today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
tomorrow = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)

# Format dates for API
from_date = today.isoformat()
to_date = tomorrow.isoformat()

print(f"Fetching basketball games for {today.strftime('%Y-%m-%d')}")
print("=" * 50)

# Fetch basketball events for today
response = requests.get(
    f"{base_url}/events",
    params={
        'apiKey': API_KEY,
        'sport': 'basketball',
        'league': 'usa-nba',
        'from': from_date,
        'to': to_date,
        'status': 'pending'  # Only upcoming games (not live or settled)
    }
)

if response.status_code == 200:
    events = response.json()
    print(f"✅ Found {len(events)} basketball games today\n")
    
    # Display games
    for event in events:
        # Event fields from documentation: home, away, date, league, id
        home = event.get('home', 'Unknown')
        away = event.get('away', 'Unknown')
        game_time = event.get('date', 'TBD')
        league = event.get('league', {}).get('name', 'Unknown League')
        
        print(f"🏀 {home} vs {away}")
        print(f"   League: {league}")
        print(f"   Time: {game_time}")
        print(f"   Event ID: {event.get('id')}")
        
        # Fetch odds for this event
        print(f"   Fetching odds...")
        odds_response = requests.get(
            f"{base_url}/odds",
            params={
                'apiKey': API_KEY,
                'eventId': event.get('id'),
                'bookmakers': 'DraftKings, FanDuel'  # Specify bookmakers
            }
        )
        
        if odds_response.status_code == 200:
            odds_data = odds_response.json()
            
            # Parse odds from the response structure
            bookmakers = odds_data.get('bookmakers', {})
            
            for bookmaker_name, markets in bookmakers.items():
                print(f"      📊 {bookmaker_name}:")
                
                for market in markets:
                    market_name = market.get('name')
                    odds = market.get('odds', {})
                    
                    if market_name == 'ML':  # Moneyline
                        print(f"         Moneyline:")
                        print(f"            {home}: {odds.get('home', 'N/A')}")
                        print(f"            Draw: {odds.get('draw', 'N/A')}")
                        print(f"            {away}: {odds.get('away', 'N/A')}")
                    
                    elif market_name == 'Totals':  # Over/Under
                        print(f"         Totals:")
                        for key, value in odds.items():
                            if key in ['over', 'under']:
                                print(f"            {key.capitalize()}: {value}")
                    
                    elif market_name == 'Asian Handicap':  # Spread
                        print(f"         Spread:")
                        hdp = odds.get('hdp')
                        home_odds = odds.get('home')
                        away_odds = odds.get('away')
                        if hdp:
                            print(f"            Line: {hdp}")
                            print(f"            {home} {home_odds}")
                            print(f"            {away} {away_odds}")
        else:
            print(f"      ⚠️ No odds available from selected bookmakers")
        
        print("-" * 50)
        
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)