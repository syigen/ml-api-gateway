import pytest
from unittest.mock import patch

from app.schemas.user import UserCreate

def test_user_create_valid():
    user = UserCreate(email="test@example.com", password="Password123")
    assert user.email == "test@example.com"
    assert user.password == "Password123"

@pytest.mark.parametrize("email, password, value_error " , [
    ("test@example.com", "password", "Password must contain at least one digit"),
    ("test@example.com", "Password", "Password must contain at least one digit"),
    ("test@example.com", "password1", "Password must contain at least one uppercase letter"),
    ("test@example.com", "PASSWORD", "Password must contain at least one digit"),
    ("test@example.com", "PASSWORD1", "Password must contain at least one lowercase letter"),
])
def test_user_create_invalid_password(email, password,value_error):
    with pytest.raises(ValueError, match=value_error):
        UserCreate(email=email, password=password)

@pytest.mark.parametrize("email, password", [
    ("not-an-email", "Password123"),
    ("testmail.com", "Password123"),
    ("testmail@.com", "Password123"),
    ("testmail@gamil", "Password123"),
    ("testmail@gamil.", "Password123"),
])
def test_user_create_invalid_email(email, password):
    with pytest.raises(ValueError):
        UserCreate(email=email, password=password)

@patch('app.schemas.user.UserCreate.validate_password')
def test_user_create_validates_password(mock_validate_password):
    mock_validate_password.side_effect = ValueError("Password must contain at least one digit")
    with pytest.raises(ValueError):
        UserCreate(email="test@example.com", password="password")