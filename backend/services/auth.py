# services/auth.py

import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from db.database import get_user_by_email, create_user

SECRET_KEY = os.getenv("JWT_SECRET", "visa-for-you-secret-key-2024")
ALGORITHM  = "HS256"
EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(days=EXPIRE_DAYS)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def register_user(name: str, email: str, password: str, is_admin: bool = False):
    existing = get_user_by_email(email)
    if existing:
        return None, "Email already registered"
    hashed = hash_password(password)
    user = create_user(name=name, email=email, hashed_password=hashed, is_admin=is_admin)
    token = create_token({"user_id": user.id, "email": user.email, "is_admin": user.is_admin})
    return token, None

def login_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None, None, "User not found"
    if not verify_password(password, user.password):
        return None, None, "Incorrect password"
    token = create_token({"user_id": user.id, "email": user.email, "is_admin": user.is_admin})
    return token, user, None