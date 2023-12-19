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
        # ligues
        "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures",
        "https://fbref.com/en/comps/12/schedule/La-Liga-Scores-and-Fixtures",
        "https://fbref.com/en/comps/11/schedule/Serie-A-Scores-and-Fixtures",
        "https://fbref.com/en/comps/20/schedule/Bundesliga-Scores-and-Fixtures",
        "https://fbref.com/en/comps/13/schedule/Ligue-1-Scores-and-Fixtures",
        # uefa competitions
        "https://fbref.com/en/comps/8/schedule/Champions-League-Scores-and-Fixtures",
        "https://fbref.com/en/comps/19/schedule/Europa-League-Scores-and-Fixtures",
        "https://fbref.com/en/comps/882/schedule/Europa-Conference-League-Scores-and-Fixtures",
        # domestic cups
        "https://fbref.com/en/comps/514/schedule/FA-Cup-Scores-and-Fixtures",
        "https://fbref.com/en/comps/569/schedule/Copa-del-Rey-Scores-and-Fixtures",
        "https://fbref.com/en/comps/521/schedule/DFB-Pokal-Scores-and-Fixtures",
        "https://fbref.com/en/comps/518/schedule/Coupe-de-France-Scores-and-Fixtures",
        "https://fbref.com/en/comps/529/schedule/Coppa-Italia-Scores-and-Fixtures"
        ]
    try:
        for url in urls:
            scraper.scrape_data(url=url)
    except Exception as e:
        raise e
    finally:
        if db:
            db.con.close()
            
if __name__ == "__main__":
    main()