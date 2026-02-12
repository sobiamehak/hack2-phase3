import requests
import json

# Base URL for the backend
BASE_URL = "http://localhost:8000"

def register_user():
    """Register a new user"""
    register_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print("Register Response:", response.status_code, response.json())
    return response

def login_user():
    """Login the user and get token"""
    login_data = {
        "email": "test@example.com", 
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print("Login Response:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        print("Login Success!")
        print("Access Token:", data.get("access_token"))
        print("User ID:", data.get("user_id"))
        print("Email:", data.get("email"))
        return data
    else:
        print("Login Failed:", response.text)
        return None

def test_protected_endpoint(user_id, token):
    """Test a protected endpoint with the token"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try to get tasks for the user
    response = requests.get(f"{BASE_URL}/api/{user_id}/tasks/", headers=headers)
    print("Protected Endpoint Test:", response.status_code)
    if response.status_code == 200:
        print("Success! Got tasks:", response.json())
    else:
        print("Failed to access protected endpoint:", response.text)
    return response

def test_add_task(user_id, token):
    """Test adding a task"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    task_data = {
        "title": "Exam preparation",
        "description": "Study for upcoming exams",
        "completed": False
    }
    
    response = requests.post(f"{BASE_URL}/api/{user_id}/tasks/", json=task_data, headers=headers)
    print("Add Task Response:", response.status_code)
    if response.status_code == 200:
        print("Task added successfully:", response.json())
    else:
        print("Failed to add task:", response.text)
    return response

if __name__ == "__main__":
    print("Testing backend authentication flow...")
    
    # Register user (might fail if user already exists, which is OK)
    print("\n1. Registering user...")
    register_user()
    
    # Login user to get token
    print("\n2. Logging in user...")
    auth_data = login_user()
    
    if auth_data:
        user_id = auth_data["user_id"]
        token = auth_data["access_token"]
        
        print(f"\n3. Testing with User ID: {user_id}")
        
        # Test protected endpoint
        print("\n4. Testing protected endpoint...")
        test_protected_endpoint(user_id, token)
        
        # Test adding a task
        print("\n5. Testing add task...")
        test_add_task(user_id, token)
        
        print(f"\nSUCCESS! You can now use:")
        print(f"User ID: {user_id}")
        print(f"Token: {token}")
        print("Store these in your frontend's localStorage for API calls.")
    else:
        print("Failed to authenticate user. Please check if the backend is running on port 8000.")