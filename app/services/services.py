from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.db.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_user(email: EmailStr, password: str, db: Session):
    email_user = db.query(User).filter(User.email == email).first()
    if email_user and pwd_context.verify(password, email_user.password):
        email_user.password = None
        return email_user
    raise ValueError("Password does not match!")