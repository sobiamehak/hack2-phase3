---
id: 3
title: Todo AI Chatbot Task Generation
stage: tasks
date: 2026-02-11
surface: agent
model: claude-opus-4-6
feature: 004-todo-ai-chatbot
branch: 004-todo-ai-chatbot
user: sobiamehak
command: /sp.tasks
labels: ["tasks", "implementation", "mcp-tools", "agent", "chat-endpoint"]
links:
  spec: specs/004-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-todo-ai-chatbot/tasks.md
tests:
  - none
---

## Prompt

/sp.tasks

Project:
Todo AI Chatbot – Backend Implementation Plan

Phase 1 – Database
1. Create SQLModel models (Task, Conversation, Message)
2. Configure Neon PostgreSQL connection
3. Setup Alembic migrations
4. Add indexes on user_id and conversation_id

Phase 2 – MCP Layer
5. Implement 5 MCP tool handlers
6. Add strict user ownership validation
7. Standardize JSON error format
8. Register tools in MCP server

Phase 3 – Agent Setup
9. Configure OpenAI client
10. Create system prompt
11. Enable tool calling
12. Implement run_agent logic

Phase 4 – API Layer
13. Implement chat endpoint
14. Fetch conversation history
15. Store messages persistently
16. Execute tool calls via MCP
17. Return structured response

Phase 5 – Security & Validation
18. Add input validation
19. Add rate limiting
20. Configure CORS
21. Secure environment variables

Phase 6 – Testing
22. Unit tests for all MCP tools
23. Integration test for chat endpoint
24. Database transaction tests
25. Tool calling behavior tests
26. E

## Response snapshot

Generated 44 tasks in specs/004-todo-ai-chatbot/tasks.md organized into 7 phases mapped to 3 user stories:

- Phase 1 (Setup): 3 tasks — dependencies, database config, structured logging
- Phase 2 (Foundational): 13 tasks — models (Conversation, Message), Alembic migration, 5 MCP tools, agent module (OpenAI client, system prompt, run_agent loop)
- Phase 3 (US1 - NL Task Management): 5 tasks — ChatRequest/Response models, endpoint rewrite, error handling, router registration, tool call logging
- Phase 4 (US2 - Context Persistence): 5 tasks — get_or_create_conversation, store_message, load_history (20-msg window), endpoint wiring, tool message persistence
- Phase 5 (US3 - Secure Access): 6 tasks — JWT auth, ownership validation, slowapi rate limiting, 429 handler, tool user isolation verification
- Phase 6 (Testing): 7 tasks — MCP tool unit tests, chat endpoint integration tests, auth/rate-limit tests
- Phase 7 (Polish): 5 tasks — .env.example, CORS update, DB error handling, input validation, quickstart validation

Parallel opportunities: Phase 1 (all 3), Phase 2 tools (3 parallel), Phase 4+5 parallel, Phase 6 tool tests (3 parallel), Phase 7 (2 parallel).

MVP scope: Phases 1-3 (21 tasks) deliver working single-message AI chatbot.

## Outcome

- ✅ Impact: 44 actionable tasks with file paths, dependency graph, parallel opportunities, and MVP-first strategy
- 🧪 Tests: 7 test tasks included (T033-T039) covering MCP tools, chat endpoint, auth, rate limiting
- 📁 Files: specs/004-todo-ai-chatbot/tasks.md
- 🔁 Next prompts: /sp.implement to execute tasks, or /sp.analyze for cross-artifact consistency check
- 🧠 Reflection: User's phase outline was technical; reorganized around user stories per SDD methodology while preserving all requested work items

## Evaluation notes (flywheel)

- Failure modes observed: User input was truncated at item 26 ("E"); inferred remaining testing tasks from context
- Graders run and results (PASS/FAIL): Format validation PASS — all 44 tasks have checkbox, ID, file paths; story labels on US phases only
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
