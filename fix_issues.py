#!/usr/bin/env python3
"""
Fix common issues with the chatbot services
"""

import os
import sys
import subprocess
import time
import requests
import json

def check_python_packages():
    """Check and install required Python packages"""
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'langchain', 'langchain-openai',
        'openai', 'faiss-cpu', 'sqlalchemy', 'alembic', 'psycopg2-binary',
        'python-jose[cryptography]', 'passlib[bcrypt]', 'python-multipart',
        'pydantic', 'requests', 'numpy', 'pandas', 'python-dotenv', 'redis',
        'httpx', 'PyPDF2', 'docx2txt'
    ]
    
    print("🔧 Checking Python packages...")
    for package in required_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    print("✅ All packages installed")
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("❌ .env file not found. Creating from template...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
        else:
            # Create basic .env file
            env_content = """# OpenAI API Key (required for chat and vector services)
OPENAI_API_KEY=your-openai-api-key-here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/chatbot_db

# Redis Configuration  
REDIS_URL=redis://localhost:6379

# Service URLs (for local development)
AUTH_SERVICE_URL=http://localhost:8001
CHAT_SERVICE_URL=http://localhost:8002
USER_SERVICE_URL=http://localhost:8003
VECTOR_SERVICE_URL=http://localhost:8004
GATEWAY_URL=http://localhost:8000

# Security
SECRET_KEY=your-super-secret-key-change-in-production-minimum-32-characters
"""
            with open('.env', 'w') as f:
                f.write(env_content)
        
        print("✅ .env file created. Please edit it with your settings!")
        return False
    
    # Check if OpenAI key is set
    with open('.env', 'r') as f:
        content = f.read()
        if 'your-openai-api-key-here' in content:
            print("⚠️  Please update OPENAI_API_KEY in .env file with your actual API key")
            return False
    
    print("✅ .env file exists and appears configured")
    return True

def start_infrastructure():
    """Start PostgreSQL and Redis using Docker"""
    print("🚀 Starting infrastructure services...")
    try:
        # Check if Docker is available
        subprocess.check_call(['docker', '--version'], stdout=subprocess.DEVNULL)
        
        # Start PostgreSQL and Redis
        subprocess.run(['docker', 'run', '-d', '--name', 'chatbot-postgres', 
                       '-e', 'POSTGRES_DB=chatbot_db',
                       '-e', 'POSTGRES_USER=user', 
                       '-e', 'POSTGRES_PASSWORD=password',
                       '-p', '5432:5432', 'postgres:15'], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        subprocess.run(['docker', 'run', '-d', '--name', 'chatbot-redis',
                       '-p', '6379:6379', 'redis:7-alpine'],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print("✅ Infrastructure services started")
        time.sleep(5)  # Wait for services to be ready
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not available. Please install Docker or start services manually")
        return False

def test_service_health(service_name, port):
    """Test if a service is healthy"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name} (port {port}) is healthy")
            return True
        else:
            print(f"❌ {service_name} (port {port}) returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print(f"❌ {service_name} (port {port}) is not responding")
        return False

def start_service_in_background(service_dir, service_name, port):
    """Start a service in the background"""
    try:
        print(f"🚀 Starting {service_name}...")
        env = os.environ.copy()
        
        # Load .env file variables
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env[key] = value
        
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            cwd=service_dir,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait a bit and check if service is responding
        time.sleep(3)
        if test_service_health(service_name, port):
            return process
        else:
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Failed to start {service_name}: {e}")
        return None

def main():
    print("🔧 Chatbot Services Fix Tool")
    print("=" * 40)
    
    # Step 1: Check Python packages
    if not check_python_packages():
        print("❌ Package installation failed")
        return
    
    # Step 2: Check environment file
    if not check_env_file():
        print("⚠️  Please configure .env file before continuing")
        return
    
    # Step 3: Start infrastructure
    print("\n🏗️  Setting up infrastructure...")
    start_infrastructure()
    
    # Step 4: Start services
    print("\n🚀 Starting microservices...")
    
    services = [
        ('auth-service', 'Auth Service', 8001),
        ('user-service', 'User Service', 8003),
        ('vector-service', 'Vector Service', 8004),
        ('chat-service', 'Chat Service', 8002),
        ('gateway', 'Gateway', 8000),
    ]
    
    processes = []
    for service_dir, service_name, port in services:
        if os.path.exists(service_dir):
            process = start_service_in_background(service_dir, service_name, port)
            if process:
                processes.append((process, service_name))
    
    # Step 5: Start frontend
    print("\n💻 Starting frontend...")
    if os.path.exists('frontend'):
        try:
            env = os.environ.copy()
            env['GATEWAY_URL'] = 'http://localhost:8000'
            
            frontend_process = subprocess.Popen(
                [sys.executable, '-m', 'streamlit', 'run', 'app.py', '--server.port', '8501'],
                cwd='frontend',
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            processes.append((frontend_process, 'Frontend'))
            print("✅ Frontend started on port 8501")
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
    
    # Step 6: Final health check
    print("\n🏥 Final health check...")
    time.sleep(5)
    
    healthy_services = 0
    for service_dir, service_name, port in services:
        if test_service_health(service_name, port):
            healthy_services += 1
    
    # Test frontend
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend (port 8501) is accessible")
            healthy_services += 1
    except:
        print("❌ Frontend (port 8501) is not accessible")
    
    print(f"\n📊 Services Status: {healthy_services}/{len(services)+1} healthy")
    
    if healthy_services == len(services) + 1:
        print("\n🎉 All services are running successfully!")
        print("\n📱 Access points:")
        print("   Frontend: http://localhost:8501")
        print("   API Gateway: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        print("\n👤 Default login:")
        print("   Username: admin")
        print("   Password: admin123")
        
        print("\n🛑 To stop all services, press Ctrl+C")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all services...")
            for process, name in processes:
                try:
                    process.terminate()
                    print(f"✅ Stopped {name}")
                except:
                    pass
    else:
        print(f"\n⚠️  {len(services)+1-healthy_services} services are not working properly")
        print("Please check the following:")
        print("1. Your OpenAI API key is valid and has credits")
        print("2. All required ports are available (8000-8004, 8501)")
        print("3. PostgreSQL and Redis are running")
        print("4. No firewall blocking the services")

if __name__ == "__main__":
    main()