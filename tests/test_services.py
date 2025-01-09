import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from app.schemas.auth_schemas import AuthRequest
from app.services.auth_services import verify_user
from app.db.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

valid_user_credentials = AuthRequest(email="user1@example.com", password="password1")
invalid_user_credentials = AuthRequest(email="user1@example.com", password="wrongpassword")
non_existent_user_credentials = AuthRequest(email="nonexistent@example.com", password="password")

mock_users = [
    User(id=1, email="user1@example.com", hashed_password=pwd_context.hash("password1")),
    User(id=2, email="user2@example.com", hashed_password=pwd_context.hash("password2")),
    User(id=3, email="user3@example.com", hashed_password=pwd_context.hash("password3")),
]

def mock_query_filter(email):
    for user in mock_users:
        if user.email == email:
            return user
    return None

# Test: Valid credentials
def test_verify_user_valid_credentials():
    """
        Test Case: Valid Credentials
        - Verifies that the `verify_user` function authenticates a user with correct credentials.
        - Preconditions: User exists in the database with email `user1@example.com` and password `password1`.
        - Steps:
            1. Mock the database session to return the correct user.
            2. Call `verify_user` with valid credentials.
        - Expected Outcome: Returns a `User` object with the correct email and ID.
    """
    mock_db = MagicMock(spec=Session)
    mock_db.query().filter().first.side_effect = lambda: mock_query_filter(valid_user_credentials.email)
    result = verify_user(valid_user_credentials, mock_db)
    assert result is not None
    assert result.email == valid_user_credentials.email


# Test: Invalid password
def test_verify_user_invalid_password():
    mock_db = MagicMock(spec=Session)
    mock_db.query().filter().first.side_effect = lambda: mock_query_filter(invalid_user_credentials.email)
    with pytest.raises(ValueError) as excinfo:
        verify_user(invalid_user_credentials, mock_db)
    assert str(excinfo.value) == "Credentials do not match!"


# Test: Non-existent user
def test_verify_user_non_existent_user():
    mock_db = MagicMock(spec=Session)
    mock_db.query().filter().first.side_effect = lambda: mock_query_filter(non_existent_user_credentials.email)
    with pytest.raises(ValueError) as excinfo:
        verify_user(non_existent_user_credentials, mock_db)
    assert str(excinfo.value) == "Credentials do not match!"
