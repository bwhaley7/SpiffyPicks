import requests
from pymongo import MongoClient
from datetime import datetime

def scrape__picks_pickswise(dbInfo):
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
        
        # Extract relevant information
        formatted_picks = []
        for game in picks_data:
            for pick in game.get('basePicks', []):
                formatted_pick = {
                    'away_team_name': pick.get('awayTeam', {}).get('name', 'N/A'),
                    'home_team_name': pick.get('homeTeam', {}).get('name', 'N/A'),
                    'market': pick.get('market', 'N/A'),
                    'outcome': pick.get('outcome', 'N/A'),
                    'reasoning': pick.get('reasoning', 'N/A'),
                    'data_added': datetime.now()
                }
                formatted_picks.append(formatted_pick)

        client = MongoClient(dbInfo)
        db = client['spiffypicks']
        collection = db['scraped_picks']
        collection.insert_many(formatted_picks)

        print(f"Inserted {len(formatted_picks)} records into MongoDB from pickswise.com")
        # Debug output
        # print(f"{len(formatted_picks)} picks scraped from Pickswise.")
        # print(json.dumps(formatted_picks, indent=4))
        # result_json = json.dumps(formatted_picks, indent=4)

        # return result_json

    except requests.RequestException as e:
        print(f"Request failed: {e}")

    except Exception as e:
        print(f"An error occured: {e}")

def scrape_pickswise(dbInfo):
    scrape__picks_pickswise(dbInfo)
    #Add scrape method for player props