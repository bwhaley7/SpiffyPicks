from covers import scrape_covers
from dimers import scrape_dimers
from pickswise import scrape_pickswise
from wagertalk import scrape_wagertalk

def run_all_scrapers():
    scrape_covers()
    scrape_dimers()
    scrape_pickswise()
    scrape_wagertalk()

if __name__ == "__main__":
    run_all_scrapers()