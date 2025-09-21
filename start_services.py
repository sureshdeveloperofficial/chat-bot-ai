#!/usr/bin/env python3
"""
Script to start all microservices locally
"""
import subprocess
import time
import sys
import os
import requests
from threading import Thread

def start_service(service_name, port, directory):
    """Start a service in a separate process"""
    print(f"🚀 Starting {service_name} on port {port}...")
    try:
        # Change to service directory and start uvicorn
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.getcwd(), directory)
        
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port)],
            cwd=directory,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    except Exception as e:
        print(f"❌ Failed to start {service_name}: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend"""
    print("🚀 Starting Frontend on port 8501...")
    try:
        env = os.environ.copy()
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"],
            cwd="frontend",
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    except Exception as e:
        print(f"❌ Failed to start Frontend: {e}")
        return None

def check_health(service_name, port, path="/health"):
    """Check if a service is healthy"""
    try:
        response = requests.get(f"http://localhost:{port}{path}", timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} is healthy")
            return True
        else:
            print(f"⚠️  {service_name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {service_name} health check failed: {e}")
        return False

def main():
    print("🤖 Starting Microservice Chatbot locally...")
    print("=" * 50)
    
    # List of services to start
    services = [
        ("Auth Service", 8001, "auth-service"),
        ("User Service", 8003, "user-service"),
        ("Vector Service", 8004, "vector-service"),
        ("Chat Service", 8002, "chat-service"),
        ("Gateway", 8000, "gateway"),
    ]
    
    processes = []
    
    # Start all backend services
    for service_name, port, directory in services:
        process = start_service(service_name, port, directory)
        if process:
            processes.append((service_name, port, process))
    
    # Start frontend
    frontend_process = start_frontend()
    if frontend_process:
        processes.append(("Frontend", 8501, frontend_process))
    
    # Wait for services to start
    print("\n⏳ Waiting for services to start...")
    time.sleep(10)
    
    # Check health of all services
    print("\n🏥 Checking service health...")
    healthy_services = 0
    
    for service_name, port, _ in processes:
        if service_name == "Frontend":
            # For Streamlit, just check if the port is responding
            try:
                response = requests.get(f"http://localhost:{port}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service_name} is running")
                    healthy_services += 1
                else:
                    print(f"⚠️  {service_name} returned status {response.status_code}")
            except:
                print(f"❌ {service_name} is not responding")
        else:
            if check_health(service_name, port):
                healthy_services += 1
    
    print(f"\n📊 {healthy_services}/{len(processes)} services are healthy")
    
    if healthy_services > 0:
        print("\n🎉 Application is running!")
        print("📱 Access points:")
        print("   Frontend UI: http://localhost:8501")
        print("   API Gateway: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        print("\n👤 Default users:")
        print("   Username: admin, Password: admin123")
        print("   Username: user, Password: user123")
        print("\n⚠️  Press Ctrl+C to stop all services")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all services...")
            for service_name, port, process in processes:
                try:
                    process.terminate()
                    print(f"✅ Stopped {service_name}")
                except:
                    pass
            print("👋 All services stopped")
    else:
        print("❌ Failed to start services properly")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())