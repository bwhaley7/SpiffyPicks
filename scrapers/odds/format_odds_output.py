import json

def reformat_odds(input_file):
    # Load the JSON data from the file
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Determine if the input data is for game odds or prop odds
    is_prop_odds = any(offer.get('market_id') == 105 for offer in data.get('offers', []))

    if is_prop_odds:
        # Handle prop odds
        reformatted_data = reformat_prop_odds(data)
    else:
        # Handle game odds
        reformatted_data = reformat_game_odds(data)

    # Save the reformatted data back to the input file
    with open(input_file, 'w', encoding='utf-8') as file:
        json.dump(reformatted_data, file, ensure_ascii=False, indent=4)

    print(f"Output {len(reformatted_data)} odds records to {input_file}")

def reformat_game_odds(data):
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

    return reformatted_data

def reformat_prop_odds(data):
    reformatted_data = []
    bookmaker_map = {
        0: "BettingPros",
        10: "FanDuel",
        12: "DraftKings",
        19: "BetMGM",
        33: "ESPNBet",
        13: "Caesars",
        15: "PlaySugarHouse"
    }

    market_type_map = {
        66: "First TD Scorer",
        71: "Player To Score Last TD",
        78: "Anytime TD Scorer",
        100: "Passing Completions Over/Under",
        101: "Interceptions Over/Under",
        102: "Passing TDs Over/Under",
        103: "Passing Yards Over/Under",
        104: "Receptions Over/Under",
        105: "Receiving Yards Over/Under",
        106: "Rushing Attempts Over/Under",
        107: "Rushing Yards Over/Under",
        253: "Fantasy Points Over/Under",
        333: "Passing Attempts Over/Under"
    }

    for offer in data.get('offers', []):
        market_id = offer['market_id']
        market_type = market_type_map.get(market_id, "Unknown Bet Type")

        if market_id in [66, 71, 78]:  # TD Scorer markets
            participants = offer.get('participants', [])
            participant_map = {p['id']: p for p in participants}

            for selection in offer.get('selections', []):
                participant_id = selection.get('participant')
                player_info = participant_map.get(participant_id, {}).get('player', {})
                player_name = f"{player_info.get('first_name', 'Unknown')} {player_info.get('last_name', 'Unknown')}"
                team_abbreviation = player_info.get('team', "Unknown Team")

                # Extract odds and line info
                opening_line = selection.get('opening_line', {})
                opening_line_value = opening_line.get('line')
                opening_odds = opening_line.get('cost')
                bookmaker_name = bookmaker_map.get(opening_line.get('book_id'), "Unknown Bookmaker")

                reformatted_data.append({
                    "market": market_type,
                    "player_name": player_name,
                    "team": team_abbreviation,
                    "bookmaker": bookmaker_name,
                    "opening_line": opening_line_value,
                    "opening_odds": opening_odds,
                    "current_line": next((line.get('line') for line in selection.get('books', [])[0].get('lines', []) if line.get('line') is not None), None),
                    "current_odds": next((line.get('cost') for line in selection.get('books', [])[0].get('lines', []) if line.get('cost') is not None), None),
                    "over_under": None  # No Over/Under for TD scorer markets
                })
        else:  # Handle Over/Under and other prop markets
            if offer.get('participants'):
                player_info = offer['participants'][0].get('player', {})
                player_name = f"{player_info.get('first_name', 'Unknown')} {player_info.get('last_name', 'Unknown')}"
                team_abbreviation = player_info.get('team', "Unknown Team")
            else:
                player_name = "Unknown Player"
                team_abbreviation = "Unknown Team"

            for selection in offer.get('selections', []):
                label = selection.get('label')

                # Extract odds and line info
                opening_line = selection.get('opening_line', {})
                opening_line_value = opening_line.get('line')
                opening_odds = opening_line.get('cost')
                bookmaker_name = bookmaker_map.get(opening_line.get('book_id'), "Unknown Bookmaker")

                if label in ["Over", "Under"]:
                    reformatted_data.append({
                        "market": market_type,
                        "player_name": player_name,  # Use full player name
                        "team": team_abbreviation,
                        "bookmaker": bookmaker_name,
                        "opening_line": opening_line_value,
                        "opening_odds": opening_odds,
                        "current_line": next((line.get('line') for line in selection.get('books', [])[0].get('lines', []) if line.get('line') is not None), None),
                        "current_odds": next((line.get('cost') for line in selection.get('books', [])[0].get('lines', []) if line.get('cost') is not None), None),
                        "over_under": label  # Capture "Over" or "Under" in a separate field
                    })

    return reformatted_data





def format_odds(input_file):
    reformat_odds(input_file)
