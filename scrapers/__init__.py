import os
import json
from json import JSONEncoder
from dotenv import load_dotenv, find_dotenv
from picks.covers import scrape_picks_covers
from picks.dimers import scrape_dimers
from picks.pickswise import scrape_pickswise
from picks.wagertalk import scrape_wagertalk
from picks.oddsshark import scrape_oddsshark
from projections.fantasypros import scrape_fantasypros
from articles.actionnetwork import scrape_action_articles
from articles.coversArticles import scrape_covers_articles
from articles.bettingspros import scrape_bettingpros_articles
from odds.bettingpros_game_odds import output_game_odds_file
from odds.bettingspros_prop_odds import get_props
from odds.format_odds_output import format_odds
from datetime import datetime, date
from util.nfl_data_util import get_current_week, MARKET_ID_MAP
import pymysql

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)
    
load_dotenv(find_dotenv())

def connect_to_db():
    connection = pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )
    return connection

def upload_json_to_db(connection, table_name, json_data):
    with connection.cursor() as cursor:  # Create a cursor from the connection
        if table_name == 'analyst_articles':
            query = f"""
            INSERT INTO {table_name} (article, url, date, site, scraped_at, matchup, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                article = VALUES(article), 
                url = VALUES(url), 
                date = VALUES(date), 
                site = VALUES(site), 
                scraped_at = VALUES(scraped_at), 
                matchup = VALUES(matchup),
                content = VALUES(content);
            """
            for record in json_data:
                values = (
                    record['article'],
                    record['url'],
                    record['date'],
                    record['site'],
                    record['scraped_at'],
                    json.dumps(record['matchup']),
                    record['content']
                )
                cursor.execute(query, values)

        elif table_name == 'expert_picks':
            query = f"""
            INSERT INTO {table_name} (
                matchup, date, time, away_team, home_team, outcome, explanation, site, data_added, 
                venue, predicted_away_score, predicted_home_score, best_bets, best_parlay, betting_info, 
                market, predicted_score, predicted_game_ou, expert_prediction, game_trends, last10head2head
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                matchup = VALUES(matchup), 
                date = VALUES(date), 
                time = VALUES(time), 
                away_team = VALUES(away_team), 
                home_team = VALUES(home_team), 
                outcome = VALUES(outcome), 
                explanation = VALUES(explanation), 
                site = VALUES(site), 
                data_added = VALUES(data_added), 
                venue = VALUES(venue), 
                predicted_away_score = VALUES(predicted_away_score), 
                predicted_home_score = VALUES(predicted_home_score), 
                best_bets = VALUES(best_bets), 
                best_parlay = VALUES(best_parlay), 
                betting_info = VALUES(betting_info), 
                market = VALUES(market), 
                predicted_score = VALUES(predicted_score), 
                predicted_game_ou = VALUES(predicted_game_ou), 
                expert_prediction = VALUES(expert_prediction), 
                game_trends = VALUES(game_trends), 
                last10head2head = VALUES(last10head2head);
            """
            for record in json_data:
                # Check if all required fields are present and properly formatted
                required_fields = [
                    'matchup', 'date', 'time', 'away_team', 'home_team', 'outcome', 
                    'explanation', 'site', 'data_added', 'venue', 'predicted_away_score', 
                    'predicted_home_score', 'best_bets', 'best_parlay', 'betting_info', 
                    'market', 'predicted_score', 'predicted_game_ou', 'expert_prediction', 
                    'game_trends', 'last10head2head'
                ]
                
                # Fill missing fields with defaults
                for field in required_fields:
                    if field not in record:
                        print(f"Missing field {field} in record, filling with default value.")
                        # Default to valid JSON objects or arrays where applicable
                        record[field] = '[]' if field in ['best_bets', 'best_parlay', 'betting_info', 'game_trends', 'last10head2head'] else 'Unknown' if field not in ['predicted_away_score', 'predicted_home_score'] else 0

                # Convert list and dict fields to JSON string
                matchup_json = json.dumps(record['matchup']) if isinstance(record['matchup'], list) else record['matchup']
                best_bets_json = json.dumps(record['best_bets']) if isinstance(record['best_bets'], (list, dict)) and record['best_bets'] else '[]'
                best_parlay_json = json.dumps(record['best_parlay']) if isinstance(record['best_parlay'], (list, dict)) and record['best_parlay'] else '[]'
                betting_info_json = json.dumps(record['betting_info']) if isinstance(record['betting_info'], (list, dict)) and record['betting_info'] else '[]'
                game_trends_json = json.dumps(record['game_trends']) if isinstance(record['game_trends'], (list, dict)) and record['game_trends'] else '[]'
                last10head2head_json = json.dumps(record['last10head2head']) if isinstance(record['last10head2head'], (list, dict)) and record['last10head2head'] else '[]'

                # Prepare the values tuple
                values = (
                    matchup_json,
                    record['date'],
                    record['time'],
                    record['away_team'],
                    record['home_team'],
                    record['outcome'],
                    record['explanation'],
                    record['site'],
                    record['data_added'],
                    record['venue'],
                    record['predicted_away_score'],
                    record['predicted_home_score'],
                    best_bets_json,
                    best_parlay_json,
                    betting_info_json,
                    record['market'],
                    record['predicted_score'],
                    record['predicted_game_ou'],
                    record['expert_prediction'],
                    game_trends_json,
                    last10head2head_json
                )
                
                # Debug: print the values tuple to ensure everything is correct
                #print(f"Inserting values: {values}")
                
                cursor.execute(query, values)

        elif table_name == 'player_projections':
            query = f"""
            INSERT INTO {table_name} (player_name, position, team, projected_fantasy_points, site, data_added,
                                       projected_passing_yards, projected_rushing_yards, projected_passing_touchdowns, 
                                       projected_rushing_touchdowns, projected_interceptions, projected_fumbles, 
                                       projected_receiving_yards, projected_receiving_receptions, projected_receiving_touchdowns, 
                                       projected_field_goals_attempted, projected_field_goals_made, projected_extra_points, 
                                       projected_sacks, projected_touchdowns, projected_points_allowed, 
                                       projected_total_yards_allowed, projected_fumbles_forced, projected_fumbles_recovered, 
                                       projected_safeties, week)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                player_name = VALUES(player_name), 
                position = VALUES(position), 
                team = VALUES(team), 
                projected_fantasy_points = VALUES(projected_fantasy_points), 
                site = VALUES(site), 
                data_added = VALUES(data_added),
                projected_passing_yards = VALUES(projected_passing_yards), 
                projected_rushing_yards = VALUES(projected_rushing_yards), 
                projected_passing_touchdowns = VALUES(projected_passing_touchdowns), 
                projected_rushing_touchdowns = VALUES(projected_rushing_touchdowns), 
                projected_interceptions = VALUES(projected_interceptions), 
                projected_fumbles = VALUES(projected_fumbles), 
                projected_receiving_yards = VALUES(projected_receiving_yards), 
                projected_receiving_receptions = VALUES(projected_receiving_receptions), 
                projected_receiving_touchdowns = VALUES(projected_receiving_touchdowns), 
                projected_field_goals_attempted = VALUES(projected_field_goals_attempted), 
                projected_field_goals_made = VALUES(projected_field_goals_made), 
                projected_extra_points = VALUES(projected_extra_points), 
                projected_sacks = VALUES(projected_sacks), 
                projected_touchdowns = VALUES(projected_touchdowns), 
                projected_points_allowed = VALUES(projected_points_allowed), 
                projected_total_yards_allowed = VALUES(projected_total_yards_allowed), 
                projected_fumbles_forced = VALUES(projected_fumbles_forced), 
                projected_fumbles_recovered = VALUES(projected_fumbles_recovered), 
                projected_safeties = VALUES(projected_safeties),
                week = VALUES(week);
            """
            for record in json_data:
                values = (
                    record['player_name'],
                    record['position'],
                    record['team'],
                    record.get('projected_fantasy_points', 0),
                    record['site'],
                    record['data_added'],
                    record.get('projected_passing_yards', 0),
                    record.get('projected_rushing_yards', 0),
                    record.get('projected_passing_touchdowns', 0),
                    record.get('projected_rushing_touchdowns', 0),
                    record.get('projected_interceptions', 0),
                    record.get('projected_fumbles', 0),
                    record.get('projected_receiving_yards', 0),
                    record.get('projected_receiving_receptions', 0),
                    record.get('projected_receiving_touchdowns', 0),
                    record.get('projected_field_goals_attempted', 0),
                    record.get('projected_field_goals_made', 0),
                    record.get('projected_extra_points', 0),
                    record.get('projected_sacks', 0),
                    record.get('projected_touchdowns', 0),
                    record.get('projected_points_allowed', 0),
                    record.get('projected_total_yards_allowed', 0),
                    record.get('projected_fumbles_forced', 0),
                    record.get('projected_fumbles_recovered', 0),
                    record.get('projected_safeties', 0),
                    record.get('week', 0.0)
                )
                cursor.execute(query, values)
        elif table_name == 'game_odds':
            query = f"""
            INSERT INTO {table_name} (event_id, matchup_name, matchup_date, bet_type, team, label, opening_bookmaker, opening_line, opening_odds, bookmaker, current_line, current_odds, is_off)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                matchup_name = VALUES(matchup_name),
                matchup_date = VALUES(matchup_date),
                bet_type = VALUES(bet_type),
                team = VALUES(team),
                label = VALUES(label),
                opening_bookmaker = VALUES(opening_bookmaker),
                opening_line = VALUES(opening_line),
                opening_odds = VALUES(opening_odds),
                bookmaker = VALUES(bookmaker),
                current_line = VALUES(current_line),
                current_odds = VALUES(current_odds),
                is_off = VALUES(is_off);
            """
            for record in json_data:
                matchup_info = record.get('matchup', {})
                values = (
                    record.get('event_id', 0),
                    matchup_info.get('matchup', 'Unknown Matchup'),
                    matchup_info.get('date', '0000-00-00 00:00:00'),
                    record.get('bet_type', 'Unknown Bet Type'),
                    record.get('team', 'Unknown Team'),
                    record.get('label', 'Unknown Label'),
                    record.get('opening_bookmaker', 'Unknown Bookmaker'),
                    record.get('opening_line', 0.0),
                    record.get('opening_odds', 0),
                    record.get('bookmaker', 'Unknown Bookmaker'),
                    record.get('current_line', 0.0),
                    record.get('current_odds', 0),
                    record.get('is_off', False)
                )
                cursor.execute(query, values)

        elif table_name == 'player_odds':
            query = f"""
            INSERT INTO {table_name} (market, player_name, team, bookmaker, opening_line, opening_odds, current_line, current_odds, over_under)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                market = VALUES(market), 
                player_name = VALUES(player_name), 
                team = VALUES(team), 
                bookmaker = VALUES(bookmaker), 
                opening_line = VALUES(opening_line), 
                opening_odds = VALUES(opening_odds), 
                current_line = VALUES(current_line), 
                current_odds = VALUES(current_odds), 
                over_under = VALUES(over_under);
            """
            for record in json_data:
                # Ensure all required fields are present and assign default values if missing
                market = record.get('market', 'Unknown')
                player_name = record.get('player_name', 'Unknown Player')
                team = record.get('team', 'Unknown Team')
                bookmaker = record.get('bookmaker', 'Unknown Bookmaker')
                opening_line = record.get('opening_line', 0)
                opening_odds = record.get('opening_odds', 0)
                current_line = record.get('current_line', 0)
                current_odds = record.get('current_odds', 0)
                over_under = record.get('over_under', 'Unknown')

                values = (
                    market,
                    player_name,
                    team,
                    bookmaker,
                    opening_line,
                    opening_odds,
                    current_line,
                    current_odds,
                    over_under
                )

                # Debug: print the values tuple to ensure everything is correct
                #print(f"Inserting values: {values}")

                cursor.execute(query, values)

        connection.commit()




def run_all_scrapers():
    load_dotenv(find_dotenv())
    dataPath = os.getenv('DATA_PATH')
    week = get_current_week()

    covers_picks = scrape_picks_covers()
    dimers_picks = scrape_dimers()
    pickswise_picks = scrape_pickswise()
    wagertalk_picks = scrape_wagertalk()
    oddsshark_picks = scrape_oddsshark()
    fp_proj = scrape_fantasypros(week)
    action_articles = scrape_action_articles()
    covers_articles = scrape_covers_articles()

    get_props(MARKET_ID_MAP.keys(), week, dataPath)
    output_game_odds_file(week, dataPath)
    format_odds(os.path.join(dataPath, f"nfl_odds_week_{week}.json"))
    format_odds(os.path.join(dataPath, f"nfl_props_week_{week}.json"))

    expert_picks = (
        covers_picks +
        dimers_picks +
        pickswise_picks +
        wagertalk_picks +
        oddsshark_picks
    )

    analyst_articles = (
        action_articles +
        covers_articles
    )

    expert_picks_file = os.path.join(dataPath, 'expert_picks.json')
    analyst_articles_file = os.path.join(dataPath, 'analyst_articles.json')
    player_projections_file = os.path.join(dataPath, 'player_projections.json')

    with open(expert_picks_file, 'w', encoding='utf-8') as file:
        json.dump(expert_picks, file, ensure_ascii=False, indent=4, cls=CustomJSONEncoder)
    
    with open(analyst_articles_file, 'w', encoding='utf-8') as file:
        json.dump(analyst_articles, file, ensure_ascii=False, indent=4, cls=CustomJSONEncoder)

    with open(player_projections_file, 'w', encoding='utf-8') as file:
        json.dump(fp_proj, file, ensure_ascii=False, indent=4, cls=CustomJSONEncoder)

    print(f"All data has been written to their respective files.")

def upload_all_json_to_db():
    connection = connect_to_db()

    dataPath = os.getenv('DATA_PATH')
    week = get_current_week()

    expert_picks_file = os.path.join(dataPath, 'expert_picks.json')
    analyst_articles_file = os.path.join(dataPath, 'analyst_articles.json')
    player_projections_file = os.path.join(dataPath, 'player_projections.json')
    odds_file = os.path.join(dataPath, f"nfl_odds_week_{week}.json")
    props_file = os.path.join(dataPath, f"nfl_props_week_{week}.json")

    # Upload data
    for file_path, table_name in [
        (expert_picks_file, 'expert_picks'),
        (analyst_articles_file, 'analyst_articles'),
        (player_projections_file, 'player_projections'),
        (odds_file, 'game_odds'),
        (props_file, 'player_odds')
    ]:
        print(f"Processing file: {file_path} for table: {table_name}")

        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

            if not json_data:
                print(f"No data found in {file_path} for table: {table_name}")
                continue

            for i, record in enumerate(json_data):
                if record is None:
                    print(f"Found NoneType record in {file_path} at index {i} for table: {table_name}")
                    continue

            upload_json_to_db(connection, table_name, json_data)

    connection.close()
    print("All data has been uploaded to the MySQL database.")

if __name__ == "__main__":
    #scrape_bettingpros_articles()
    #run_all_scrapers()
    upload_all_json_to_db()
