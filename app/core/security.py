from datetime import datetime
import hashlib
import os
from typing import Optional, Dict

from fastapi import HTTPException
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import UserAPIKeys, User

class APIKeyManager:
    """Manages API key operations including generation, verification, and storage."""

    def __init__(self) -> None:
        self.private_salt = self._load_private_salt()
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
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

    def hash_key(self, key: str) -> str:
        """
        Hash a key using bcrypt.

        Args:
            key (str): The key to hash

        Returns:
            str: The hashed version of the provided key

        Raises:
            ValueError: If the key is empty
        """
        if not key:
            raise ValueError("Key must not be empty")
        return self.pwd_context.hash(key)

    def verify_key(self, plain_key: str, hashed_key: str) -> bool:
        """
        Verify if a plain key matches its hashed version.

        Args:
            plain_key (str): The plain key to verify
            hashed_key (str): The hashed version of the key

        Returns:
            bool: True if the keys match, False otherwise

        Raises:
            ValueError: If either the plain key or hashed key is not provided
        """
        if not plain_key or not hashed_key:
            raise ValueError("Both plain key and hashed key must be provided")
        return self.pwd_context.verify(plain_key, hashed_key)

    def generate_key(self, email: EmailStr) -> str:
        """
        Generate a secure API key based on email and salt.

        Args:
            email (EmailStr): The email address to use in generating the key

        Returns:
            str: The generated API key
        """
        key_base = f"{email}{self.private_salt}{datetime.utcnow().timestamp()}"
        generated_key = hashlib.sha256(key_base.encode('utf-8')).hexdigest()
        return f"{self.key_prefix}{generated_key}"

    async def save_key(self, user_id: int, db: AsyncSession) -> Dict[str, str]:
        """
        Save a generated API key for a user.

        Args:
            user_id (int): The integer ID of the user
            db (AsyncSession): The database session

        Returns:
            Dict[str, str]: Dictionary containing the generated API key

        Raises:
            HTTPException: If there is an error saving the API key
        """
        try:
            # Check for existing key
            existing_key = await db.execute(select(UserAPIKeys).where(UserAPIKeys.user_id == user_id))
            existing_key = existing_key.scalars().first()
            print(existing_key)
            if existing_key:
                return {"api_key": existing_key.api_key}

            # Get user and generate key
            user = await self._get_user(user_id, db)
            api_key = self.generate_key(user.email)
            print(api_key)

            # Save key
            new_key = UserAPIKeys(
                user_id=user_id,
                api_key=self.hash_key(api_key),
                created_at=datetime.utcnow()
            )
            db.add(new_key)
            await db.commit()

            return {"api_key": api_key}
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save API key: {str(e)}"
            )

    async def verify_api_key(self, db: AsyncSession, api_key: str) -> Optional[User]:
        """
        Verify an API key and return the associated user.

        Args:
            db (AsyncSession): The database session
            api_key (str): The API key to verify

        Returns:
            Optional[User]: The user associated with the API key if valid

        Raises:
            HTTPException: If the API key is invalid or there is an error verifying it
        """
        try:
            # Get key record
            result = await db.execute(select(UserAPIKeys).where(UserAPIKeys.api_key == api_key))
            key_record = result.scalars().first()
            if not key_record:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid API key"
                )

            # Verify key
            if not self.verify_key(api_key, key_record.api_key):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid API key"
                )

            # Get and return user
            user = await self._get_user(key_record.user_id, db)
            return user

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error verifying API key: {str(e)}"
            )

    async def _get_user(self, user_id: int, db: AsyncSession) -> User:
        """
        Get user by ID.

        Args:
            user_id (int): The integer ID of the user
            db (AsyncSession): The database session

        Returns:
            User: The user record

        Raises:
            HTTPException: If user is not found
        """
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        return user

