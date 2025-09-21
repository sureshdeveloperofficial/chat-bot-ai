#!/usr/bin/env python3
"""
Local Installation Script for Microservice Chatbot
This script installs all dependencies and sets up the local environment
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, description="", check=True):
    """Run a command and handle errors"""
    print(f"🔄 {description}")
    print(f"   Running: {command}")
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True)
        
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   Error details: {e.stderr.strip()}")
        return False

def check_python_version():
    """Check if Python version is 3.10+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_prerequisites():
    """Check if required software is installed"""
    print("\n🔍 Checking Prerequisites...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check pip
    if not shutil.which("pip"):
        print("❌ pip not found. Please install pip")
        return False
    print("✅ pip - OK")
    
    # Check if we can install packages
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip working - OK")
    except subprocess.CalledProcessError:
        print("❌ pip not working properly")
        return False
    
    return True

def create_virtual_environment():
    """Create virtual environment"""
    print("\n🔧 Creating Virtual Environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("📁 Virtual environment already exists")
        return True
    
    return run_command(f"{sys.executable} -m venv venv", "Creating virtual environment")

def get_venv_python():
    """Get path to virtual environment Python"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\python.exe"
    else:
        return "venv/bin/python"

def get_venv_pip():
    """Get path to virtual environment pip"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\pip.exe"
    else:
        return "venv/bin/pip"

def upgrade_pip():
    """Upgrade pip in virtual environment"""
    print("\n📦 Upgrading pip...")
    venv_python = get_venv_python()
    return run_command(f"{venv_python} -m pip install --upgrade pip", "Upgrading pip")

def install_global_dependencies():
    """Install main project dependencies"""
    print("\n📦 Installing Global Dependencies...")
    venv_pip = get_venv_pip()
    return run_command(f"{venv_pip} install -r requirements.txt", "Installing main dependencies")

def install_service_dependencies():
    """Install dependencies for each service"""
    print("\n📦 Installing Service Dependencies...")
    
    services = [
        "auth-service",
        "gateway", 
        "chat-service",
        "user-service",
        "vector-service",
        "frontend"
    ]
    
    venv_pip = get_venv_pip()
    
    for service in services:
        req_file = Path(service) / "requirements.txt"
        if req_file.exists():
            success = run_command(
                f"{venv_pip} install -r {req_file}",
                f"Installing {service} dependencies"
            )
            if not success:
                return False
        else:
            print(f"⚠️  No requirements.txt found for {service}")
    
    return True

def create_env_files():
    """Create .env files from examples"""
    print("\n📝 Creating Environment Files...")
    
    # Main .env file
    if not Path(".env").exists():
        if Path(".env.example").exists():
            shutil.copy(".env.example", ".env")
            print("✅ Created main .env file")
        else:
            print("⚠️  No .env.example found")
    
    # Service .env files
    services = ["auth-service", "gateway", "chat-service", "user-service", "vector-service", "frontend"]
    
    for service in services:
        service_env = Path(service) / ".env"
        service_env_example = Path(service) / ".env.example"
        
        if not service_env.exists() and service_env_example.exists():
            shutil.copy(service_env_example, service_env)
            print(f"✅ Created {service}/.env file")

def install_additional_dependencies():
    """Install additional system dependencies if needed"""
    print("\n🔧 Installing Additional Dependencies...")
    
    venv_pip = get_venv_pip()
    
    # Additional packages that might be needed
    additional_packages = [
        "python-multipart",
        "aiofiles",
        "httpx[http2]",
    ]
    
    for package in additional_packages:
        run_command(
            f"{venv_pip} install {package}",
            f"Installing {package}",
            check=False  # Don't fail if already installed
        )

def check_docker():
    """Check if Docker is available (optional)"""
    print("\n🐳 Checking Docker (Optional)...")
    
    if shutil.which("docker"):
        print("✅ Docker found")
        # Check if Docker is running
        try:
            subprocess.run(["docker", "ps"], check=True, capture_output=True)
            print("✅ Docker is running")
            return True
        except subprocess.CalledProcessError:
            print("⚠️  Docker found but not running")
            return False
    else:
        print("⚠️  Docker not found (optional for infrastructure)")
        return False

def display_next_steps():
    """Display next steps to user"""
    print("\n" + "="*60)
    print("🎉 INSTALLATION COMPLETE!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file with your OpenAI API key:")
    print("   OPENAI_API_KEY=your-actual-api-key-here")
    
    print("\n2. Start infrastructure (choose one option):")
    print("   Option A - With Docker (recommended):")
    print("   docker-compose up postgres redis -d")
    print("\n   Option B - Install locally:")
    print("   - Install PostgreSQL and create database 'chatbot_db'")
    print("   - Install Redis server")
    
    print("\n3. Run the application:")
    if platform.system() == "Windows":
        print("   .\\start_local.bat")
    else:
        print("   ./start_local.sh")
    
    print("\n4. Access the application:")
    print("   Frontend: http://localhost:8501")
    print("   API Gateway: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    
    print("\n👤 Default Users:")
    print("   Username: admin, Password: admin123")
    print("   Username: user, Password: user123")

def main():
    """Main installation function"""
    print("🚀 Microservice Chatbot - Local Installation")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install missing components.")
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("\n❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Upgrade pip
    if not upgrade_pip():
        print("\n❌ Failed to upgrade pip")
        sys.exit(1)
    
    # Install global dependencies
    if not install_global_dependencies():
        print("\n❌ Failed to install global dependencies")
        sys.exit(1)
    
    # Install service dependencies
    if not install_service_dependencies():
        print("\n❌ Failed to install service dependencies")
        sys.exit(1)
    
    # Install additional dependencies
    install_additional_dependencies()
    
    # Create environment files
    create_env_files()
    
    # Check Docker (optional)
    check_docker()
    
    # Display next steps
    display_next_steps()

if __name__ == "__main__":
    main()