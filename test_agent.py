#!/usr/bin/env python3
"""
Test script to verify the todo agent functionality.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing module imports...")
    
    try:
        import requests
        print("+ requests imported successfully")
    except ImportError as e:
        print(f"- Failed to import requests: {e}")
        return False
    
    try:
        from todo_agent import TodoAgent
        print("+ TodoAgent imported successfully")
    except ImportError as e:
        print(f"- Failed to import TodoAgent: {e}")
        return False
        
    try:
        from dotenv import load_dotenv
        print("+ dotenv imported successfully")
    except ImportError as e:
        print(f"- Failed to import dotenv: {e}")
        return False
    
    return True

def test_environment():
    """Test if environment variables are set."""
    print("\nTesting environment variables...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-openrouter-api-key-here":
        print("+ OPENAI_API_KEY is set")
        return True
    else:
        print("? OPENAI_API_KEY is not set (this is OK for testing, but needed for actual usage)")
        return True

def test_agent_creation():
    """Test creating a todo agent instance."""
    print("\nTesting agent creation...")
    
    try:
        from todo_agent import TodoAgent
        agent = TodoAgent(base_url="http://invalid-url-for-test:8000")
        print("+ TodoAgent instance created successfully")
        return True
    except Exception as e:
        print(f"- Failed to create TodoAgent instance: {e}")
        return False

def main():
    print("Todo Agent Verification Test")
    print("=" * 40)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    # Test environment
    if not test_environment():
        all_tests_passed = False
    
    # Test agent creation
    if not test_agent_creation():
        all_tests_passed = False
    
    print("\n" + "=" * 40)
    if all_tests_passed:
        print("+ All tests passed! The todo agent is ready to use.")
        print("\nTo start using the agent:")
        print("1. Make sure your OpenRouter API key is in the .env file")
        print("2. Run: python run_todo_agent.py")
    else:
        print("- Some tests failed. Please check the errors above.")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)