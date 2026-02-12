# Data Model: Todo AI Chatbot

**Feature**: 004-todo-ai-chatbot
**Date**: 2026-02-11

## Existing Entities (no changes)

### User
- `id`: UUID (primary key, auto-generated)
- `email`: string (unique, not null)
- `password_hash`: string (not null)
- `created_at`: datetime (auto-set)
- `updated_at`: datetime (auto-set)
- **Relationships**: has many Tasks, has many Conversations

### Task
- `id`: UUID (primary key, auto-generated)
- `title`: string (1-200 chars, not null)
- `description`: string (optional)
- `completed`: boolean (default false)
- `user_id`: UUID (foreign key → User.id, indexed)
- `created_at`: datetime (auto-set)
- `updated_at`: datetime (auto-set)
- **Relationships**: belongs to User

## New Entities

### Conversation
- `id`: UUID (primary key, auto-generated)
- `user_id`: UUID (foreign key → User.id, not null, indexed)
- `created_at`: datetime (auto-set)
- `updated_at`: datetime (auto-set on each new message)
- **Relationships**: belongs to User, has many Messages
- **Constraints**: user_id indexed for fast lookup

### Message
- `id`: UUID (primary key, auto-generated)
- `conversation_id`: UUID (foreign key → Conversation.id, not null, indexed)
- `role`: string (enum: "user", "assistant", "tool", not null)
- `content`: text (the message body, not null)
- `tool_call_id`: string (optional, set when role="tool" to link to a specific tool call)
- `tool_name`: string (optional, the name of the tool called)
- `tool_args`: text (optional, JSON string of tool call arguments)
- `created_at`: datetime (auto-set)
- **Relationships**: belongs to Conversation
- **Constraints**: (conversation_id, created_at) indexed for efficient
  "last 20 messages" query
- **Ordering**: Messages within a conversation are ordered by
  `created_at` ascending

## Entity Relationship Diagram

```
User (1) ──── (N) Task
  │
  └── (1) ──── (N) Conversation
                      │
                      └── (1) ──── (N) Message
```

## Indexes

| Table        | Index                              | Purpose                           |
|-------------|-------------------------------------|-----------------------------------|
| tasks       | idx_tasks_user_id ON (user_id)      | Fast task lookup by user          |
| conversations| idx_conv_user_id ON (user_id)      | Fast conversation lookup by user  |
| messages    | idx_msg_conv_created ON (conversation_id, created_at DESC) | Fast "last 20 messages" query |

## Migration Notes

- Conversation and Message tables are net-new; no data migration
  needed for existing data.
- The existing User model gains a `conversations` relationship
  (backref only — no column change).
- Alembic migration: `alembic revision --autogenerate -m "add conversation and message tables"`
