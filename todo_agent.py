#!/usr/bin/env python3
"""
Todo Management Agent for connecting to the chatbot and managing tasks.
This agent connects to your existing chatbot and provides task management functionality
through the OpenRouter API.
"""

import os
import sys
import uuid
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path to access modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chatbot', 'backend'))

class TodoAgent:
    """
    Agent that connects to the existing chatbot API to manage tasks.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        
        # Generate a consistent user ID for this session
        self.user_id = str(uuid.uuid4())
        print(f"Initialized Todo Agent with user ID: {self.user_id}")
    
    def _make_request(self, endpoint: str, data: Dict[str, Any], method: str = "POST") -> Dict[str, Any]:
        """
        Make a request to the chatbot API.
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return {"error": str(e)}
    
    def add_task(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new task through the chatbot API.
        """
        message = f"Add a task: {title}"
        if description:
            message += f" Description: {description}"
            
        data = {
            "message": message
        }
        
        endpoint = f"/{self.user_id}/chat"
        result = self._make_request(endpoint, data)
        return result
    
    def list_tasks(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        List tasks through the chatbot API.
        """
        if status:
            message = f"Show me my {status} tasks"
        else:
            message = "Show me all my tasks"
            
        data = {
            "message": message
        }
        
        endpoint = f"/{self.user_id}/chat"
        result = self._make_request(endpoint, data)
        return result
    
    def complete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Complete a task through the chatbot API.
        """
        message = f"Complete the task with ID {task_id}"
        
        data = {
            "message": message
        }
        
        endpoint = f"/{self.user_id}/chat"
        result = self._make_request(endpoint, data)
        return result
    
    def update_task(self, task_id: str, title: Optional[str] = None, 
                   description: Optional[str] = None, completed: Optional[bool] = None) -> Dict[str, Any]:
        """
        Update a task through the chatbot API.
        """
        message_parts = [f"Update the task with ID {task_id}"]
        
        if title:
            message_parts.append(f"New title: {title}")
        if description:
            message_parts.append(f"New description: {description}")
        if completed is not None:
            status = "completed" if completed else "not completed"
            message_parts.append(f"Set as {status}")
        
        message = ". ".join(message_parts)
        
        data = {
            "message": message
        }
        
        endpoint = f"/{self.user_id}/chat"
        result = self._make_request(endpoint, data)
        return result
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """
        Delete a task through the chatbot API.
        """
        message = f"Delete the task with ID {task_id}"
        
        data = {
            "message": message
        }
        
        endpoint = f"/{self.user_id}/chat"
        result = self._make_request(endpoint, data)
        return result
    
    def chat(self, message: str) -> Dict[str, Any]:
        """
        Send a general chat message to the bot.
        """
        data = {
            "message": message
        }
        
        endpoint = f"/{self.user_id}/chat"
        result = self._make_request(endpoint, data)
        return result


def main():
    """
    Main function to demonstrate the Todo Agent functionality.
    """
    print("Todo Management Agent")
    print("=" * 30)
    
    # Initialize the agent
    agent = TodoAgent()
    
    print("\nAvailable commands:")
    print("1. add <title> [description] - Add a new task")
    print("2. list [all|pending|completed] - List tasks")
    print("3. complete <task_id> - Mark a task as completed")
    print("4. update <task_id> [title|description|status] - Update a task")
    print("5. delete <task_id> - Delete a task")
    print("6. chat <message> - Send a general message to the bot")
    print("7. quit - Exit the program")
    
    while True:
        try:
            command_input = input("\nEnter command: ").strip()
            
            if not command_input:
                continue
                
            parts = command_input.split(" ", 2)  # Split into at most 3 parts
            command = parts[0].lower()
            
            if command == "quit":
                print("Goodbye!")
                break
            
            elif command == "add":
                if len(parts) < 2:
                    print("Usage: add <title> [description]")
                    continue
                    
                title = parts[1]
                description = parts[2] if len(parts) > 2 else None
                
                result = agent.add_task(title, description)
                print(f"Result: {json.dumps(result, indent=2)}")
                
            elif command == "list":
                status = parts[1] if len(parts) > 1 else None
                result = agent.list_tasks(status)
                print(f"Result: {json.dumps(result, indent=2)}")
                
            elif command == "complete":
                if len(parts) < 2:
                    print("Usage: complete <task_id>")
                    continue
                    
                task_id = parts[1]
                result = agent.complete_task(task_id)
                print(f"Result: {json.dumps(result, indent=2)}")
                
            elif command == "update":
                if len(parts) < 2:
                    print("Usage: update <task_id> [title|description|status]")
                    continue
                    
                task_id = parts[1]
                update_info = parts[2] if len(parts) > 2 else ""
                
                # Simple parsing - in a real app you'd want more sophisticated parsing
                title = None
                description = None
                completed = None
                
                if "title:" in update_info.lower():
                    title_start = update_info.lower().find("title:") + 6
                    title = update_info[title_start:].strip()
                    
                if "description:" in update_info.lower():
                    desc_start = update_info.lower().find("description:") + 12
                    description = update_info[desc_start:].strip()
                    
                if "completed" in update_info.lower():
                    completed = True
                elif "not completed" in update_info.lower():
                    completed = False
                    
                result = agent.update_task(task_id, title, description, completed)
                print(f"Result: {json.dumps(result, indent=2)}")
                
            elif command == "delete":
                if len(parts) < 2:
                    print("Usage: delete <task_id>")
                    continue
                    
                task_id = parts[1]
                result = agent.delete_task(task_id)
                print(f"Result: {json.dumps(result, indent=2)}")
                
            elif command == "chat":
                if len(parts) < 2:
                    print("Usage: chat <message>")
                    continue
                    
                message = parts[1]
                result = agent.chat(message)
                print(f"Result: {json.dumps(result, indent=2)}")
                
            else:
                print(f"Unknown command: {command}")
                print("Available commands: add, list, complete, update, delete, chat, quit")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()