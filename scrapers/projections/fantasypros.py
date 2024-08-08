import os
import requests
import json
from pymongo import MongoClient

def scrape_fantasypros_projections(dbInfo, week):
    url = f'https://api.fantasypros.com/v2/json/nfl/undefined/projections?position=ALL&scoring=HALF&week={week}'

    headers = {
        'User-Agent': 'PostmanRuntime/7.41.0',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'X-Api-Key': 'zjxN52G3lP4fORpHRftGI2mTU8cTwxVNvkjByM3j'
    }

    session = requests.Session()
    session.headers.update(headers)

    try:

        response = session.get(url)
        response.raise_for_status()

        data = response.json()

        player_projections = data.get('players', [])

        projection_data = []

        for player in player_projections:
            player_data = {
                'name': player.get('name'),
                'position_id': player.get('position_id'),
                'team_id': player.get('team_id'),
                'projected stats': {
                    'points': player.get('stats', {}).get('points'),
                    'points_ppr': player.get('stats', {}).get('points_ppr'),
                    'points_half': player.get('stats', {}).get('points_half'),
                    'pass_att': player.get('stats', {}).get('pass_att'),
                    'pass_cmp': player.get('stats', {}).get('pass_cmp'),
                    'pass_yds': player.get('stats', {}).get('pass_yds'),
                    'pass_tds': player.get('stats', {}).get('pass_tds'),
                    'pass_ints': player.get('stats', {}).get('pass_ints'),
                    'rush_att': player.get('stats', {}).get('rush_att'),
                    'rush_yds': player.get('stats', {}).get('rush_yds'),
                    'rush_tds': player.get('stats', {}).get('rush_tds'),
                    'fumbles': player.get('stats', {}).get('fumbles'),
                    'ret_tds': player.get('stats', {}).get('ret_tds'),
                    '2pt_tds': player.get('stats', {}).get('2pt_tds')
                }
            }
            projection_data.append(player_data)

        client = MongoClient(dbInfo)
        db = client['spiffypicks']
        collection = db['scraped_projections']
        collection.insert_many(projection_data)
        
        print(f"{len(player_projections)} player projections added for week {week} from fantasypros.com")


    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occured: {e}")

def scrape_fantasypros(dbInfo, week):
    scrape_fantasypros_projections(dbInfo, week)