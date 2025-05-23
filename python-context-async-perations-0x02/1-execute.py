class ExcuteQuery:
    def __init__(self, query):
        self.query = query
    def __enter__(self):
        print(f"Preparing to execute query: {self.query}")
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            print(f"An error occurred: {exc_value}")
        print("Cleaning up after query execution")

    def execute(self):
        print(f"Executing query: {self.query}")
        # Simulate a database operation
        return f"Result of {self.query}"