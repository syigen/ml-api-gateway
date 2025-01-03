from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..db.models import User
from ..schemas.user_create import UserCreate

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
    return new_user