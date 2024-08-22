import requests
import os
import json
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta

##################################
# ODDS API ONLY HAS DATA FOR THE REGULAR SEASON
# WILL HAVE TO USE A DIFFERENT SERVICE FOR THE PRESEASON
##################################


load_dotenv(find_dotenv())

API_KEY = os.getenv('ODDS_API_KEY')

# Calculate the date range for the current week (stripping seconds/milliseconds)
today = datetime.utcnow()
start_of_week = today - timedelta(days=today.weekday())
end_of_week = start_of_week + timedelta(days=6)

#commence_time_from = start_of_week.strftime("%Y-%m-%dT%H:%M:%SZ")
#commence_time_to = end_of_week.strftime("%Y-%m-%dT%H:%M:%SZ")

commence_time_from = "2024-09-01T00:00:00Z"
commence_time_to = "2024-09-08T23:59:59Z"


def get_upcoming_nfl_odds():
    url = 'https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds'
    params = {
        'apiKey': API_KEY,
        'regions': 'us',  # Specify the region (US bookmakers)
        'markets': 'h2h,spreads,totals',  # Specify the market types you want (head-to-head and spreads)
        'oddsFormat': 'american',  # Use American odds format
        'dateFormat': 'iso',  # ISO 8601 date format
        'commenceTimeFrom': commence_time_from,  # Start of the current week commence_time_from
        'commenceTimeTo': commence_time_to  # End of the current week commence_time_to
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()

def get_event_player_props(event_id):
    url = f'https://api.the-odds-api.com/v4/sports/americanfootball_nfl/events/{event_id}/odds'
    params = {
        'apiKey': API_KEY,
        'regions': 'us',  # Specify the region (US bookmakers)
        'markets': 'player_pass_tds,player_pass_yds,player_pass_completions,player_pass_attempts,player_pass_interceptions,player_pass_longest_completion,player_rush_yds,player_rush_attempts,player_rush_longest,player_receptions,player_reception_yds,player_reception_longest,player_kicking_points,player_field_goals,player_tackles_assists,player_1st_td,player_last_td,player_anytime_td',
        'oddsFormat': 'american',  # Use American odds format
        'dateFormat': 'iso'  # ISO 8601 date format
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()

def write_odds_to_file(odds_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(odds_data, file, indent=4)

def scrape_odds_and_props():
    try:
        # Get upcoming NFL events
        events = get_upcoming_nfl_odds()

        all_odds_data = []

        # Get player props for each event
        for event in events:
            event_id = event['id']
            prop_odds = get_event_player_props(event_id)
            all_odds_data.append(event)
            all_odds_data.append(prop_odds)

        # Write all the odds and props data to a file
        with open('odds_and_props_output.json', 'w', encoding='utf-8') as file:
            json.dump(all_odds_data, file, indent=4)

        print("Data has been written to 'odds_and_props_output.json'.")

    except requests.RequestException as e:
        print(f"Request failed: {e}")

# Run the scraping function
scrape_odds_and_props()