import os
import json
import re
import pymysql
import nfl_data_py as nfl
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_current_week():
    today = pd.to_datetime(datetime.today().date())
    schedule = nfl.import_schedules([2024])

    schedule['gameday'] = pd.to_datetime(schedule['gameday']).dt.normalize()

    past_games = schedule[schedule['gameday'] <= today]

    if past_games.empty:
        return 1
    
    current_week = past_games['week'].max()

    return current_week

nfl_week = get_current_week()

def connect_to_db():
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        autocommit=True
    )

def clean_json_content(raw_content):
    try:
        match = re.search(r'{.*}', raw_content, re.DOTALL)
        if match:
            return match.group(0)  # Return only the matched valid JSON string
        else:
            raise ValueError("No valid JSON found in the file")
    except Exception as e:
        print(f"Error cleaning JSON: {e}")
        return None

def process_game_file(filepath, connection, is_top_pick=False):
    with open(filepath, 'r') as file:
        raw_content = file.read()
        clean_content = clean_json_content(raw_content)

        if clean_content:
            data = json.loads(clean_content)
            
            if is_top_pick:
                game_date = '2096-12-25'  # Placeholder date for top picks
                game_time = '01:00:00'
            else:
                game_info = data.get('Game Info')
                game_date = game_info.get('date')
                game_time = game_info.get('time')

            with connection.cursor() as cursor:
                insert_picks(data, game_date, game_time, is_top_pick, cursor)
                insert_player_props(data, cursor, is_top_pick)
                if not is_top_pick:
                    insert_parlays(data, cursor)
            connection.commit()

# Insert picks based on file type
def insert_picks(data, game_date, game_time, is_top_pick, cursor):
    if is_top_pick:
        print(f"Picks (Top Picks): {len(data.get('Best Bets', {}).get('Best Game Bets', []))}")
        for pick in data.get('Best Bets', {}).get('Best Game Bets', []):
            game = pick.get('game') if pick.get('game') is not None else "N/A",
            try:
                cursor.execute("""
                    INSERT INTO picks (game_date, game_time, game, pick_type, bet_name, bet_line, bet_odds, star_rating, explanation, is_top_pick, nfl_week)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    game_date,
                    game_time,
                    game,
                    pick.get('type'),
                    pick.get('team') or pick.get('bet'),
                    pick.get('line', 'N/A'),
                    pick.get('odds'),
                    pick.get('star_rating', 0),
                    pick.get('explanation'),
                    is_top_pick,
                    nfl_week
                ))
                print(f"Inserted pick: {pick.get('team', 'Unknown')} - {pick.get('type', 'Unknown')}")
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:  # Error code for duplicate entry
                    print(f"Duplicate entry detected for {pick.get('team', 'Unknown')} - {pick.get('type', 'Unknown')}, skipping...")
                else:
                    raise e 
    else:
        print(f"Picks (Game File): {len(data.get('Primary Betting Opportunities', {}))}")
        for key, bet_data in data.get('Primary Betting Opportunities', {}).items():
            pick = bet_data.get('best_bet')
            game = pick.get('game') if pick.get('game') is not None else "N/A",
            try:
                cursor.execute("""
                    INSERT INTO picks (game_date, game_time, game, pick_type, bet_name, bet_line, bet_odds, star_rating, explanation, is_top_pick, nfl_week)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    game_date,
                    game_time,
                    game,
                    key,
                    pick.get('team') or pick.get('bet'),
                    pick.get('line', 'N/A'),
                    pick.get('odds'),
                    1,  # Default star rating for game files
                    pick.get('explanation'),
                    is_top_pick,
                    nfl_week
                ))
                print(f"Inserted pick: {pick.get('team', 'Unknown')} - {key}")
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:  # Error code for duplicate entry
                    print(f"Duplicate entry detected for {pick.get('team', 'Unknown')} - {pick.get('type', 'Unknown')}, skipping...")
                else:
                    raise e 

# Insert player props based on file type
def insert_player_props(data, cursor, is_top_pick=False):
    if is_top_pick:
        print(f"Props (Top Picks): {len(data.get('Best Bets', {}).get('Best Player Props', []))}")
        for prop in data.get('Best Bets', {}).get('Best Player Props', []):
            try:
                cursor.execute("""
                    INSERT INTO player_props (player_name, prop_type, line, bet, probability, reasoning, is_top_pick, nfl_week)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    prop.get('player'),
                    prop.get('market'),
                    prop.get('line'),
                    prop.get('bet'),
                    prop.get('probability'),
                    prop.get('reasoning'),
                    is_top_pick,
                    nfl_week
                ))
                print(f"Inserted player prop: {prop.get('player')}")
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:  # Error code for duplicate entry
                    print(f"Duplicate entry detected for {prop.get('player', 'Unknown')} - {prop.get('type', 'Unknown')}, skipping...")
                else:
                    raise e 
    else:
        print(f"Props (Game File): {len(data.get('Player Prop Bets', {}).get('profitable_props', []))}")
        for prop in data.get('Player Prop Bets', {}).get('profitable_props', []):
            try:
                cursor.execute("""
                    INSERT INTO player_props (player_name, prop_type, line, bet, probability, reasoning, is_top_pick, nfl_week)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    prop.get('player'),
                    prop.get('market'),
                    prop.get('line'),
                    prop.get('bet'),
                    prop.get('probability'),
                    prop.get('reasoning'),
                    is_top_pick,
                    nfl_week
                ))
                print(f"Inserted player prop: {prop.get('player')}")
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:  # Error code for duplicate entry
                    print(f"Duplicate entry detected for {prop.get('player', 'Unknown')} - {prop.get('type', 'Unknown')}, skipping...")
                else:
                    raise e

# Insert parlays for game files (top picks don’t have parlays)
def insert_parlays(data, cursor, is_top_pick=False):
    if is_top_pick:
        parlays = data.get('Parlay Construction', {}).values()
        print(f"Lays (Top Picks): {len(parlays)}")
    else:
        parlays = data.get('Parlay Opportunities', {}).values()
        print(f"Lays (Game File): {len(parlays)}")

    for parlay_group in parlays:
        bets_array = json.dumps(parlay_group.get('bets', []))
        try:
            cursor.execute("""
                INSERT INTO parlays (parlay_odds, explanation, bets, nfl_week)
                VALUES (%s, %s, %s, %s)
            """, (
                parlay_group.get('combined_odds'),
                parlay_group.get('explanation'),
                bets_array,
                nfl_week
            ))
            print(f"Inserted parlay with odds {parlay_group.get('combined_odds')}")
        except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:  # Error code for duplicate entry
                    print(f"Duplicate entry detected for parlay skipping...")
                else:
                    raise e

# Main loop to process all game files and top picks
def main():
    connection = connect_to_db()
    picks_path = os.getenv('PICKS_PATH')

    for filepath in os.listdir(picks_path):
        filepath = os.path.join(picks_path, filepath)
        if 'final_predictions' in filepath:
            process_game_file(filepath, connection, is_top_pick=True)
        else:
            process_game_file(filepath, connection, is_top_pick=False)

if __name__ == "__main__":
    main()
