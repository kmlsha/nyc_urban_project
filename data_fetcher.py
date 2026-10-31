import requests
import pandas as pd
from database.db_config import get_connection

#API used for fetching the data from nyc gorvn -- sample data
URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
#Columns fetched form the api
SELECT = "unique_key,created_date,closed_date,due_date,agency,complaint_type,borough,status,latitude,longitude"
#Total size if the data lake
total=100000
#Batchs of data fetched at a time in a API call
batch_size=1000

def fetch_data():
    
    all_data = []
    conn = get_connection()

    #dynamically fetch data in batches
    for offset in range(0, total, batch_size):
        params = {
            "$select": SELECT,
            "$order": "created_date DESC, unique_key DESC",
            "$limit": batch_size,
            "$offset": offset,
        }

        response = requests.get(URL, params=params, timeout=30)
        batch = response.json()
        
        # no more rows in the response, break the loop
        if not batch:        
            break

        # push the current batch to the all_data list
        all_data.extend(batch)
        # print(batch)

        insert_query = """
        INSERT INTO service_requests
        (unique_key, created_date, closed_date, due_date, agency, complaint_type, borough, status, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor = conn.cursor()

       
        for i in batch:
            # print(i["unique_key"])
            cursor.execute(insert_query, (
                        i["unique_key"],
                        i.get("created_date"),
                        i.get("closed_date"),
                        i.get("due_date"),
                        i.get("agency"),
                        i.get("complaint_type"),
                        i.get("borough"),
                        i.get("status"),
                        i.get("latitude"),
                        i.get("longitude"),
                    ))
            conn.commit()
        # print(batch[0]['unique_key'])
        # print(batch[0]['created_date'])

        print(f"offset {offset}: total {len(all_data)}")   
    

def main():
    print("Going to fetch data using the API.")
    fetch_data()
    print("Data fetching completed.")

main()