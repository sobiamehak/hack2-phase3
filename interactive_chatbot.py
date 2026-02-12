#!/usr/bin/env python3
"""
Interactive Chatbot for Todo Management

This script provides an interactive interface to the Todo chatbot.
You can type commands like "add task", "show my tasks", etc.
and the chatbot will convert them to the appropriate JSON format.
"""

from todo_chatbot_json import TodoChatbotJSON
import json

def main():
    print("You are an AI Task Assistant.")
    print("You must respond ONLY in valid JSON.")
    print("Do not add any extra text.")
    print("\nAllowed actions:")
    print("- ADD_TASK")
    print("- DELETE_TASK") 
    print("- UPDATE_TASK")
    print("- COMPLETE_TASK")
    print("- GET_TASKS")
    print("\nJSON format:")
    print('{')
    print('  "action": "ADD_TASK",')
    print('  "title": "Task title"')
    print('}')
    print("-" * 50)

    # Initialize the chatbot
    chatbot = TodoChatbotJSON()

    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            # Check if user wants to quit
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print(json.dumps({"action": "EXIT", "message": "Goodbye! Have a productive day!"}))
                break

            # Skip empty input
            if not user_input:
                continue

            # Process the message with the chatbot
            response = chatbot.process_message(user_input)

            # Print ONLY the raw JSON response (this is what gets sent to the API)
            print(json.dumps(response))

        except KeyboardInterrupt:
            print(json.dumps({"action": "EXIT", "message": "Goodbye! Have a productive day!"}))
            break
        except Exception as e:
            print(json.dumps({"action": "ERROR", "message": str(e)}))

if __name__ == "__main__":
    main()