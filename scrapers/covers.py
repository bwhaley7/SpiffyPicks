import requests
import json
import re
from lxml import html

def scrape_picks_covers():
    url = 'https://www.covers.com/picks/nfl'

    try:

        response = requests.get(url)
        response.raise_for_status()

        tree = html.fromstring(response.content)

        matchup_xpath = '/html[1]/body[1]/div[4]/div[1]/div[1]/div[1]/div[2]/div/div[1]/div[1]'
        pick_xpath = '/html[1]/body[1]/div[4]/div[1]/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[1]'
        explanation_xpath = '/html[1]/body[1]/div[4]/div[1]/div[1]/div[1]/div[2]/div/div[2]/div[3]/p[1]'

        matchups = tree.xpath(matchup_xpath)
        picks = tree.xpath(pick_xpath)
        explanations = tree.xpath(explanation_xpath)

        picks_data = []

        date_time_pattern = re.compile(r'(\d{2}/\d{2}/\d{4})(\d{1,2}:\d{2} [AP]M ET)')

        # Loop through each matchup and corresponding pick and explanation
        for matchup, pick, explanation in zip(matchups, picks, explanations):
            matchup_text = matchup.text_content().strip()
            pick_text = pick.text_content().strip()
            explanation_text = explanation.text_content().strip()

            matchup_text_clean = re.sub(r'\(\d+\)', '', matchup_text)
            matchup_text_clean = " ".join(matchup_text_clean.split())

            date_time_match = date_time_pattern.search(matchup_text_clean)
            if date_time_match:
                date = date_time_match.group(1)
                time = date_time_match.group(2)
                # Remove date/time from the matchup text
                matchup_text_clean = date_time_pattern.sub('', matchup_text_clean).strip()

            # Clean up whitespace and newline characters in pick and explanation
            pick_text_clean = " ".join(pick_text.split())
            explanation_text_clean = " ".join(explanation_text.split())

            picks_data.append({
                'matchup': matchup_text_clean,
                'date': date,
                'time': time,
                'pick': pick_text_clean,
                'explanation': explanation_text_clean
            })

        # Convert the list of picks to JSON format
        picks_json = json.dumps(picks_data, indent=4)
        
        print(picks_json)
        # Return the JSON string
        #return picks_json


    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def scrape_covers():
    scrape_picks_covers()

scrape_covers()