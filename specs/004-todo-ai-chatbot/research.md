# Research: Todo AI Chatbot

**Feature**: 004-todo-ai-chatbot
**Date**: 2026-02-11

## R1: AI Agent Tool Calling — OpenAI-Compatible API via OpenRouter

**Decision**: Use OpenAI Python SDK's `chat.completions.create()` with
`tools` parameter for function calling, accessed through OpenRouter.

**Rationale**: The project uses OpenRouter (`OPENAI_BASE_URL=
https://openrouter.ai/api/v1`) with `qwen/qwen-2.5-72b-instruct`.
OpenRouter exposes an OpenAI-compatible API. The `openai` Python SDK
(already in `requirements.txt` at version 1.57.4) supports custom
`base_url`, making OpenRouter integration seamless. Function/tool
calling is the standard mechanism for the AI to invoke structured
operations.

**Alternatives considered**:
- **Anthropic MCP protocol (stdio/SSE transport)**: Overkill for
  in-process tool execution. MCP protocol is designed for
  inter-process tool servers, not for tools running in the same
  Python process. Would add unnecessary complexity.
- **LangChain agent**: Heavy dependency, unnecessary abstraction
  layer for 5 simple tools. The OpenAI SDK handles tool calling
  natively.
- **OpenAI Agents SDK (beta)**: Newer SDK with built-in agent
  loop, but adds an extra dependency and is less stable than the
  core `openai` SDK. The tool calling loop is simple enough to
  implement directly.

**Conclusion**: The 5 MCP tools will be implemented as Python async
functions, registered as OpenAI tool definitions (JSON schema), and
dispatched via a tool execution loop in the agent module. The "MCP"
naming convention is retained for the tool interface pattern (structured
input/output, stateless handlers, JSON responses) even though the
Anthropic MCP protocol transport is not used.

## R2: Database — SQLite vs PostgreSQL (Neon)

**Decision**: Keep SQLite as default for local development; support
PostgreSQL (Neon) via `DATABASE_URL` environment variable.

**Rationale**: The current codebase uses SQLite
(`sqlite:///./chatbot.db`). The constitution mandates PostgreSQL, and
the spec assumes migration to Neon. However, forcing PostgreSQL for
local development creates friction. SQLAlchemy/SQLModel abstracts the
database engine, so the same ORM code works with both.

**Approach**:
- Read `DATABASE_URL` from environment (fallback to SQLite).
- When `DATABASE_URL` starts with `postgresql://`, use asyncpg or
  psycopg2 driver.
- Alembic migrations already exist in `backend/alembic/`.
- New Conversation and Message models will be added to the existing
  migration chain.

**Alternatives considered**:
- **Force PostgreSQL only**: Blocks local dev without a PG instance.
- **Keep SQLite only**: Violates constitution Principle II.

## R3: Conversation State Management

**Decision**: One active conversation per user. New conversation
created on first message; reused for all subsequent messages.

**Rationale**: The spec (FR-006) says "create a new conversation
automatically when a user sends their first message, and reuse the
existing conversation for subsequent messages." A single-conversation
model is simplest and sufficient for a todo chatbot. Multi-conversation
support can be added later without schema changes (the Conversation
model already supports it).

**Context window**: Load last 20 messages (FR-005) ordered by
`created_at` descending, then reverse for chronological order before
sending to the AI agent.

## R4: Rate Limiting Strategy

**Decision**: Use `slowapi` library (built on `limits`) with
in-memory storage for rate limiting.

**Rationale**: The spec requires 100 requests per user per hour with
burst capacity of 10 (FR-008). `slowapi` is the standard FastAPI
rate limiting library. In-memory storage is acceptable because rate
limiting is best-effort — if the server restarts, rate limit counters
reset, which is an acceptable tradeoff for simplicity.

**Alternatives considered**:
- **Redis-backed rate limiting**: More robust but adds a dependency.
  Not justified for current scale.
- **Custom middleware**: Unnecessary when `slowapi` exists.

## R5: Structured Logging

**Decision**: Upgrade existing `logging_config.py` to emit structured
JSON logs using Python's built-in `logging` with a JSON formatter.

**Rationale**: Constitution Principle VI mandates structured JSON
logging. The current implementation uses plain-text format. A custom
JSON formatter can be applied without changing any `logger.info()`
call sites.

**Alternatives considered**:
- **structlog**: Powerful but heavy dependency for this use case.
- **python-json-logger**: Lightweight JSON formatter for stdlib
  logging. Good option — minimal dependency.

**Decision**: Use `python-json-logger` for minimal overhead.

## R6: Tool Response Structure

**Decision**: All MCP tools return a consistent JSON structure:
```json
{
  "success": true,
  "data": { ... },
  "message": "Human-readable description"
}
```
On error:
```json
{
  "success": false,
  "error": "Error description"
}
```

**Rationale**: Consistent structure allows the AI agent to parse
tool results reliably and generate appropriate user-facing responses.
The `message` field gives the AI a starting point for its response.
