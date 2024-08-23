import requests
from lxml import html
from datetime import datetime
from util.teamExtractor import TeamAbbreviationExtractor

def scrape_page_articles():
    url = "https://www.covers.com/nfl/betting-news"
    article_xpath = '//div[@id="mainContainer"]//h2/a'
    date_xpath = '/html[1]/body[1]/div[4]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div/div[1]/div[2]'
    
    # Adding a User-Agent header to mimic a request from a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    }

    try:
        # Send a GET request to the URL with headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content
        tree = html.fromstring(response.content)

        # Extract articles and dates using the provided XPath
        articles = tree.xpath(article_xpath)
        dates = tree.xpath(date_xpath)

        # Print the number of articles found
        print(f"Found {len(articles)} articles at covers.com.")

        article_data_list = []

        # Loop through each article element and create JSON objects
        for index, article in enumerate(articles):
            article_text = article.text_content().strip()
            href = "https://covers.com" + article.get('href')
            article_response = requests.get(href, headers=headers)
            article_response.raise_for_status()

            extractor = TeamAbbreviationExtractor(article_response.content, '//div[@id="mainContainer"]', tags_to_search=['p'])
            team_abbreviations = extractor.extract_team_abbreviations()
            article_content = extractor.extract_content()

            # Check if the date exists for the corresponding article
            if index < len(dates):
                date_text = dates[index].text_content().strip()
                
                # Clean up the date text by removing the bullet and timezone
                date_text_clean = date_text.replace('•', '').replace('ET', '').strip()

                try:
                    # Convert the date to ISO format
                    date_time_obj = datetime.strptime(date_text_clean, "%b %d, %Y %I:%M %p")
                    date_iso = date_time_obj.strftime("%Y-%m-%dT%H:%M:%S")
                except ValueError as ve:
                    print(f"Error parsing date for Article {index + 1}: {ve}")
                    date_iso = "Invalid Date"
            else:
                date_iso = "Not Found"

            # Create a JSON object for each article
            article_data = {
                'article': article_text,
                'content': article_content,
                'url': href,
                'date': date_iso,
                'site': "Covers.com",
                'scraped_at': datetime.now().isoformat(),
                'matchup': team_abbreviations  # Add the team abbreviations here
            }
            
            # Add the JSON object to the list
            article_data_list.append(article_data)

        return article_data_list

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def scrape_covers_articles():
    articles = scrape_page_articles()
    return articles
