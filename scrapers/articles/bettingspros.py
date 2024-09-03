import requests
import re
import json
from lxml import html
from datetime import datetime
from util.teamExtractor import TeamAbbreviationExtractor

def scrape_articles():
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
        return extracted_articles

    except requests.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_article_content(articles): #Still not successfully pulling in the article content.
    article_contents = []

    for article in articles:
        article_url = article['link']
        try:
            response = requests.get(article_url)
            response.raise_for_status()

            html_content = response.content.decode('utf-8')
            
            # Extract content between specific markers
            match = re.search(r'const bpArticlePageData\s*=\s*(\{.*?});\s*</script>', html_content, re.DOTALL)
            if match:
                json_like_data = match.group(1)

                # Attempt to find the article content within the extracted JSON-like string
                content_match = re.findall(r'<p[^>]*>(.*?)</p>', json_like_data, re.DOTALL)
                
                # Clean and append content
                cleaned_content = [re.sub('<[^<]+?>', '', c).strip() for c in content_match if c.strip()]
                
                if cleaned_content:
                    article_contents.append({
                        'title': article['title'],
                        'content': cleaned_content,
                        'link': article_url
                    })
                else:
                    print(f"No relevant content found in the article for {article_url}.")
            else:
                print(f"No JSON-like content found in the article for {article_url}.")

        except requests.RequestException as e:
            print(f"Request failed for {article_url}: {e}")

    return article_contents



def scrape_bettingpros_articles():
    articles = scrape_articles()
    content = get_article_content(articles)
    print(content)
