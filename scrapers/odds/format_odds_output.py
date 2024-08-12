import json
import os
from pymongo import MongoClient

def reformat_odds(input_file, output_file, dataPath):
    output_path = os.path.join(dataPath, output_file)
    # Load the JSON data from the file
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Extract game_info and odds_data
    game_info = data.get("game_info", {})
    odds_data = data.get("odds_data", {})

    # Map market IDs to descriptive bet types
    market_type_map = {
        1: "Moneyline",
        2: "Totals",
        3: "Spreads"
    }

    # Map book IDs to bookmaker names based on the extracted links
    bookmaker_map = {
        0: "BettingPros",
        10: "FanDuel",
        12: "DraftKings",
        19: "BetMGM",
        33: "ESPNBet",
        13: "Caesars",
        15: "PlaySugarHouse"
    }

    # Initialize a list to hold the reformatted data
    reformatted_data = []

    # Iterate through the offers to extract odds and replace book IDs with bookmaker names
    for offer in odds_data.get('offers', []):
        event_id = offer['event_id']
        market_id = offer['market_id']
        market_type = market_type_map.get(market_id, "Unknown Bet Type")
        participants = offer.get('participants', [])
        selections = offer.get('selections', [])

        # Get the matchup name using the event_id
        matchup = game_info.get(str(event_id), "Unknown Matchup")
        
        # Iterate through selections to get the opening and current odds for each team
        for selection in selections:
            team = selection.get('participant')
            label = selection.get('label')
            opening_line = selection.get('opening_line', {})
            opening_line_value = opening_line.get('line')
            opening_odds = opening_line.get('cost')
            opening_bookmaker = bookmaker_map.get(opening_line.get('book_id'), "Unknown Bookmaker")

            # Iterate through books to get the current line and odds for each sportsbook
            for book in selection.get('books', []):
                book_id = book.get('id')
                bookmaker_name = bookmaker_map.get(book_id, f"Bookmaker {book_id}")
                for line in book.get('lines', []):
                    current_line_value = line.get('line')
                    current_odds = line.get('cost')
                    is_off = line.get('is_off', False)

                    # Add the reformatted data
                    reformatted_data.append({
                        "event_id": event_id,
                        "matchup": matchup,
                        "bet_type": market_type,
                        "team": team,
                        "label": label,
                        "opening_bookmaker": opening_bookmaker,
                        "opening_line": opening_line_value,
                        "opening_odds": opening_odds,
                        "bookmaker": bookmaker_name,
                        "current_line": current_line_value,
                        "current_odds": current_odds,
                        "is_off": is_off
                    })

    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(reformatted_data, file, ensure_ascii=False, indent=4)

    if os.path.exists(input_file):
        os.remove(input_file)

    print(f"Output {len(reformatted_data)} odds records to {output_path}")

def format_odds(week, dataPath):
    input_file = os.path.join(dataPath,'nfl_odds_week_')
    input_append = f"{week}.json"
    output_file = 'reformatted_odds.json'
    reformat_odds(input_file+input_append, output_file, dataPath)