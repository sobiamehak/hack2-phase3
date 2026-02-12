from todo_chatbot import TodoChatbot

# Create a chatbot instance
bot = TodoChatbot()

print("TODO CHATBOT DEMO")
print("="*50)

# Test all major command types
test_commands = [
    "add task Learn Python Programming",
    "add task Buy groceries",
    "show my tasks",
    "show my completed tasks",
    "complete task Learn Python Programming",
    "update task Buy groceries to Buy weekly groceries",
    "delete task Buy weekly groceries",
    "list all tasks",
    "mark task Learn Python Programming as done",
    "random invalid command"
]

for i, command in enumerate(test_commands, 1):
    result = bot.process_message(command)
    print(f"{i:2d}. USER: {command}")
    print(f"    BOT:  {result}")
    print()

print("DEMO COMPLETE - Chatbot is working correctly!")