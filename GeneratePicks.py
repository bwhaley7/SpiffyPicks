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

path = os.getenv("PICKS_PATH")

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


def fetch_redzone_stats(cursor, player_name, position):
    rushing_data = []
    receiving_data = []

    if position in ["RB", "WR", "TE"]:
        if position == "RB":
            # Fetch rushing data
            cursor.execute("""
                SELECT season, inside_20_attempts, inside_20_yards, inside_20_touchdowns, inside_20_rushing_share,
                       inside_10_attempts, inside_10_yards, inside_10_touchdowns, inside_10_rushing_share,
                       inside_5_attempts, inside_5_yards, inside_5_touchdowns, inside_5_rushing_share
                FROM redzone_rushing_historical
                WHERE player_name = %s
            """, (player_name,))
            rushing_data = cursor.fetchall()

            # Fetch receiving data for RBs
            cursor.execute("""
                SELECT season, inside_20_targets, inside_20_receptions, inside_20_catch_percentage, inside_20_yards, inside_20_touchdowns, inside_20_target_share,
                       inside_10_targets, inside_10_receptions, inside_10_catch_percentage, inside_10_yards, inside_10_touchdowns, inside_10_target_share
                FROM redzone_receiving_historical
                WHERE player_name = %s
            """, (player_name,))
            receiving_data = cursor.fetchall()
        
        elif position in ["WR", "TE"]:
            # Fetch receiving data for WRs and TEs
            cursor.execute("""
                SELECT season, inside_20_targets, inside_20_receptions, inside_20_catch_percentage, inside_20_yards, inside_20_touchdowns, inside_20_target_share,
                       inside_10_targets, inside_10_receptions, inside_10_catch_percentage, inside_10_yards, inside_10_touchdowns, inside_10_target_share
                FROM redzone_receiving_historical
                WHERE player_name = %s
            """, (player_name,))
            receiving_data = cursor.fetchall()
    
    return {
        "player_name": player_name,
        "rushing_data": rushing_data,
        "receiving_data": receiving_data
    }

# Function to pull data from the database based on team abbreviations
def fetch_data_for_game(cursor, table_name, team_abbr):
    if table_name == 'expert_picks':
        query = f"""
        SELECT * FROM {table_name} 
        WHERE matchup LIKE %s 
        AND matchup LIKE %s;
        """
        cursor.execute(query, (f'%{team_abbr[0]}%', f'%{team_abbr[1]}%'))
    
    elif table_name == 'analyst_articles':
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

def fetch_goofy_data_for_game(cursor, table_name, team_abbr):
    query = f"""
    SELECT * FROM {table_name}
    WHERE ï»¿Team = %s or ï»¿Team = %s
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

        rushing_defense_historical = fetch_player_data_for_game(cursor, 'rushing_defense_historical', team_abbr)

        passing_defense_historical = fetch_player_data_for_game(cursor, 'passing_defense_historical', team_abbr)

        defense_vs_qb_historical = fetch_goofy_data_for_game(cursor, 'defense_vs_QB_historical', team_abbr)

        defense_vs_rb_historical = fetch_goofy_data_for_game(cursor, 'defense_vs_RB_historical', team_abbr)

        defense_vs_te_historical = fetch_goofy_data_for_game(cursor, 'defense_vs_TE_historical', team_abbr)

        defense_vs_wr_historical = fetch_goofy_data_for_game(cursor, 'defense_vs_WR_historical', team_abbr)

        insights = fetch_player_data_for_game(cursor, 'insights', team_abbr)

        redzone_stats = []
        for player in player_projections:
            player_name = player['player_name']
            position = player['position']
            stats = fetch_redzone_stats(cursor, player_name, position)
            if stats["rushing_data"] or stats["receiving_data"]:
                redzone_stats.append({
                    "player_name": player_name,
                    "rushing_data": stats["rushing_data"],
                    "receiving_data": stats["receiving_data"]
                })

        # Create the prompt with all the data
        prompt = {
            "prompt": (
                """
                    Objective:
                    Generate accurate and profitable sports betting picks using the provided data for each game. Focus on identifying the best opportunities across moneyline, spread, totals, and player props. Ensure the output is consistent across all games.

                    Data Provided:
                    Analyst articles related to the game
                    Sports betting picks from analysts
                    Current game odds
                    Current player prop odds
                    Player projections (e.g., projected rushing/receiving yards)
                    Historical redzone stats from 2023
                    Historical data (per game stats) for defenses' performance against rushing and passing, including league averages.
                    Team defense performance vs. a given position
                    Insights from audio transcripts provided by NFL analysts.

                    Output Requirements:
                    Primary Betting Opportunities:

                    Moneyline, Spread, and Total Bets:
                    Identify the best opportunities for moneyline, spread, and total bets based on the provided data.
                    Highlight any strong trends or patterns in the data that support these bets.
                    Player Prop Bets:

                    List of Profitable Player Props:
                    Identify as many player prop lines as possible that have a high probability of success.
                    When suggesting an over/under prop, please specify whether to bet on the Over or the Under.
                    Include prop bets related to projected player performance (e.g., rushing yards, receiving yards) and Anytime Touchdown Scorer probabilities.
                    Indicate the probability of each prop hitting and provide reasoning based on the data.
                    Utilize the defense vs. position data to help aid in choosing player props for those positions.
                    Parlay Opportunities:

                    Multiple Parlay Options:
                    Create multiple parlay opportunities for each game:
                    Low-Risk Parlay: Odds around +100, using higher-probability bets.
                    Medium-Risk Parlay: Balancing safety and potential returns, with odds ranging from +300 to +600.
                    High-Risk Parlay: Including bets with lower consensus but higher potential payouts, with odds up to +1000.
                    Mix in player props with moneyline, spread, or total bets in these parlays.
                    Summary of Picks:

                    Summary Explanation:
                    Summarize why each pick was chosen, detailing how the data supports these decisions.
                    Include a brief analysis of how expert opinions, odds, and projections align with the picks.
                    AI Insights:

                    Speculative Picks:
                    Based on the data provided, allow the AI to speculate and generate additional picks or parlays.
                    These picks should be labeled as "AI Insights" and may include bets not directly backed by the provided data.
                    Guidelines for Analysis:
                    Player Projections: Factor in opposing defense projections, compare player projections across teams, and analyze variance between prop lines and projections.
                    Expert Picks: Incorporate insights from expert picks, leverage last10head2head data, and prioritize higher edge values.
                    Odds: Track line movements from opening to current odds to identify value.
                    Formatting:
                    Consistent Output: Ensure each game’s output follows the same structure and includes all relevant sections as outlined above.

                    **JSON Output Requirement:**
                    Please format the entire output as a JSON object, with keys corresponding to each section (e.g., "Primary Betting Opportunities", "Player Prop Bets", "Parlay Opportunities", "Summary of Picks", "AI Insights"). Ensure all nested elements are also structured as JSON objects or arrays as appropriate. This will facilitate storing the data directly in a database.
                """
            ),
            "expert_picks": serialize_data(expert_picks),
            "analyst_articles": serialize_data(analyst_articles),
            "game_odds": serialize_data(game_odds),
            "player_odds": serialize_data(player_odds),
            "player_projections": serialize_data(player_projections),
            "redzone_stats": serialize_data(redzone_stats),
            "rushing_defense_historical": serialize_data(rushing_defense_historical),
            #"rushing_league_average": serialize_data(rushing_league_average_historical),
            "passing_defense_historical": serialize_data(passing_defense_historical),
            #"passing_league_average": serialize_data(passing_league_average_historical)
            "defense_vs_qb_historical": serialize_data(defense_vs_qb_historical),
            "defense_vs_rb_historical": serialize_data(defense_vs_rb_historical),
            "defense_vs_te_historical": serialize_data(defense_vs_te_historical),
            "defense_vs_wr_historical": serialize_data(defense_vs_wr_historical),
            "analyst_insights": serialize_data(insights)
        }

        with open(os.path.join(path,f"game_prompt_{away_team} {home_team}.txt"), "w", encoding="utf-8") as file:
            json.dump(prompt, file, ensure_ascii=False, indent=4, cls=CustomJSONEncoder)

        # Make the API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            top_p = 0.9,
            n=1,
            messages=[{"role": "user", "content": json.dumps(prompt, cls=CustomJSONEncoder)}],
        )

        text = str(response.choices[0].message.content)

        all_predictions.append(text)

        with open(os.path.join(path,f"game_data_{away_team} {home_team}.txt"), "w", encoding="utf-8") as file:
            file.write(text)
        
        print(f"Predicitons for {away_team} vs {home_team} written to text file.")

    final_prompt = (
        """Final Review of Best Bets and Parlays:
                Based on the analysis of predictions for all games, please complete the following tasks:

                Identify the Best Bets:

                Select 5-6 of the most confident game bets (moneyline, total, spread) for the scheduled week. You can only pick either moneyline, total, or spread. Decide which one is the best bet and display that one.
                Choose 5-6 of the best player props.
                Provide an in-depth explanation for each bet, highlighting how the data supports these selections.
                Star rating: Give each best bet a star rating from 1-3 stars. 3 stars being the highest confidence bet.

                Create Multiple Parlays:

                Parlay Construction:
                Low-Risk Parlays: Construct at least 2 low-risk parlays using a combination of player props and game lines.
                Medium-Risk Parlays: Create at least 2 medium-risk parlays, balancing safety and potential returns.
                High-Risk Parlays: Design at least 2 high-risk parlays with higher potential payouts.
                Longshot Parlays:
                Develop 1-3 longshot parlays with odds in the +500 to +1000 range, aiming for the highest possible chance of success.
                Parlay Flexibility:
                Parlays can mix player props and game bets from different games; they do not need to be same-game parlays.
                Ensure each parlay is unique and optimizes the chances of winning.

                Provide Explanations and Probabilities:

                For each parlay and pick, provide clear explanations and probabilities to justify the selections.
                Ensure the reasoning is data-driven and ties back to the analysis of the games.

                Important Details:

                Odds Format: Provide all odds in American format.
                Game Association for Totals: When including over/under bets in parlays, specify the corresponding game.
                Exclusion: Do not include exact win point margin bets.
                Best Bets Section: Reserve this section for the most confident bets, which are backed by multiple data sources and have a high probability of success.
                Goal:
                Ensure all games and their respective bets are included in this analysis, offering a comprehensive and well-justified set of final predictions and parlay opportunities.

                **JSON Output Requirement:**
                Please format the entire output as a JSON object, with keys corresponding to each section (e.g., "Best Bets", "Parlay Construction", "Explanations and Probabilities", "Important Details"). Ensure all nested elements are also structured as JSON objects or arrays as appropriate. This will facilitate storing the data directly in a database."""
    )

    combined_prompt = {
        "prompt": final_prompt,
        "all_predictions": all_predictions
    }

    with open("all_predictions", "w", encoding='utf-8') as file:
        file.write(str(combined_prompt))

    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        top_p = 0.9,
        n=1,
        messages=[{"role": "user", "content": json.dumps(combined_prompt, cls=CustomJSONEncoder)}],
    )

    # Write the final response to a file
    with open(os.path.join(path,"final_predictions.txt"), "w", encoding="utf-8") as file:
        file.write(final_response.choices[0].message.content)

    print("Final predictions and parlays have been written to final_predictions.txt")
    # Close the database connection
    connection.close()

if __name__ == "__main__":
    # Generate picks
    generate_picks()
