import pytest
from unittest.mock import MagicMock

from pydantic.v1 import EmailStr
from sqlalchemy.orm import Session
from app.schemas.auth_schemas import AuthRequest
from app.services.auth_services import verify_user
from app.db.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

valid_user_credentials = AuthRequest(email=EmailStr("user1@example.com"), password="password1")
invalid_user_credentials = AuthRequest(email=EmailStr("user1@example.com"), password="wrongpassword")
non_existent_user_credentials = AuthRequest(email=EmailStr("nonexistent@example.com"), password="password")

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
    Test Case: Valid user login credentials

    Description:
        This test case verifies that the `verify_user` function successfully authenticates
        and returns the correct user when valid credentials are provided.

    Steps:
        1. Mock the database session query to return a user with matching credentials.
        2. Call the `verify_user` function with valid user credentials.
        3. Validate that the `verify_user` function returns the correct `User` object.

    Expected Result:
        The function returns a `User` object with:
        - Email matching the valid user credentials
        - Correct user ID
    """
    mock_db = MagicMock(spec=Session)
    mock_db.query().filter().first.side_effect = lambda: mock_query_filter(valid_user_credentials.email)
    result = verify_user(valid_user_credentials, mock_db)
    assert result is not None
    assert result.email == valid_user_credentials.email


# Test: Invalid password
def test_verify_user_invalid_password():
    """
        Test Case: Invalid user password

        Description:
            This test case ensures that the `verify_user` function raises a `ValueError`
            when an invalid password is provided for an existing user.

        Steps:
            1. Mock the database session query to return a user corresponding to the email provided in the credentials.
            2. Call the `verify_user` function with invalid credentials (correct email but wrong password).
            3. Confirm that a `ValueError` with the message "Credentials do not match!" is raised.

        Expected Result:
            A `ValueError` is raised with the correct error message.
    """
    mock_db = MagicMock(spec=Session)
    mock_db.query().filter().first.side_effect = lambda: mock_query_filter(invalid_user_credentials.email)
    with pytest.raises(ValueError) as excinfo:
        verify_user(invalid_user_credentials, mock_db)
    assert str(excinfo.value) == "Credentials do not match!"


# Test: Non-existent user
def test_verify_user_non_existent_user():
    """
        Test Case: Non-existent user

        Description:
            This test checks if the `verify_user` function raises a `ValueError`
            when attempting to authenticate with credentials for a user that does not exist in the database.

        Steps:
            1. Mock the database session query to simulate no user being found for the provided email.
            2. Call the `verify_user` function with credentials of a non-existent user.
            3. Validate that a `ValueError` with the message "Credentials do not match!" is raised.

        Expected Result:
            A `ValueError` is raised with the appropriate error message.
        """
    mock_db = MagicMock(spec=Session)
    mock_db.query().filter().first.side_effect = lambda: mock_query_filter(non_existent_user_credentials.email)
    with pytest.raises(ValueError) as excinfo:
        verify_user(non_existent_user_credentials, mock_db)
    assert str(excinfo.value) == "Credentials do not match!"
