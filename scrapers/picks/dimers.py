import requests
import json
from pymongo import MongoClient
from datetime import datetime

def replace_bet_team_name(bets, away_team_name, home_team_name):
    for bet in bets:
        if bet.get("bet") == "away":
            bet["bet"] = away_team_name
        elif bet.get("bet") == "home":
            bet["bet"] = home_team_name
    return bets

def scrape_dimers(dbInfo):
    url = 'https://levy-edge.statsinsider.com.au/matches/upcoming?Sport=NFL,WNBA,MLB,MLS,CFB,LMX&days=7&strip=true&best_bets=true&bookmakers=fanduel,betmgm,draftkings,bet_365'

    # Headers as specified in your request
    headers = {
        'Host': 'levy-edge.statsinsider.com.au',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/111.0.0.0',
        'sec-ch-ua': '"Opera GX";v="111", "Chromium";v="125", "Not.A/Brand";v="24"',
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'origin': 'https://www.dimers.com',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.dimers.com/',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=1, i'
    }

    # Data to be sent in the POST request
    data = {"sport_exclusive_bookmakers":{}}

    try:
        # Send POST request
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()

        games = []
        for match in data:
            match_data = match.get("MatchData", {})
            if match_data.get("Sport") == "NFL":
                pre_data = match.get("PreData", {})
                aggregated_best_bets = match.get("aggregatedBestBets", [])
                aggregated_best_parlay = match.get("aggregatedBestParlay", {}).get("elements", [])
                aggregated_betting_info = match.get("aggregatedBettingInfo", {})

                # Get the team names
                away_team_name = match_data.get("AwayTeam", {}).get("Market", "") + " " + match_data.get("AwayTeam", {}).get("Nickname", "")
                home_team_name = match_data.get("HomeTeam", {}).get("Market", "") + " " + match_data.get("HomeTeam", {}).get("Nickname", "")

                # Replace "home" and "away" in best bets and parlay with actual team names
                aggregated_best_bets = replace_bet_team_name(aggregated_best_bets, away_team_name, home_team_name)
                aggregated_best_parlay = replace_bet_team_name(aggregated_best_parlay, away_team_name, home_team_name)

                game_info = {
                    "away_team": away_team_name,
                    "home_team": home_team_name,
                    "date": match_data.get("Date"),
                    "venue": match_data.get("Venue"),
                    "pred_away_score": pre_data.get("PredAwayScore"),
                    "pred_home_score": pre_data.get("PredHomeScore"),
                    "best_bets": aggregated_best_bets,
                    "best_parlay": aggregated_best_parlay,
                    "betting_info": aggregated_betting_info,
                    "site": "Dimers.com",
                    "data_added": datetime.now()
                }
                games.append(game_info)

        client = MongoClient(dbInfo)
        db = client['spiffypicks']
        collection = db['scraped_picks']
        collection.insert_many(games)

        print(f"Inserted {len(games)} records into MongoDB from Dimers.com")

        # Convert the list of games to JSON format and print it
        # games_json = json.dumps(games, indent=4)
        # print(games_json)

    except requests.RequestException as e:
        print(f"Request failed: {e}")