import mysql.connector

def get_connection():
    
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        port=3306,
        database="urban_nyc_complaints"
    )
