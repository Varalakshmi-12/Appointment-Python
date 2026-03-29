import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="Sarigama12@",
        database="clinic"
    )
    print("Connected successfully!")
except Exception as e:
    print("Error:", e)