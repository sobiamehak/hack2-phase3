# Todo Management Agent

This project contains a todo management agent that connects to your existing chatbot and manages tasks through the OpenRouter API.

## Features

- Connects to your existing chatbot API
- Add, list, update, complete, and delete tasks
- Natural language processing for task management
- Integration with OpenRouter API for AI processing

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your OpenRouter API key in the `.env` file:
   ```bash
   OPENAI_API_KEY=your-openrouter-api-key-here
   ```

3. Make sure your API key is from OpenRouter (you can get it from https://openrouter.ai/keys)

## Usage

Run the combined server and agent:

```bash
python run_todo_agent.py
```

This will:
1. Start the chatbot server in the background
2. Launch the todo agent interface
3. Allow you to manage tasks through natural language commands

## Available Commands

- `add <title> [description]` - Add a new task
- `list [all|pending|completed]` - List tasks (optional status filter)
- `complete <task_id>` - Mark a task as completed
- `update <task_id> [title|description|status]` - Update a task
- `delete <task_id>` - Delete a task
- `chat <message>` - Send a general message to the bot
- `quit` - Exit the program

## Example Usage

```
Enter command: add Buy groceries
Result: {"conversation_id": "...", "response": "I've added the task 'Buy groceries' for you.", "tool_calls": [...]}

Enter command: list all
Result: {"conversation_id": "...", "response": "Here are your tasks...", "tool_calls": [...]}

Enter command: complete 123e4567-e89b-12d3-a456-426614174000
Result: {"conversation_id": "...", "response": "Task marked as completed.", "tool_calls": [...]}
```

## Architecture

The system consists of:
- A FastAPI backend server that handles chat requests
- An AI agent that processes natural language and calls task management tools
- A database layer for storing tasks and conversations
- The todo agent that provides a command-line interface

## Troubleshooting

If you encounter issues:
1. Make sure your OpenRouter API key is valid
2. Check that the server starts properly
3. Verify that the database connection works
4. Look at the server logs for error messages