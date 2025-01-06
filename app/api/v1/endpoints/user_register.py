from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException

from app.db.database import get_db
from app.schemas.user import UserCreate, RegisterResponse
from app.services.user_service import create_user

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        created_user = create_user(user, db)
        return RegisterResponse(email=created_user.email, message="User  registered successfully.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))