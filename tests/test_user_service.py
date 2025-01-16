"""
Test module for user-related services and utilities.

This module contains test cases for user creation, password hashing, and duplicate user handling.
It uses pytest fixtures for database session management and sample test data.

Dependencies:
    - pytest
    - SQLAlchemy
    - app.db.models
    - app.schemas.user
    - app.services.user_service
"""

import pytest
from pydantic.v1 import EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.schemas.user_schemas import UserCreate
from app.services.user_service import create_user, get_password_hash

# Test Database Setup
db_url = "sqlite:///:memory:"
engine = create_engine(db_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_session():
    """
    Creates and manages a SQLAlchemy database session for testing.

    Yields:
        SQLAlchemy Session: A database session for test operations.

    Notes:
        - Uses an in-memory SQLite database
        - Creates all tables before yielding the session
        - Closes the session after tests complete
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def sample_user():
    """
    Creates a sample user for testing.

    Returns:
        UserCreate: A user creation schema with test data.
    """
    return UserCreate(
        email=EmailStr("Dileepa@gmail.com"),
        password="Sadeepa@2004"
    )


@pytest.fixture
def duplicate_user():
    """
    Creates a duplicate user with the same email for testing uniqueness constraints.

    Returns:
        UserCreate: A user creation schema with the same email as sample_user.
    """
    return UserCreate(
        email=EmailStr("Sadeepa@gmail.com"),
        password="Sadeepa@2004"
    )


def test_get_password_hash():
    """
    Tests the password hashing functionality.

    Verifies that:
        - The hashing function returns a non-null value
        - The hashed password is different from the original
        - The hash has a non-zero length
    """
    password = "testpassword"
    hashed_password = get_password_hash(password)

    assert hashed_password is not None
    assert hashed_password != password
    assert len(hashed_password) > 0


def test_create_user_success(db_session, sample_user):
    """
    Tests successful user creation.

    Args:
        db_session: The test database session fixture
        sample_user: The sample user creation data fixture

    Verifies that:
        - The created user's email matches the input
        - The password is properly hashed
    """
    user = create_user(sample_user, db_session)

    assert user.email == sample_user.email
    assert user.hashed_password != sample_user.password


def test_create_user_duplicate_email(db_session, duplicate_user):
    """
    Tests the handling of duplicate email registration attempts.

    Args:
        db_session: The test database session fixture
        duplicate_user: A user creation fixture with a duplicate email

    Verifies that:
        - Creating a user with a duplicate email raises ValueError
        - The error message matches the expected string
    """
    create_user(duplicate_user, db_session)

    with pytest.raises(ValueError, match="Email already registered."):
        create_user(duplicate_user, db_session)
