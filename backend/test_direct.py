from todo_chatbot_json import TodoChatbotJSON
bot = TodoChatbotJSON()
result = bot.process_message('add task test')
print('Result:', result)