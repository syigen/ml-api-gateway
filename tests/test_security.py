import os
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from pydantic.v1 import EmailStr

from app.core.security import verify_api_key, APIKeyManager
from app.schemas.auth_schemas import AuthRequest
from .test_database import db_session, api_key_manager, test_key_user, background_tasks, UserAPIKeys

# Constant Values
const_key_prefix = 'sk_live_'


def test_api_key_manager_initialization(api_key_manager):
    """
    Test the initialization of the APIKeyManager class.

    Ensures that:
    - `private_salt` is set to the `API_SALT` environment variable.
    - `key_prefix` is initialized to 'sk_live_'.

    Args:
        api_key_manager: An instance or mock of the APIKeyManager class.

    Steps:
    - Patch `os.environ` with a test value for `API_SALT`.
    - Instantiate `APIKeyManager` and verify attribute values.
    """
    with patch.dict(os.environ, {'API_SALT': 'test_salt'}):
        manager = APIKeyManager()
        assert manager.private_salt == 'test_salt'
        assert manager.key_prefix == const_key_prefix


def test_api_key_manager_initialization_no_salt(api_key_manager):
    """
    Test APIKeyManager initialization without `API_SALT`.

    Ensures that:
    - A `ValueError` is raised if `API_SALT` is not set in the environment.

    Args:
        api_key_manager: An instance or mock of the APIKeyManager class.

    Steps:
    - Clear all environment variables using `patch.dict`.
    - Attempt to instantiate `APIKeyManager` and verify the exception.
    """
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            APIKeyManager()


def test_generate_key(api_key_manager):
    """
    Test the `generate_key` method of the APIKeyManager class.

    Ensures that:
    - The generated key starts with 'sk_live_'.
    - The key is longer than the prefix, indicating additional data.

    Args:
        api_key_manager: An instance or mock of the APIKeyManager class.

    Steps:
    - Call `generate_key` with a test email.
    - Assert the key starts with the correct prefix and has a valid length.
    """
    key = api_key_manager.generate_key("test@email.com")
    assert key.startswith(const_key_prefix)
    assert len(key) > len(const_key_prefix)


def test_save_key(api_key_manager, db_session, test_key_user):
    """
    Test the `save_key` method of the APIKeyManager class.

    Ensures that:
    - An API key is generated and saved to the database.
    - The saved key matches the generated key.
    - The `created_at` and `updated_at` timestamps are properly set.

    Args:
        api_key_manager: An instance or mock of the APIKeyManager class.
        db_session: A database session used for testing.
        test_key_user: A test user object with a valid `id`.

    Steps:
    - Call `save_key` with the user ID and database session.
    - Query the database to retrieve the saved key.
    - Assert that the saved key is not `None` and matches the generated key.
    - Verify that the `created_at` and `updated_at` fields are populated.
    """
    api_key = api_key_manager.save_key(test_key_user.id, db_session)

    # Verify key was saved
    saved_key = db_session.query(UserAPIKeys).filter_by(user_id=test_key_user.id).first()
    assert saved_key is not None
    assert saved_key.api_key == api_key
    assert saved_key.created_at is not None
    assert saved_key.updated_at is not None


def test_save_key_existing(api_key_manager, db_session, test_key_user):
    """
    Test the `save_key` method for an existing user key.

    Ensures that:
    - Calling `save_key` for the same user ID returns the same API key.

    Args:
        api_key_manager: An instance or mock of the APIKeyManager class.
        db_session: A database session used for testing.
        test_key_user: A test user object with a valid `id`.

    Steps:
    - Call `save_key` twice for the same user.
    - Assert that the returned keys from both calls are identical.
    """
    # First save
    first_key = api_key_manager.save_key(test_key_user.id, db_session)

    # Second save should return the same key
    second_key = api_key_manager.save_key(test_key_user.id, db_session)
    assert first_key == second_key


def test_save_key_invalid_user(api_key_manager, db_session):
    """
    Test the `save_key` method with an invalid user ID.

    Ensures that:
    - Calling `save_key` with a non-existent user ID raises a 404 HTTPException.

    Args:
        api_key_manager: An instance or mock of the APIKeyManager class.
        db_session: A database session used for testing.

    Steps:
    - Call `save_key` with an invalid user ID (e.g., 999).
    - Assert that a 404 HTTPException is raised.
    """
    with pytest.raises(HTTPException) as exc_info:
        api_key_manager.save_key(999, db_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_old_key(api_key_manager, db_session, test_key_user):
    """
    Test the `delete_old_key` method of the APIKeyManager class.

    Ensures that:
    - Old API keys are deleted based on the provided delay.
    - Only one key remains after deletion when two keys are created.

    Args:
        api_key_manager: An instance or mock of the APIKeyManager class.
        db_session: A database session used for testing.
        test_key_user: A test user object with a valid `id`.

    Steps:
    - Create two API keys with different timestamps for the same user.
    - Call `delete_old_key` with a minimal delay.
    - Verify that only one key remains for the user.

    """
    # Create multiple API keys with different timestamps
    key1 = UserAPIKeys(
        user_id=test_key_user.id,
        api_key="test_key_1",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    key2 = UserAPIKeys(
        user_id=test_key_user.id,
        api_key="test_key_2",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add_all([key1, key2])
    db_session.commit()

    # Test deletion with minimal delay
    await api_key_manager.delete_old_key(db_session, test_key_user.id, delay_minutes=0)

    # Verify only one key remains
    remaining_keys = db_session.query(UserAPIKeys).filter_by(user_id=test_key_user.id).all()
    assert len(remaining_keys) == 1


def test_reset_key(api_key_manager, db_session, test_key_user, background_tasks):
    """
    Test the `reset_key` method of the APIKeyManager class.

    Ensures that:
    - A new API key is generated and returned.
    - The new key is saved to the database with the correct user ID and timestamps.

    Args:
        api_key_manager: An instance or mock of the APIKeyManager class.
        db_session: A database session used for testing.
        test_key_user: A test user object with a valid `id`.
        background_tasks: A mock or instance for handling background tasks.

    Steps:
    - Create an `AuthRequest` with user credentials.
    - Call `reset_key` to generate and save a new API key.
    - Verify the new key is returned and stored in the database with the correct attributes.
    """
    auth_request = AuthRequest(email=EmailStr("user@email.com"), password="User@123")
    new_key = api_key_manager.reset_key(auth_request, db_session, background_tasks)

    # Verify new key
    assert new_key is not None
    assert new_key.startswith(const_key_prefix)

    # Verify database record
    key_record = db_session.query(UserAPIKeys).filter_by(api_key=new_key).first()
    assert key_record is not None
    assert key_record.user_id == test_key_user.id
    assert key_record.created_at is not None
    assert key_record.updated_at is not None


def test_reset_key_invalid_user(api_key_manager, db_session, background_tasks):
    """
    Test the `reset_key` method for an invalid user.

    Ensures that:
    - A `400 HTTPException` is raised when attempting to reset the key for a non-existent user.

    Args:
        api_key_manager: An instance or mock of the APIKeyManager class.
        db_session: A database session used for testing.
        background_tasks: A mock or instance for handling background tasks.

    Steps:
    - Create an `AuthRequest` with a non-existent user email.
    - Call `reset_key` and assert that a `400 HTTPException` is raised.
    """
    auth_request = AuthRequest(email=EmailStr("nonexistent@email.com"), password="test_password")
    with pytest.raises(HTTPException) as exc_info:
        api_key_manager.reset_key(auth_request, db_session, background_tasks)
    assert exc_info.value.status_code == 400


def test_verify_api_key(db_session, test_key_user):
    """
    Test the `verify_api_key` function.

    Ensures that:
    - The correct user is returned when a valid API key is provided.

    Args:
        db_session: A database session used for testing.
        test_key_user: A test user object with a valid `id` and `email`.

    Steps:
    - Create a test API key and store it in the database.
    - Call `verify_api_key` with the test API key.
    - Assert that the correct user is returned based on the API key.
    """
    # Create test API key
    api_key = "test_api_key_verify"
    key_record = UserAPIKeys(
        user_id=test_key_user.id,
        api_key=api_key,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(key_record)
    db_session.commit()

    # Verify key
    verified_user = verify_api_key(api_key, db_session)
    assert verified_user.id == test_key_user.id
    assert verified_user.email == test_key_user.email


def test_verify_api_key_invalid(db_session):
    """
    Test the `verify_api_key` function with an invalid API key.

    Ensures that:
    - A `401 HTTPException` is raised when an invalid API key is provided.

    Args:
        db_session: A database session used for testing.

    Steps:
    - Call `verify_api_key` with an invalid API key.
    - Assert that a `401 HTTPException` is raised.
    """
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key("invalid_key", db_session)
    assert exc_info.value.status_code == 401


def test_verify_api_key_no_user(db_session):
    """
    Test the `verify_api_key` function when the API key belongs to a non-existent user.

    Ensures that:
    - A `404 HTTPException` is raised when the API key is valid but the user is not found in the database.

    Args:
        db_session: A database session used for testing.

    Steps:
    - Create a key record with a non-existent user ID.
    - Call `verify_api_key` with the key.
    - Assert that a `404 HTTPException` is raised.
    """
    key_record = UserAPIKeys(
        user_id=999,
        api_key="test_api_key_no_user",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(key_record)
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key("test_api_key_no_user", db_session)
    assert exc_info.value.status_code == 404


def test_database_cascade_delete(db_session, test_key_user):
    """
    Test the cascading delete behavior in the database.

    Ensures that:
    - When a user is deleted, all related API keys are also deleted from the database.

    Args:
        db_session: A database session used for testing.
        test_key_user: A test user object with a valid `id`.

    Steps:
    - Create an API key record for the test user.
    - Delete the test user from the database.
    - Verify that the associated API key is also deleted.

    """
    key_record = UserAPIKeys(
        user_id=test_key_user.id,
        api_key="test_cascade_key",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(key_record)
    db_session.commit()

    db_session.delete(test_key_user)
    db_session.commit()

    deleted_key = db_session.query(UserAPIKeys).filter_by(user_id=test_key_user.id).first()
    assert deleted_key is None
