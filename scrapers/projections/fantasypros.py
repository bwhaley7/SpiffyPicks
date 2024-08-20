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
            position = player.get('position_id')
            stats = player.get('stats', {})

            player_data = {
                'player_name': player.get('name'),
                'position': position,
                'team': player.get('team_id'),
                'game': '',  # Add game info if available
                'projected_fantasy_points': stats.get('points', 0.0),
                'site': "fantasypros.com",
                'data_added': datetime.now()
            }

            # Add stats based on position
            if position == 'QB':
                player_data.update({
                    'projected_passing_yards': stats.get('pass_yds', 0.0),
                    'projected_rushing_yards': stats.get('rush_yds', 0.0),
                    'projected_passing_touchdowns': stats.get('pass_tds', 0.0),
                    'projected_rushing_touchdowns': stats.get('rush_tds', 0.0),
                    'projected_interceptions': stats.get('pass_ints', 0.0),
                    'projected_fumbles': stats.get('fumbles', 0.0)
                })

            elif position == 'RB':
                player_data.update({
                    'projected_rushing_yards': stats.get('rush_yds', 0.0),
                    'projected_rushing_touchdowns': stats.get('rush_tds', 0.0),
                    'projected_receiving_yards': stats.get('rec_yds', 0.0),
                    'projected_receiving_receptions': stats.get('rec_rec', 0.0),
                    'projected_receiving_touchdowns': stats.get('rec_tds', 0.0),
                    'projected_fumbles': stats.get('fumbles', 0.0)
                })

            elif position == 'WR' or position == 'TE':
                player_data.update({
                    'projected_receiving_yards': stats.get('rec_yds', 0.0),
                    'projected_receiving_receptions': stats.get('rec_rec', 0.0),
                    'projected_receiving_touchdowns': stats.get('rec_tds', 0.0),
                    'projected_rushing_yards': stats.get('rush_yds', 0.0),  # WRs and TEs may have rushing yards
                    'projected_rushing_touchdowns': stats.get('rush_tds', 0.0),
                    'projected_fumbles': stats.get('fumbles', 0.0)
                })

            elif position == 'K':
                player_data.update({
                    'projected_field_goals_attempted': stats.get('fga', 0.0),
                    'projected_field_goals_made': stats.get('fg', 0.0),
                    'projected_extra_points': stats.get('xpt', 0.0)
                })

            elif position == 'DST':
                player_data.update({
                    'projected_sacks': stats.get('def_sack', 0.0),
                    'projected_interceptions': stats.get('def_int', 0.0),
                    'projected_touchdowns': stats.get('def_td', 0.0),
                    'projected_points_allowed': stats.get('def_pa', 0.0),
                    'projected_total_yards_allowed': stats.get('def_tyda', 0.0),
                    'projected_fumbles_forced': stats.get('def_ff', 0.0),
                    'projected_fumbles_recovered': stats.get('def_fr', 0.0),
                    'projected_safeties': stats.get('def_safety', 0.0)
                })

            if player_data['projected_fantasy_points'] > 1:
                projection_data.append(player_data)
                count += 1
        
        print(f"{count} player projections added for week {week} from fantasypros.com")
        return projection_data

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def scrape_fantasypros(week):
    projections = scrape_fantasypros_projections(week)
    return projections
