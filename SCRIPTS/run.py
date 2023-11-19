from Scraper.scraper import Scraper
from Scraper.database import SQLiteDatabase
from Scraper.config import Config
from Scraper.api_consumer import APIConsumer
from Scraper.parser import Parser


def main():
    """ 
    Valid URL should contain 'Scores-and-Fixtures' like: 
    https://fbref.com/en/comps/8/schedule/Champions-League-Scores-and-Fixtures
    https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures
    """
    config_file = "config.yaml"
    db_name = "football_db_prod.db"

    config = Config(config_file).load_config()
    db = SQLiteDatabase(db_name=db_name)
    api_consumer = APIConsumer(config)
    parser = Parser(api_consumer, config)
    scraper = Scraper(parser, db)

    urls = [
        "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
        ]
    for url in urls:
        scraper.scrape_data(url=url, clear_db=True, number_of_matches_to_scrape=5)

if __name__ == "__main__":
    main()