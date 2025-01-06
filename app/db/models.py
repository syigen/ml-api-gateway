from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
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
