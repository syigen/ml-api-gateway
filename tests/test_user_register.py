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

from fastapi.testclient import TestClient


def test_register_user_success(client, test_db):
    """Test successful user registration.

    Verifies that a user can be registered with valid credentials and
    receives the expected success response.

    Args:
        client (TestClient): The test client fixture
        test_db (Session): The test database session fixture
    """
    response = client.post(
        "api/v1/auth/register",
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
        "api/v1/auth/register",
        json={
            "email": "duplicateuser@example.com",
            "password": "Password123"
        }
    )

    # Try creating the same user again
    response = client.post(
        "api/v1/auth/register",
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
        "api/v1/auth/register",
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
        "api/v1/auth/register",
        json={}
    )
    assert response.status_code == 422
