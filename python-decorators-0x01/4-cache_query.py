import time
import sqlite3 
import functools
import pyodbc


def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = pyodbc.connect(
                'DRIVER={ODBC Driver 18 for SQL Server};'
                'SERVER=localhost,1433;'  
                'DATABASE=AirBnB_Clone;'
                'UID=sa;'
                'PWD=20252025aS@;'
                'Encrypt=yes;'
                'TrustServerCertificate=yes;'
            )
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper

query_cache = {}

def cache_query(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        query = args[0]  # Assuming the first argument is the query
        if query in query_cache:
            print("Using cached result")
            return query_cache[query]
        else:
            print("Executing query")
            result = func(conn, *args, **kwargs)
            query_cache[query] = result
            return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")