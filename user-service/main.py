from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

from database import get_db, create_tables, User, ChatSession, ChatMessage

app = FastAPI(title="User Data Service", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

create_tables()

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

class ChatMessageSave(BaseModel):
    username: str
    session_id: str
    user_message: str
    ai_response: str
    timestamp: str

class ChatMessageResponse(BaseModel):
    id: int
    user_message: str
    ai_response: str
    timestamp: datetime

class ChatSessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    messages: List[ChatMessageResponse]

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.get("/users/{username}", response_model=UserResponse)
async def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/chat/save")
async def save_chat_message(message: ChatMessageSave, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == message.username).first()
    if not user:
        user = User(username=message.username, email=f"{message.username}@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    session = db.query(ChatSession).filter(
        ChatSession.session_id == message.session_id
    ).first()
    
    if not session:
        session = ChatSession(session_id=message.session_id, user_id=user.id)
        db.add(session)
        db.commit()
        db.refresh(session)
    
    chat_message = ChatMessage(
        session_id=session.id,
        user_message=message.user_message,
        ai_response=message.ai_response,
        timestamp=datetime.fromisoformat(message.timestamp.replace('Z', '+00:00'))
    )
    
    db.add(chat_message)
    db.commit()
    
    return {"message": "Chat message saved successfully"}

@app.get("/chat/history", response_model=List[ChatSessionResponse])
async def get_chat_history(
    username: str = Query(...),
    session_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return []
    
    query = db.query(ChatSession).filter(ChatSession.user_id == user.id)
    
    if session_id:
        query = query.filter(ChatSession.session_id == session_id)
    
    sessions = query.all()
    
    result = []
    for session in sessions:
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.timestamp).all()
        
        result.append(ChatSessionResponse(
            session_id=session.session_id,
            created_at=session.created_at,
            messages=[
                ChatMessageResponse(
                    id=msg.id,
                    user_message=msg.user_message,
                    ai_response=msg.ai_response,
                    timestamp=msg.timestamp
                ) for msg in messages
            ]
        ))
    
    return result

@app.delete("/chat/history/{session_id}")
async def delete_chat_session(session_id: str, username: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    db.query(ChatMessage).filter(ChatMessage.session_id == session.id).delete()
    db.delete(session)
    db.commit()
    
    return {"message": f"Chat session {session_id} deleted successfully"}

@app.get("/users/{username}/stats")
async def get_user_stats(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    total_sessions = db.query(ChatSession).filter(ChatSession.user_id == user.id).count()
    total_messages = db.query(ChatMessage).join(ChatSession).filter(
        ChatSession.user_id == user.id
    ).count()
    
    return {
        "username": username,
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "member_since": user.created_at
    }

@app.get("/health")
async def health_check():
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "service": "user",
        "database_status": db_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)