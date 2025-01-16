from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """
        Represents a user in the database.

        Attributes:
        - __tablename__ (str): The name of the database table.
        - id (Column): The user's ID.
        - email (Column): The user's email address.
        - hashed_password (Column): The user's hashed password.
        - created_at (Column): The timestamp when the user was created.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    api_keys = relationship(
        "UserAPIKeys",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class UserAPIKeys(Base):
    """
        Represents the API keys associated with users.

        Attributes:
            __tablename__ (str): The name of the database table ("user_api_keys").
            id (int): The primary key for the API key record.
            user_id (int): The ID of the user this API key belongs to. Foreign key referencing the "users" table.
            api_key (str): The API key string.
            created_at (datetime): The timestamp when the API key was created. Defaults to the current time.
            updated_at (datetime): The timestamp when the API key was last updated. Automatically updates on modification.
            user (relationship): The relationship to the User model, enabling back-population of API keys.
        """
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    api_key = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)

    user = relationship("User", back_populates="api_keys")
