import requests
import json

# Test the backend API directly
BASE_URL = "http://127.0.0.1:8000"

# First, login to get a token
login_data = {
    "email": "test@example.com",
    "password": "password123"
}

print("Logging in to get token...")
login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"Login Status Code: {login_response.status_code}")

if login_response.status_code == 200:
    login_result = login_response.json()
    token = login_result.get("access_token")
    user_id = login_result.get("user_id")
    print(f"Login successful! Token: {token[:20]}...")
    print(f"User ID: {user_id}")
    
    # Create a test task using the token
    task_data = {
        "title": "Test task from API",
        "description": "This is a test task created via API",
        "completed": False
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("\nTesting task creation with token...")
    response = requests.post(f"{BASE_URL}/api/{user_id}/tasks/", json=task_data, headers=headers)

    print(f"Task Creation Status Code: {response.status_code}")
    print(f"Task Creation Response: {response.text}")

    if response.status_code == 200:
        print("Task created successfully!")
        task_response = response.json()
        print(f"Created task ID: {task_response['id']}")
    else:
        print("Failed to create task")
else:
    print("Login failed")

# Test chat endpoint (should work without authentication for now)
print("\nTesting chat endpoint...")
chat_data = {
    "message": "add task Learn NextJS"
}

# Use the known test user ID
test_user_id = "33c9c93a-6c85-4ada-9645-e8501132e7ab"
response = requests.post(f"{BASE_URL}/api/{test_user_id}/chat", json=chat_data)
print(f"Chat Status Code: {response.status_code}")
print(f"Chat Response: {response.text}")

# Test the chatbot action - simulate what would happen when the chatbot returns ADD_TASK
print("\nTesting task creation via chatbot workflow...")
chat_response = {
    "action": "ADD_TASK",
    "title": "Learn React"
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

task_data = {
    "title": chat_response["title"],
    "description": "",
    "completed": False
}

response = requests.post(f"{BASE_URL}/api/{user_id}/tasks/", json=task_data, headers=headers)
print(f"Chatbot Task Creation Status Code: {response.status_code}")
print(f"Chatbot Task Creation Response: {response.text}")

if response.status_code == 200:
    print("Task created successfully via chatbot workflow!")
    task_response = response.json()
    print(f"Created task ID: {task_response['id']}")
else:
    print("Failed to create task via chatbot workflow")