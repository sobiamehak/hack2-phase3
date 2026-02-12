# Test script to check if there are any import issues with the models
import sys
import os
sys.path.append('./backend')

try:
    print("Importing models...")
    from backend.models import User, Task, TaskCreate, TaskUpdate
    print("Models imported successfully")
    
    print("Creating a sample task...")
    sample_task = Task(
        id="test-id",
        title="Test Task",
        description="Test Description",
        completed=False,
        user_id="test-user-id"
    )
    print(f"Sample task created: {sample_task.title}")
    
    print("Checking database connection...")
    from backend.database import engine
    print(f"Engine created successfully: {engine}")
    
    from backend.database import get_session
    print("Session generator imported successfully")
    
    print("Checking auth module...")
    from backend.auth import get_current_user, verify_password
    print("Auth module imported successfully")
    
    print("\nAll imports successful! No obvious issues found.")
    
except Exception as e:
    print(f"Error during import/check: {e}")
    import traceback
    traceback.print_exc()