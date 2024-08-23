import requests
from lxml import html
from datetime import datetime
from util.teamExtractor import TeamAbbreviationExtractor

def scrape_action_articles():
    url = "https://www.actionnetwork.com/nfl/archive/1"
    article_xpath = '/html/body/div/div/main/div/div[1]/div/div[2]/div/div[1]/div/a[3]'
    date_xpath = '/html[1]/body[1]/div[1]/div[1]/main[1]/div[1]/div[1]/div[2]/div[1]/section[1]/div[4]/div[2]/div[2]/div[1]/div[2]'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        tree = html.fromstring(response.content)
        articles = tree.xpath(article_xpath)
        print(f"Found {len(articles)} articles.")

        article_data_list = []

        for index, article in enumerate(articles):
            article_text = article.text_content().strip()
            href = article.get('href')
            if href:
                article_response = requests.get(href, headers=headers)
                article_response.raise_for_status()

                # Parse the article content to create a new tree for each article
                article_tree = html.fromstring(article_response.content)

                # Use TeamAbbreviationExtractor with the appropriate div's XPath
                extractor = TeamAbbreviationExtractor(article_response.content, '//div[contains(@class, "contentBody__main")]')
                team_abbreviations = extractor.extract_team_abbreviations()
                article_content = extractor.extract_content()

                date_element = article_tree.xpath(date_xpath)
                if date_element:
                    date_text = date_element[0].text_content().strip()
                    try:
                        date_text_clean = date_text.rsplit(' ', 1)[0]
                        date_time_obj = datetime.strptime(date_text_clean, "%b %d, %Y, %I:%M %p")
                        date_iso = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S")
                    except ValueError as ve:
                        print(f"Error parsing date for Article {index + 1}: {ve}")
                        continue
                else:
                    print(f"No date found for Article {index + 1}")
                    continue

            article_data = {
                'article': article_text,
                'content': article_content,
                'url': href,
                'date': date_iso,
                'site': "Actionnetwork.com",
                'scraped_at': datetime.now().isoformat(),
                'matchup': team_abbreviations
            }

            article_data_list.append(article_data)

        return article_data_list

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
