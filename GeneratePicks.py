import os
import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import pandas as pd
from datetime import datetime
import pymysql
import nfl_data_py as nfl
from datetime import datetime, date
import pandas as pd

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()  # Convert date objects to ISO 8601 string format
        return super().default(obj)

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

# Load environment variables from the .env file using find_dotenv
load_dotenv(find_dotenv())

# Access the OpenAI API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# Define a custom JSON encoder to handle datetime and pandas timestamps
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()  # Convert datetime objects to ISO 8601 string
        return super().default(obj)

# Function to load JSON data from a file
def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to connect to the database
def connect_to_db():
    connection = pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )
    return connection

# Function to pull data from the database based on team abbreviations
def fetch_data_for_game(cursor, table_name, team_abbr):
    if table_name == 'expert_picks':
        query = f"""
        SELECT * FROM {table_name} 
        WHERE matchup LIKE %s 
        AND matchup LIKE %s;
        """
        cursor.execute(query, (f'%{team_abbr[0]}%', f'%{team_abbr[1]}%'))

    return cursor.fetchall()

def fetch_player_data_for_game(cursor, table_name, team_abbr):
    query = f"""
    SELECT * FROM {table_name}
    WHERE team = %s OR team = %s
    """
    cursor.execute(query, (team_abbr[0], team_abbr[1]))
    return cursor.fetchall()

def serialize_data(data):
    if isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, (date, datetime)):
        return data.isoformat()
    else:
        return data

all_predictions = []

# Function to generate picks using OpenAI's API
def generate_picks():
    global all_predictions
    current_week = get_current_week()

    # Get games for the current week
    games_for_week = return_games_by_week(current_week)

    # Initialize database connection
    connection = connect_to_db()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # Loop through each game to pull relevant data
    for index, game in games_for_week.iterrows():
        away_team = game['away_team']
        home_team = game['home_team']
        team_abbr = (away_team, home_team)

        # Fetch expert picks for the teams
        expert_picks = fetch_data_for_game(cursor, 'expert_picks', team_abbr)

        # Fetch analyst articles for the teams
        analyst_articles = fetch_data_for_game(cursor, 'analyst_articles', team_abbr)

        # Fetch game odds for the teams
        game_odds = fetch_player_data_for_game(cursor, 'game_odds', team_abbr)

        # Fetch player odds for the teams
        player_odds = fetch_player_data_for_game(cursor, 'player_odds', team_abbr)

        # Fetch player projections for the teams
        player_projections = fetch_player_data_for_game(cursor, 'player_projections', team_abbr)

        # Create the prompt with all the data
        prompt = {
            "prompt": (
                """
                    You are a seasoned sports analyst with over 30 years of experience in analyzing sports data to beat the sportsbooks. Your task is to generate accurate and profitable sports betting picks using the following guidelines:

                    Data Utilization Guidelines:

                    Player Projections:
                    - Factor in opposing defense projections; a strong defense may reduce the likelihood of success for the opposing team's players.
                    - Compare player projections across both teams; teams with more high-projected players are more likely to win.
                    - Analyze variance between player prop lines and projections to identify potential value.

                    Expert Picks:
                    - Incorporate explanations from expert picks to gain insights into team and player dynamics that could influence game and prop outcomes.
                    - Use last10head2head data (where available) to enhance predictions based on historical matchups.
                    - Consider trends and any available edge data to refine picks, prioritizing higher edge values for stronger betting opportunities.

                    Odds:
                    - Monitor line movements by comparing opening lines to current odds to identify potential value or market shifts.

                    General Approach:
                    - Combine all the data provided to identify the best betting opportunities for each game, including spreads, totals, and moneylines.
                    - Offer multiple bet opportunities for each game, ensuring that all relevant data is incorporated, including both quantitative (e.g., projections, odds) and qualitative (e.g., expert opinions, articles) insights.
                    - Craft a set of parlays with varying levels of risk:
                    - A low-risk parlay with higher-probability bets.
                    - A medium-risk parlay balancing safety and potential returns.
                    - A high-risk parlay with bets that have lower consensus but higher potential payouts.
                    - Explain the reasoning behind each prediction and provide probabilities for each bet being successful.
                    - Summarize the top expert opinions and how they align or contrast with the data.
                    - If you see high value in player props, include them in parlays as well, not just game bets like spreads/moneyline
                    - Please provide all odds in American. Not decimal.
                    - When converting decimal odds to American odds:
                    - For decimal odds greater than 2.00, use the formula `(decimal odds - 1) * 100` to determine the American odds.
                    - For decimal odds less than 2.00, use the formula `-100 / (decimal odds - 1)` to determine the American odds.
                    - Ensure that all odds are correctly labeled as either positive or negative based on this conversion.
                    - Line Movement Tracking: Track how betting lines have moved since they opened and whether sharp (professional) money has caused significant shifts.
                    - Betting Units: Suggest optimal bet sizing based on confidence levels, using units rather than flat betting.
                    - Correlation of Bets: Identify correlations between different bets (e.g., a high total points line might correlate with a high passing yards prop) to suggest correlated parlays or avoid conflicting bets.
                    - Adjust predictions based on contextual factors such as home/away advantages, weather conditions, and team motivation or fatigue.
                    - Apply Monte Carlo simulations to estimate the probability of various outcomes based on a range of potential inputs and scenarios.
                    - Correlate bets to identify and recommend parlays or avoid conflicts where one outcome might negate another.
                """
            ),
            "expert_picks": serialize_data(expert_picks),
            "analyst_articles": serialize_data(analyst_articles),
            "game_odds": serialize_data(game_odds),
            "player_odds": serialize_data(player_odds),
            "player_projections": serialize_data(player_projections),
        }

        # Make the API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": json.dumps(prompt, cls=CustomJSONEncoder)}],
        )

        text = str(response.choices[0].message.content)

        all_predictions.append(text)

        with open(f"game_data_{away_team} {home_team}", "w", encoding="utf-8") as file:
            file.write(text)
        
        print(f"Predicitons for {away_team} vs {home_team} written to text file.")

    final_prompt = (
        "You have analyzed the predictions for all games. Based on these predictions, please do the following:\n"
        "- Identify the best bets across all games.\n"
        "- Create multiple parlays with varying levels of risk usings player props and game lines:\n"
        "  - Low-risk parlay\n"
        "  - Medium-risk parlay\n"
        "  - High-risk parlay\n"
        "- Provide explanations and probabilities for each parlay and all picks."
        "- Find many possible parlays combinations using player props and game lines. I would like at least 2 low risk, 2 medium risk, and 2 high risk. Make them unique."
        "- On top of the parlays you are already making, please create 1-3 longshot parlays. These should be parlays in the +500-+1000 odds range with the highest possible chance of success."
        "- Please provide all odds in american. Not decimal."
    )

    combined_prompt = {
        "prompt": final_prompt,
        "all_predictions": all_predictions
    }

    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": json.dumps(combined_prompt, cls=CustomJSONEncoder)}],
    )

    # Write the final response to a file
    with open("final_predictions.txt", "w", encoding="utf-8") as file:
        file.write(final_response.choices[0].message.content)

    print("Final predictions and parlays have been written to final_predictions.txt")
    # Close the database connection
    connection.close()

if __name__ == "__main__":
    # Generate picks
    generate_picks()
