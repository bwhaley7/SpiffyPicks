import requests
import re
import json
from lxml import html
from datetime import datetime
from util.teamExtractor import TeamAbbreviationExtractor

def scrape_bettingspros_articles():
    url = 'https://www.bettingpros.com/articles/sports/nfl/'
    article_xpath = '/html/body/div[1]/div/div/div[1]/div/main/div/article/section/div/a'
    date_xpath = '/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/main[1]/div[2]/div[1]/article[1]/div[1]/div[1]/div[1]/span[4]'

    try:

        response = requests.get(url)
        response.raise_for_status()

        with open("response.html", 'w', encoding='utf-8') as file:
            file.write(response.text)

        tree = html.fromstring(response.content)

        script_content = tree.xpath('//script[contains(text(), "const bpArticlesPageData")]/text()')[0]

        json_data_match = re.search(r'articles:\s*(\[\{.*\}\])', script_content, re.DOTALL)

        if json_data_match:
            json_data = json_data_match.group(1)
            articles_data = json.loads(json_data)

        extracted_articles = []

# Iterate through each article in the JSON
        for article in articles_data:
            if "Podcast" in article['title']['rendered']:
                continue
            title = article['title']['rendered']
            article_date = article['date_gmt']
            article_link = article['link']

            article_info = {
                'title': title,
                'date': article_date,
                'link': article_link
            }


            extracted_articles.append(article_info)

        print(f"Found {len(extracted_articles)} articles at bettingpros.com")
        
        for article in extracted_articles:
            print(f"Title: {article['title']}")
            print(f"Date: {article['date']}")
            print(f"Link: {article['link']}")
            print("-" * 40)

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")