from typing import Type

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.core.security import APIKeyManager, verify_api_key
from app.db.database import get_db
from app.db.models import User

api_manager = APIKeyManager()

def validate_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)) -> Type[User]:
    """
    Validate the API key provided in the request header.

    Args:
        x_api_key (str): API key from the header
        db (Session): Database session

    Returns:
        User: Authenticated user

    Raises:
        HTTPException: If the API key is invalid
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = verify_api_key(x_api_key, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return user
