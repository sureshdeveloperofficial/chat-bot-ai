from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uuid
import json
import logging
from datetime import datetime
import random
import httpx

app = FastAPI(title="Mock Chat Service", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USER_SERVICE_URL = "http://localhost:8003"

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    username: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

# Mock responses for testing
MOCK_RESPONSES = [
    "Hello! I'm a mock chatbot for testing. Your message was: '{message}'",
    "That's interesting! Tell me more about that.",
    "I understand what you're saying. How can I help you further?",
    "Thanks for sharing that with me! Is there anything else you'd like to discuss?",
    "I'm here to help. What would you like to know?",
    "That's a great question! Here's what I think about that topic.",
    "I see what you mean. Let me provide some insights on that.",
    "Thank you for that information. Would you like to explore this topic more?",
]

async def save_chat_history(username: str, session_id: str, user_message: str, ai_response: str):
    """Save chat to user service"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"{USER_SERVICE_URL}/chat/save",
                json={
                    "username": username,
                    "session_id": session_id,
                    "user_message": user_message,
                    "ai_response": ai_response,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            logger.info(f"Chat history saved for user {username}")
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    # Generate a mock response
    response_template = random.choice(MOCK_RESPONSES)
    response = response_template.format(message=request.message)
    
    # Add some context-aware responses
    message_lower = request.message.lower()
    if "hello" in message_lower or "hi" in message_lower:
        response = f"Hello {request.username}! Nice to meet you. How can I assist you today?"
    elif "help" in message_lower:
        response = "I'm here to help! I'm currently running in mock mode for testing. In production, I would use advanced AI to provide more intelligent responses."
    elif "bye" in message_lower or "goodbye" in message_lower:
        response = "Goodbye! It was nice chatting with you. Feel free to come back anytime!"
    elif "test" in message_lower:
        response = "This is indeed a test! The mock chat service is working correctly. All your messages are being processed and stored."
    
    # Save to chat history
    await save_chat_history(request.username, session_id, request.message, response)
    
    return ChatResponse(
        response=response,
        session_id=session_id,
        timestamp=datetime.utcnow().isoformat()
    )

@app.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    return {"message": f"Session {session_id} cleared (mock implementation)"}

@app.get("/chat/sessions")
async def list_sessions():
    return {"sessions": []}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mock-chat",
        "openai_configured": False,
        "redis_connected": False,
        "mode": "mock"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)