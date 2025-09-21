#!/usr/bin/env python3
"""
Quick start script for local development
"""
import subprocess
import sys
import os
import time

def run_service(name, directory, port):
    """Run a service and return immediately"""
    print(f"Starting {name} on port {port}...")
    
    # Create a simple run command
    cmd = f'cd {directory} && python main.py'
    
    # Start the service in a new process
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix/Linux/Mac
            subprocess.Popen(cmd, shell=True)
        print(f"✅ {name} started")
        return True
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return False

def main():
    print("🚀 Quick Start - Microservice Chatbot")
    print("=" * 40)
    
    # Services to start
    services = [
        ("Auth Service", "auth-service", 8001),
        ("User Service", "user-service", 8003),
        ("Vector Service", "vector-service", 8004),
        ("Chat Service", "chat-service", 8002),
        ("Gateway", "gateway", 8000),
    ]
    
    # Start backend services
    for name, directory, port in services:
        run_service(name, directory, port)
        time.sleep(2)  # Brief pause between starts
    
    # Start frontend
    print("\nStarting Frontend...")
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen('cd frontend && streamlit run app.py', shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix/Linux/Mac
            subprocess.Popen('cd frontend && streamlit run app.py', shell=True)
        print("✅ Frontend started")
    except Exception as e:
        print(f"❌ Failed to start Frontend: {e}")
    
    print("\n🎉 All services started!")
    print("\n📱 Access the application:")
    print("   Frontend: http://localhost:8501")
    print("   API Gateway: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n👤 Default credentials:")
    print("   Username: admin, Password: admin123")
    print("   Username: user, Password: user123")
    print("\n⏳ Services may take 30-60 seconds to fully start")
    print("💡 Check individual console windows for service logs")

if __name__ == "__main__":
    main()