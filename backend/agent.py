"""
AI Agent: OpenAI-compatible client with tool calling via OpenRouter.
Handles the chat completion + tool execution loop.
"""
import json
import logging
import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from sqlmodel import Session
from mcp_tools import TOOL_DEFINITIONS, TOOL_DISPATCH

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)
logger = logging.getLogger(__name__)

# T014: Initialize OpenAI client pointing at OpenRouter
# Support both OPEN_ROUTER_API_KEY and OPENAI_API_KEY env var names
API_KEY = os.getenv("OPEN_ROUTER_API_KEY") or os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.getenv("OPENAI_MODEL", "qwen/qwen-2.5-72b-instruct")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

# T015: System prompt
SYSTEM_PROMPT = """You are a helpful todo assistant. You help users manage their tasks using the provided tools.

Rules:
- ALWAYS use the provided tools (add_task, list_tasks, complete_task, delete_task, update_task) to perform task operations.
- NEVER fabricate or make up task data. Only report what the tools return.
- If the user's request is ambiguous, ask for clarification before acting.
- Be concise and friendly in your responses.
- When listing tasks, format them clearly.
- If a tool returns an error, relay it to the user in a helpful way.
- You can ONLY manage tasks for the current user. Do not reference other users.
- If the user asks something unrelated to task management, politely explain that you can help with adding, listing, completing, deleting, and updating tasks."""


async def run_agent(
    messages: list[dict],
    user_id: str,
    session: Session,
) -> dict:
    """
    Run the AI agent with tool calling loop.

    Args:
        messages: Conversation history as list of {"role": ..., "content": ...} dicts
        user_id: The authenticated user's ID (passed to tools for scoping)
        session: SQLModel database session

    Returns:
        dict with keys:
            - "response": str (final assistant message)
            - "tool_name": Optional[str] (last tool called, if any)
            - "tool_result": Optional[str] (last tool result JSON, if any)
            - "tool_messages": list[dict] (all tool-related messages to store)
    """
    # Build full messages with system prompt
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    tool_name_used = None
    tool_result_raw = None
    tool_messages = []  # messages generated during tool calling

    # Tool call loop (max 5 iterations to prevent infinite loops)
    for iteration in range(5):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=full_messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "response": "I'm having trouble connecting to the AI service right now. Please try again in a moment.",
                "tool_name": None,
                "tool_result": None,
                "tool_messages": [],
            }

        choice = response.choices[0]
        message = choice.message

        # If the model wants to call tools
        if message.tool_calls:
            # Add the assistant message with tool calls to context
            full_messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            })

            # Execute each tool call
            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                try:
                    fn_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}

                logger.info(f"Tool call: {fn_name} args={fn_args}")

                if fn_name not in TOOL_DISPATCH:
                    logger.warning(f"Unknown tool requested: {fn_name}")
                    result = json.dumps({"success": False, "error": f"Unknown tool: {fn_name}"})
                else:
                    tool_fn = TOOL_DISPATCH[fn_name]
                    result = tool_fn(user_id=user_id, session=session, **fn_args)

                logger.info(f"Tool result: {fn_name} -> {result[:200]}")
                tool_name_used = fn_name
                tool_result_raw = result

                # Store tool message for persistence
                tool_messages.append({
                    "role": "tool",
                    "content": result,
                    "tool_call_id": tool_call.id,
                    "tool_name": fn_name,
                    "tool_args": json.dumps(fn_args),
                })

                # Add tool result to context for next model call
                full_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            # Continue loop to get model's final response after tool execution
            continue

        # No tool calls — model returned a final text response
        final_text = message.content or "I'm not sure how to help with that. I can assist with adding, listing, completing, deleting, and updating tasks."
        return {
            "response": final_text,
            "tool_name": tool_name_used,
            "tool_result": tool_result_raw,
            "tool_messages": tool_messages,
        }

    # If we exhausted the loop, return what we have
    return {
        "response": "I've completed the operation. Is there anything else you need?",
        "tool_name": tool_name_used,
        "tool_result": tool_result_raw,
        "tool_messages": tool_messages,
    }
