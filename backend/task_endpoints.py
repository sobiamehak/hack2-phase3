import uuid as _uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, delete
from auth import get_current_user
from database import get_session
from models import Task, User, TaskCreate, TaskUpdate
from typing import List, Optional
from logging_config import logger
import html
import re


def _to_uuid(val):
    """Convert string to uuid.UUID if needed."""
    return _uuid.UUID(val) if isinstance(val, str) else val

router = APIRouter(prefix="/{user_id}/tasks", tags=["tasks"])

@router.get("/", response_model=List[Task])
async def get_tasks(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
    status_filter: Optional[str] = None
):
    """
    Get all tasks for the authenticated user.
    """
    # Sanitize and validate user_id
    if not user_id or not isinstance(user_id, str) or len(user_id.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    # Verify that the requested user_id matches the authenticated user's ID
    if current_user.get("sub") != user_id:
        logger.warning(f"Unauthorized access attempt: user {current_user.get('sub')} tried to access tasks for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )

    # Build query
    uid = _to_uuid(user_id)
    query = select(Task).where(Task.user_id == uid)

    # Apply status filter if provided
    if status_filter:
        if status_filter.lower() == "completed":
            query = query.where(Task.completed == True)
        elif status_filter.lower() == "incomplete":
            query = query.where(Task.completed == False)
        # If status_filter is "all" or any other value, don't apply additional filtering

    tasks = session.exec(query).all()
    logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")
    return tasks


@router.post("/", response_model=Task)
async def create_task(
    user_id: str,
    task: TaskCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.
    """
    # Sanitize and validate user_id
    if not user_id or not isinstance(user_id, str) or len(user_id.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    # Verify that the requested user_id matches the authenticated user's ID
    if current_user.get("sub") != user_id:
        logger.warning(f"Unauthorized access attempt: user {current_user.get('sub')} tried to create task for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for this user"
        )

    # Sanitize input data
    sanitized_title = html.escape(task.title.strip())
    sanitized_description = html.escape(task.description.strip()) if task.description else None

    # Validate title length
    if len(sanitized_title) < 1 or len(sanitized_title) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must be between 1 and 200 characters"
        )

    # Create task with the authenticated user's ID
    uid = _to_uuid(user_id)
    db_task = Task(
        title=sanitized_title,
        description=sanitized_description,
        completed=task.completed,
        user_id=uid
    )

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    logger.info(f"Created task {db_task.id} for user {user_id}")
    return db_task


@router.get("/{task_id}", response_model=Task)
async def get_task(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task by ID for the authenticated user.
    """
    # Sanitize and validate user_id and task_id
    if not user_id or not isinstance(user_id, str) or len(user_id.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    if not task_id or not isinstance(task_id, str) or len(task_id.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID"
        )

    # Verify that the requested user_id matches the authenticated user's ID
    if current_user.get("sub") != user_id:
        logger.warning(f"Unauthorized access attempt: user {current_user.get('sub')} tried to access task {task_id} for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )

    task = session.get(Task, _to_uuid(task_id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify that the task belongs to the user
    if str(task.user_id) != user_id:
        logger.warning(f"Unauthorized access attempt: user {user_id} tried to access task {task_id} belonging to another user")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )

    logger.info(f"Retrieved task {task_id} for user {user_id}")
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    user_id: str,
    task_id: str,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task by ID for the authenticated user.
    """
    # Sanitize and validate user_id and task_id
    if not user_id or not isinstance(user_id, str) or len(user_id.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    if not task_id or not isinstance(task_id, str) or len(task_id.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID"
        )

    # Verify that the requested user_id matches the authenticated user's ID
    if current_user.get("sub") != user_id:
        logger.warning(f"Unauthorized access attempt: user {current_user.get('sub')} tried to update task {task_id} for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's tasks"
        )

    db_task = session.get(Task, _to_uuid(task_id))
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify that the task belongs to the user
    if str(db_task.user_id) != user_id:
        logger.warning(f"Unauthorized access attempt: user {user_id} tried to update task {task_id} belonging to another user")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    # Sanitize input data if provided
    if task_update.title is not None:
        sanitized_title = html.escape(task_update.title.strip())
        if len(sanitized_title) < 1 or len(sanitized_title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title must be between 1 and 200 characters"
            )
        task_update.title = sanitized_title

    if task_update.description is not None:
        task_update.description = html.escape(task_update.description.strip())

    # Update task with provided values
    for var, value in task_update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(db_task, var, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    logger.info(f"Updated task {task_id} for user {user_id}")
    return db_task


@router.delete("/{task_id}")
async def delete_task(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task by ID for the authenticated user.
    """
    # Sanitize and validate user_id and task_id
    if not user_id or not isinstance(user_id, str) or len(user_id.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    if not task_id or not isinstance(task_id, str) or len(task_id.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID"
        )

    # Verify that the requested user_id matches the authenticated user's ID
    if current_user.get("sub") != user_id:
        logger.warning(f"Unauthorized access attempt: user {current_user.get('sub')} tried to delete task {task_id} for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user's tasks"
        )

    task = session.get(Task, _to_uuid(task_id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify that the task belongs to the user
    if str(task.user_id) != user_id:
        logger.warning(f"Unauthorized access attempt: user {user_id} tried to delete task {task_id} belonging to another user")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )

    session.delete(task)
    session.commit()
    logger.info(f"Deleted task {task_id} for user {user_id}")
    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/complete", response_model=Task)
async def toggle_task_completion(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a specific task.
    """
    # Sanitize and validate user_id and task_id
    if not user_id or not isinstance(user_id, str) or len(user_id.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    if not task_id or not isinstance(task_id, str) or len(task_id.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task ID"
        )

    # Verify that the requested user_id matches the authenticated user's ID
    if current_user.get("sub") != user_id:
        logger.warning(f"Unauthorized access attempt: user {current_user.get('sub')} tried to update task {task_id} for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's tasks"
        )

    task = session.get(Task, _to_uuid(task_id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Verify that the task belongs to the user
    if str(task.user_id) != user_id:
        logger.warning(f"Unauthorized access attempt: user {user_id} tried to update task {task_id} belonging to another user")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )

    # Toggle the completion status
    task.completed = not task.completed
    session.add(task)
    session.commit()
    session.refresh(task)
    logger.info(f"Toggled completion status for task {task_id} for user {user_id}")
    return task