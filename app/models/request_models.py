from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    mood: Optional[str] = None
    sessionId: Optional[str] = None
    intensity: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    timestamp: datetime

# --- Auth Models ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

