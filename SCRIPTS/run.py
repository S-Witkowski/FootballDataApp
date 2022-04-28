from Scraper.scraper import Scraper

def main():
    """ 
    Valid URL should contain 'Scores-and-Fixtures' like: 
    https://fbref.com/en/comps/8/schedule/Champions-League-Scores-and-Fixtures
    https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures
    """

    s = Scraper()
    urls = [
        "https://fbref.com/en/comps/8/schedule/Champions-League-Scores-and-Fixtures"
        ]
    for url in urls:
        s.scrape_data(url=url, clear_db=False, test=True)

if __name__ == "__main__":
    main()