"""
MCP Tools: 5 stateless tool functions for todo task management.
Each tool receives user_id and session, operates only on that user's data,
and returns a standardized JSON response.
"""
import json
import logging
import uuid as _uuid
from typing import Optional
from sqlmodel import Session, select
from models import Task

logger = logging.getLogger(__name__)


def _to_uuid(val):
    """Convert string to uuid.UUID if needed."""
    return _uuid.UUID(val) if isinstance(val, str) else val


def _task_to_dict(task: Task) -> dict:
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
    }


def add_task(user_id: str, session: Session, title: str, description: Optional[str] = None) -> str:
    """Create a new task for the user."""
    try:
        user_id = _to_uuid(user_id)
        task = Task(title=title, description=description, user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"add_task: created '{title}' for user {user_id}")
        return json.dumps({
            "success": True,
            "data": _task_to_dict(task),
            "message": f"Task '{title}' created successfully.",
        })
    except Exception as e:
        session.rollback()
        logger.error(f"add_task error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def list_tasks(user_id: str, session: Session, status_filter: Optional[str] = None) -> str:
    """List tasks for the user, optionally filtered by status."""
    try:
        user_id = _to_uuid(user_id)
        query = select(Task).where(Task.user_id == user_id)
        if status_filter == "completed":
            query = query.where(Task.completed == True)
        elif status_filter == "incomplete":
            query = query.where(Task.completed == False)
        tasks = session.exec(query).all()
        logger.info(f"list_tasks: {len(tasks)} tasks for user {user_id}")
        return json.dumps({
            "success": True,
            "data": [_task_to_dict(t) for t in tasks],
            "message": f"Found {len(tasks)} task(s).",
        })
    except Exception as e:
        logger.error(f"list_tasks error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def complete_task(user_id: str, session: Session, task_title: str) -> str:
    """Mark a task as completed by matching title substring."""
    try:
        user_id = _to_uuid(user_id)
        query = select(Task).where(
            Task.user_id == user_id,
            Task.title.ilike(f"%{task_title}%"),
        )
        matches = session.exec(query).all()
        if len(matches) == 0:
            return json.dumps({"success": False, "error": f"No task found matching '{task_title}'."})
        if len(matches) > 1:
            titles = [m.title for m in matches]
            return json.dumps({"success": False, "error": f"Multiple tasks match '{task_title}': {titles}. Please be more specific."})
        task = matches[0]
        task.completed = True
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"complete_task: '{task.title}' for user {user_id}")
        return json.dumps({
            "success": True,
            "data": _task_to_dict(task),
            "message": f"Task '{task.title}' marked as complete.",
        })
    except Exception as e:
        session.rollback()
        logger.error(f"complete_task error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def delete_task(user_id: str, session: Session, task_title: str) -> str:
    """Delete a task by matching title substring."""
    try:
        user_id = _to_uuid(user_id)
        query = select(Task).where(
            Task.user_id == user_id,
            Task.title.ilike(f"%{task_title}%"),
        )
        matches = session.exec(query).all()
        if len(matches) == 0:
            return json.dumps({"success": False, "error": f"No task found matching '{task_title}'."})
        if len(matches) > 1:
            titles = [m.title for m in matches]
            return json.dumps({"success": False, "error": f"Multiple tasks match '{task_title}': {titles}. Please be more specific."})
        task = matches[0]
        task_data = _task_to_dict(task)
        session.delete(task)
        session.commit()
        logger.info(f"delete_task: '{task_data['title']}' for user {user_id}")
        return json.dumps({
            "success": True,
            "data": task_data,
            "message": f"Task '{task_data['title']}' deleted.",
        })
    except Exception as e:
        session.rollback()
        logger.error(f"delete_task error: {e}")
        return json.dumps({"success": False, "error": str(e)})


def update_task(
    user_id: str,
    session: Session,
    task_title: str,
    new_title: Optional[str] = None,
    new_description: Optional[str] = None,
) -> str:
    """Update a task by matching title substring."""
    try:
        user_id = _to_uuid(user_id)
        query = select(Task).where(
            Task.user_id == user_id,
            Task.title.ilike(f"%{task_title}%"),
        )
        matches = session.exec(query).all()
        if len(matches) == 0:
            return json.dumps({"success": False, "error": f"No task found matching '{task_title}'."})
        if len(matches) > 1:
            titles = [m.title for m in matches]
            return json.dumps({"success": False, "error": f"Multiple tasks match '{task_title}': {titles}. Please be more specific."})
        task = matches[0]
        if new_title is not None:
            task.title = new_title
        if new_description is not None:
            task.description = new_description
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"update_task: '{task.title}' for user {user_id}")
        return json.dumps({
            "success": True,
            "data": _task_to_dict(task),
            "message": f"Task updated successfully.",
        })
    except Exception as e:
        session.rollback()
        logger.error(f"update_task error: {e}")
        return json.dumps({"success": False, "error": str(e)})


# T013: OpenAI-format tool definitions and dispatch map

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The task title (1-200 chars)"},
                    "description": {"type": "string", "description": "Optional task description"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the user. Optionally filter by status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["all", "completed", "incomplete"],
                        "description": "Filter tasks by status. Default is 'all'.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed. Identifies the task by title or partial title match.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_title": {"type": "string", "description": "The title (or part of the title) of the task to complete"},
                },
                "required": ["task_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task. Identifies the task by title or partial title match.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_title": {"type": "string", "description": "The title (or part of the title) of the task to delete"},
                },
                "required": ["task_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title or description. Identifies the task by current title or partial title match.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_title": {"type": "string", "description": "The current title (or part of it) to identify the task"},
                    "new_title": {"type": "string", "description": "The new title for the task"},
                    "new_description": {"type": "string", "description": "The new description for the task"},
                },
                "required": ["task_title"],
            },
        },
    },
]

TOOL_DISPATCH = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "delete_task": delete_task,
    "update_task": update_task,
}
