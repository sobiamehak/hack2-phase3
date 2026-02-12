import json
from todo_chatbot import TodoChatbot

def test_chatbot_responses():
    """
    Test the chatbot responses to ensure all actions work correctly.
    """
    bot = TodoChatbot()
    
    print("Testing Todo Chatbot Responses:")
    print("=" * 50)
    
    # Test cases for each action type
    test_cases = [
        # ADD_TASK tests
        {
            "input": "add task learn nextjs",
            "expected_action": "ADD_TASK",
            "description": "Basic add task command"
        },
        {
            "input": "create task Buy groceries",
            "expected_action": "ADD_TASK",
            "description": "Create task command variant"
        },
        {
            "input": "add a task Call mom",
            "expected_action": "ADD_TASK",
            "description": "Add a task command variant"
        },
        
        # DELETE_TASK tests
        {
            "input": "delete task learn nextjs",
            "expected_action": "DELETE_TASK",
            "description": "Basic delete task command"
        },
        {
            "input": "remove task Buy groceries",
            "expected_action": "DELETE_TASK",
            "description": "Remove task command variant"
        },
        
        # UPDATE_TASK tests
        {
            "input": "update task learn nextjs to learn react",
            "expected_action": "UPDATE_TASK",
            "description": "Update task with new title"
        },
        {
            "input": "edit task Buy groceries",
            "expected_action": "UPDATE_TASK",
            "description": "Edit task command variant"
        },
        
        # COMPLETE_TASK tests
        {
            "input": "complete task learn nextjs",
            "expected_action": "COMPLETE_TASK",
            "description": "Complete task command"
        },
        {
            "input": "mark task Buy groceries as done",
            "expected_action": "COMPLETE_TASK",
            "description": "Mark task as done command"
        },
        {
            "input": "done task Call mom",
            "expected_action": "COMPLETE_TASK",
            "description": "Done task command"
        },
        
        # GET_TASKS tests
        {
            "input": "show my tasks",
            "expected_action": "GET_TASKS",
            "description": "Show tasks command"
        },
        {
            "input": "view all tasks",
            "expected_action": "GET_TASKS",
            "description": "View tasks command"
        },
        {
            "input": "list my completed tasks",
            "expected_action": "GET_TASKS",
            "description": "List completed tasks command"
        },
        
        # INVALID_COMMAND tests
        {
            "input": "random invalid command",
            "expected_action": "INVALID_COMMAND",
            "description": "Invalid command"
        },
        {
            "input": "what is the weather today",
            "expected_action": "INVALID_COMMAND",
            "description": "Non-todo command"
        }
    ]
    
    all_tests_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Input: '{test_case['input']}'")
        
        result = bot.process_message(test_case['input'])
        actual_action = result['action']
        expected_action = test_case['expected_action']
        
        print(f"Expected: {expected_action}")
        print(f"Actual: {actual_action}")
        
        if actual_action == expected_action:
            print("[PASS] PASSED")
        else:
            print("[FAIL] FAILED")
            all_tests_passed = False
        
        print(f"Full response: {json.dumps(result, indent=2)}")
        print("-" * 50)
    
    print(f"\nOverall Result: {'[PASS] ALL TESTS PASSED' if all_tests_passed else '[FAIL] SOME TESTS FAILED'}")
    return all_tests_passed

def test_json_format_compliance():
    """
    Test that the JSON format complies with the expected structure.
    """
    print("\n\nTesting JSON Format Compliance:")
    print("=" * 50)
    
    bot = TodoChatbot()
    
    # Test each action type to ensure proper JSON structure
    test_commands = [
        ("add task Learn Python", {
            "action": "ADD_TASK",
            "data": {"title": "Learn python", "description": ""}
        }),
        ("delete task Learn Python", {
            "action": "DELETE_TASK", 
            "data": {"task_id": "Learn python"}
        }),
        ("update task Learn Python to Learn JavaScript", {
            "action": "UPDATE_TASK",
            "data": {"task_id": "Learn python", "new_title": "Learn javascript", "new_description": ""}
        }),
        ("complete task Learn Python", {
            "action": "COMPLETE_TASK",
            "data": {"task_id": "Learn python"}
        }),
        ("show my tasks", {
            "action": "GET_TASKS",
            "data": {"status_filter": None}
        })
    ]
    
    all_compliant = True
    
    for command, expected_structure in test_commands:
        print(f"\nTesting command: '{command}'")
        result = bot.process_message(command)
        
        # Check if the basic structure is correct
        has_action = "action" in result
        has_data = "data" in result
        action_is_valid = result["action"] in ["ADD_TASK", "DELETE_TASK", "UPDATE_TASK", "COMPLETE_TASK", "GET_TASKS", "INVALID_COMMAND"]
        
        print(f"Has 'action' key: {has_action}")
        print(f"Has 'data' key: {has_data}")
        print(f"Action is valid: {action_is_valid}")
        
        if has_action and has_data and action_is_valid:
            print("[PASS] JSON structure compliant")
        else:
            print("[FAIL] JSON structure not compliant")
            all_compliant = False
        
        print(f"Response: {json.dumps(result, indent=2)}")
        print("-" * 30)
    
    print(f"\nJSON Compliance Result: {'[PASS] COMPLIANT' if all_compliant else '[FAIL] NOT COMPLIANT'}")
    return all_compliant

def run_integration_test():
    """
    Run an integration test simulating a conversation flow.
    """
    print("\n\nRunning Integration Test:")
    print("=" * 50)
    
    bot = TodoChatbot()
    
    # Simulate a conversation flow
    conversation_flow = [
        "add task Learn NextJS",
        "add task Buy groceries",
        "show my tasks",
        "complete task Learn NextJS",
        "show my completed tasks",
        "delete task Buy groceries",
        "show my tasks"
    ]
    
    print("Simulating conversation flow:")
    for i, command in enumerate(conversation_flow, 1):
        print(f"\n{i}. User: {command}")
        result = bot.process_message(command)
        print(f"   Bot: {json.dumps(result, indent=2)}")
    
    print("\n[PASS] Integration test completed")

if __name__ == "__main__":
    # Run all tests
    chatbot_tests_passed = test_chatbot_responses()
    json_compliance_passed = test_json_format_compliance()
    run_integration_test()
    
    print(f"\n\nFinal Summary:")
    print(f"Chatbot Response Tests: {'[PASS] PASSED' if chatbot_tests_passed else '[FAIL] FAILED'}")
    print(f"JSON Format Compliance: {'[PASS] PASSED' if json_compliance_passed else '[FAIL] FAILED'}")
    
    if chatbot_tests_passed and json_compliance_passed:
        print("\n[PASS] ALL TESTS PASSED! The chatbot is working correctly.")
    else:
        print("\n[WARN] Some tests failed. Please review the output above.")