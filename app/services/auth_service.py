import bcrypt
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.core.config import settings

SECRET_KEY = getattr(settings, "SECRET_KEY", "sukoon_super_secret_key_change_this_in_prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

class AuthService:
    def get_password_hash(self, password: str) -> str:
        # SHA256 first to avoid bcrypt 72-byte limit
        hashed_input = hashlib.sha256(password.encode()).digest()
        return bcrypt.hashpw(hashed_input, bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        hashed_input = hashlib.sha256(plain_password.encode()).digest()
        return bcrypt.checkpw(hashed_input, hashed_password.encode('utf-8'))

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload if payload.get("sub") else None
        except JWTError:
            return None

auth_service = AuthService()