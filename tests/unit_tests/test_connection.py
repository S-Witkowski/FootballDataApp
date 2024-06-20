from Scraper.database import SQLiteDatabaseConnection, AzureSQLDatabaseConnection
import os

def test_connect_sqllite():
    db = SQLiteDatabaseConnection(":memory:")
    with db.connect() as con:
        assert con