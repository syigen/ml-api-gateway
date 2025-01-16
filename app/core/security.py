import asyncio
import hashlib
import os
from datetime import datetime
from typing import Type, Union

from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, InstrumentedAttribute

from app.db.models import UserAPIKeys, User
from app.schemas.auth_schemas import AuthRequest
from app.services.auth_services import verify_user


class APIKeyManager:
    """Manages API key operations including generation, verification, and storage."""

    def __init__(self) -> None:
        self.private_salt = self._load_private_salt()
        self.key_prefix = self._load_key_prefix()

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

    @staticmethod
    def _load_key_prefix() -> str:
        """
        Load key prefix from environment variables.

        Returns:
            str: The key prefix value

        Raises:
            ValueError: If the 'API_KEY_PREFIX' environment variable is not set
        """
        key_prefix = os.getenv("API_KEY_PREFIX")
        if not key_prefix:
            raise ValueError("Environment variable 'API_KEY_PREFIX' is not set")
        return key_prefix

    def generate_key(self, email: str) -> str:
        """
        Generate a secure API key based on email and salt.

        Args:
            email (EmailStr): The email address to use in generating the key

        Returns:
            str: The generated API key
        """
        key_base = f"{email}{self.private_salt}{datetime.now().timestamp()}"
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
            created_at=datetime.now()
        )
        db.add(new_key)
        db.commit()

        return api_key

    @staticmethod
    async def delete_old_key(db: Session, user_id: int, delay_minutes: int = 5):
        """
        Asynchronously delete the old API key after a specified delay.

        Args:
            db (Session): Database session
            user_id (int): User ID
            delay_minutes (int): Delay in minutes before deletion
        """
        await asyncio.sleep(delay_minutes * 60)

        try:
            # Get all API keys for the user except the newest one
            old_keys = (
                db.query(UserAPIKeys)
                .filter(UserAPIKeys.user_id == user_id)
                .order_by(UserAPIKeys.created_at.desc())
                .offset(1)
                .all()
            )

            # Delete old keys
            for key in old_keys:
                db.delete(key)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error deleting old API keys: {str(e)}")

    def reset_key(self, user: AuthRequest, db: Session, background_tasks: BackgroundTasks) -> Union[str, None]:
        """
        Reset the API key for a user.

        Args:
            user (AuthRequest): The user object containing the email of the user.
            db (Session): The database session.
            background_tasks: FastAPI BackgroundTasks for async execution.

        Returns:
            str: The new generated API key.

        Raises:
            HTTPException: If the user is not found or there's an error updating the API key.
        """
        # Fetch the user from the database

        try:
            current_user = verify_user(user, db)
            if not current_user:
                raise HTTPException(status_code=404, detail="User not found")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # Generate a new API key
        try:
            new_api_key = self.generate_key(str(current_user.email))

            # Update the API key and timestamp
            store_key = UserAPIKeys(
                user_id=int(str(current_user.id)),
                api_key=new_api_key,
                created_at=datetime.now()
            )
            db.add(store_key)
            db.commit()

            # Schedule the deletion of old keys
            background_tasks.add_task(
                self.delete_old_key,
                db=db,
                user_id=int(str(current_user.id)),
                delay_minutes=5
            )

            return new_api_key
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating API key: {str(e)}")


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
