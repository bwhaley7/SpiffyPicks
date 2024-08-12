import requests
from datetime import datetime

def scrape__picks_pickswise():
    url = 'https://www.pickswise.com/_next/data/mH9ttVCAg7OXa5acQnTfn/_sport/nfl/picks.json?pageSlug=%2Fnfl%2Fpicks%2F&sport=nfl'

    params = {
        'pageSlug': '%2Fnfl%2Fpicks%2F',
        'sport': 'nfl'
    }

    try:
        # Send GET
        response = requests.get(url, params=params)
        response.raise_for_status() #Raise exception for HTTP issues

        # Parse Json
        data = response.json()

        picks_data = data.get('pageProps', {}).get('initialState', {}).get('sportPredictionsPicks', {}).get('%2Fnfl%2Fpicks%2F', [])

        # Debugging: Print the contents of picks_data
        #print(json.dumps(picks_data, indent=4))

        if not picks_data:
            print("No picks found.")

            return
        
        formatted_picks = []
        for game in picks_data:
            start_time_string = game.get('startTimeString', 'N/A')
            if start_time_string != 'N/A':
                try:
                    # Convert the startTimeString to a datetime object
                    parsed_date = datetime.strptime(start_time_string, "%Y-%m-%dT%H:%M:%S%z")
                    # Extract only the date (YYYY-MM-DD)
                    date_only = parsed_date.date().isoformat()
                except ValueError:
                    date_only = 'Invalid date format'
            else:
                date_only = 'N/A'

            # Access the basePicks within each game
            for pick in game.get('basePicks', []):
                pick_data = {
                    'matchup': f"{pick.get('awayTeam', {}).get('name', 'N/A')} at {pick.get('homeTeam', {}).get('name', 'N/A')}",
                    'date': date_only,
                    'time': '',
                    'away_team': pick.get('awayTeam', {}).get('name', 'N/A'),
                    'home_team': pick.get('homeTeam', {}).get('name', 'N/A'),
                    'venue': '',
                    'predicted_away_score': None,
                    'predicted_home_score': None,
                    'predicted_score': '',
                    'predicted_game_ou': '',
                    'best_bets': '',
                    'best_parlay': '',
                    'betting_info': '',
                    'market': pick.get('market', 'N/A'),
                    'outcome': pick.get('outcome', 'N/A'),
                    'explanation': pick.get('reasoning', 'N/A'),
                    'expert_prediction': '',
                    'game_trends': '',
                    'last10head2head': '',
                    'site': "pickswise.com",
                    'data_added': datetime.now()
                }

                formatted_picks.append(pick_data)

        print(f"Inserted {len(formatted_picks)} records into MongoDB from pickswise.com")
        return formatted_picks

    except requests.RequestException as e:
        print(f"Request failed: {e}")

    except Exception as e:
        print(f"An error occured: {e}")

def scrape_pickswise():
    picks = scrape__picks_pickswise()
    return picks
    #Add scrape method for player props