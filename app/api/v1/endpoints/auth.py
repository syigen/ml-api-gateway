from fastapi import Depends, APIRouter, HTTPException
from pydantic.v1 import EmailStr
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth_schemas import AuthRequest, AuthResponse
from app.schemas.user_schemas import UserCreate, RegisterResponse
from app.services.auth_services import verify_user, get_user_api_key
from app.services.user_service import create_user

router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
        Registers a new user.

        Args:
            user (User): User registration details
            db (Session): Database session

        Returns:
            RegisterResponse: Newly created user's email and success message
        """
    try:
        # Create the user
        created_user = create_user(user, db)
        return RegisterResponse(email=EmailStr(created_user.email), message="User registered successfully.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
