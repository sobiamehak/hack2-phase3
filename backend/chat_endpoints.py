"""
Chat endpoint: AI-powered todo assistant with conversation persistence.
Implements US1 (NL task management), US2 (context persistence), US3 (auth/security).
"""
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import get_session
from models import Conversation, Message
from agent import run_agent
from auth import get_current_user

RATE_LIMIT = os.getenv("RATE_LIMIT_USER_REQUESTS_PER_HOUR", "100")
limiter = Limiter(key_func=get_remote_address)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


# T017: Request/Response models
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    response: str
    action: Optional[Dict[str, Any]] = None
    conversation_id: str


# T022: Find or create conversation for user
def get_or_create_conversation(user_id: str, session: Session) -> Conversation:
    """Get the user's existing conversation or create a new one."""
    uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
    query = select(Conversation).where(Conversation.user_id == uid)
    conversation = session.exec(query).first()
    if conversation is None:
        conversation = Conversation(user_id=uid)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        logger.info(f"Created new conversation {conversation.id} for user {user_id}")
    return conversation


# T023: Store a message in the database
def store_message(
    session: Session,
    conversation_id,
    role: str,
    content: str,
    tool_call_id: Optional[str] = None,
    tool_name: Optional[str] = None,
    tool_args: Optional[str] = None,
) -> Message:
    """Persist a message to the database."""
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_call_id=tool_call_id,
        tool_name=tool_name,
        tool_args=tool_args,
    )
    session.add(msg)
    session.commit()
    session.refresh(msg)
    return msg


# T024: Load conversation history (last 20 messages)
def load_conversation_history(conversation_id, session: Session, limit: int = 20) -> list[dict]:
    """Load the most recent user/assistant messages for the conversation.

    Tool messages are excluded because they lack the preceding assistant
    tool_calls context, which causes LLM providers to reject the request.
    """
    query = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.role.in_(["user", "assistant"]),
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = session.exec(query).all()
    # Reverse to chronological order
    messages = list(reversed(messages))

    history = []
    for msg in messages:
        history.append({"role": msg.role, "content": msg.content})
    return history


# T018 + T025: Main chat endpoint
@router.post("/{user_id}/chat", response_model=ChatResponse)
@limiter.limit(f"{RATE_LIMIT}/hour")
async def chat_endpoint(
    request: Request,
    user_id: str,
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Process a natural language message through the AI agent.
    Requires JWT authentication. user_id must match the authenticated user.
    """
    # T028: Ownership validation
    if current_user.get("sub") != user_id:
        logger.warning(f"Ownership mismatch: token sub={current_user.get('sub')} != url user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's chat",
        )

    try:
        # T022: Get or create conversation
        conversation = get_or_create_conversation(user_id, session)

        # T023: Store the user's message
        store_message(session, conversation.id, role="user", content=chat_request.message)

        # T024: Load conversation history
        history = load_conversation_history(conversation.id, session)

        # T016/T018: Run the AI agent
        result = await run_agent(
            messages=history,
            user_id=user_id,
            session=session,
        )

        # T026: Store tool messages
        for tool_msg in result.get("tool_messages", []):
            store_message(
                session,
                conversation.id,
                role="tool",
                content=tool_msg["content"],
                tool_call_id=tool_msg.get("tool_call_id"),
                tool_name=tool_msg.get("tool_name"),
                tool_args=tool_msg.get("tool_args"),
            )

        # Store assistant response
        store_message(session, conversation.id, role="assistant", content=result["response"])

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        # Build action payload
        action = None
        if result.get("tool_name"):
            try:
                tool_result_parsed = json.loads(result["tool_result"]) if result.get("tool_result") else None
            except (json.JSONDecodeError, TypeError):
                tool_result_parsed = None
            action = {
                "tool": result["tool_name"],
                "result": tool_result_parsed,
            }

        return ChatResponse(
            response=result["response"],
            action=action,
            conversation_id=str(conversation.id),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat service temporarily unavailable. Please try again.",
        )
