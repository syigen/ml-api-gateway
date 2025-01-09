"""Test suite for user registration endpoint functionality.

This module contains pytest fixtures and test cases for the user registration API endpoint.
It uses SQLite as a test database and includes tests for successful registration,
duplicate user handling, invalid email formats, and missing required fields.

Fixtures:
    client: Provides a TestClient instance with a test database session
    test_db: Provides a test database session and handles cleanup after tests

Test Cases:
    - test_register_user_success: Tests successful user registration
    - test_register_user_duplicate: Tests duplicate email registration handling
    - test_register_user_invalid_email: Tests invalid email format validation
    - test_register_user_missing_fields: Tests required field validation
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from app.db.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    """Fixture that provides a test client with a test database session.

    Overrides the database dependency with a test database session and yields
    a TestClient instance for making test requests.

    Yields:
        TestClient: A configured test client for making HTTP requests
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


def test_register_user_success(client, test_db):
    """Test successful user registration.

    Verifies that a user can be registered with valid credentials and
    receives the expected success response.

    Args:
        client (TestClient): The test client fixture
        test_db (Session): The test database session fixture
    """
    response = client.post(
        "api/v1/user/register",
        json={
            "email": "testuser@example.com",
            "password": "Password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["message"] == "User registered successfully."


def test_register_user_duplicate(client, test_db):
    """Test duplicate user registration handling.

    Verifies that attempting to register with an existing email address
    returns an appropriate error response.

    Args:
        client (TestClient): The test client fixture
        test_db (Session): The test database session fixture
    """
    # Create a user first
    client.post(
        "api/v1/user/register",
        json={
            "email": "duplicateuser@example.com",
            "password": "Password123"
        }
    )

    # Try creating the same user again
    response = client.post(
        "api/v1/user/register",
        json={
            "email": "duplicateuser@example.com",
            "password": "Password1"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_register_user_invalid_email(client, test_db):
    """Test invalid email format validation.

    Verifies that attempting to register with an invalid email format
    returns a validation error response.

    Args:
        client (TestClient): The test client fixture
        test_db (Session): The test database session fixture
    """
    response = client.post(
        "api/v1/user/register",
        json={
            "email": "invalidemail",
            "password": "Password1"
        }
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_register_user_missing_fields(client, test_db):
    """Test required field validation.

    Verifies that attempting to register without required fields
    returns a validation error response.

    Args:
        client (TestClient): The test client fixture
        test_db (Session): The test database session fixture
    """
    response = client.post(
        "api/v1/user/register",
        json={}
    )
    assert response.status_code == 422