import requests
from lxml import html
from pymongo import MongoClient
from datetime import datetime

def scrape_sportsline_dfs():
    url = "https://www.sportsline.com/nfl/expert-projections/simulation/"

    try:
        
        response = requests.get(url)
        response.raise_for_status()

        tree = html.fromstring(response.content)

        player_xpath = '/html[1]/body[1]/div[1]/div[5]/div[1]/section[1]/div[1]/main[1]/div[1]/section[1]/section[1]/section[1]/table[1]/tbody[1]/tr/td[1]'
        pos_xpath = '/html[1]/body[1]/div[1]/div[5]/div[1]/section[1]/div[1]/main[1]/div[1]/section[1]/section[1]/section[1]/table[1]/tbody[1]/tr/td[2]'
        team_xpath = '/html[1]/body[1]/div[1]/div[5]/div[1]/section[1]/div[1]/main[1]/div[1]/section[1]/section[1]/section[1]/table[1]/tbody[1]/tr/td[3]'
        game_xpath = '/html[1]/body[1]/div[1]/div[5]/div[1]/section[1]/div[1]/main[1]/div[1]/section[1]/section[1]/section[1]/table[1]/tbody[1]/tr/td[4]'
        projected_fp_xpath = '/html[1]/body[1]/div[1]/div[5]/div[1]/section[1]/div[1]/main[1]/div[1]/section[1]/section[1]/section[1]/table[1]/tbody[1]/tr/td[5]'
        pass_yds_xpath = '/html[1]/body[1]/div[1]/div[5]/div[1]/section[1]/div[1]/main[1]/div[1]/section[1]/section[1]/section[1]/table[1]/tbody[1]/tr/td[9]'
        rush_yds_xpath = '/html[1]/body[1]/div[1]/div[5]/div[1]/section[1]/div[1]/main[1]/div[1]/section[1]/section[1]/section[1]/table[1]/tbody[1]/tr/td[10]'
        rec_yds_xpath = '/html[1]/body[1]/div[1]/div[5]/div[1]/section[1]/div[1]/main[1]/div[1]/section[1]/section[1]/section[1]/table[1]/tbody[1]/tr/td[11]'

        # Extracting data using the XPaths
        players = tree.xpath(player_xpath)
        positions = tree.xpath(pos_xpath)
        teams = tree.xpath(team_xpath)
        games = tree.xpath(game_xpath)
        projected_fps = tree.xpath(projected_fp_xpath)
        pass_yds = tree.xpath(pass_yds_xpath)
        rush_yds = tree.xpath(rush_yds_xpath)
        rec_yds = tree.xpath(rec_yds_xpath)

        min_length = min(len(players), len(positions), len(teams), len(games), len(projected_fps), 
                         len(pass_yds), len(rush_yds), len(rec_yds))
        
        projections = []
        for i in range(min_length):
            projection = {
                "player": players[i].text_content().strip(),
                "position": positions[i].text_content().strip(),
                "team": teams[i].text_content().strip(),
                "game": games[i].text_content().strip(),
                "projected_fantasy_points": projected_fps[i].text_content().strip(),
                "projected_passing_yards": pass_yds[i].text_content().strip(),
                "projected_rushing_yards": rush_yds[i].text_content().strip(),
                "projected_receiving_yards": rec_yds[i].text_content().strip(),
                "site": "sportsline.com",
                "data_added": datetime.now()
            }
            projections.append(projection)

        print(f"Returned {len(projections)} projections from sportsline.com")
        return projections
    
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")