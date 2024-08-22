import nfl_data_py as nfl
from datetime import datetime
import pandas as pd

def get_current_week():
    today = pd.to_datetime(datetime.today().date())
    schedule = nfl.import_schedules([2024])

    schedule['gameday'] = pd.to_datetime(schedule['gameday']).dt.normalize()

    past_games = schedule[schedule['gameday'] <= today]

    if past_games.empty:
        return 1
    
    current_week = past_games['week'].max()

    return current_week

def return_games_by_week(week):
    schedule = nfl.import_schedules([2024])
    games_for_week = schedule[schedule['week'] == week]
    return games_for_week

MARKET_ID_MAP = {
    100: "Passing Completions Over/Under",
    101: "Interceptions Over/Under",
    102: "Passing TDs Over/Under",
    103: "Passing Yards Over/Under",
    104: "Receptions Over/Under",
    105: "Receiving Yards Over/Under",
    106: "Rushing Attempts Over/Under",
    107: "Rushing Yards Over/Under",
    66: "First TD Scorer",
    71: "Player To Score Last TD",
    78: "Anytime TD Scorer",
    73: "Most Passing TDs",
    74: "Most Passing Yards",
    75: "Most Receiving Yards",
    76: "Most Rushing Yards Over/Under",
    333: "Passing Attempts Over/Under",
    253: "Fantasy Points Over/Under"
}

def get_market_description(market_id):
    return MARKET_ID_MAP.get(market_id, "Unknown Market ID")
