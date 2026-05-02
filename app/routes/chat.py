from fastapi import APIRouter, HTTPException, Depends, status
from app.models.request_models import ChatRequest, ChatResponse
from app.services.llm_service import llm_service
from app.services.db_service import DatabaseService
from app.services.auth_service import auth_service
from datetime import datetime
from typing import List
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
db_service = DatabaseService()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user=Depends(get_current_user)):
    try:
        user_id = user["sub"]
        # Handle Session ID (ensure we have one for DB storage)
        session_id = request.sessionId or f"sess_{user_id}_{datetime.now().timestamp()}"

        # 1. Save the user's current message to DB
        if request.messages:
            user_msg = request.messages[-1]
            await db_service.save_message(
                session_id=session_id,
                role=user_msg.role,
                content=user_msg.content,
                mood=request.mood,
                user_id=user_id
            )

        # 2. Get the AI response
        reply = await llm_service.get_chat_response(request)

        # 3. Save the AI's response to DB
        await db_service.save_message(
            session_id=session_id,
            role="assistant",
            content=reply,
            user_id=user_id
        )

        return ChatResponse(
            reply=reply,
            timestamp=datetime.now()
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/history/{session_id}")
async def get_history(session_id: str, user=Depends(get_current_user)):
    try:
        user_id = user["sub"]
        history = await db_service.get_chat_history(session_id, user_id)
        return {
            "sessionId": session_id,
            "messages": history
        }
    except Exception as e:
        print(f"History Error: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve chat history")

@router.get("/sessions")
async def list_sessions(user=Depends(get_current_user)):
    try:
        user_id = user["sub"]
        sessions = await db_service.get_all_sessions(user_id)
        return sessions
    except Exception as e:
        print(f"Sessions Error: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve sessions")
