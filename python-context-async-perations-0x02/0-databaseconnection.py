import pyodbc

class DatabaseConnection:
    def __init__(self, db_name, conn):
        self.conn = conn
        self.db_name = db_name
        self.connection = None

    def __enter__(self):
        print(f"Connecting to database: {self.db_name}")
        return self
    
    def connect(self):
        try:
            self.conn = pyodbc.connect(
                'DRIVER={ODBC Driver 18 for SQL Server};'
                'SERVER=localhost,1433;'
                'DATABASE=AirBnB_Clone;'
                'UID=sa;'
                'PWD=20252025aS@;'
                'Encrypt=yes;'
                'TrustServerCertificate=yes;'
            )
            self.connection = True
        except pyodbc.Error as e:
            print(f"Error connecting to database: {e}")

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print(f"An error occurred: {exc_value}")
        self.__disconnect()
        print("Exit method called")


    def __disconnect(self):
        print(f"Disconnecting from database: {self.db_name}")
        self.conn.close()
        self.connection = False

    def execute_query(self, query):
        if not self.connection:
            raise Exception("Database not connected")
        else:
            print(f"Executing query: {query}")

with DatabaseConnection("AirBnB_Clone", None) as db:
    db.connect()
    db.execute_query("SELECT * FROM users")
    print("Query executed successfully")

    