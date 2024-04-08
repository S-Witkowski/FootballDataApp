## About The Project
This app is the example of how to scrape data from a website and put it into a database.

App can scrape data from https://fbref.com/ for any competition's 'Scores $ Fixtures' bookmark. For example:
https://fbref.com/en/comps/8/schedule/Champions-League-Scores-and-Fixtures for Champions League data. 

Scraper's data scope is divided into two tables: matches and player_stats. To avoid unwanted values beeing inserted into database, app uses the same naming rules for three key areas:

1. Website data-stat name. That's where the naming comes from.
2. SQL column name.
3. Pydantic data model item.
   
The downside of that solution is that if we want to add a new column to player_stats table we should check name of the corresponding data-stat from website, update pydantic datamodel and recreate DB or update it with new columns. 
<br>
<br>
App contains requests limiter to prevent from straining the server - one request per 5 seconds.

## Installation
1. Clone the repo.
  ```sh
git clone https://github.com/S-Witkowski/FootballDataApp.git
  ```
2. Install packages.
  ```sh
pip install -r requirements.txt
  ```
 
 ## Usage
Run app from SCRIPTS folder 
  ```sh
python run.py
  ```
 Database will be created and filled with one record.

 You can modify ```main``` function in ```run.py``` file to work with diffrent leagues or choosing to download whole league data.
 
Code below will get whole data for Champions League and Premier League from present season:
 ```
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
     "https://fbref.com/en/comps/8/schedule/Champions-League-Scores-and-Fixtures",
     "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
     ]
 for url in urls:
     s.scrape_data(url=url)
```
 
<br>
Example matches data:

<table border="1" class="dataframe">  <thead>    <tr style="text-align: right;">      <th></th>      <th>id</th>      <th>round</th>      <th>date</th>      <th>home</th>      <th>score</th>      <th>away</th>      <th>match_id</th>      <th>season</th>      <th>competition</th>    </tr>  </thead>  <tbody>    <tr>      <th>0</th>      <td>1</td>      <td>Group stage</td>      <td>2021-09-14</td>      <td>Sevilla</td>      <td>1–1</td>      <td>RB Salzburg</td>      <td>4053e749</td>      <td>2021-2022</td>      <td>Champions League</td>    </tr>    <tr>      <th>1</th>      <td>2</td>      <td>Group stage</td>      <td>2021-09-14</td>      <td>Young Boys</td>      <td>2–1</td>      <td>Manchester Utd</td>      <td>b3e0c6ca</td>      <td>2021-2022</td>      <td>Champions League</td>    </tr>    <tr>      <th>2</th>      <td>3</td>      <td>Group stage</td>      <td>2021-09-14</td>      <td>Chelsea</td>      <td>1–0</td>      <td>Zenit</td>      <td>97ff5d03</td>      <td>2021-2022</td>      <td>Champions League</td>    </tr>    <tr>      <th>3</th>      <td>4</td>      <td>Group stage</td>      <td>2021-09-14</td>      <td>Villarreal</td>      <td>2–2</td>      <td>Atalanta</td>      <td>647a3ef3</td>      <td>2021-2022</td>      <td>Champions League</td>    </tr>    <tr>      <th>4</th>      <td>5</td>      <td>Group stage</td>      <td>2021-09-14</td>      <td>Barcelona</td>      <td>0–3</td>      <td>Bayern Munich</td>      <td>9673a872</td>      <td>2021-2022</td>      <td>Champions League</td>    </tr>  </tbody></table>

<br>
Example player_stats data:

<table border="1" class="dataframe"> <thead>    <tr style="text-align: right;">      <th></th>      <th>id</th>      <th>match_id</th>      <th>team</th>      <th>player</th>      <th>player_id</th>      <th>minutes</th>      <th>goals</th>      <th>assists</th>      <th>shots_total</th>      <th>cards_yellow</th>      <th>cards_red</th>      <th>touches</th>      <th>pressures</th>      <th>tackles</th>      <th>interceptions</th>      <th>blocks</th>      <th>xg</th>      <th>xa</th>      <th>sca</th>      <th>gca</th>      <th>passes_completed</th>      <th>passes</th>      <th>progressive_passes</th>      <th>dribbles_completed</th>      <th>dribbles</th>      <th>fouls</th>      <th>fouled</th>    </tr>  </thead>  <tbody>    <tr>      <th>0</th>      <td>1</td>      <td>4053e749</td>      <td>Sevilla</td>      <td>Youssef En-Nesyri</td>      <td>04e17fd5</td>      <td>49</td>      <td>0</td>      <td>0</td>      <td>2</td>      <td>2</td>      <td>1</td>      <td>19</td>      <td>8</td>      <td>0</td>      <td>0</td>      <td>1</td>      <td>0.5</td>      <td>0.0</td>      <td>1</td>      <td>1</td>      <td>5</td>      <td>8</td>      <td>0</td>      <td>0</td>      <td>0</td>      <td>2</td>      <td>3</td>    </tr>    <tr>      <th>1</th>      <td>2</td>      <td>4053e749</td>      <td>Sevilla</td>      <td>Papu Gómez</td>      <td>6e4df551</td>      <td>57</td>      <td>0</td>      <td>0</td>      <td>1</td>      <td>0</td>      <td>0</td>      <td>32</td>      <td>5</td>      <td>0</td>      <td>0</td>      <td>0</td>      <td>0.1</td>      <td>0.2</td>      <td>3</td>      <td>0</td>      <td>20</td>      <td>27</td>      <td>1</td>      <td>2</td>      <td>5</td>      <td>0</td>      <td>2</td>    </tr>    <tr>      <th>2</th>      <td>3</td>      <td>4053e749</td>      <td>Sevilla</td>      <td>Érik Lamela</td>      <td>abe66106</td>      <td>33</td>      <td>0</td>      <td>0</td>      <td>1</td>      <td>0</td>      <td>0</td>      <td>25</td>      <td>11</td>      <td>3</td>      <td>2</td>      <td>2</td>      <td>0.0</td>      <td>0.2</td>      <td>4</td>      <td>0</td>      <td>9</td>      <td>12</td>      <td>2</td>      <td>3</td>      <td>3</td>      <td>1</td>      <td>3</td>    </tr>    <tr>      <th>3</th>      <td>4</td>      <td>4053e749</td>      <td>Sevilla</td>      <td>Suso</td>      <td>4e219ad2</td>      <td>45</td>      <td>0</td>      <td>0</td>      <td>1</td>      <td>0</td>      <td>0</td>      <td>29</td>      <td>9</td>      <td>0</td>      <td>0</td>      <td>2</td>      <td>0.0</td>      <td>0.0</td>      <td>1</td>      <td>0</td>      <td>17</td>      <td>23</td>      <td>3</td>      <td>2</td>      <td>2</td>      <td>1</td>      <td>1</td>    </tr>    <tr>      <th>4</th>      <td>5</td>      <td>4053e749</td>      <td>Sevilla</td>      <td>Lucas Ocampos</td>      <td>a08b974a</td>      <td>45</td>      <td>0</td>      <td>0</td>      <td>2</td>      <td>0</td>      <td>0</td>      <td>21</td>      <td>9</td>      <td>0</td>      <td>1</td>      <td>1</td>      <td>0.0</td>      <td>0.0</td>      <td>0</td>      <td>0</td>      <td>7</td>      <td>10</td>      <td>0</td>      <td>0</td>      <td>2</td>      <td>0</td>      <td>1</td>    </tr>  </tbody></table>

## Acknowledgments
Data from https://fbref.com/ should only be used accoring to website's Terms of Use: https://www.sports-reference.com/data_use.html
