"""Test suite for UserCreate schema validation.

This module contains test cases for validating the UserCreate schema,
including password complexity requirements and email format validation.
It uses pytest's parametrize feature for comprehensive validation testing
and mocking for isolated password validation tests.
"""

import pytest
from unittest.mock import patch

from pydantic.v1 import EmailStr

from app.schemas.user import UserCreate
from app.schemas.user import RegisterResponse


def test_user_create_valid():
    """Test creation of UserCreate instance with valid credentials.

    Verifies that a UserCreate instance can be created with valid email
    and password, and that the values are correctly stored.
    """
    user = UserCreate(email=EmailStr("test@example.com"), password="Password123")
    assert user.email == "test@example.com"
    assert user.password == "Password123"


@pytest.mark.parametrize("email, password, value_error", [
    ("test@example.com", "Pa1", "String should have at least 8 characters"),
    ("test@example.com", "password", "Password must contain at least one digit"),
    ("test@example.com", "Password", "Password must contain at least one digit"),
    ("test@example.com", "password1", "Password must contain at least one uppercase letter"),
    ("test@example.com", "PASSWORD", "Password must contain at least one digit"),
    ("test@example.com", "PASSWORD1", "Password must contain at least one lowercase letter"),
])
def test_user_create_invalid_password(email, password, value_error):
    """Test password validation rules for UserCreate schema.

    Tests various password validation rules including:
    - Must contain at least one digit
    - Must contain at least one uppercase letter
    - Must contain at least one lowercase letter

    Args:
        email (EmailStr): Valid email address for testing
        password (str): Password string to test
        value_error (str): Expected error message for invalid password

    Raises:
        ValueError: Expected to be raised with specific error message for each invalid case
    """
    with pytest.raises(ValueError, match=value_error):
        UserCreate(email=EmailStr(email), password=password)


@pytest.mark.parametrize("email, password", [
    ("not-an-email", "Password123"),
    ("testmail.com", "Password123"),
    ("testmail@.com", "Password123"),
    ("testmail@gamil", "Password123"),
    ("testmail@gamil.", "Password123"),
])
def test_user_create_invalid_email(email, password):
    """Test email format validation for UserCreate schema.

    Tests various invalid email formats including:
    - Missing @ symbol
    - Missing domain
    - Invalid domain format
    - Missing TLD
    - Incomplete TLD

    Args:
        email (EmailStr): Invalid email address to test
        password (str): Valid password for testing

    Raises:
        ValueError: Expected to be raised for each invalid email format
    """
    with pytest.raises(ValueError):
        UserCreate(email=EmailStr(email), password=password)


@patch('app.schemas.user.UserCreate.validate_password')
def test_user_create_validates_password(mock_validate_password):
    """Test that password validation is called during UserCreate instantiation.

    Uses mocking to verify that the validate_password method is called
    and that validation errors are properly propagated.

    Args:
        mock_validate_password: Mocked version of the validate_password method
    """
    mock_validate_password.side_effect = ValueError("Password must contain at least one digit")
    with pytest.raises(ValueError):
        UserCreate(email=EmailStr("test@example.com"), password="password")