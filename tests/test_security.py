import pytest
from datetime import datetime
import os
from unittest.mock import patch
from fastapi import HTTPException

from app.core.security import verify_api_key, APIKeyManager
from app.schemas.schemas import AuthRequest
from .test_database import db_session, api_key_manager, test_key_user, background_tasks, UserAPIKeys


def test_api_key_manager_initialization(api_key_manager):
    with patch.dict(os.environ, {'API_SALT': 'test_salt'}):
        manager = APIKeyManager()
        assert manager.private_salt == 'test_salt'
        assert manager.key_prefix == 'sk_live_'


def test_api_key_manager_initialization_no_salt(api_key_manager):
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            APIKeyManager()


def test_generate_key(api_key_manager):
    key = api_key_manager.generate_key("test@email.com")
    assert key.startswith("sk_live_")
    assert len(key) > len("sk_live_")


def test_save_key(api_key_manager, db_session, test_key_user):
    api_key = api_key_manager.save_key(test_key_user.id, db_session)

    # Verify key was saved
    saved_key = db_session.query(UserAPIKeys).filter_by(user_id=test_key_user.id).first()
    assert saved_key is not None
    assert saved_key.api_key == api_key
    assert saved_key.created_at is not None
    assert saved_key.updated_at is not None


def test_save_key_existing(api_key_manager, db_session, test_key_user):
    # First save
    first_key = api_key_manager.save_key(test_key_user.id, db_session)

    # Second save should return the same key
    second_key = api_key_manager.save_key(test_key_user.id, db_session)
    assert first_key == second_key


def test_save_key_invalid_user(api_key_manager, db_session):
    with pytest.raises(HTTPException) as exc_info:
        api_key_manager.save_key(999, db_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_old_key(api_key_manager, db_session, test_key_user):
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
    auth_request = AuthRequest(email="user@email.com", password="User@123")
    new_key = api_key_manager.reset_key(auth_request, db_session, background_tasks)

    # Verify new key
    assert new_key is not None
    assert new_key.startswith("sk_live_")

    # Verify database record
    key_record = db_session.query(UserAPIKeys).filter_by(api_key=new_key).first()
    assert key_record is not None
    assert key_record.user_id == test_key_user.id
    assert key_record.created_at is not None
    assert key_record.updated_at is not None


def test_reset_key_invalid_user(api_key_manager, db_session, background_tasks):
    auth_request = AuthRequest(email="nonexistent@email.com", password="test_password")
    with pytest.raises(HTTPException) as exc_info:
        api_key_manager.reset_key(auth_request, db_session, background_tasks)
    assert exc_info.value.status_code == 400


def test_verify_api_key(db_session, test_key_user):
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
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key("invalid_key", db_session)
    assert exc_info.value.status_code == 401


def test_verify_api_key_no_user(db_session):
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
