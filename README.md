Automotive BI Pipeline
Final assignment for MADSC301 (Business Intelligence) — EUBS Munich, Summer 2026.
What this project does
I built an ETL pipeline around automotive data — vehicle makes/models from NHTSA and fuel efficiency data from the EPA. The goal was to look at fuel efficiency trends across manufacturers and model years (2015–2024), something that ties into pricing and supply chain decisions in the automotive industry.
Both APIs are public and don't require an API key, which made setup a lot simpler.
Data sources

NHTSA vPIC API — vehicle makes, models, manufacturer info (vpic.nhtsa.dot.gov)
EPA FuelEconomy.gov API — MPG, CO2 emissions, vehicle class (fueleconomy.gov)

How it's structured
01_collect_data.py          → pulls data from both APIs
02_clean_data.py            → cleans and transforms with pandas
03_store_postgres.py        → loads into PostgreSQL, runs analysis queries
etl_pipeline.py             → runs all 3 steps, scheduled every 24h
Automotive_BI_Dashboard.pbix → Power BI dashboard
data/processed/              → cleaned CSVs end up here
Setting it up
Clone the repo, then:
bashpython -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
You'll need a .env file with your PostgreSQL credentials:
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=AutomotiveBI
PG_USER=postgres
PG_PASSWORD=your_password
And create the database first:
sqlCREATE DATABASE "AutomotiveBI";
Running it
One step at a time:
bashpython 01_collect_data.py
python 02_clean_data.py
python 03_store_postgres.py
Or just run the whole pipeline:
bashpython etl_pipeline.py
Database
Three tables in PostgreSQL: vehicle_makes, vehicle_models, and epa_fuel_economy (the main one, with 1,065 records covering 2015–2024).
There's also a view called top_efficient_vehicles with the 50 most fuel-efficient vehicles.
A few of the queries I used for analysis:
sql-- average MPG per manufacturer
SELECT make, ROUND(AVG(combined_mpg)::numeric, 2) AS avg_mpg
FROM epa_fuel_economy GROUP BY make ORDER BY avg_mpg DESC;

-- efficiency trend across years
SELECT year, ROUND(AVG(combined_mpg)::numeric, 2) AS avg_mpg
FROM epa_fuel_economy GROUP BY year ORDER BY year;

-- most efficient vehicle class
SELECT vehicle_class, ROUND(AVG(combined_mpg)::numeric, 2) AS avg_mpg
FROM epa_fuel_economy GROUP BY vehicle_class ORDER BY avg_mpg DESC;
Orchestration
The pipeline is automated with APScheduler — etl_pipeline.py runs the full sequence once immediately, then repeats every 24 hours.
Dashboard
Built in Power BI, connected directly to the PostgreSQL database. The dashboard combines six visuals across two rows:
Top row — distribution overview:

Pie chart — fuel type distribution
Donut chart — efficiency category breakdown (Low/Medium/High/Very High)
Pie chart — drive type distribution (FWD/RWD/AWD/4WD)

Bottom row — trends and comparisons:

Bar chart — average MPG by manufacturer
Line chart — fuel efficiency trend by model year (2015–2024)
Scatter plot — efficiency vs. emissions by vehicle class

Plus three KPI cards (average CO2, total vehicles analyzed, average MPG) and a fuel type slicer for interactive filtering.
What the data shows
Fuel efficiency has improved noticeably since 2018, which lines up with the broader shift toward electric and hybrid vehicles in the market. Electric and hybrid-leaning brands (Fisker, BYD) top the efficiency rankings, while the scatter plot shows the expected trade-off between vehicle class size and combined MPG.
Assignment requirements

 Public API as data source
 Data cleaning with pandas
 PostgreSQL (not SQLite)
 Orchestration via APScheduler
 Analysis + visualization (SQL + Power BI)
 Virtual environment
 .env for credentials
 requirements.txt
