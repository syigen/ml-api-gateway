from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import User, UserAPIKeys
from passlib.context import CryptContext

from app.schemas.schemas import AuthRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_user(user:AuthRequest, db: Session):
    email_user = db.query(User).filter(User.email == user.email).first()
    if email_user and pwd_context.verify(user.password, email_user.hashed_password):
        email_user.password = None
        return email_user
    raise ValueError("Credentials do not match!")

def get_user_api_key(user_id: int, db: Session) -> Type[UserAPIKeys]:
    user_api_key = db.query(UserAPIKeys).filter(UserAPIKeys.user_id == user_id).first()
    if not user_api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return user_api_key