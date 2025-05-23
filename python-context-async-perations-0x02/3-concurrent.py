import aiosqlite
import asyncio

DB_PATH = "users.db"

# Sample setup: creating a table and inserting dummy data (only once)
async def setup_database():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER
            );
        """)
        await db.execute("DELETE FROM users;")  # Clear table if rerunning
        await db.executemany(
            "INSERT INTO users (name, age) VALUES (?, ?);",
            [
                ("Alice", 30),
                ("Bob", 45),
                ("Charlie", 22),
                ("Diana", 50),
            ]
        )
        await db.commit()

# Function to fetch all users
async def async_fetch_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users;") as cursor:
            users = await cursor.fetchall()
            print("\n👥 All Users:")
            for user in users:
                print(user)
            return users

# Function to fetch users older than 40
async def async_fetch_older_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE age > 40;") as cursor:
            users = await cursor.fetchall()
            print("\n🧓 Users older than 40:")
            for user in users:
                print(user)
            return users

# Run both fetches concurrently
async def fetch_concurrently():
    await setup_database()  # Setup DB with sample data
    await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

# Run it
if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
