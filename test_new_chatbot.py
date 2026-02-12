from todo_chatbot_json import TodoChatbotJSON
import json

def test_chatbot():
    bot = TodoChatbotJSON()
    
    test_inputs = [
        'add task buy groceries',
        'delete task buy groceries', 
        'update task buy groceries to buy food',
        'complete task buy groceries',
        'show my tasks'
    ]
    
    print("Testing the new JSON-only chatbot:")
    print("=" * 50)
    
    for inp in test_inputs:
        result = bot.process_message(inp)
        print(f'Input: {inp}')
        print(f'Output: {json.dumps(result)}')
        print()

if __name__ == "__main__":
    test_chatbot()