from fastapi import APIRouter, HTTPException, Depends, status
from app.models.request_models import UserCreate, UserResponse, Token, LoginRequest
from app.services.auth_service import auth_service
from app.services.db_service import DatabaseService
from datetime import datetime

router = APIRouter()
db_service = DatabaseService()

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
    user = await db_service.db["users"].find_one({"email": user_data.email})
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = auth_service.get_password_hash(user_data.password)
    user_doc = {
        "email": user_data.email,
        "username": user_data.username,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }

    result = await db_service.db["users"].insert_one(user_doc)
    user_id = str(result.inserted_id)

    return UserResponse(id=user_id, email=user_data.email, username=user_data.username)

@router.post("/login", response_model=Token)
async def login(user_data: LoginRequest):
    user = await db_service.db["users"].find_one({"email": user_data.email})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not auth_service.verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = auth_service.create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]}
    )
    return Token(access_token=access_token, token_type="bearer")