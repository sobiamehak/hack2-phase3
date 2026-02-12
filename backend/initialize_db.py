"""
Script to initialize the database and create tables.
"""
from sqlmodel import SQLModel, create_engine
from models import User, Task, Conversation, Message
import uuid
from datetime import datetime
from sqlmodel import Session
import os

# Use the correct path for the database file
current_dir = os.getcwd()
db_path = os.path.join(current_dir, "chatbot.db")
DATABASE_URL = f"sqlite:///{db_path}"

print(f"Using database URL: {DATABASE_URL}")

def create_tables():
    """Create all database tables."""
    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")

def create_test_user():
    """Create a test user for development purposes."""
    engine = create_engine(DATABASE_URL)
    
    # Create a test user with a simple password hash (for development only)
    # In production, use proper password hashing
    test_user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="password123",  # Plain text for development
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    with Session(engine) as session:
        # Check if test user already exists
        existing_user = session.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print(f"Test user already exists with ID: {existing_user.id}")
            return existing_user.id
        
        session.add(test_user)
        session.commit()
        session.refresh(test_user)
        print(f"Test user created with ID: {test_user.id}")
        return test_user.id

if __name__ == "__main__":
    create_tables()
    user_id = create_test_user()
    print(f"Database initialized successfully! Test user ID: {user_id}")