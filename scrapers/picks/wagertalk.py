import requests
import re
from lxml import html
from pymongo import MongoClient
from datetime import datetime

def scrape__picks_wagertalk(dbInfo):
    url = 'https://www.wagertalk.com/free-sports-picks/nfl'

    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content
        tree = html.fromstring(response.content)

        # Define the XPath expressions
        event_xpath = '/html[1]/body[1]/div[2]/div[1]/section[3]/div[1]/main[1]/section/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[2]'
        datetime_xpath = '/html[1]/body[1]/div[2]/div[1]/section[3]/div[1]/main[1]/section/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]'
        play_xpath = '/html[1]/body[1]/div[2]/div[1]/section[3]/div[1]/main[1]/section/div[1]/div[1]/div[2]/div[1]/div[2]/div[2]/div[2]'

        # Extract data using XPath
        events = tree.xpath(event_xpath)
        datetimes = tree.xpath(datetime_xpath)
        plays = tree.xpath(play_xpath)

        # Prepare list to store the extracted picks
        picks = []

        # Loop through each event and corresponding datetime and play
        for event, datetime, play in zip(events, datetimes, plays):
            event_text = event.text_content().strip()
            datetime_text = datetime.text_content().strip()
            play_text = play.text_content().strip()

            event_text_clean = re.sub(r'\(\d+\)', '', event_text).strip()

            # Check if the event includes the word "at"
            if "at" in event_text:
                picks.append({
                    'event': event_text_clean,
                    'datetime': datetime_text,
                    'play': play_text
                })

        client = MongoClient(dbInfo)
        db = client['spiffypicks']
        collection = db['scraped_picks']
        collection.insert_many(picks)

        print(f"Inserted {len(picks)} records into MongoDB from wagertalk.com")
#
        # picks_json = json.dumps(picks, indent=4)

        # print(picks_json)

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def scrape_wagertalk(dbInfo):
    scrape__picks_wagertalk(dbInfo)
    #Add scrape method for player props