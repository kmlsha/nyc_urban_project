import mysql.connector
import os 

def get_connection():
    
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 3306),
        database=os.getenv("DB_NAME")
    )
