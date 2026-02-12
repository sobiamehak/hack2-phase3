# API Contract: Chat Endpoint

**Feature**: 004-todo-ai-chatbot
**Date**: 2026-02-11

## POST /api/{user_id}/chat

Send a natural language message to the AI todo assistant.

### Path Parameters

| Parameter | Type   | Required | Description             |
|-----------|--------|----------|-------------------------|
| user_id   | string | yes      | UUID of the requesting user |

### Headers

| Header        | Value             | Required | Description              |
|---------------|-------------------|----------|--------------------------|
| Authorization | Bearer {token}    | yes      | JWT access token         |
| Content-Type  | application/json  | yes      | Request body format      |

### Request Body

```json
{
  "message": "Add a task to buy groceries"
}
```

| Field   | Type   | Required | Constraints          | Description              |
|---------|--------|----------|----------------------|--------------------------|
| message | string | yes      | min 1 char, max 2000 | Natural language message  |

### Success Response — 200 OK

```json
{
  "response": "I've added a new task: \"Buy groceries\".",
  "action": {
    "tool": "add_task",
    "result": {
      "success": true,
      "data": {
        "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "title": "Buy groceries",
        "completed": false
      },
      "message": "Task 'Buy groceries' created successfully."
    }
  },
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

| Field            | Type   | Description                                      |
|------------------|--------|--------------------------------------------------|
| response         | string | Human-readable AI-generated response             |
| action           | object | Structured tool call result (null if no tool called) |
| action.tool      | string | Name of the MCP tool that was invoked            |
| action.result    | object | Tool execution result                            |
| conversation_id  | string | UUID of the conversation                         |

### Error Responses

**400 Bad Request** — Empty or invalid message
```json
{
  "detail": "Message is required and must be between 1 and 2000 characters"
}
```

**401 Unauthorized** — Missing or invalid JWT token
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden** — user_id does not match authenticated user
```json
{
  "detail": "Not authorized to access this user's chat"
}
```

**429 Too Many Requests** — Rate limit exceeded
```json
{
  "detail": "Rate limit exceeded. Maximum 100 requests per hour."
}
```

**500 Internal Server Error** — AI agent or database failure
```json
{
  "detail": "Chat service temporarily unavailable. Please try again."
}
```

**503 Service Unavailable** — Database connection failure
```json
{
  "detail": "Service temporarily unavailable"
}
```

## GET /health

Health check endpoint for monitoring.

### Response — 200 OK

```json
{
  "status": "healthy"
}
```

---

## MCP Tool Definitions (Internal)

These are the 5 tool definitions registered with the AI agent.
They are not HTTP endpoints — they are internal function calls.

### add_task

**Parameters**:
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional)"
}
```

**Returns**:
```json
{
  "success": true,
  "data": { "id": "uuid", "title": "...", "completed": false },
  "message": "Task '...' created successfully."
}
```

### list_tasks

**Parameters**:
```json
{
  "status_filter": "string (optional: 'all', 'completed', 'incomplete')"
}
```

**Returns**:
```json
{
  "success": true,
  "data": [
    { "id": "uuid", "title": "...", "completed": false },
    { "id": "uuid", "title": "...", "completed": true }
  ],
  "message": "Found 2 tasks."
}
```

### complete_task

**Parameters**:
```json
{
  "task_title": "string (required, matches by title substring)"
}
```

**Returns**:
```json
{
  "success": true,
  "data": { "id": "uuid", "title": "...", "completed": true },
  "message": "Task '...' marked as complete."
}
```

### delete_task

**Parameters**:
```json
{
  "task_title": "string (required, matches by title substring)"
}
```

**Returns**:
```json
{
  "success": true,
  "data": { "id": "uuid", "title": "..." },
  "message": "Task '...' deleted."
}
```

### update_task

**Parameters**:
```json
{
  "task_title": "string (required, identifies task by title substring)",
  "new_title": "string (optional, 1-200 chars)",
  "new_description": "string (optional)"
}
```

**Returns**:
```json
{
  "success": true,
  "data": { "id": "uuid", "title": "...", "completed": false },
  "message": "Task updated successfully."
}
```

### Tool Error Response (all tools)

```json
{
  "success": false,
  "error": "No task found matching 'xyz'"
}
```
