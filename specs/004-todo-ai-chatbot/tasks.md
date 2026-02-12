# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/004-todo-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included — user requested testing phase explicitly.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3)
- Exact file paths included in all tasks

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependency updates and configuration changes required before any feature work.

- [ ] T001 [P] Add slowapi and python-json-logger to backend/requirements.txt
- [ ] T002 [P] Update backend/database.py to read DATABASE_URL from environment variable with SQLite fallback per research.md R2
- [ ] T003 [P] Update backend/logging_config.py to emit structured JSON logs using python-json-logger per research.md R5

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, tools, and agent infrastructure that MUST be complete before any user story.

**CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T004 Add Conversation model (id, user_id, created_at, updated_at) to backend/models.py per data-model.md
- [ ] T005 Add Message model (id, conversation_id, role, content, tool_call_id, tool_name, tool_args, created_at) to backend/models.py per data-model.md
- [ ] T006 Add conversations relationship to existing User model in backend/models.py (backref only, no column change)
- [ ] T007 Generate Alembic migration for Conversation and Message tables with indexes (idx_conv_user_id, idx_msg_conv_created) by running `alembic revision --autogenerate` in backend/
- [ ] T008 Create backend/mcp_tools.py with add_task tool: async function accepting (user_id, session, title, description?) returning standardized JSON response per contracts/chat-api.md
- [ ] T009 Add list_tasks tool to backend/mcp_tools.py: async function accepting (user_id, session, status_filter?) returning task list per contracts/chat-api.md
- [ ] T010 [P] Add complete_task tool to backend/mcp_tools.py: async function accepting (user_id, session, task_title) matching by title substring, returning updated task per contracts/chat-api.md
- [ ] T011 [P] Add delete_task tool to backend/mcp_tools.py: async function accepting (user_id, session, task_title) matching by title substring, returning confirmation per contracts/chat-api.md
- [ ] T012 [P] Add update_task tool to backend/mcp_tools.py: async function accepting (user_id, session, task_title, new_title?, new_description?) matching by title substring per contracts/chat-api.md
- [ ] T013 Add TOOL_DEFINITIONS list to backend/mcp_tools.py: OpenAI-format JSON schema for all 5 tools and a TOOL_DISPATCH dict mapping tool names to functions
- [ ] T014 Create backend/agent.py with OpenAI client initialization reading OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL from environment variables per research.md R1
- [ ] T015 Add SYSTEM_PROMPT constant to backend/agent.py instructing the AI to use provided tools for task operations, never fabricate data, ask for clarification when ambiguous, and only operate on current user's tasks per plan.md D3
- [ ] T016 Implement run_agent async function in backend/agent.py: accepts messages list and user_id, calls chat.completions.create with tools, executes tool call loop (parse tool_calls → dispatch via TOOL_DISPATCH → collect results → re-call model), returns final assistant message and tool results per plan.md chat flow steps 9-10

**Checkpoint**: Foundation ready — all 5 MCP tools functional, agent can process messages with tool calling. User story implementation can begin.

---

## Phase 3: User Story 1 — Natural Language Task Management (Priority: P1) MVP

**Goal**: User sends a natural language message, the AI agent interprets it, executes the correct task operation via MCP tools, and returns a human-readable response with structured result.

**Independent Test**: Send "Add a task to buy groceries" via POST /api/{user_id}/chat → verify task created and response confirms it.

### Implementation for User Story 1

- [ ] T017 [US1] Create ChatRequest Pydantic model (message: str, min 1 char, max 2000) and ChatResponse model (response: str, action: Optional[dict], conversation_id: str) in backend/chat_endpoints.py per contracts/chat-api.md
- [ ] T018 [US1] Rewrite POST /{user_id}/chat endpoint in backend/chat_endpoints.py: accept ChatRequest, build messages array with system prompt, call run_agent from agent.py, return ChatResponse per contracts/chat-api.md
- [ ] T019 [US1] Add error handling in backend/chat_endpoints.py: catch OpenAI API errors (timeout, auth failure, rate limit) and return user-friendly 500 response without exposing internals per spec.md edge cases
- [ ] T020 [US1] Register chat router in backend/main.py (verify existing registration, ensure prefix is /api) and remove import of old TodoChatbotJSON from backend/chat_endpoints.py
- [ ] T021 [US1] Add tool call logging in backend/agent.py run_agent function: log tool name, arguments, and result using logger per FR-010

**Checkpoint**: US1 complete — single-message AI chat works. User can add/list/complete/delete/update tasks via natural language. Messages are not yet persisted across requests.

---

## Phase 4: User Story 2 — Conversation Context Persistence (Priority: P2)

**Goal**: Conversation history persisted in database. AI agent receives last 20 messages as context. Multi-turn conversations work. Server restart does not lose history.

**Independent Test**: Send "Add task buy milk", then send "Delete that one" → verify context resolves "that one" to the milk task.

### Implementation for User Story 2

- [ ] T022 [US2] Implement get_or_create_conversation async function in backend/chat_endpoints.py: query Conversation by user_id, create new if none exists, return Conversation instance per FR-006
- [ ] T023 [US2] Implement store_message async function in backend/chat_endpoints.py: create Message record with role, content, and optional tool metadata, commit to DB per FR-004
- [ ] T024 [US2] Implement load_conversation_history async function in backend/chat_endpoints.py: fetch last 20 Messages for conversation ordered by created_at DESC then reverse for chronological order per FR-005 and research.md R3
- [ ] T025 [US2] Update POST /{user_id}/chat in backend/chat_endpoints.py: call get_or_create_conversation, store user message, load history, pass history to run_agent, store assistant response and tool messages, include conversation_id in ChatResponse
- [ ] T026 [US2] Update run_agent in backend/agent.py: store each tool call result as Message(role="tool") via callback or return value, ensuring full message chain is persisted per plan.md D4

**Checkpoint**: US2 complete — multi-turn conversations work, context persists across requests, server restart preserves all history.

---

## Phase 5: User Story 3 — Secure User-Scoped Access (Priority: P3)

**Goal**: JWT authentication enforced on chat endpoint. user_id ownership validated. Rate limiting active. Complete user data isolation.

**Independent Test**: Create tasks for User A and User B via chat, verify User A cannot see User B's tasks.

### Implementation for User Story 3

- [ ] T027 [US3] Add JWT authentication dependency (get_current_user from auth.py) to POST /{user_id}/chat endpoint in backend/chat_endpoints.py per FR-007
- [ ] T028 [US3] Add user_id ownership validation in backend/chat_endpoints.py: compare URL user_id with JWT token sub claim, return 403 if mismatch per contracts/chat-api.md error responses
- [ ] T029 [US3] Configure slowapi rate limiter in backend/main.py: create Limiter instance with key_func extracting user_id from path, set default limit from RATE_LIMIT_USER_REQUESTS_PER_HOUR env var per FR-008 and research.md R4
- [ ] T030 [US3] Apply rate limit decorator to POST /{user_id}/chat endpoint in backend/chat_endpoints.py with burst capacity from RATE_LIMIT_BURST_CAPACITY env var
- [ ] T031 [US3] Add 429 error handler in backend/main.py for RateLimitExceeded exception returning JSON error per contracts/chat-api.md
- [ ] T032 [US3] Verify all MCP tools in backend/mcp_tools.py filter queries by user_id parameter — ensure no tool can return or modify another user's data

**Checkpoint**: US3 complete — authentication, authorization, rate limiting, and user isolation all enforced.

---

## Phase 6: Testing

**Purpose**: Verify correctness of MCP tools, chat flow, and security boundaries.

- [ ] T033 [P] Create backend/tests/test_mcp_tools.py: unit test add_task tool — verify task created in DB with correct user_id and title
- [ ] T034 [P] Add unit tests to backend/tests/test_mcp_tools.py: test list_tasks with status_filter (all, completed, incomplete), verify user isolation
- [ ] T035 [P] Add unit tests to backend/tests/test_mcp_tools.py: test complete_task, delete_task, update_task — verify title matching, error on no match, error on ambiguous match
- [ ] T036 Create backend/tests/test_chat_endpoint.py: integration test POST /api/{user_id}/chat with mocked OpenAI API — verify request/response schema matches contracts/chat-api.md
- [ ] T037 Add integration test to backend/tests/test_chat_endpoint.py: verify conversation is created on first message and reused on subsequent messages
- [ ] T038 Add integration test to backend/tests/test_chat_endpoint.py: verify unauthenticated request returns 401, mismatched user_id returns 403
- [ ] T039 Add integration test to backend/tests/test_chat_endpoint.py: verify rate limiting returns 429 after exceeding limit

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Production readiness improvements.

- [ ] T040 [P] Create backend/.env.example with all required environment variables (placeholder values only, no real secrets) per FR-013 and quickstart.md
- [ ] T041 [P] Update CORS configuration in backend/main.py: read FRONTEND_URL from environment variable for allow_origins instead of wildcard "*"
- [ ] T042 Add database connection error handling in backend/chat_endpoints.py: catch SQLAlchemy connection errors, return 503 Service Unavailable per spec.md edge cases
- [ ] T043 Validate empty/invalid message in POST /{user_id}/chat before calling agent: return 400 with clear error message per contracts/chat-api.md
- [ ] T044 Run quickstart.md validation checklist end-to-end: start server, register user, login, send chat messages for all 5 operations, verify responses

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on T001 (requirements) and T002 (database config)
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion (models, tools, agent)
- **User Story 2 (Phase 4)**: Depends on Phase 3 (chat endpoint exists)
- **User Story 3 (Phase 5)**: Depends on Phase 3 (chat endpoint exists); can run in parallel with Phase 4
- **Testing (Phase 6)**: Depends on Phase 5 (all features implemented)
- **Polish (Phase 7)**: Depends on Phase 5 (all features implemented)

### Within Each Phase

- Models before migration (T004-T006 before T007)
- Tools before agent (T008-T013 before T014-T016)
- Agent before endpoint (T014-T016 before T017-T018)
- Tasks marked [P] can run in parallel within their phase

### Parallel Opportunities

```text
Phase 1 — All 3 tasks run in parallel:
  T001 (requirements) | T002 (database.py) | T003 (logging)

Phase 2 — Tool implementations in parallel after T008-T009:
  T010 (complete_task) | T011 (delete_task) | T012 (update_task)

Phase 5 + Phase 4 can run in parallel:
  US2 (T022-T026) | US3 (T027-T032) — different concerns, minimal file overlap

Phase 6 — Tool tests in parallel:
  T033 | T034 | T035

Phase 7 — Independent polish tasks:
  T040 (.env.example) | T041 (CORS)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T016)
3. Complete Phase 3: User Story 1 (T017-T021)
4. **STOP and VALIDATE**: Send chat messages, verify AI responds with correct tool actions
5. Deploy/demo if ready — single-message AI chatbot works

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP demo
3. Add User Story 2 → Multi-turn conversations work
4. Add User Story 3 → Security and rate limiting enforced
5. Testing + Polish → Production ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Existing backend/auth.py, backend/auth_endpoints.py, backend/task_endpoints.py require NO changes
- Old regex chatbot files (backend/todo_chatbot.py, backend/todo_chatbot_json.py) will be superseded — removed in T020 via import cleanup
- All MCP tools receive user_id as parameter to enforce data isolation at the tool level
