import requests
import json
from typing import Dict, Any, Optional
from todo_chatbot import TodoChatbot

class TodoAPIClient:
    """
    Client to connect the chatbot to the existing Todo API endpoints.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", user_id: str = None):
        self.base_url = base_url
        self.user_id = user_id
        self.chatbot = TodoChatbot()
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def set_user_id(self, user_id: str):
        """Set the user ID for API requests."""
        self.user_id = user_id
    
    def set_auth_token(self, token: str):
        """Set the authentication token for API requests."""
        self.headers["Authorization"] = f"Bearer {token}"
    
    def process_command(self, message: str) -> Dict[str, Any]:
        """
        Process a user message through the chatbot and execute the corresponding API call.
        
        Args:
            message: The user's natural language command
            
        Returns:
            The result of the API call or chatbot processing
        """
        # Process the message with the chatbot to get the action and data
        action_data = self.chatbot.process_message(message)
        action = action_data["action"].lower()
        data = action_data["data"]
        
        # Execute the appropriate API call based on the action
        if action == "add_task":
            return self.add_task(data)
        elif action == "delete_task":
            return self.delete_task(data)
        elif action == "update_task":
            return self.update_task(data)
        elif action == "complete_task":
            return self.complete_task(data)
        elif action == "get_tasks":
            return self.get_tasks(data)
        else:
            return {"error": "Invalid command", "original_message": message}
    
    def get_tasks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get all tasks for the user."""
        if not self.user_id:
            return {"error": "User ID not set"}
        
        try:
            url = f"{self.base_url}/api/{self.user_id}/tasks/"
            
            # Add status filter if provided
            params = {}
            if data.get("status_filter"):
                params["status_filter"] = data["status_filter"]
            
            response = requests.get(url, headers=self.headers, params=params)
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to get tasks: {str(e)}"}
    
    def add_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new task for the user."""
        if not self.user_id:
            return {"error": "User ID not set"}
        
        try:
            url = f"{self.base_url}/api/{self.user_id}/tasks/"
            payload = {
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "completed": False
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to add task: {str(e)}"}
    
    def delete_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a task for the user."""
        if not self.user_id:
            return {"error": "User ID not set"}
        
        try:
            # Find the task by ID or title
            task_id = data.get("task_id")
            
            # If task_id is not a UUID, we might need to find the task first
            # For now, assuming it's the task ID
            url = f"{self.base_url}/api/{self.user_id}/tasks/{task_id}"
            
            response = requests.delete(url, headers=self.headers)
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to delete task: {str(e)}"}
    
    def update_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task for the user."""
        if not self.user_id:
            return {"error": "User ID not set"}
        
        try:
            task_id = data.get("task_id")
            url = f"{self.base_url}/api/{self.user_id}/tasks/{task_id}"
            
            payload = {}
            if data.get("new_title"):
                payload["title"] = data["new_title"]
            if data.get("new_description"):
                payload["description"] = data["new_description"]
            
            response = requests.put(url, headers=self.headers, json=payload)
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to update task: {str(e)}"}
    
    def complete_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Toggle the completion status of a task."""
        if not self.user_id:
            return {"error": "User ID not set"}
        
        try:
            task_id = data.get("task_id")
            url = f"{self.base_url}/api/{self.user_id}/tasks/{task_id}/complete"
            
            response = requests.patch(url, headers=self.headers)
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Failed to complete task: {str(e)}"}


# Example usage
if __name__ == "__main__":
    # Initialize the client
    client = TodoAPIClient(base_url="http://localhost:8000", user_id="some-user-id")
    
    # Example commands
    commands = [
        "add task Learn NextJS",
        "show my tasks",
        "complete task Learn NextJS",
        "delete task Learn NextJS"
    ]
    
    for cmd in commands:
        print(f"Processing: {cmd}")
        result = client.process_command(cmd)
        print(f"Result: {json.dumps(result, indent=2)}")
        print("-" * 40)