# Test script to check the database connection
import os
import sys
sys.path.append('./backend')

from backend.database import DATABASE_URL, engine
from sqlalchemy import inspect

print(f"DATABASE_URL: {DATABASE_URL}")
print(f"Current working directory: {os.getcwd()}")

try:
    # Try to connect and inspect the database
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")
    
    if 'users' in tables:
        from backend.models import User
        from sqlmodel import select
        from backend.database import get_session
        
        # Try to get a session and query users
        for session in get_session():
            users = session.exec(select(User)).all()
            print(f"Users in database: {len(users)}")
            for user in users:
                print(f"  - {user.email} ({user.id})")
            break  # Just get the first session
    
except Exception as e:
    print(f"Error connecting to database: {e}")