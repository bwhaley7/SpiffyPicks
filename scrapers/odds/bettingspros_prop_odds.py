import requests
from lxml import html
import json
import os
from util.nfl_data_util import MARKET_ID_MAP

headers = {
        'X-Api-Key': 'CHi8Hy5CEE4khd46XNYL23dCFX96oUdw6qOt1Dnh',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    }

def get_player_slugs():
    event_ids = get_event_ids(1)

    event_ids_str = ':'.join(map(str,event_ids))

    slugAPI = f'https://api.bettingpros.com/v3/markets/offer-counts?sport=NFL&market_category=player-props&event_id={event_ids_str}'

    try:
        response = requests.get(slugAPI, headers=headers)
        response.raise_for_status()

        data = response.json()

        player_slugs = []

        for detail in data.get('details', []):
            participants = detail.get('participants', [])
            for participant in participants:
                player_slug = participant['player'].get('slug')
                if player_slug:
                    player_slugs.append(player_slug)

        return player_slugs
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except Exception as e:
        print(f"An error occured: {e}")
        return []

def get_event_ids(week):
    eventAPI = f'https://api.bettingpros.com/v3/events?sport=NFL&week={week}&season=2024'
    try:
        response = requests.get(eventAPI, headers=headers)
        response.raise_for_status()

        data = response.json()

        event_ids = [event['id'] for event in data.get('events', [])]

        return event_ids
    except requests.RequestException as e:
        print(f"Request Failed: {e}")
        return []
    except Exception as e:
        print(f"An error occured: {e}")
        return []
    
def return_player_props(market_ids, event_ids, dataPath, week):
    market_ids_str = ":".join(map(str, market_ids))
    event_ids_str = ":".join(map(str, event_ids))

    url = f'https://api.bettingpros.com/v3/offers?sport=NFL&market_id={market_ids_str}&event_id={event_ids_str}'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        with open(os.path.join(dataPath, f'nfl_props_week_{week}.json'), 'w') as json_file:
            json.dump(data, json_file, indent=4)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def get_props(market_ids,week, dataPath):
    ids = market_ids
    return_player_props(ids, get_event_ids(week), dataPath, week)


