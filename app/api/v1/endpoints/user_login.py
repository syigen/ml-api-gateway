from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException

from app.db.database import get_db
from app.schemas.schemas import UserLogin, LoginResponse
from app.services.services import verify_user

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    try:
        authenticated_user = verify_user(user.email, user.password, db)
        if not authenticated_user:
            return LoginResponse(
                email=authenticated_user.email,
                message="Login successful.",
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
