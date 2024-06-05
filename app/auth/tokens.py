import jwt

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import Depends

from auth.hashing import SECRET_KEY, ALGORITHM, verify_password
from auth.crud import get_user_by_username
from db.dependencies import get_db

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(
        username: str, 
        password: str,
        db: Session = Depends(get_db), 
    ):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user