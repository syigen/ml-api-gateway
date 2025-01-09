from typing import Type

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.db.models import User, UserAPIKeys
from app.schemas.auth_schemas import AuthRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_user(user: AuthRequest, db: Session):
    """
        Verifies the user's credentials.

        Args:
        - user (AuthRequest): The user's login credentials.
        - db (Session): The database session.

        Returns:
        - User: The authenticated user.

        Raises:
        - ValueError: If the credentials do not match.
    """

    email_user = db.query(User).filter(User.email == user.email).first()
    if email_user and pwd_context.verify(user.password, email_user.hashed_password):
        email_user.password = None
        return email_user
    raise ValueError("Credentials do not match!")


def get_user_api_key(user_id: int, db: Session) -> Type[UserAPIKeys]:
    """
     Retrieve the API key for a specific user.

     Args:
         user_id (int): The ID of the user.
         db (Session): The database session to execute queries.

     Returns:
         UserAPIKeys: The API key object associated with the user.

     Raises:
         HTTPException: If no API key is found for the user (401 Unauthorized).
     """
    user_api_key = db.query(UserAPIKeys).filter(UserAPIKeys.user_id == user_id).first()
    if not user_api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return user_api_key
