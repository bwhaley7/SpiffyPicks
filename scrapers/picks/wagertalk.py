import requests
import re
import pytz
from lxml import html
from pymongo import MongoClient
from datetime import datetime

def scrape__picks_wagertalk(dbInfo):
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

        picks = []

        for event, dateandtime, play in zip(events, datetimes, plays):
            event_text = event.text_content().strip()
            dateandtime_text = dateandtime.text_content().strip()
            play_text = play.text_content().strip()

            event_text_clean = re.sub(r'\(\d+\)', '', event_text).strip()

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
                picks.append({
                    'event': event_text_clean,
                    'date': iso_date,  # Use the converted ISO date
                    'play': play_text,
                    'site': 'wagertalk.com',
                    'data_added': datetime.now()
                })

        client = MongoClient(dbInfo)
        db = client['spiffypicks']
        collection = db['scraped_picks']
        collection.insert_many(picks)
        client.close()

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