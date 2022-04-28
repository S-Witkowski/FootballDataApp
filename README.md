This app is the example of how to scrape data from a website and put it into a database.

App can scrape data from https://fbref.com/ for any competition's 'Scores $ Fixtures' bookmark. For example:
https://fbref.com/en/comps/8/schedule/Champions-League-Scores-and-Fixtures for Champions League data. 

Scraper's data scope is divided into two tables: matches and player_stats. To avoid unwanted values beeing inserted into database, app uses the same naming rules for three key areas:
1. Website data-stat name. That's where the naming comes from.
2. SQL column name.
3. Pydantic data model item.
The downside of that solution is that if we want to add a new column to player_stats table we should check name of the corresponding data-stat from website, update pydantic datamodel, update sql table creating function and delete whole content of the table. 

Example player_stats data:
	id	match_id	team	player	player_id	minutes	goals	assists	shots_total	cards_yellow	...	xa	sca	gca	passes_completed	passes	progressive_passes	dribbles_completed	dribbles	fouls	fouled
0	1	4053e749	Sevilla	Youssef En-Nesyri	04e17fd5	49	0	0	2	2	...	0.0	1	1	5	8	0	0	0	2	3
1	2	4053e749	Sevilla	Papu Gómez	6e4df551	57	0	0	1	0	...	0.2	3	0	20	27	1	2	5	0	2
2	3	4053e749	Sevilla	Érik Lamela	abe66106	33	0	0	1	0	...	0.2	4	0	9	12	2	3	3	1	3
3	4	4053e749	Sevilla	Suso	4e219ad2	45	0	0	1	0	...	0.0	1	0	17	23	3	2	2	1	1
4	5	4053e749	Sevilla	Lucas Ocampos	a08b974a	45	0	0	2	0	...	0.0	0	0	7	10	0	0	2	0	1

Data from https://fbref.com/ should only be used accoring to website's Terms of Use: https://www.sports-reference.com/data_use.html