#!/usr/bin/env python3
"""
Start script for running services with mock chat (no OpenAI required)
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def start_service(service_dir, script_name, port, service_name):
    """Start a service in a new process"""
    print(f"🚀 Starting {service_name} on port {port}...")
    
    try:
        cmd = [sys.executable, script_name]
        process = subprocess.Popen(
            cmd,
            cwd=service_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        return process
    except Exception as e:
        print(f"❌ Failed to start {service_name}: {e}")
        return None

def check_service_health(port, service_name, max_retries=10):
    """Check if service is healthy"""
    for i in range(max_retries):
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} is healthy")
                return True
        except:
            pass
        
        print(f"⏳ Waiting for {service_name} ({i+1}/{max_retries})...")
        time.sleep(3)
    
    print(f"❌ {service_name} failed to start properly")
    return False

def main():
    print("🤖 Starting Chatbot Services (Mock Mode)")
    print("=" * 50)
    
    # Service configurations
    services = [
        ("auth-service", "main.py", 8001, "Auth Service"),
        ("user-service", "main.py", 8003, "User Service"),
        ("vector-service", "main.py", 8004, "Vector Service"),
        ("chat-service", "mock_main.py", 8002, "Mock Chat Service"),
        ("gateway", "main.py", 8000, "API Gateway"),
    ]
    
    processes = []
    
    # Start all services
    for service_dir, script, port, name in services:
        process = start_service(service_dir, script, port, name)
        if process:
            processes.append((process, name))
            time.sleep(2)  # Brief delay between starts
    
    print("\n⏳ Waiting for services to initialize...")
    time.sleep(10)
    
    # Check health of all services
    print("\n🏥 Health Check:")
    all_healthy = True
    for service_dir, script, port, name in services:
        if not check_service_health(port, name):
            all_healthy = False
    
    if all_healthy:
        print("\n🎉 All services are running!")
        print("\n📱 Access the application:")
        print("   API Gateway: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        print("   Frontend: Start manually with 'cd frontend && streamlit run app.py'")
        print("\n👤 Default users:")
        print("   Username: admin, Password: admin123")
        print("   Username: user, Password: user123")
        print("\n📝 Note: Using mock chat service (no OpenAI required)")
        
        # Test basic functionality
        print("\n🧪 Testing basic functionality...")
        try:
            # Test login
            login_response = requests.post(
                "http://localhost:8000/auth/login",
                json={"username": "admin", "password": "admin123"}
            )
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                print("✅ Authentication working")
                
                # Test mock chat
                chat_response = requests.post(
                    "http://localhost:8000/chat",
                    json={"message": "Hello, this is a test!"},
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if chat_response.status_code == 200:
                    print("✅ Mock chat working")
                    print(f"   Response: {chat_response.json().get('response', 'No response')}")
                else:
                    print(f"❌ Chat test failed: {chat_response.status_code}")
            else:
                print(f"❌ Login test failed: {login_response.status_code}")
                
        except Exception as e:
            print(f"❌ Testing failed: {e}")
        
        print("\n✨ Services are ready for use!")
        
    else:
        print("\n❌ Some services failed to start. Check the console windows for errors.")
    
    print("\n⚠️  Keep this window open to monitor services")
    print("Press Ctrl+C to stop all services")
    
    try:
        # Keep script running
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        for process, name in processes:
            try:
                process.terminate()
                print(f"   Stopped {name}")
            except:
                pass

if __name__ == "__main__":
    main()