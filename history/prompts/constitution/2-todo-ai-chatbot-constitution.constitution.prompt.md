---
id: 2
title: Todo AI Chatbot Constitution
stage: constitution
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: sobiamehak
command: /sp.constitution
labels: ["constitution", "fastapi", "mcp", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

/sp.constitution

Project Name:
Todo AI Chatbot – FastAPI Backend

Mission:
Build a stateless, scalable, and secure FastAPI backend that enables natural language todo management using OpenAI Agents SDK integrated with MCP tools.

Core Principles:

1. Stateless Architecture
- No in-memory state
- All conversations and messages stored in database
- Server restart-safe

2. Database-Driven Context
- Conversation history fetched from PostgreSQL on every request
- All tool calls logged and persisted
- User-scoped data isolation

3. Tool-Based AI Execution
- AI must not modify database directly
- All task operations must go through MCP tools
- Exactly 5 tools: add, list, complete, delete, update

4. Security First
- Strict user_id validation
- ORM-based database access (no raw SQL)
- Secrets only via environment variables
- Rate limiting on chat endpoint

5. Clean Architecture
- Modular folder structure
- Separation of concerns (API, Agent, MCP, Models)
- Async-first FastAPI design

6. Reliability & Scalability
-

## Response snapshot

Created constitution v1.0.0 for Todo AI Chatbot – FastAPI Backend with 6 core principles: Stateless Architecture, Database-Driven Context, Tool-Based AI Execution, Security First, Clean Architecture, Reliability & Scalability. Added Technology Stack & Constraints section (Python 3.11+, FastAPI, SQLAlchemy/SQLModel, PostgreSQL, OpenAI Agents SDK, MCP). Added Development Workflow section (branching, testing, code review, conventional commits). Added Governance section with SemVer amendment policy. All template placeholders resolved. No dependent templates required updates. Sync Impact Report embedded as HTML comment.

## Outcome

- ✅ Impact: Constitution v1.0.0 established — all 6 principles codified with testable MUST/MUST NOT rules
- 🧪 Tests: N/A (documentation artifact)
- 📁 Files: .specify/memory/constitution.md (created from template)
- 🔁 Next prompts: /sp.specify to create feature spec, /sp.plan for architecture planning
- 🧠 Reflection: User's 6th principle was cut off; completed Reliability & Scalability based on project context (health checks, structured logging, graceful error handling)

## Evaluation notes (flywheel)

- Failure modes observed: User input truncated at principle 6; inferred reasonable defaults
- Graders run and results (PASS/FAIL): Manual validation PASS — no unresolved placeholders, all dates ISO, all principles declarative and testable
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
