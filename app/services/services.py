from sqlalchemy.orm import Session
from app.db.models import User
from passlib.context import CryptContext

from app.schemas.schemas import AuthRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_user(user:AuthRequest, db: Session):
    email_user = db.query(User).filter(User.email == user.email).first()
    if email_user and pwd_context.verify(user.password, email_user.hashed_password):
        email_user.password = None
        return email_user
    raise ValueError("Credentials do not match!")