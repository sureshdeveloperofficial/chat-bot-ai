from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv
import httpx
import uuid
import json
import logging
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
import redis

load_dotenv()

app = FastAPI(title="Chat Service", version="1.0.0")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8003")
VECTOR_SERVICE_URL = os.getenv("VECTOR_SERVICE_URL", "http://localhost:8004")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("Redis connected successfully")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Using in-memory storage.")
    redis_client = None

llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=500
)

memory_store = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    username: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

def get_memory(session_id: str) -> ConversationBufferWindowMemory:
    if redis_client:
        try:
            memory_data = redis_client.get(f"memory:{session_id}")
            if memory_data:
                data = json.loads(memory_data)
                memory = ConversationBufferWindowMemory(k=10, return_messages=True)
                for msg in data.get("messages", []):
                    if msg["type"] == "human":
                        memory.chat_memory.add_user_message(msg["content"])
                    else:
                        memory.chat_memory.add_ai_message(msg["content"])
                return memory
        except Exception as e:
            logger.error(f"Error loading memory from Redis: {e}")
    
    if session_id not in memory_store:
        memory_store[session_id] = ConversationBufferWindowMemory(k=10, return_messages=True)
    return memory_store[session_id]

def save_memory(session_id: str, memory: ConversationBufferWindowMemory):
    if redis_client:
        try:
            messages = []
            for msg in memory.chat_memory.messages:
                if isinstance(msg, HumanMessage):
                    messages.append({"type": "human", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages.append({"type": "ai", "content": msg.content})
            
            memory_data = {"messages": messages}
            redis_client.setex(f"memory:{session_id}", 3600, json.dumps(memory_data))
        except Exception as e:
            logger.error(f"Error saving memory to Redis: {e}")

async def get_relevant_context(message: str, username: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{VECTOR_SERVICE_URL}/search",
                json={"query": message, "username": username, "top_k": 3}
            )
            if response.status_code == 200:
                results = response.json()
                if results.get("results"):
                    context = "\n".join([doc["content"] for doc in results["results"]])
                    return f"Relevant context:\n{context}\n\n"
    except Exception as e:
        logger.error(f"Error getting context from vector service: {e}")
    return ""

async def save_chat_history(username: str, session_id: str, user_message: str, ai_response: str):
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
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    session_id = request.session_id or str(uuid.uuid4())
    memory = get_memory(session_id)
    
    try:
        context = await get_relevant_context(request.message, request.username)
        
        enhanced_prompt = f"{context}User question: {request.message}"
        
        memory.chat_memory.add_user_message(enhanced_prompt)
        
        messages = memory.chat_memory.messages
        response = llm.invoke(messages)
        
        memory.chat_memory.add_ai_message(response.content)
        save_memory(session_id, memory)
        
        await save_chat_history(
            request.username, 
            session_id, 
            request.message, 
            response.content
        )
        
        return ChatResponse(
            response=response.content,
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat processing: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

@app.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    if redis_client:
        try:
            redis_client.delete(f"memory:{session_id}")
        except Exception as e:
            logger.error(f"Error clearing session from Redis: {e}")
    
    if session_id in memory_store:
        del memory_store[session_id]
    
    return {"message": f"Session {session_id} cleared"}

@app.get("/chat/sessions")
async def list_sessions():
    sessions = []
    
    if redis_client:
        try:
            keys = redis_client.keys("memory:*")
            sessions.extend([key.replace("memory:", "") for key in keys])
        except Exception as e:
            logger.error(f"Error listing Redis sessions: {e}")
    
    sessions.extend(list(memory_store.keys()))
    
    return {"sessions": list(set(sessions))}

@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "service": "chat",
        "openai_configured": bool(OPENAI_API_KEY),
        "redis_connected": redis_client is not None
    }
    
    if redis_client:
        try:
            redis_client.ping()
            health_status["redis_status"] = "connected"
        except:
            health_status["redis_status"] = "disconnected"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)