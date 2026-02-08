import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import uuid
from datetime import datetime
import urllib.parse
import re

# Simple in-memory storage
users = {}
conversations = {}
messages = {}
tasks = {}

class TodoChatbotHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "version": "1.0.0", "service": "Todo Chatbot API"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        # Parse the path to extract user_id
        path_parts = self.path.split('/')
        if len(path_parts) >= 4 and path_parts[1] == 'api' and path_parts[3] == 'chat':
            user_id = path_parts[2]
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message_text = data.get('message', '')
            
            # Create user if doesn't exist
            if user_id not in users:
                users[user_id] = {"id": user_id, "created_at": datetime.now().isoformat()}
            
            # Create conversation if doesn't exist
            conversation_id = data.get('conversation_id')
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                conversations[conversation_id] = {
                    "id": conversation_id,
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            
            # Store user message
            message_id = str(uuid.uuid4())
            messages[message_id] = {
                "id": message_id,
                "conversation_id": conversation_id,
                "user_id": user_id,
                "role": "user",
                "content": message_text,
                "created_at": datetime.now().isoformat()
            }
            
            # Process the message and generate response
            response_text, tool_calls = self.process_todo_request(message_text, user_id)
            
            # Store AI response
            ai_message_id = str(uuid.uuid4())
            messages[ai_message_id] = {
                "id": ai_message_id,
                "conversation_id": conversation_id,
                "user_id": user_id,
                "role": "assistant",
                "content": response_text,
                "tool_calls": tool_calls,
                "created_at": datetime.now().isoformat()
            }
            
            # Update conversation timestamp
            conversations[conversation_id]["updated_at"] = datetime.now().isoformat()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "conversation_id": conversation_id,
                "response": response_text,
                "tool_calls": tool_calls
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def process_todo_request(self, message, user_id):
        message_lower = message.lower()
        tool_calls = []
        
        if "add task" in message_lower or "add a task" in message_lower or "create task" in message_lower:
            # Extract task description
            task_desc = re.sub(r'^(add task|add a task|create task)\s*', '', message_lower).strip()
            if not task_desc:
                task_desc = "unnamed task"
            
            task_id = str(uuid.uuid4())
            tasks[task_id] = {
                "id": task_id,
                "user_id": user_id,
                "title": task_desc,
                "description": task_desc,
                "completed": False,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            tool_calls.append({
                "name": "add_task",
                "arguments": {"title": task_desc},
                "result": {"success": True, "task_id": task_id, "message": f"Task '{task_desc}' added successfully"}
            })
            
            return f"I've added the task '{task_desc}' to your list.", tool_calls
        
        elif "list tasks" in message_lower or "show tasks" in message_lower or "my tasks" in message_lower:
            user_tasks = [task for task in tasks.values() if task["user_id"] == user_id]
            if not user_tasks:
                return "You don't have any tasks yet. You can add tasks by saying 'add task [task description]'.", tool_calls
            
            task_list = "\n".join([f"- [{task['id']}] {task['title']} ({'completed' if task['completed'] else 'pending'})" for task in user_tasks])
            return f"Here are your tasks:\n{task_list}", tool_calls
        
        elif "complete task" in message_lower or "finish task" in message_lower:
            # Extract task ID or title
            task_identifier = re.sub(r'^(complete task|finish task)\s*', '', message_lower).strip()
            
            # Find task by ID or title
            target_task = None
            for task_id, task in tasks.items():
                if task["user_id"] == user_id:
                    if task_id == task_identifier or task["title"].lower() == task_identifier:
                        target_task = task
                        break
            
            if target_task:
                target_task["completed"] = True
                target_task["updated_at"] = datetime.now().isoformat()
                
                tool_calls.append({
                    "name": "complete_task",
                    "arguments": {"task_id": target_task["id"]},
                    "result": {"success": True, "message": f"Task '{target_task['title']}' marked as completed"}
                })
                
                return f"I've marked the task '{target_task['title']}' as completed.", tool_calls
            else:
                return f"Sorry, I couldn't find a task with identifier '{task_identifier}'. Please check the task ID or name.", tool_calls
        
        elif "delete task" in message_lower:
            # Extract task ID or title
            task_identifier = re.sub(r'^delete task\s*', '', message_lower).strip()
            
            # Find task by ID or title
            target_task = None
            task_id_to_delete = None
            for task_id, task in tasks.items():
                if task["user_id"] == user_id:
                    if task_id == task_identifier or task["title"].lower() == task_identifier:
                        target_task = task
                        task_id_to_delete = task_id
                        break
            
            if target_task and task_id_to_delete:
                del tasks[task_id_to_delete]
                
                tool_calls.append({
                    "name": "delete_task",
                    "arguments": {"task_id": task_id_to_delete},
                    "result": {"success": True, "message": f"Task '{target_task['title']}' deleted successfully"}
                })
                
                return f"I've deleted the task '{target_task['title']}'.", tool_calls
            else:
                return f"Sorry, I couldn't find a task with identifier '{task_identifier}'. Please check the task ID or name.", tool_calls
        
        else:
            return "Hi! I'm your todo chatbot. You can ask me to:\n- Add a task: 'Add task buy groceries'\n- List tasks: 'Show my tasks'\n- Complete a task: 'Complete task [task_id_or_name]'\n- Delete a task: 'Delete task [task_id_or_name]'", tool_calls

if __name__ == "__main__":
    server = HTTPServer(('127.0.0.1', 8000), TodoChatbotHandler)
    print("Todo Chatbot Server running on http://127.0.0.1:8000")
    print("Endpoints:")
    print("- GET /health - Health check")
    print("- POST /api/{user_id}/chat - Chat endpoint")
    server.serve_forever()