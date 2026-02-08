# hack2-phase3

## Todo Chatbot Application

A simple yet powerful todo chatbot that allows users to manage their tasks through natural language commands.

## Features

- Add tasks: "Add a task to buy groceries"
- List tasks: "Show my tasks" 
- Complete tasks: "Complete task [task_id]"
- Delete tasks: "Delete task [task_id]"

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/sobiamehak/hack2-phase3.git
cd hack2-phase3
```

2. Navigate to the backend directory:
```bash
cd chatbot/backend
```

3. Install dependencies:
```bash
pip install flask
```

4. Run the application:
```bash
python minimal_todo_chatbot.py
```

5. The server will start on `http://127.0.0.1:8000`

## API Endpoints

- `GET /health` - Health check
- `POST /api/{user_id}/chat` - Chat endpoint

## Environment Variables

Create a `.env` file in the backend directory with your configuration:
```env
OPENAI_API_KEY=your_openrouter_api_key_here
```

## Usage

Send POST requests to the chat endpoint with JSON payload:
```json
{
  "message": "Add a task to buy groceries"
}
```

## Commands Supported

- Add task: "Add task [task description]"
- List tasks: "Show my tasks"
- Complete task: "Complete task [task_id]"
- Delete task: "Delete task [task_id]"