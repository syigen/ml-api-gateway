from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..core.security import APIKeyManager
from ..db.models import User
from ..schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_user(user: UserCreate, db: Session):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError("Email already registered.")

    hashed_password = get_password_hash(user.password)
    new_user = User(email=str(user.email), hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    #Generate API key and save it to the database
    api_key = APIKeyManager().save_key(new_user.id, db)
    return new_user