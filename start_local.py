#!/usr/bin/env python3
"""
Local Development Startup Script
This script starts all microservices locally for development
"""

import os
import sys
import subprocess
import threading
import time
import signal
import platform
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.services = [
            {"name": "auth-service", "port": 8001, "path": "auth-service", "file": "main.py"},
            {"name": "user-service", "port": 8003, "path": "user-service", "file": "main.py"},
            {"name": "vector-service", "port": 8004, "path": "vector-service", "file": "main.py"},
            {"name": "chat-service", "port": 8002, "path": "chat-service", "file": "main.py"},
            {"name": "gateway", "port": 8000, "path": "gateway", "file": "main.py"},
            {"name": "frontend", "port": 8501, "path": "frontend", "file": "app.py", "cmd": "streamlit"}
        ]
        
    def get_venv_python(self):
        """Get path to virtual environment Python"""
        if platform.system() == "Windows":
            return "venv\\Scripts\\python.exe"
        else:
            return "venv/bin/python"
    
    def check_prerequisites(self):
        """Check if virtual environment exists and dependencies are installed"""
        print("🔍 Checking Prerequisites...")
        
        # Check virtual environment
        venv_python = self.get_venv_python()
        if not Path(venv_python).exists():
            print("❌ Virtual environment not found. Run install_local.py first.")
            return False
        
        # Check if main dependencies are installed
        try:
            subprocess.run([venv_python, "-c", "import fastapi, streamlit, langchain"], 
                         check=True, capture_output=True)
            print("✅ Dependencies found")
        except subprocess.CalledProcessError:
            print("❌ Dependencies not installed. Run install_local.py first.")
            return False
        
        return True
    
    def check_env_files(self):
        """Check if .env files exist"""
        print("📝 Checking Environment Files...")
        
        missing_files = []
        
        # Check main .env
        if not Path(".env").exists():
            missing_files.append(".env")
        
        # Check service .env files
        for service in self.services:
            env_file = Path(service["path"]) / ".env"
            if not env_file.exists():
                missing_files.append(f"{service['path']}/.env")
        
        if missing_files:
            print(f"⚠️  Missing environment files: {', '.join(missing_files)}")
            print("   Creating from examples...")
            
            # Create missing .env files
            if ".env" in missing_files and Path(".env.example").exists():
                os.system("copy .env.example .env" if platform.system() == "Windows" else "cp .env.example .env")
            
            for service in self.services:
                env_file = Path(service["path"]) / ".env"
                env_example = Path(service["path"]) / ".env.example"
                if not env_file.exists() and env_example.exists():
                    if platform.system() == "Windows":
                        os.system(f"copy {env_example} {env_file}")
                    else:
                        os.system(f"cp {env_example} {env_file}")
        
        print("✅ Environment files ready")
        return True
    
    def check_openai_key(self):
        """Check if OpenAI API key is configured"""
        print("🔑 Checking OpenAI API Key...")
        
        # Check in main .env
        if Path(".env").exists():
            with open(".env", "r") as f:
                content = f.read()
                if "OPENAI_API_KEY=your-openai-api-key-here" in content or "OPENAI_API_KEY=" in content and "sk-" not in content:
                    print("⚠️  OpenAI API key not configured in .env file")
                    print("   Please edit .env and add: OPENAI_API_KEY=your-actual-api-key")
                    return False
                elif "OPENAI_API_KEY=sk-" in content:
                    print("✅ OpenAI API key configured")
                    return True
        
        print("⚠️  Please configure OpenAI API key in .env file")
        return False
    
    def start_infrastructure(self):
        """Start PostgreSQL and Redis using Docker"""
        print("🐳 Starting Infrastructure Services...")
        
        try:
            # Check if docker is available
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            
            # Start PostgreSQL and Redis
            cmd = "docker-compose up postgres redis -d"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Infrastructure services started")
                print("   Waiting for services to be ready...")
                time.sleep(10)
                return True
            else:
                print(f"❌ Failed to start infrastructure: {result.stderr}")
                return False
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Docker not available. Please start PostgreSQL and Redis manually.")
            print("   PostgreSQL: localhost:5432, database: chatbot_db")
            print("   Redis: localhost:6379")
            return True  # Continue anyway
    
    def start_service(self, service):
        """Start a single service"""
        venv_python = self.get_venv_python()
        
        # Change to service directory
        original_dir = os.getcwd()
        service_dir = Path(service["path"])
        
        if not service_dir.exists():
            print(f"❌ Service directory not found: {service['path']}")
            return None
        
        os.chdir(service_dir)
        
        try:
            if service.get("cmd") == "streamlit":
                # Start Streamlit
                cmd = [venv_python, "-m", "streamlit", "run", service["file"], 
                      "--server.address", "0.0.0.0", "--server.port", str(service["port"])]
            else:
                # Start FastAPI service
                cmd = [venv_python, service["file"]]
            
            print(f"🚀 Starting {service['name']} on port {service['port']}")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Store process info
            service_info = {
                "name": service["name"],
                "port": service["port"],
                "process": process,
                "path": service["path"]
            }
            
            return service_info
            
        except Exception as e:
            print(f"❌ Failed to start {service['name']}: {e}")
            return None
        finally:
            os.chdir(original_dir)
    
    def check_service_health(self, service_name, port, max_attempts=30):
        """Check if service is healthy"""
        url = f"http://localhost:{port}/health"
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
            
            time.sleep(1)
        
        return False
    
    def monitor_service(self, service_info):
        """Monitor a service and restart if needed"""
        while True:
            try:
                # Check if process is still running
                if service_info["process"].poll() is not None:
                    print(f"❌ {service_info['name']} stopped unexpectedly")
                    break
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                break
    
    def start_all_services(self):
        """Start all services"""
        print("\n🚀 Starting All Services...")
        
        for service in self.services:
            service_info = self.start_service(service)
            if service_info:
                self.processes.append(service_info)
                
                # Start monitoring thread
                monitor_thread = threading.Thread(
                    target=self.monitor_service, 
                    args=(service_info,),
                    daemon=True
                )
                monitor_thread.start()
            else:
                print(f"❌ Failed to start {service['name']}")
        
        print(f"\n✅ Started {len(self.processes)} services")
        
        # Wait a bit for services to start
        print("⏳ Waiting for services to initialize...")
        time.sleep(15)
        
        # Check health
        print("\n🏥 Checking Service Health...")
        healthy_services = 0
        
        for service_info in self.processes:
            if self.check_service_health(service_info["name"], service_info["port"]):
                print(f"✅ {service_info['name']} is healthy")
                healthy_services += 1
            else:
                print(f"❌ {service_info['name']} is not responding")
        
        print(f"\n📊 {healthy_services}/{len(self.processes)} services are healthy")
    
    def display_status(self):
        """Display current status"""
        print("\n" + "="*60)
        print("🎯 SERVICES RUNNING")
        print("="*60)
        
        for service_info in self.processes:
            status = "🟢 Running" if service_info["process"].poll() is None else "🔴 Stopped"
            print(f"{service_info['name']:15} | Port {service_info['port']:4} | {status}")
        
        print("\n🌐 Access URLs:")
        print(f"Frontend:     http://localhost:8501")
        print(f"API Gateway:  http://localhost:8000")
        print(f"API Docs:     http://localhost:8000/docs")
        
        print("\n👤 Default Users:")
        print("Username: admin, Password: admin123")
        print("Username: user, Password: user123")
        
        print("\n⌨️  Press Ctrl+C to stop all services")
    
    def stop_all_services(self):
        """Stop all services"""
        print("\n🛑 Stopping All Services...")
        
        for service_info in self.processes:
            try:
                service_info["process"].terminate()
                service_info["process"].wait(timeout=5)
                print(f"✅ Stopped {service_info['name']}")
            except subprocess.TimeoutExpired:
                service_info["process"].kill()
                print(f"🔨 Force killed {service_info['name']}")
            except Exception as e:
                print(f"❌ Error stopping {service_info['name']}: {e}")
    
    def run(self):
        """Main run function"""
        print("🚀 Microservice Chatbot - Local Development")
        print("=" * 50)
        
        # Check prerequisites
        if not self.check_prerequisites():
            sys.exit(1)
        
        # Check environment files
        if not self.check_env_files():
            sys.exit(1)
        
        # Check OpenAI key (warning only)
        self.check_openai_key()
        
        # Start infrastructure
        self.start_infrastructure()
        
        try:
            # Start all services
            self.start_all_services()
            
            # Display status
            self.display_status()
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all_services()
            print("\n👋 All services stopped. Goodbye!")

def main():
    manager = ServiceManager()
    manager.run()

if __name__ == "__main__":
    main()