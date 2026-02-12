import json
import re
from typing import Dict, Any

class TodoChatbotJSON:
    """
    A chatbot that converts natural language commands to JSON actions
    for the Todo Dashboard API in the required format.
    """

    def __init__(self):
        self.actions = {
            "add_task": self._parse_add_task,
            "delete_task": self._parse_delete_task,
            "update_task": self._parse_update_task,
            "complete_task": self._parse_complete_task,
            "get_tasks": self._parse_get_tasks,
            "invalid_command": self._parse_invalid_command
        }

    def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and return the corresponding JSON action
        in the required format.

        Args:
            message: The user's natural language command

        Returns:
            A dictionary containing the action and data in the required JSON format
        """
        message = message.strip().lower()

        # Determine the action based on the message content
        action = self._identify_action(message)

        # Parse the message to extract relevant data
        data = self.actions[action](message)

        # Format the response according to the required JSON structure
        if action == "add_task":
            return {
                "action": "ADD_TASK",
                "title": data.get("title", "")
            }
        elif action == "delete_task":
            return {
                "action": "DELETE_TASK",
                "title": data.get("task_id", "")
            }
        elif action == "update_task":
            return {
                "action": "UPDATE_TASK",
                "title": data.get("task_id", ""),
                "new_title": data.get("new_title", "")
            }
        elif action == "complete_task":
            return {
                "action": "COMPLETE_TASK",
                "title": data.get("task_id", "")
            }
        elif action == "get_tasks":
            # For get_tasks, return a simple action
            return {
                "action": "GET_TASKS"
            }
        else:
            # For invalid commands, return a simple action
            return {
                "action": "INVALID_COMMAND"
            }

    def _identify_action(self, message: str) -> str:
        """
        Identify the appropriate action based on the message content.

        Args:
            message: The user's message

        Returns:
            The action name as a string
        """
        # Check for get tasks commands
        if any(keyword in message for keyword in [
            "show", "view", "list", "my tasks", "all tasks", "get tasks", "display"
        ]):
            return "get_tasks"

        # Check for add task commands
        if any(keyword in message for keyword in [
            "add task", "create task", "new task", "add a task", "create a task"
        ]):
            return "add_task"

        # Check for delete task commands
        if any(keyword in message for keyword in [
            "delete", "remove", "delete task", "remove task"
        ]):
            return "delete_task"

        # Check for update task commands
        if any(keyword in message for keyword in [
            "update", "edit", "change", "modify", "update task", "edit task"
        ]):
            return "update_task"

        # Check for complete task commands
        if any(keyword in message for keyword in [
            "complete", "done", "finish", "mark as done", "mark complete", "toggle"
        ]):
            return "complete_task"

        # Default to invalid command
        return "invalid_command"

    def _parse_add_task(self, message: str) -> Dict[str, Any]:
        """
        Parse a message to extract task details for adding a task.

        Args:
            message: The user's message

        Returns:
            A dictionary containing task details
        """
        # Extract the task title after keywords like "add task" or "create task"
        title = ""

        # Look for patterns like "add task [title]" or "create task [title]"
        patterns = [
            r"(?:add task|create task|add a task|create a task)\s+(.+)",
            r"(?:add|create)\s+(.+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                break

        # If we couldn't extract a title, use the whole message after removing command words
        if not title:
            # Remove common command words to isolate the title
            cleaned_message = re.sub(r"(?:add task|create task|add a task|create a task|add|create)", "", message, flags=re.IGNORECASE)
            title = cleaned_message.strip()

        # Capitalize the first letter of each word in the title
        if title:
            title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()

        return {
            "title": title,
            "description": ""
        }

    def _parse_delete_task(self, message: str) -> Dict[str, Any]:
        """
        Parse a message to extract task details for deleting a task.

        Args:
            message: The user's message

        Returns:
            A dictionary containing task details
        """
        # Extract the task identifier after keywords like "delete" or "remove"
        task_identifier = ""

        # Look for patterns like "delete [task title/id]" or "remove [task title/id]"
        patterns = [
            r"(?:delete|remove)\s+(?:task\s+)?(.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                task_identifier = match.group(1).strip()
                break

        # If we couldn't extract an identifier, use the whole message after removing command words
        if not task_identifier:
            # Remove common command words to isolate the identifier
            cleaned_message = re.sub(r"(?:delete|remove|task)", "", message, flags=re.IGNORECASE)
            task_identifier = cleaned_message.strip()

        # Capitalize the first letter of each word in the identifier
        if task_identifier:
            task_identifier = task_identifier[0].upper() + task_identifier[1:] if len(task_identifier) > 1 else task_identifier.upper()

        return {
            "task_id": task_identifier
        }

    def _parse_update_task(self, message: str) -> Dict[str, Any]:
        """
        Parse a message to extract task details for updating a task.

        Args:
            message: The user's message

        Returns:
            A dictionary containing task details
        """
        # Extract the task identifier and new details
        task_identifier = ""
        new_title = ""

        # Look for patterns like "update [task title/id] to [new title]"
        patterns = [
            r"(?:update|edit|change|modify)\s+(?:task\s+)?(.+?)\s+to\s+(.+)",
            r"(?:update|edit|change|modify)\s+(?:task\s+)?(.+)"
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                task_identifier = match.group(1).strip()

                # If there's a second group (for "to [new title]" pattern)
                if len(match.groups()) > 1:
                    new_title = match.group(2).strip()
                break

        # Capitalize the first letter of each word in the identifiers
        if task_identifier:
            task_identifier = task_identifier[0].upper() + task_identifier[1:] if len(task_identifier) > 1 else task_identifier.upper()

        if new_title:
            new_title = new_title[0].upper() + new_title[1:] if len(new_title) > 1 else new_title.upper()

        return {
            "task_id": task_identifier,
            "new_title": new_title,
            "new_description": ""
        }

    def _parse_complete_task(self, message: str) -> Dict[str, Any]:
        """
        Parse a message to extract task details for completing a task.

        Args:
            message: The user's message

        Returns:
            A dictionary containing task details
        """
        # Extract the task identifier after keywords like "complete" or "done"
        task_identifier = ""

        # Look for patterns like "complete [task title/id]" or "mark [task title/id] as done"
        patterns = [
            r"(?:complete|done|finish|mark as done|mark complete|toggle)\s+(?:task\s+)?(.+)",
            r"mark\s+(.+?)\s+(?:as )?(?:done|complete|finished)"
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                task_identifier = match.group(1).strip()
                break

        # If we couldn't extract an identifier, use the whole message after removing command words
        if not task_identifier:
            # Remove common command words to isolate the identifier
            cleaned_message = re.sub(r"(?:complete|done|finish|mark|as|task)", "", message, flags=re.IGNORECASE)
            task_identifier = cleaned_message.strip()

        # Capitalize the first letter of each word in the identifier
        if task_identifier:
            task_identifier = task_identifier[0].upper() + task_identifier[1:] if len(task_identifier) > 1 else task_identifier.upper()

        return {
            "task_id": task_identifier
        }

    def _parse_get_tasks(self, message: str) -> Dict[str, Any]:
        """
        Parse a message to extract parameters for getting tasks.

        Args:
            message: The user's message

        Returns:
            A dictionary containing parameters
        """
        # Check if the user wants to filter by status
        status_filter = None
        if "completed" in message:
            status_filter = "completed"
        elif "incomplete" in message or "pending" in message:
            status_filter = "incomplete"

        return {
            "status_filter": status_filter
        }

    def _parse_invalid_command(self, message: str) -> Dict[str, Any]:
        """
        Return empty data for invalid commands.

        Args:
            message: The user's message

        Returns:
            An empty dictionary
        """
        return {}


# Example usage and testing
if __name__ == "__main__":
    bot = TodoChatbotJSON()

    # Test cases
    test_messages = [
        "add task learn nextjs",
        "delete task learn nextjs", 
        "show my tasks",
        "update task learn nextjs to learn react",
        "complete task learn nextjs",
        "random invalid command"
    ]

    for msg in test_messages:
        result = bot.process_message(msg)
        print(f"Input: {msg}")
        print(f"Output: {json.dumps(result, indent=2)}")
        print("-" * 40)