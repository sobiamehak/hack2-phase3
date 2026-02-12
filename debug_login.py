import requests
import json

# Test the backend API directly
BASE_URL = "http://127.0.0.1:8000"

# First, try to get all users to see what's in the DB
print("Getting all users...")
users_response = requests.get(f"{BASE_URL}/users")
print(f"Users Status Code: {users_response.status_code}")
print(f"Users Response: {users_response.text}")

# Try to login to get a token
login_data = {
    "email": "test@example.com",
    "password": "password123"
}

print("\nLogging in to get token...")
login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"Login Status Code: {login_response.status_code}")
print(f"Login Response: {login_response.text}")