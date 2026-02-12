---
id: 2
title: Todo AI Chatbot Implementation Plan
stage: plan
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: 004-todo-ai-chatbot
branch: 004-todo-ai-chatbot
user: sobiamehak
command: /sp.plan
labels: ["plan", "architecture", "mcp-tools", "openai", "fastapi"]
links:
  spec: specs/004-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-todo-ai-chatbot/plan.md
  - specs/004-todo-ai-chatbot/research.md
  - specs/004-todo-ai-chatbot/data-model.md
  - specs/004-todo-ai-chatbot/contracts/chat-api.md
  - specs/004-todo-ai-chatbot/quickstart.md
tests:
  - none
---

## Prompt

/sp.plan

Project Name:
Todo AI Chatbot – FastAPI Backend (Stateless + MCP + OpenAI Agent)

Goal:
Strategically design and implement a production-ready AI-powered todo backend using FastAPI, PostgreSQL, OpenAI Agents SDK, and MCP tools.

Implementation Strategy:

Phase 1 – Architecture Planning
Phase 2 – Database Foundation
Phase 3 – MCP Tool Layer
Phase 4 – Agent Integration
Phase 5 – Chat API Layer
Phase 6 – Security & Reliability
Phase 7 – Testing & Optimization
Phase 8 – Deployment

Expected Outcome:
A scalable, secure, stateless AI-powered todo backend that safely manages tasks using structured MCP tool execution and persistent conversation history.

## Response snapshot

Generated complete implementation plan for Todo AI Chatbot with 5 artifacts:

1. **plan.md**: Full implementation plan with technical context (Python 3.11+, FastAPI, SQLModel, OpenAI SDK via OpenRouter), constitution check (all 6 principles PASS), project structure (backend flat-module pattern), architecture overview with chat request flow (12-step sequence), and 4 key design decisions (title-based tool matching, single tool call per turn, system prompt design, message storage granularity).

2. **research.md**: 6 research decisions — R1: OpenAI function calling via OpenRouter (not full MCP protocol); R2: SQLite dev / PostgreSQL prod via DATABASE_URL; R3: single conversation per user; R4: slowapi rate limiting; R5: python-json-logger for structured logging; R6: consistent tool response JSON structure.

3. **data-model.md**: 2 new entities (Conversation, Message) with relationships, indexes, and migration notes. Existing User and Task models preserved unchanged.

4. **contracts/chat-api.md**: Full API contract for POST /api/{user_id}/chat including request/response schemas, error codes (400/401/403/429/500/503), and all 5 MCP tool definitions with input/output schemas.

5. **quickstart.md**: Setup instructions, environment config, verification commands, and validation checklist.

Agent context (CLAUDE.md) updated with technology stack from plan.

## Outcome

- ✅ Impact: Complete architecture plan with all Phase 0 and Phase 1 artifacts ready for /sp.tasks
- 🧪 Tests: N/A (planning artifact)
- 📁 Files: plan.md, research.md, data-model.md, contracts/chat-api.md, quickstart.md
- 🔁 Next prompts: /sp.tasks to generate implementation tasks, then /sp.implement
- 🧠 Reflection: Key architectural decision was NOT using full MCP protocol transport — OpenAI function calling is simpler and sufficient for in-process tools. Tool matching by title substring (not UUID) is pragmatic for NL chatbot but has ambiguity risk.

## Evaluation notes (flywheel)

- Failure modes observed: None — all constitution gates passed, no NEEDS CLARIFICATION remaining
- Graders run and results (PASS/FAIL): Constitution check 6/6 PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
