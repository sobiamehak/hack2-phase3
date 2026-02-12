import os
from backend.database import DATABASE_URL
print(f"DATABASE_URL from database.py: {DATABASE_URL}")

# Also test directly
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL from env: {db_url}")

# Test if we can connect to the database directly
import sqlite3
db_path = os.path.abspath("chatbot.db")
print(f"Absolute path to database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables in database: {tables}")
    conn.close()
    print("Successfully connected to the database!")
except Exception as e:
    print(f"Error connecting to database: {e}")