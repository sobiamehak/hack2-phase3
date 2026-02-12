#!/usr/bin/env python3
"""
Script to start the chatbot server and run the todo agent.
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def start_server():
    """
    Start the chatbot server in a subprocess.
    """
    server_dir = Path("chatbot/backend")
    server_script = server_dir / "run_server.py"
    
    if not server_script.exists():
        print(f"Server script not found at {server_script}")
        return None
    
    # Change to the server directory and start the server
    env = os.environ.copy()
    env["PYTHONPATH"] = str(server_dir)
    
    process = subprocess.Popen([
        sys.executable, str(server_script)
    ], cwd=server_dir, env=env)
    
    return process

def check_server_health(base_url="http://localhost:8000"):
    """
    Check if the server is running by hitting the health endpoint.
    """
    try:
        import requests
        response = requests.get(f"{base_url}/health")
        return response.status_code == 200
    except:
        return False

def main():
    print("Starting Todo Chatbot Server and Agent...")
    print("=" * 50)
    
    # Start the server
    print("Starting server...")
    server_process = start_server()
    
    if not server_process:
        print("Failed to start server")
        return
    
    # Wait a bit for the server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    # Check if server is healthy
    server_ready = False
    for i in range(10):  # Try for up to 30 seconds
        if check_server_health():
            server_ready = True
            break
        print(f"Server not ready yet... ({i+1}/10)")
        time.sleep(3)
    
    if not server_ready:
        print("Server failed to start properly")
        server_process.terminate()
        return
    
    print("Server is running!")
    print("\nStarting Todo Agent...")
    
    # Import and run the agent
    try:
        from todo_agent import main as agent_main
        print("Todo Agent started. Type 'quit' to exit.")
        agent_main()
    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nShutting down server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")


if __name__ == "__main__":
    main()