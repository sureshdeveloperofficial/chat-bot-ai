from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import os
from dotenv import load_dotenv
import json
import logging

load_dotenv()

app = FastAPI(title="API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
CHAT_SERVICE_URL = os.getenv("CHAT_SERVICE_URL", "http://localhost:8002")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8003")
VECTOR_SERVICE_URL = os.getenv("VECTOR_SERVICE_URL", "http://localhost:8004")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/verify",
                headers={"Authorization": f"Bearer {credentials.credentials}"}
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return response.json()
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable"
        )

@app.post("/auth/login")
async def login(user_login: UserLogin):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/login",
                json=user_login.dict()
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Login failed")
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable"
        )

@app.post("/auth/register")
async def register(user_register: UserRegister):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/register",
                json=user_register.dict()
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Registration failed")
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable"
        )

@app.post("/chat")
async def chat(message: ChatMessage, user: Dict = Depends(verify_token)):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{CHAT_SERVICE_URL}/chat",
                json={
                    "message": message.message,
                    "session_id": message.session_id,
                    "username": user["username"]
                }
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Chat service error")
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chat service unavailable"
        )

@app.get("/chat/history")
async def get_chat_history(session_id: Optional[str] = None, user: Dict = Depends(verify_token)):
    try:
        async with httpx.AsyncClient() as client:
            params = {"username": user["username"]}
            if session_id:
                params["session_id"] = session_id
            
            response = await client.get(
                f"{USER_SERVICE_URL}/chat/history",
                params=params
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Failed to get chat history")
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service unavailable"
        )

@app.post("/documents/upload")
async def upload_document(request: Request, user: Dict = Depends(verify_token)):
    try:
        body = await request.body()
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{VECTOR_SERVICE_URL}/documents/upload",
                content=body,
                headers={"content-type": request.headers.get("content-type")},
                params={"username": user["username"]}
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Document upload failed")
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector service unavailable"
        )

@app.get("/documents")
async def list_documents(user: Dict = Depends(verify_token)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{VECTOR_SERVICE_URL}/documents",
                params={"username": user["username"]}
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Failed to list documents")
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vector service unavailable"
        )

@app.get("/health")
async def health_check():
    services_status = {}
    
    services = {
        "auth": AUTH_SERVICE_URL,
        "chat": CHAT_SERVICE_URL,
        "user": USER_SERVICE_URL,
        "vector": VECTOR_SERVICE_URL
    }
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, url in services.items():
            try:
                response = await client.get(f"{url}/health")
                services_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                services_status[service_name] = "unavailable"
    
    return {
        "status": "healthy",
        "service": "gateway",
        "services": services_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)