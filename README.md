Project Title :
URBAN PULSE
Citizen Complaint Intelligence & Resolution Analytics

Last updated: 2026-10-27

## OVERVIEW

Fetches NYC 311 service requests from the NYC Open Data API, inserts 10
fields into a local MySQL table, and analyzes them with pandas and Streamlit.

## ARCHITECTURE

1. requests calls the NYC Open Data endpoint and receives JSON records.
2. Each record has 10 fields.
3. mysql.connector inserts rows into service_requests in the
   urban_nyc_complaints database (MySQL, localhost:3307).
4. pandas and streamlit analyze the stored data; tabulate formats
   tabular console output.

## DATA SOURCE

Provider : NYC Open Data (311 service requests)
Endpoint : https://data.cityofnewyork.us/resource/erm2-nwe9.json
Format : JSON
Fields kept: unique_key, created_date, closed_date, due_date, agency,
complaint_type, borough, status, latitude, longitude
Params for api call : {
"$select": {{Fields kept}},
            "$order": "created_date DESC, unique_key DESC",
"$limit": batch_size,
            "$offset": offset,
}

rate limits: 1,00,000 is the total size took data in batchs like 1000

## ENVIRONMENT

Required libraries:
requests - calls the API
pandas - loads and analyzes data
streamlit - analysis UI
mysql-connector-python - MySQL driver (imported as mysql.connector)
python-dotenv - loads settings from a .env file
tabulate - formats console tables

Install:
pip install requests pandas streamlit mysql-connector-python python-dotenv tabulate

## DATABASE

Server : MySQL, localhost, port 3307
User : root (empty password)
Database : urban_nyc_complaints
Table : service_requests

Schema of the table name - service_requests

unique_key varchar(50) NO PRI NULL
created_date datetime YES NULL
closed_date datetime YES NULL
due_date datetime YES NULL
agency varchar(50) YES NULL
complaint_type varchar(255) YES NULL
borough varchar(50) YES NULL
status varchar(50) YES NULL
latitude decimal(10,7) YES NULL
longitude decimal(10,7) YES NULL

## ANALYSIS

Built on pandas, streamlit and tabulate.
Queries, charts and findings: not yet recorded. Add them here.
