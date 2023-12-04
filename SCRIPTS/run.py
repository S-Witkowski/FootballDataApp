def main():
    from Scraper.scraper import Scraper
    from Scraper.database import SQLiteDatabase
    from Scraper.config import Config
    from Scraper.api_consumer import APIConsumer
    from Scraper.parser import Parser

    config_file = "config.yaml"
    db_name = "football_db_prod.db"

    config = Config(config_file).load_config()
    db = SQLiteDatabase(db_name=db_name)
    api_consumer = APIConsumer(config)
    parser = Parser(api_consumer, config)
    scraper = Scraper(parser, db)

    if config["recreate_db"]:
        db.db_state.recreate_db()

    urls = [
        "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
        ]
    try:
        for url in urls:
            scraper.scrape_data(url=url, number_of_matches_to_scrape=1)
    except Exception as e:
        raise e
    finally:
        if db:
            db.con.close()
            
if __name__ == "__main__":
    main()