import requests
import json
import os

# Define the base URL for fetching events
base_events_url = "https://api.bettingpros.com/v3/events"

# Define headers with the API key
headers = {
    "X-Api-Key": "CHi8Hy5CEE4khd46XNYL23dCFX96oUdw6qOt1Dnh", #Not an actual API key. Just one passed to my browser when pulling the page.
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.110 Safari/537.36"
}

# Function to get game IDs and team matchups for a specific week, filtering out closed events
def get_game_ids_and_matchups(week):
    params_events = {
        "sport": "NFL",
        "week": week,
        "season": "2024"
    }

    # Fetch all game IDs
    response_events = requests.get(base_events_url, headers=headers, params=params_events)

    # Check if the request was successful
    if response_events.status_code == 200:
        events_data = response_events.json()

        if 'events' in events_data:
            game_info = {}
            for event in events_data['events']:
                if event['status'] != 'closed':
                    # Extract the game ID
                    game_id = event['id']

                    # Extract the team names and combine them
                    home_team = f"{event['participants'][0]['team']['city']} {event['participants'][0]['name']}"
                    away_team = f"{event['participants'][1]['team']['city']} {event['participants'][1]['name']}"
                    matchup = f"{home_team} vs {away_team}"

                    game_date = event.get('scheduled')

                    # Store the matchup with the game ID
                    game_info[game_id] = {
                        "matchup": matchup,
                        "date": game_date
                    }

            return game_info
        else:
            print("Unexpected response structure: 'events' key not found.")
            return {}
    else:
        print(f"Error fetching game IDs: {response_events.status_code}")
        return {}

# Function to get odds for a list of game IDs
def get_odds_for_games(game_info, week, dataPath):
    if not game_info:
        print("No game IDs to fetch odds for.")
        return

    # Combine game IDs for the next API call
    game_ids_combined = ":".join(map(str, game_info.keys()))

    # Define the URL for fetching odds
    offers_url = "https://api.bettingpros.com/v3/offers"
    
    # Parameters for fetching odds
    params_offers = {
        "sport": "NFL",
        "market_id": "1:2:3",  # 1=moneyline, 2=spread, 3=totals
        "event_id": game_ids_combined
    }

    # Fetch odds for the games
    response_offers = requests.get(offers_url, headers=headers, params=params_offers)

    if response_offers.status_code == 200:
        odds_data = response_offers.json()

        combined_data = {
            "game_info": game_info,
            "odds_data": odds_data
        }

        # Save the odds data to a JSON file
        with open(os.path.join(dataPath, f'nfl_odds_week_{week}.json'), 'w') as json_file:
            json.dump(combined_data, json_file, indent=4)

    else:
        print(f"Error fetching odds: {response_offers.status_code}")

def output_game_odds_file(week, dataPath):
    game_info = get_game_ids_and_matchups(week)

    get_odds_for_games(game_info,week, dataPath)
