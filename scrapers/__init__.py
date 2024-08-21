import os
import json
from json import JSONEncoder
from dotenv import load_dotenv, find_dotenv
from picks.covers import scrape_picks_covers
from picks.dimers import scrape_dimers
from picks.pickswise import scrape_pickswise
from picks.wagertalk import scrape_wagertalk
from picks.oddsshark import scrape_oddsshark
from projections.sportsline import scrape_sportsline_dfs
from projections.fantasypros import scrape_fantasypros
from articles.actionnetwork import scrape_action_articles
from articles.coversArticles import scrape_covers_articles
from odds.bettingpros_game_odds import output_game_odds_file
from odds.format_odds_output import format_odds
from datetime import datetime, date

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

load_dotenv(find_dotenv())

dataPath = os.getenv('DATA_PATH')

def run_all_scrapers():
    covers_picks = scrape_picks_covers()
    dimers_picks = scrape_dimers()
    pickswise_picks = scrape_pickswise()
    wagertalk_picks = scrape_wagertalk()
    #oddsshark_picks = scrape_oddsshark()
    fp_proj = scrape_fantasypros(2) #number is for the NFL week you are on.
    action_articles = scrape_action_articles()
    covers_articles = scrape_covers_articles()

    output_game_odds_file("pre3", dataPath)
    format_odds("pre3", dataPath)

    expert_picks = (
    covers_picks +
    dimers_picks +
    pickswise_picks +
    wagertalk_picks #+
    #oddsshark_picks
    )

    analyst_articles = (
        action_articles +
        covers_articles
    )

    # Write combined data to JSON file
    with open(os.path.join(dataPath, 'expert_picks.json'), 'w', encoding='utf-8') as file:
        json.dump(expert_picks, file, ensure_ascii=False, indent=4, cls=CustomJSONEncoder)
    
    with open(os.path.join(dataPath, 'analyst_articles.json'), 'w', encoding='utf-8') as file:
        json.dump(analyst_articles, file, ensure_ascii=False, indent=4, cls=CustomJSONEncoder)

    with open(os.path.join(dataPath, 'player_projections.json'), 'w', encoding='utf-8') as file:
        json.dump(fp_proj, file, ensure_ascii=False, indent=4, cls=CustomJSONEncoder)

    print(f"All data has been written to their respective files.")

if __name__ == "__main__":
    run_all_scrapers()