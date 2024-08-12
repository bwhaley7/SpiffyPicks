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
                formatted_pick = {
                    'away_team_name': pick.get('awayTeam', {}).get('name', 'N/A'),
                    'home_team_name': pick.get('homeTeam', {}).get('name', 'N/A'),
                    'market': pick.get('market', 'N/A'),
                    'date': date_only,  # Use the converted ISO 8601 date from startTimeString
                    'outcome': pick.get('outcome', 'N/A'),
                    'reasoning': pick.get('reasoning', 'N/A'),
                    'site': "pickswise.com",
                    'data_added': datetime.now()
                }
                formatted_picks.append(formatted_pick)

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