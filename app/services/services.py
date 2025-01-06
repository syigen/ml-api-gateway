from sqlalchemy.orm import Session
from app.db.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if user and pwd_context.verify(password, user.password):
        return user
    return None
