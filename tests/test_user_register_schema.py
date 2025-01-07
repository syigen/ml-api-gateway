import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from unittest.mock import patch

from app.schemas.user import UserCreate

def test_user_create_valid():
    user = UserCreate(email="test@example.com", password="Password123")
    assert user.email == "test@example.com"
    assert user.password == "Password123"

@pytest.mark.parametrize("email, password", [
    ("test@example.com", "password"),
    ("test@example.com", "Password"),
    ("test@example.com", "password1"),
    ("test@example.com", "PASSWORD"),
    ("test@example.com", "PASSWORD1"),
])
def test_user_create_invalid_password(email, password):
    with pytest.raises(ValueError):
        UserCreate(email=email, password=password)

@pytest.mark.parametrize("email, password", [
    ("not-an-email", "Password123"),
    ("testmail.com", "Password123"),
    ("testmail@.com", "Password123"),
    ("testmail@gamil", "Password123"),
    ("testmail@gamil.", "Password123"),
])
def test_user_create_invalid_email(email,password):
    with pytest.raises(ValueError):
        UserCreate(email=email, password=password)

@patch('app.schemas.user.UserCreate.validate_password')
def test_user_create_validates_password(mock_validate_password):
    mock_validate_password.side_effect = ValueError("Password must contain at least one digit")
    with pytest.raises(ValueError):
        UserCreate(email="test@example.com", password="password")
