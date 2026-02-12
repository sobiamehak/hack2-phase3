# Implementation Plan: Todo AI Chatbot

**Branch**: `004-todo-ai-chatbot` | **Date**: 2026-02-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-todo-ai-chatbot/spec.md`

## Summary

Replace the existing regex-based chatbot (`todo_chatbot_json.py`) with an
AI-powered conversational agent that uses OpenAI-compatible function calling
(via OpenRouter) to manage todo tasks through 5 structured MCP tools. Add
Conversation and Message models for persistent, database-driven context.
Integrate JWT authentication into the chat endpoint, add rate limiting, and
upgrade logging to structured JSON format.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.115.6, SQLModel 0.0.22, OpenAI SDK 1.57.4, slowapi, python-json-logger
**Storage**: SQLite (dev) / PostgreSQL via Neon (production), accessed via SQLAlchemy/SQLModel ORM
**Testing**: pytest with httpx (TestClient)
**Target Platform**: Linux server (Render/Railway) or Docker container
**Project Type**: Web application (backend focus for this feature)
**Performance Goals**: <5s response time per chat message (AI latency dependent)
**Constraints**: No in-memory state, ORM-only DB access, exactly 5 MCP tools, env-only secrets
**Scale/Scope**: Single backend service, multi-user, ~100 req/user/hour rate limit

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Gate | Status |
|---|-----------|------|--------|
| I | Stateless Architecture | No in-memory state; all data in DB | PASS — Conversation/Message models store all state in DB. No process-level caches. |
| II | Database-Driven Context | History fetched from DB per request; tool calls logged | PASS — Last 20 messages loaded from DB per chat request. All tool calls persisted as Message records. |
| III | Tool-Based AI Execution | AI uses 5 MCP tools only; no direct DB writes | PASS — 5 tools defined (add, list, complete, delete, update). Agent cannot bypass tool interface. |
| IV | Security First | user_id validation, ORM-only, env secrets, rate limiting | PASS — JWT auth on chat endpoint, SQLModel ORM only, secrets from env, slowapi rate limiting. |
| V | Clean Architecture | Modular separation, async-first, middleware for cross-cutting | PASS — Separate modules: models.py, mcp_tools.py, agent.py, chat_endpoints.py. All async. Auth/rate-limit as middleware/dependencies. |
| VI | Reliability & Scalability | Health checks, structured logging, graceful errors | PASS — Health endpoint exists. JSON logging via python-json-logger. Try/except with user-friendly errors. |

**Gate result**: ALL PASS — proceed to implementation.

## Project Structure

### Documentation (this feature)

```text
specs/004-todo-ai-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chat-api.md      # Phase 1 output
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py              # FastAPI app entry (MODIFY: add rate limiting)
├── models.py            # SQLModel models (MODIFY: add Conversation, Message)
├── database.py          # DB engine config (MODIFY: env-based DATABASE_URL)
├── auth.py              # JWT auth (existing, no changes)
├── auth_endpoints.py    # Auth routes (existing, no changes)
├── task_endpoints.py    # Task CRUD routes (existing, no changes)
├── chat_endpoints.py    # Chat route (REWRITE: AI agent integration)
├── mcp_tools.py         # NEW: 5 MCP tool functions
├── agent.py             # NEW: AI agent config and execution loop
├── logging_config.py    # Logging setup (MODIFY: structured JSON)
├── alembic/             # Migrations (ADD: new migration)
├── alembic.ini          # Alembic config (existing)
└── requirements.txt     # Dependencies (MODIFY: add slowapi, python-json-logger)

frontend/                # Existing Next.js frontend (no changes in this feature)
```

**Structure Decision**: Web application layout. Backend-only changes for this
feature. The existing `backend/` directory structure is preserved; new modules
(`mcp_tools.py`, `agent.py`) are added at the same level as existing modules.
No subdirectory nesting — the backend is flat-module, consistent with the
existing pattern.

## Architecture Overview

```
┌──────────────┐     POST /api/{user_id}/chat     ┌──────────────┐
│   Frontend   │ ──────────────────────────────────▶│  FastAPI App  │
│  (Next.js)   │ ◀──────────────────────────────────│              │
└──────────────┘     ChatResponse (JSON)           │  main.py     │
                                                    │  ├── auth    │
                                                    │  ├── rate    │
                                                    │  │   limit   │
                                                    │  └── routes  │
                                                    └──────┬───────┘
                                                           │
                                            ┌──────────────┼──────────────┐
                                            ▼              ▼              ▼
                                     ┌────────────┐ ┌────────────┐ ┌────────────┐
                                     │chat_endpts │ │task_endpts │ │auth_endpts │
                                     │  .py       │ │  .py       │ │  .py       │
                                     └─────┬──────┘ └────────────┘ └────────────┘
                                           │
                                           ▼
                                     ┌────────────┐
                                     │  agent.py  │ ◀── OpenAI SDK
                                     │            │     (OpenRouter)
                                     └─────┬──────┘
                                           │ tool calls
                                           ▼
                                     ┌────────────┐
                                     │mcp_tools.py│ ◀── 5 tools
                                     │            │     (add, list, complete,
                                     └─────┬──────┘      delete, update)
                                           │
                                           ▼
                                     ┌────────────┐
                                     │ database.py│ ◀── SQLModel ORM
                                     │ models.py  │     (SQLite / PostgreSQL)
                                     └────────────┘
```

### Chat Request Flow

1. **Request arrives** at `POST /api/{user_id}/chat`
2. **Rate limiter** checks user's request count (slowapi)
3. **JWT auth** validates token, extracts authenticated user_id
4. **Ownership check** confirms URL user_id matches JWT user_id
5. **Conversation lookup**: find or create Conversation for user
6. **Store user message** as Message(role="user")
7. **Load context**: fetch last 20 Messages ordered by created_at
8. **Build messages array** for OpenAI API (system prompt + history)
9. **Call AI model** via OpenAI SDK (OpenRouter)
10. **Tool call loop**: if model returns tool_calls:
    a. Parse tool name and arguments
    b. Execute MCP tool function (add/list/complete/delete/update)
    c. Store tool call as Message(role="tool")
    d. Send tool result back to model for final response
11. **Store assistant response** as Message(role="assistant")
12. **Return ChatResponse** with human-readable text + structured action

## Key Design Decisions

### D1: Tool Matching by Title (not by ID)

MCP tools match tasks by title substring rather than UUID. This is
because users communicate in natural language ("delete the groceries
task") and do not know task UUIDs. The AI agent extracts the task
title from the user's message and passes it to the tool.

**Risk**: Ambiguous matches when multiple tasks have similar titles.
**Mitigation**: Tools return an error if 0 or >1 tasks match, asking
the user to be more specific.

### D2: Single Tool Call Per Turn

The agent is configured to make at most one tool call per user
message. This simplifies the execution loop and prevents the AI from
chaining multiple destructive operations in one turn.

**Exception**: The AI may choose to call `list_tasks` before another
tool to disambiguate. This is handled by the standard tool call loop
(model can request multiple rounds).

### D3: System Prompt Design

The system prompt instructs the AI to:
- Always use the provided tools for task operations
- Never fabricate task data
- Ask for clarification when the user's intent is ambiguous
- Return concise, friendly responses
- Only operate on the current user's tasks

### D4: Message Storage Granularity

Every message is stored: user messages, assistant responses, AND tool
call results. This provides full auditability (FR-010) and allows the
conversation context to include tool results for better AI continuity.

## Complexity Tracking

> No constitution violations detected. No complexity justifications needed.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none)    | —          | —                                   |
