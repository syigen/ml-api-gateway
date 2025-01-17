import os
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from pydantic.v1 import EmailStr
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

from app.core.security import APIKeyManager
from app.db.database import get_db
from app.schemas.user_schemas import UserCreate
from main import app

# Database Configuration and Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test-ml-safe-app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password Cryptography Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# User Model: Represents the "users" table in the database
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    # Defines a relationship to the UserAPIKeys model
    api_keys = relationship(
        'UserAPIKeys',
        back_populates='user',
        cascade='all, delete-orphan'
    )


# UserAPIKeys Model: Represents the "user_api_keys" table in the database
class UserAPIKeys(Base):
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    api_key = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)

    # Relationship to the User model, providing access to the user associated with the API key
    user = relationship('User', back_populates='api_keys')


@pytest.fixture(scope="session")
def db_session():
    """
    Fixture to set up and tear down the database session for tests.

    - Creates database tables and a test user with an API key.
    - Yields the session for use in tests.
    - Cleans up by closing the session and dropping tables after tests.

    Returns:
        TestingSessionLocal: A session for interacting with the database.

    Scope:
        "session" scope, set up once per test session.
    """
    # Create tables and start session
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Add test user and API key
    test_key_user = User(
        email="user@email.com",
        hashed_password=pwd_context.hash("User@123"),
        created_at=datetime.now()
    )
    session.add(test_key_user)
    session.commit()

    user_api_key = UserAPIKeys(
        user_id=test_key_user.id,
        api_key="sk_live_22e4591b335d125f7d06b5b074bf23058a126145155f7f620eded7485e31bfe",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(user_api_key)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def api_key_manager():
    """
    Fixture to provide an instance of APIKeyManager with a mocked `API_SALT` environment variable.

    This fixture patches `API_SALT` with the value `'test_salt'` and returns an instance of
    `APIKeyManager` initialized with this mock value.

    Returns:
        APIKeyManager: An instance of the APIKeyManager class.
    """
    with patch.dict(os.environ, {'API_SALT': 'test_salt'}):
        return APIKeyManager()


@pytest.fixture
def background_tasks():
    """
    Fixture to provide an instance of `BackgroundTasks`.

    This fixture returns a new instance of `BackgroundTasks`, which can be used
    to schedule tasks for background execution in tests.

    Returns:
        BackgroundTasks: An instance of the `BackgroundTasks` class.
    """
    return BackgroundTasks()


@pytest.fixture
def test_key_user(db_session):
    """
    Fixture to retrieve the test user from the database.

    This fixture queries the database for a user with the email
    `user@email.com` and returns the first matching user record.

    Args:
        db_session (Session): The database session used to query the User model.

    Returns:
        User: The user record with the email `user@email.com` from the test database.
    """
    return db_session.query(User).filter_by(email="user@email.com").first()


@pytest.fixture
def client():
    """
    Fixture for creating a test client with an overridden database session.

    This fixture:
    - Overrides the `get_db` dependency to use a test database session.
    - Yields a `TestClient` for sending requests to the FastAPI application.

    Returns:
        TestClient: A client for making HTTP requests to the FastAPI app with a test database.

    Steps:
    - Creates a new `TestingSessionLocal` instance to be used as the database session.
    - Yields the `TestClient` to interact with the app during tests.
    - Closes the database session after the test is completed.
    """

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_db():
    """Fixture that provides a test database session and handles cleanup.

    Creates a new database session for testing and cleans up user data
    after each test to ensure a fresh state.

    Yields:
        Session: SQLAlchemy database session for testing
    """
    db = TestingSessionLocal()
    yield db
    db.query(Base.metadata.tables['users']).delete()  # Cleanup
    db.query(Base.metadata.tables['user_api_keys']).delete()  # Cleanup
    db.commit()


@pytest.fixture
def sample_user() -> UserCreate:
    """
    Creates a sample user for testing.

    Returns:
        User: A user creation schema with test data.
    """
    return UserCreate(
        email=EmailStr("Dileepa@gmail.com"),
        password="Sadeepa@2004"
    )


@pytest.fixture
def duplicate_user() -> UserCreate:
    """
    Creates a duplicate user with the same email for testing uniqueness constraints.

    Returns:
        User: A user creation schema with the same email as sample_user.
    """
    return UserCreate(
        email=EmailStr("Sadeepa@gmail.com"),
        password="Sadeepa@2004"
    )
