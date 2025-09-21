#!/usr/bin/env python3
"""
Quick fix script to resolve common service issues
"""
import subprocess
import time
import sys
import os

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    print("🔧 Quick Fix for Chatbot Services")
    print("="*40)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("⚠️  Creating .env file from template...")
        if os.path.exists('.env.example'):
            run_command('copy .env.example .env', 'Creating .env file')
        else:
            print("❌ .env.example not found!")
            return
    
    # Stop and clean existing services
    print("\n🛑 Stopping existing services...")
    run_command('docker-compose down', 'Stopping services')
    
    # Clean up containers
    print("\n🧹 Cleaning up containers...")
    run_command('docker-compose rm -f', 'Removing containers')
    
    # Start infrastructure first
    print("\n🏗️ Starting infrastructure services...")
    run_command('docker-compose up -d postgres redis', 'Starting PostgreSQL and Redis')
    
    # Wait for database
    print("\n⏳ Waiting for database to be ready...")
    time.sleep(15)
    
    # Initialize database
    print("\n📊 Initializing database...")
    run_command('python init_database.py', 'Database initialization')
    
    # Start all services
    print("\n🚀 Starting all services...")
    run_command('docker-compose up -d', 'Starting all services')
    
    # Wait for services
    print("\n⏳ Waiting for services to start...")
    time.sleep(30)
    
    # Test services
    print("\n🏥 Testing services...")
    run_command('python test_services.py', 'Service health check')
    
    print("\n✅ Quick fix complete!")
    print("\n📱 Access the application:")
    print("   Frontend: http://localhost:8501")
    print("   API Gateway: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n⚠️  If OpenAI API errors persist:")
    print("   1. Check your OpenAI API key in .env")
    print("   2. Verify your OpenAI account has credits")
    print("   3. Check API usage limits")

if __name__ == "__main__":
    main()