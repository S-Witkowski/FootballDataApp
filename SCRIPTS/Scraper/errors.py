class InvalidUrlException(Exception):
    """ Raised when a scraped URL is invalid. """
    def __init__(self, url):
        self.url = url
        self.message = f"{url} is invalid, because it does not contain 'id=all_sched' tag"
        super().__init__(self.message)

class NoScoreAndFixturesInUrlException(Exception):
    """ Raised when there is no 'Scores-and-Fixtures' in the URL. """
    def __str__(self):
        return "There is no 'Scores-and-Fixtures' in the URL."

class NoEnvaronmentalVariableException(Exception):
    """ Raised when a scraped URL is invalid. """
    def __init__(self, var_name):
        self.message = f"{var_name} is not defined. Please define it as envarionmental variable."
        super().__init__(self.message)