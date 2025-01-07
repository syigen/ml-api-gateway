from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.v1.deps import validate_api_key
from app.core.security import APIKeyManager
from app.db.database import get_db
from app.db.models import User
from app.schemas.schemas import AuthRequest

router = APIRouter()

@router.post("/reset-api-key")
async def reset_api_key(
    login_data: AuthRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Resets the user's API key and schedules the deletion of the old key after expiration.

    Args:
        login_data (AuthRequest): User's login credentials.
        background_tasks (BackgroundTasks): For running background tasks.
        user (User): The authenticated user.
        db (Session): The database session.

    Returns:
        dict: Contains the user's email, new API key, and a message about the expiration of the old key.

    Example:
        {
            "email": "user@example.com",
            "api_key": "new_generated_key",
            "message": "Your previous API key will expire in 5 minutes."
        }
    """
    new_key = APIKeyManager().reset_key(login_data, db, background_tasks)
    return {
        "email": user.email,
        "api_key": new_key,
        "message": "Your previous API key will expire in 5 minutes."
    }
