"""
Simple test to connect to the database.
"""
import sqlite3
import os

# Get the absolute path of the database file
db_path = os.path.abspath("chatbot.db")
print(f"Database path: {db_path}")

# Test connecting to the database
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a simple test table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("Successfully connected to the database and created a test table!")
except Exception as e:
    print(f"Error connecting to database: {e}")