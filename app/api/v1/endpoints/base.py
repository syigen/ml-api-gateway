from fastapi import APIRouter, HTTPException, FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .utils import get_password_hash
from .dependencies import get_user

from app.db.database import get_db
from app.db.models import User
from app.schemas.schemas import UserResponse, UserCreate

router = APIRouter()

@router.get("/")
async def root():
    return {"version": "1.0.0"}

users = {
    "user1": "12345",
    "user2": "ABCDE",
}

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/user/login/{users}/")
def login(request: LoginRequest):
    if request.username in users and users[request.username] == request.password:
        return {"message": "Login successful", "username": request.username}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

#connecting the database(not completed yet)
@router.post("/login", response_model=UserResponse)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
