import sqlite3
import functools
import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=localhost,1433;'  
    'DATABASE=AirBnB_Clone;'
    'UID=sa;'
    'PWD=20252025aS@;'
    'Encrypt=yes;'
    'TrustServerCertificate=yes;'
)


#### decorator to lof SQL queries

def log_queries(func):
    @functools.wraps(func)
    def wrapper(query):
        print(f"Executing query: {query}")
        result = func(query)
        return result
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
