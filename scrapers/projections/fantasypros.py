import requests
from datetime import datetime

def scrape_fantasypros_projections(week):
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

        count = 0

        player_projections = data.get('players', [])

        projection_data = []

        for player in player_projections:
            player_data = {
                'player_name': player.get('name'),
                'position': player.get('position_id'),
                'team': player.get('team_id'),
                'game': '',  # Add game info if available
                'projected_fantasy_points': player.get('stats', {}).get('points', 0.0),
                'projected_passing_yards': player.get('stats', {}).get('pass_yds', 0.0),
                'projected_rushing_yards': player.get('stats', {}).get('rush_yds', 0.0),
                'projected_receiving_yards': 0.0,  # Assuming not provided, so set to 0.0
                'projected_touchdowns': player.get('stats', {}).get('pass_tds', 0.0) + player.get('stats', {}).get('rush_tds', 0.0),
                'projected_interceptions': player.get('stats', {}).get('pass_ints', 0.0),
                'projected_fumbles': player.get('stats', {}).get('fumbles', 0.0),
                'site': "fantasypros.com",
                'data_added': datetime.now()
            }
            if player.get('stats', {}).get('points') > 1:
                projection_data.append(player_data)
                count+=1
        
        print(f"{count} player projections added for week {week} from fantasypros.com")
        return projection_data


    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occured: {e}")

def scrape_fantasypros(week):
    projections = scrape_fantasypros_projections(week)
    return projections