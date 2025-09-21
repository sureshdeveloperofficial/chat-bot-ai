#!/usr/bin/env python3
"""
Quick fix script for common issues in the chatbot project
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def create_sqlite_database():
    """Create SQLite database for user service"""
    print("🔧 Setting up SQLite database for user service...")
    
    db_path = Path("user-service/chatbot.db")
    
    try:
        # Create the database file if it doesn't exist
        conn = sqlite3.connect(str(db_path))
        
        # Create tables
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ SQLite database created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating SQLite database: {e}")
        return False

def update_user_service_config():
    """Update user service to use SQLite instead of PostgreSQL"""
    print("🔧 Updating user service configuration...")
    
    env_content = """DATABASE_URL=sqlite:///./chatbot.db"""
    
    env_path = Path("user-service/.env")
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print("✅ User service configuration updated!")

def check_openai_api_key():
    """Check if OpenAI API key is configured"""
    print("🔑 Checking OpenAI API key...")
    
    # Check main .env file
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path) as f:
            content = f.read()
            if "OPENAI_API_KEY=sk-" in content or "your-openai-api-key" not in content:
                print("✅ OpenAI API key appears to be configured")
                return True
    
    print("⚠️  OpenAI API key not found or using placeholder")
    print("   Please update your .env file with a valid OpenAI API key")
    print("   Or use a mock chat service for testing")
    return False

def create_mock_chat_response():
    """Create a simple mock chat service for testing without OpenAI"""
    print("🤖 Creating mock chat service...")
    
    mock_file = Path("chat-service/mock_chat.py")
    mock_content = '''
from fastapi import FastAPI
from pydantic import BaseModel
import uuid
from datetime import datetime

app = FastAPI(title="Mock Chat Service", version="1.0.0")

class ChatRequest(BaseModel):
    message: str
    session_id: str = None
    username: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    # Simple mock responses
    responses = [
        "Hello! I'm a mock chatbot. Your message was: " + request.message,
        "That's interesting! Tell me more.",
        "I understand. How can I help you further?",
        "Thanks for sharing that with me!",
        "I'm here to help. What would you like to know?"
    ]
    
    import random
    response = random.choice(responses)
    
    return ChatResponse(
        response=response,
        session_id=session_id,
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mock-chat",
        "openai_configured": False,
        "redis_connected": False
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
'''
    
    with open(mock_file, "w") as f:
        f.write(mock_content)
    
    print("✅ Mock chat service created!")
    print("   You can run it with: python chat-service/mock_chat.py")

def start_services():
    """Start individual services"""
    print("🚀 Starting services...")
    
    services = [
        ("auth-service", "main.py", 8001),
        ("user-service", "main.py", 8003),
        ("vector-service", "main.py", 8004),
        ("gateway", "main.py", 8000),
    ]
    
    print("To start services manually, run these commands in separate terminals:")
    for service, script, port in services:
        print(f"   cd {service} && python {script}")
    
    print(f"   cd frontend && streamlit run app.py")

def main():
    print("🔧 Quick Fix for Chatbot Issues")
    print("=" * 40)
    
    # Fix 1: Setup SQLite database
    create_sqlite_database()
    update_user_service_config()
    
    # Fix 2: Check OpenAI API key
    has_openai = check_openai_api_key()
    if not has_openai:
        create_mock_chat_response()
    
    # Fix 3: Instructions to start services
    start_services()
    
    print("\n🎉 Quick fixes applied!")
    print("\n📝 Next steps:")
    print("1. If you have OpenAI API key issues, use the mock chat service")
    print("2. Start each service in a separate terminal")
    print("3. Access frontend at http://localhost:8501")
    print("4. Test with default users: admin/admin123 or user/user123")

if __name__ == "__main__":
    main()