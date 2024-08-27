import requests
import re
import pandas as pd
from lxml import html
from datetime import datetime
from util.nfl_teams import get_team_abbreviation

base_url = "https://www.oddsshark.com/nfl/computer-picks"

def scrape_matchup_links():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Check for request errors
        tree = html.fromstring(response.content)

        # XPath to extract matchup links
        matchup_xpath = '/html[1]/body[1]/div[1]/div[2]/main[1]/div[2]/div[1]/article[1]/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/div/div[1]/div[1]/a[1]'
        matchup_elements = tree.xpath(matchup_xpath)

        # Extract href attributes from the matchup elements
        matchup_links = ["https://www.oddsshark.com" + element.get('href') for element in matchup_elements]
        
        return matchup_links

    except requests.RequestException as e:
        print(f"Error scraping matchup links: {e}")
        return []
    
def scrape_matchup_data(matchup_link):
    try:
        response = requests.get(matchup_link)
        response.raise_for_status()

        tree = html.fromstring(response.content)

        with open("game.txt", 'w', encoding='utf-8') as file:
            file.write(response.text)

        matchup_xpath = '/html/body/div/div[2]/main/div[2]/div/article/div/div/div/div[1]/div[7]/div/div/div[1]/div[1]/div[3]'
        team1_score_xpath = '/html/body/div/div[2]/main/div[2]/div/article/div/div/div/div[1]/div[7]/div/div/div[1]/div[2]/div/div[1]/div[3]/span[2]'
        team2_score_xpath = '/html/body/div/div[2]/main/div[2]/div/article/div/div/div/div[1]/div[7]/div/div/div[1]/div[2]/div/div[1]/div[4]/span[2]'
        game_total_pick_xpath = '/html/body/div/div[2]/main/div[2]/div/article/div/div/div/div[1]/div[7]/div/div/div[1]/div[2]/div/div[3]/div[3]/span[1]'
        expert_pick_xpath = '/html/body/div/div[2]/main/div[2]/div/article/div/div/div/div[1]/div[7]/div/div/div[1]/div[2]/div[3]/div/div[1]/div[1]'
        h2h_last10_xpath = '/html/body/div/div[2]/main/div[2]/div/article/div/div/div/div[1]/div[11]/div/div[2]'
        trends1_xpath = '/html/body/div/div[2]/main/div[2]/div/article/div/div/div/div[1]/div[14]/div/div[2]/ul'
        trends2_xpath = '/html/body/div/div[2]/main/div[2]/div/article/div/div/div/div[1]/div[14]/div/div[3]/ul'
        date_xpath = '/html/body/div/div[2]/main/div[2]/div/article/div/div/div/div[1]/div[9]/div/div/div[1]/div/h3/span[1]'

        matchup_element = tree.xpath(matchup_xpath)
        team1_score_element = tree.xpath(team1_score_xpath)
        team2_score_element = tree.xpath(team2_score_xpath)
        game_total_element = tree.xpath(game_total_pick_xpath)
        expert_pick_element = tree.xpath(expert_pick_xpath)
        h2h_last10_element = tree.xpath(h2h_last10_xpath)
        trends1_element = tree.xpath(trends1_xpath)
        trends2_element = tree.xpath(trends2_xpath)
        date_element = tree.xpath(date_xpath)

        if date_element:
            date_text = date_element[0].text_content().strip()
            parsed_date = datetime.strptime(f"2024 {date_text}", "%Y %A, %B %d")
            iso_date = parsed_date.strftime("%Y-%m-%d")
        else:
            iso_date = "Date not found"

        game_data = {}
        if team1_score_element and team2_score_element and game_total_element and matchup_element:
            matchupText = matchup_element[0].text_content().strip()
            team1_score = team1_score_element[0].text_content().strip()
            team2_score = team2_score_element[0].text_content().strip()
            gameTotalPicks = game_total_element[0].text_content().strip()

            if(expert_pick_element):
                expertPick = expert_pick_element[0].text_content().strip()
            else:
                expertPick = "No expert prediction available"

            if(h2h_last10_xpath):
                table_html = html.tostring(h2h_last10_element[0], encoding='unicode')
                tables = pd.read_html(table_html)
                table_data = tables[0].to_dict(orient='records')
            else:
                table_data = "No table data found"

            if trends1_element:
                trend1_data = [li.text_content().strip() for li in trends1_element[0].xpath('./li')]
            else:
                trend1_data = "No trend data found"

            if trends2_element:
                trend2_data = [li.text_content().strip() for li in trends2_element[0].xpath('./li')]
            else:
                trend2_data = "No trend data found"

            if "O" in gameTotalPicks:
                gameTotalPicks = gameTotalPicks.replace("O", "")
                gameTotalString = "The game will go over" + gameTotalPicks + "total points"
            else:
                gameTotalPicks = gameTotalPicks.replace("U", "")
                gameTotalString = "The game will go under" + gameTotalPicks + "total points"

            teamText = matchupText.split()

            awayTeam = get_team_abbreviation(teamText[0])
            homeTeam = get_team_abbreviation(teamText[2])

            # Check if both scores contain at least one number using regex
            if re.search(r'\d', team1_score) and re.search(r'\d', team2_score) and re.search(r'\d', gameTotalPicks):
                picks_data = {
                    'matchup': [awayTeam, homeTeam],
                    'date': iso_date,
                    'time': '',
                    'away_team': awayTeam,
                    'home_team': homeTeam,
                    'venue': '',
                    'predicted_away_score': None,
                    'predicted_home_score': None,
                    'predicted_score': f"{team1_score} - {team2_score}",
                    'predicted_game_ou': gameTotalString,
                    'best_bets': '',
                    'best_parlay': '',
                    'betting_info': '',
                    'market': '',
                    'outcome': expertPick,
                    'explanation': '',
                    'expert_prediction': expertPick,
                    'game_trends': trend1_data + trend2_data,
                    'last10head2head': table_data,
                    'site': "Oddsshark.com",
                    'data_added': datetime.now()
                }

                return picks_data
            else:
                print("Did not contain numbers. Invalid.")
        else:
            print("Predicted score not found.")
            print(f"Away Score: {team1_score_element} | Home Score: {team2_score_element} | Game Total: {game_total_element} | Matchup: {matchup_element}")



    except requests.RequestException as e:
        print(f"Error scraping matchup page {matchup_link}: {e}")



def scrape_oddsshark():
    matchup_links = scrape_matchup_links()
    data = []
    for link in matchup_links:
        data.append(scrape_matchup_data(link))
    print(f"Added {len(matchup_links)} picks from Oddsshark")
    return data
