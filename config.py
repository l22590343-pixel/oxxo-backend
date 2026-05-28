import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host="roundhouse.proxy.rlwy.net",
        port=55009,
        database="railway",
        user="postgres",
        password="nTfRMgXhodgPzxVctaoiGnmFVofFUoCJ"
    )
    return conn
