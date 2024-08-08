import os
from dotenv import load_dotenv, find_dotenv
from picks.covers import scrape_covers
from picks.dimers import scrape_dimers
from picks.pickswise import scrape_pickswise
from picks.wagertalk import scrape_wagertalk
from projections.sportsline import scrape_sportsline_dfs
from projections.fantasypros import scrape_fantasypros
from pymongo import MongoClient

load_dotenv(find_dotenv())

# Access the MongoDB connection string from the environment variable
mongo_db_string = os.getenv('MONGO_DB_CONNECTION_STRING')

if mongo_db_string is None:
    print("MongoDB connection string not found. Please check your .env file.")

def run_all_scrapers():
    #Clear all data debug method for testing
    client = MongoClient(mongo_db_string)
    db = client['spiffypicks']
    collection = db['scraped_picks']
    collection2 = db['scraped_projections']

    result = collection.delete_many({})
    result2 = collection2.delete_many({})

    scrape_covers(mongo_db_string)
    scrape_dimers(mongo_db_string)
    scrape_pickswise(mongo_db_string)
    scrape_wagertalk(mongo_db_string)
    scrape_sportsline_dfs(mongo_db_string)
    scrape_fantasypros(mongo_db_string, 1) #number is for the NFL week you are on.

if __name__ == "__main__":
    run_all_scrapers()