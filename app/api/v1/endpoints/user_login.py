from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException

from app.db.database import get_db
from app.schemas.schemas import AuthRequest, AuthResponse
from app.services.services import verify_user

router = APIRouter()

@router.post("/login", response_model=AuthResponse)
def login_user(user: AuthRequest, db: Session = Depends(get_db)):
    try:
        authenticated_user = verify_user(user, db)
        if not authenticated_user:
            raise HTTPException(
                status_code=401, detail="Invalid email or password"
            )
        return AuthResponse(
            email=authenticated_user.email,
            message="Login successful.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))