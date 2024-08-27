import requests
import re
from lxml import html
from datetime import datetime
from util.nfl_teams import get_team_abbreviation

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

        for matchup, pick, explanation in zip(matchups, picks, explanations):
            matchup_text = matchup.text_content().strip()
            pick_text = pick.text_content().strip()
            explanation_text = explanation.text_content().strip()

            # Clean and extract date and time from the matchup text
            matchup_text_clean = re.sub(r'\(\d+\)', '', matchup_text)
            matchup_text_clean = " ".join(matchup_text_clean.split())

            date_time_match = date_time_pattern.search(matchup_text_clean)
            if date_time_match:
                date_str = date_time_match.group(1)
                time_str = date_time_match.group(2)

                # Convert date to ISO format "YYYY-MM-DD"
                date_iso = datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")

                # Remove date/time from the matchup text
                matchup_text_clean = date_time_pattern.sub('', matchup_text_clean).strip()

            # Extract team names and map them to abbreviations
            away_team_name, home_team_name = matchup_text_clean.split(' at ')
            away_abbreviation = get_team_abbreviation(away_team_name.strip())
            home_abbreviation = get_team_abbreviation(home_team_name.strip())

            pick_text_clean = " ".join(pick_text.split())
            explanation_text_clean = " ".join(explanation_text.split())

            picks_data.append({
                'matchup': [away_abbreviation, home_abbreviation],
                'date': date_iso,
                'time': time_str,
                'away_team': away_team_name.strip(),
                'home_team': home_team_name.strip(),
                'outcome': pick_text_clean,
                'explanation': explanation_text_clean,
                'site': "Covers.com",
                'data_added': datetime.now()
            })

        print(f"Returned {len(picks_data)} picks from Covers.com")
        return picks_data

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def scrape_covers():
    picks = scrape_picks_covers()
    return picks
