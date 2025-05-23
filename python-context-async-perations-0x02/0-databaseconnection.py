import pyodbc

class DatabaseConnection:
    def __init__(self, db_name, conn):
        self.conn = conn
        self.db_name = db_name
        self.connection = None

    def connect(self):
        self.conn = pyodbc.connect(
            'DRIVER={ODBC Driver 18 for SQL Server};'
            'SERVER=localhost,1433;'
            'DATABASE=AirBnB_Clone;'
            'UID=sa;'
            'PWD=20252025aS@;'
            'Encrypt=yes;'
            'TrustServerCertificate=yes;'
        )
        print(f"Connecting to database: {self.db_name}")
        self.connection = True

    def disconnect(self):
        self.conn.close()
        print(f"Disconnecting from database: {self.db_name}")
        self.connection = False

    def execute_query(self, query):
        if not self.connection:
            raise Exception("Database not connected")
        else:
            print(f"Executing query: {query}")