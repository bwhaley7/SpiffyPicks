import requests
import re
import pytz
from lxml import html
from datetime import datetime
from nfl_teams import get_team_abbreviation

def scrape__picks_wagertalk():
    url = 'https://www.wagertalk.com/free-sports-picks/nfl'

    try:

        response = requests.get(url)
        response.raise_for_status() 

        tree = html.fromstring(response.content)

        # Define the XPath expressions
        event_xpath = '/html[1]/body[1]/div[2]/div[1]/section[3]/div[1]/main[1]/section/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]'
        datetime_xpath = '/html[1]/body[1]/div[2]/div[1]/section[3]/div[1]/main[1]/section/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]'
        play_xpath = '/html[1]/body[1]/div[2]/div[1]/section[3]/div[1]/main[1]/section/div[1]/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]'

        events = tree.xpath(event_xpath)
        datetimes = tree.xpath(datetime_xpath)
        plays = tree.xpath(play_xpath)
        team1_index = 0
        team2_index = 3

        picks = []

        for event, dateandtime, play in zip(events, datetimes, plays):
            event_text = event.text_content().strip()
            dateandtime_text = dateandtime.text_content().strip()
            play_text = play.text_content().strip()
            event_text_clean = re.sub(r'\(\d+\) ', '', event_text).strip()
            event_split = event_text_clean.split()

            try:
                # Clean up the date and time text
                dateandtime_text_clean = dateandtime_text.replace('EDT', '').strip()

                # Convert to datetime object
                parsed_date = datetime.strptime(dateandtime_text_clean, '%b %d, %Y %I:%M %p')
                
                # Add the timezone (EDT)
                eastern = pytz.timezone('US/Eastern')
                localized_date = eastern.localize(parsed_date)
                
                # Convert to ISO 8601 format (without timezone info for simplicity)
                iso_date = localized_date.date().isoformat()
            except ValueError as e:
                iso_date = f'Invalid date format: {e}'

            # Check if the event includes the word "at"
            if "at" in event_text:
                if('at' in event_split[team2_index]):
                    team2_index+=1

                picks.append({
                'matchup': [get_team_abbreviation(event_split[team1_index] + " " + event_split[team1_index+1]), get_team_abbreviation(event_split[team2_index] + " " + event_split[team2_index+1])],
                'date': iso_date,
                'time': '',
                'away_team': get_team_abbreviation(event_split[team1_index] + " " + event_split[team1_index+1]),
                'home_team': get_team_abbreviation(event_split[team2_index] + " " + event_split[team2_index+1]),
                'venue': '',
                'predicted_away_score': None,
                'predicted_home_score': None,
                'predicted_score': '',
                'predicted_game_ou': '',
                'best_bets': '',
                'best_parlay': '',
                'betting_info': '',
                'market': '',
                'outcome': play_text,
                'explanation': '',
                'expert_prediction': '',
                'game_trends': '',
                'last10head2head': '',
                'site': 'wagertalk.com',
                'data_added': datetime.now()
                })
                if team2_index == 4:
                    team2_index = 3


        print(f"Inserted {len(picks)} records into MongoDB from wagertalk.com")
        return picks

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def scrape_wagertalk():
    picks = scrape__picks_wagertalk()
    return picks
    #Add scrape method for player props