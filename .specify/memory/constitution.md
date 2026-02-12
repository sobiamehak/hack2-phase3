<!--
Sync Impact Report
===================
Version change: 0.0.0 (template) → 1.0.0
Modified principles: N/A (initial population from template)
Added sections:
  - 6 Core Principles (Stateless Architecture, Database-Driven Context,
    Tool-Based AI Execution, Security First, Clean Architecture,
    Reliability & Scalability)
  - Technology Stack & Constraints
  - Development Workflow
  - Governance
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md — ✅ no updates needed
    (Constitution Check section is dynamic; will be filled at plan time)
  - .specify/templates/spec-template.md — ✅ no updates needed
    (generic structure, no principle-specific coupling)
  - .specify/templates/tasks-template.md — ✅ no updates needed
    (phase structure accommodates all 6 principles)
Follow-up TODOs: None
-->

# Todo AI Chatbot – FastAPI Backend Constitution

## Core Principles

### I. Stateless Architecture

- The backend MUST NOT hold in-memory conversational or
  application state between requests.
- All conversations and messages MUST be stored in the database.
- The system MUST survive server restarts without data loss or
  session corruption.
- Horizontal scaling MUST be possible by adding instances with
  no shared process memory.

**Rationale**: Statelessness ensures any instance can serve any
request, enabling zero-downtime deployments and elastic scaling.

### II. Database-Driven Context

- Conversation history MUST be fetched from PostgreSQL on every
  chat request; no caching of conversation state in process memory.
- All tool calls and their results MUST be logged and persisted
  in the database.
- User-scoped data isolation MUST be enforced at the query level;
  one user MUST NOT access another user's data.

**Rationale**: The database is the single source of truth. This
guarantees auditability, restart safety, and multi-user isolation.

### III. Tool-Based AI Execution

- The AI agent MUST NOT modify the database directly; all task
  mutations MUST go through MCP tool invocations.
- Exactly 5 MCP tools are permitted: `add`, `list`, `complete`,
  `delete`, `update`.
- Any new task operation MUST be exposed as a dedicated MCP tool
  and registered before the agent can use it.
- Tool call inputs and outputs MUST be logged for traceability.

**Rationale**: Constraining mutations to a fixed tool surface
makes the system auditable, testable, and prevents uncontrolled
side effects from the language model.

### IV. Security First

- Strict `user_id` validation MUST be enforced on every endpoint
  that accesses user-scoped data.
- All database access MUST use the ORM (SQLAlchemy / SQLModel);
  raw SQL MUST NOT be used.
- Secrets (API keys, DB credentials) MUST be loaded exclusively
  from environment variables; hardcoded secrets are forbidden.
- The chat endpoint MUST enforce rate limiting to prevent abuse.
- Input from the user MUST be treated as untrusted and sanitized
  before processing.

**Rationale**: Defense in depth. ORM-only access prevents SQL
injection; env-only secrets prevent credential leaks; rate
limiting prevents resource exhaustion.

### V. Clean Architecture

- The codebase MUST follow a modular folder structure with clear
  separation of concerns: API routes, Agent logic, MCP tools,
  and Data models in distinct modules.
- All I/O-bound operations MUST use `async`/`await`; blocking
  calls inside async handlers are forbidden.
- Cross-cutting concerns (logging, error handling, auth) MUST
  be implemented as FastAPI middleware or dependencies, not
  inlined in route handlers.

**Rationale**: Separation of concerns reduces coupling, makes
each module independently testable, and keeps the async event
loop responsive.

### VI. Reliability & Scalability

- The system MUST handle database connection failures gracefully
  with retry logic and informative error responses.
- Health check endpoints MUST be exposed for orchestration and
  monitoring (liveness and readiness probes).
- Structured JSON logging MUST be used for all log output to
  enable machine-parseable observability.
- The API MUST return deterministic error responses with
  consistent status codes and error schemas.

**Rationale**: Production systems require observable, predictable
failure modes. Structured logging and health checks are baseline
requirements for any deployed service.

## Technology Stack & Constraints

- **Runtime**: Python 3.11+
- **Framework**: FastAPI (async-first)
- **ORM**: SQLAlchemy 2.x / SQLModel
- **Database**: PostgreSQL (primary data store)
- **AI SDK**: OpenAI Agents SDK
- **Tool Protocol**: MCP (Model Context Protocol)
- **Secret Management**: Environment variables (`.env` with
  python-dotenv; never committed to VCS)
- **Deployment Target**: Containerized (Docker) or PaaS
  (Render / Railway)

### Constraints

- No raw SQL queries; ORM-only database access.
- No in-memory state; database is the sole source of truth.
- Exactly 5 MCP tools; adding a tool requires a constitution
  amendment (MINOR version bump).
- All endpoints MUST return JSON; no HTML rendering on the
  backend.

## Development Workflow

- **Branching**: Feature branches off `main`; PRs required for
  merge.
- **Testing**: Unit tests for MCP tools and services; integration
  tests for API endpoints; contract tests for AI agent behavior.
- **Code Review**: All PRs MUST be reviewed before merge.
- **Environment**: `.env` files MUST be listed in `.gitignore`;
  a `.env.example` MUST be provided with placeholder values.
- **Commits**: Conventional Commits format (`feat:`, `fix:`,
  `docs:`, `refactor:`, `test:`, `chore:`).

## Governance

- This constitution is the authoritative reference for all
  architectural and development decisions in the project.
- Amendments MUST be documented with a version bump, rationale,
  and migration plan if breaking.
- Versioning follows Semantic Versioning:
  - **MAJOR**: Principle removal, redefinition, or backward-
    incompatible governance change.
  - **MINOR**: New principle or section added, or material
    expansion of existing guidance.
  - **PATCH**: Clarifications, wording fixes, non-semantic
    refinements.
- Compliance review: Every PR MUST verify alignment with these
  principles before merge. Violations MUST be flagged and
  resolved or justified with an ADR.
- Runtime development guidance is maintained in `CLAUDE.md`.

**Version**: 1.0.0 | **Ratified**: 2026-02-11 | **Last Amended**: 2026-02-11
