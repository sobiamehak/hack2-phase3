# Quickstart: Todo AI Chatbot

**Feature**: 004-todo-ai-chatbot
**Date**: 2026-02-11

## Prerequisites

- Python 3.11+
- pip
- An OpenRouter API key (or any OpenAI-compatible API)
- (Optional) PostgreSQL instance for production

## Setup

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies for this feature:
- `openai` (already present) — AI model client
- `slowapi` — rate limiting
- `python-json-logger` — structured JSON logging

### 2. Configure environment

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
```

Required variables:
```
OPENAI_API_KEY=your-openrouter-api-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=qwen/qwen-2.5-72b-instruct
DATABASE_URL=sqlite:///./chatbot.db
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
MAX_MESSAGE_HISTORY=20
RATE_LIMIT_USER_REQUESTS_PER_HOUR=100
RATE_LIMIT_BURST_CAPACITY=10
```

For PostgreSQL (production):
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### 3. Run database migrations

```bash
cd backend
alembic upgrade head
```

### 4. Start the server

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Verify

### Health check

```bash
curl http://localhost:8000/health
```

Expected: `{"status": "healthy"}`

### Register a user

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

Save the `access_token` and `user_id` from the response.

### Send a chat message

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{"message": "Add a task to buy groceries"}'
```

Expected: AI response confirming the task was added.

### List tasks via chat

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{"message": "Show me my tasks"}'
```

Expected: AI response listing all tasks.

## Validation Checklist

- [ ] Health endpoint returns 200
- [ ] User registration works
- [ ] Login returns JWT token
- [ ] Chat endpoint accepts messages and returns AI responses
- [ ] Tasks are created/listed/completed/deleted/updated via chat
- [ ] Conversation persists across multiple messages
- [ ] Server restart does not lose conversation history
- [ ] Rate limiting triggers after burst capacity exceeded
- [ ] Unauthenticated requests are rejected with 401
- [ ] User A cannot access User B's tasks via chat
