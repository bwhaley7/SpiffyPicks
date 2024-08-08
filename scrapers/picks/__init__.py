import os
from dotenv import load_dotenv, find_dotenv
from covers import scrape_covers
from dimers import scrape_dimers
from pickswise import scrape_pickswise
from wagertalk import scrape_wagertalk

load_dotenv(find_dotenv())

# Access the MongoDB connection string from the environment variable
mongo_db_string = os.getenv('MONGO_DB_CONNECTION_STRING')

if mongo_db_string is None:
    print("MongoDB connection string not found. Please check your .env file.")

def run_all_scrapers():
    scrape_covers(mongo_db_string)
    scrape_dimers(mongo_db_string)
    scrape_pickswise(mongo_db_string)
    scrape_wagertalk(mongo_db_string)

if __name__ == "__main__":
    run_all_scrapers()