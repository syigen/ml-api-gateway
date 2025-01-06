from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException

from app.db.database import get_db
from app.schemas.schemas import AuthRequest, AuthResponse
from app.services.services import verify_user, get_user_api_key

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login_user(user: AuthRequest, db: Session = Depends(get_db)):
    """
        Handles user login.

        Args:
        - user (AuthRequest): The user's login credentials.
        - db (Session): The database session.

        Returns:
        - AuthResponse: The authenticated user's details.

        Raises:
        - HTTPException: If the login credentials are invalid or an internal error occurs.
        """
    try:
        authenticated_user = verify_user(user, db)
        if not authenticated_user:
            raise HTTPException(
                status_code=401, detail="Invalid email or password"
            )
        # Get and return the API key
        api_key = get_user_api_key(authenticated_user.id, db).api_key
        return AuthResponse(
            email=authenticated_user.email,
            id=authenticated_user.id,
            api_key=str(api_key)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
