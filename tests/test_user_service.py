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

from app.services.user_service import create_user, get_password_hash


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
