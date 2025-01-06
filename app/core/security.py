from datetime import datetime
import hashlib
import os
from typing import Type

from sqlalchemy.orm import Session, InstrumentedAttribute
from fastapi import HTTPException
from app.db.models import UserAPIKeys, User


class APIKeyManager:
    """Manages API key operations including generation, verification, and storage."""

    def __init__(self) -> None:
        self.private_salt = self._load_private_salt()
        self.key_prefix = "sk_live_"

    @staticmethod
    def _load_private_salt() -> str:
        """
        Load private salt from environment variables.

        Returns:
            str: The private salt value

        Raises:
            ValueError: If the 'API_SALT' environment variable is not set
        """
        private_salt = os.getenv("API_SALT")
        if not private_salt:
            raise ValueError("Environment variable 'API_SALT' is not set")
        return private_salt

    def generate_key(self, email: str) -> str:
        """
        Generate a secure API key based on email and salt.

        Args:
            email (str): The email address to use in generating the key

        Returns:
            str: The generated API key
        """
        key_base = f"{email}{self.private_salt}{datetime.utcnow().timestamp()}"
        generated_key = hashlib.sha256(key_base.encode('utf-8')).hexdigest()
        return f"{self.key_prefix}{generated_key}"

    def save_key(self, user_id: int, db: Session) -> InstrumentedAttribute | str:
        """
        Save a generated API key for a user.

        Args:
            user_id (int): The integer ID of the user
            db (Session): The database session

        Returns:
            str: The generated API key

        Raises:
            HTTPException: If there is an error saving the API key
        """
        # Check for an existing key
        existing_key = db.query(UserAPIKeys).filter(UserAPIKeys.user_id == user_id).first()
        if existing_key:
            return existing_key.api_key

        # Get the user record
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")

        # Generate a new API key
        api_key = self.generate_key(str(user.email))

        # Save the key to the database
        new_key = UserAPIKeys(
            user_id=user_id,
            api_key=api_key,
            created_at=datetime.utcnow()
        )
        db.add(new_key)
        db.commit()

        return api_key

def verify_api_key(api_key: str, db: Session) -> Type[User]:
    """
    Verify an API key and return the associated user.

    Args:
        api_key (str): The API key to verify
        db (Session): The database session

    Returns:
        User: The user associated with the API key

    Raises:
        HTTPException: If the API key is invalid
    """
    # Get the API key record
    key_record = db.query(UserAPIKeys).filter(UserAPIKeys.api_key == api_key).first()
    if not key_record:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Get and return the user record
    user = db.query(User).filter(User.id == key_record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user