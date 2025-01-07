import pytest
from datetime import datetime
import os
from unittest.mock import patch
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from fastapi import BackgroundTasks, HTTPException
from app.core.security import APIKeyManager, verify_api_key
from app.schemas.schemas import AuthRequest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test-ml-safe-app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define test models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    api_keys = relationship(
        'UserAPIKeys',
        back_populates='user',
        cascade='all, delete-orphan'
    )


class UserAPIKeys(Base):
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    api_key = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)
    user = relationship('User', back_populates='api_keys')

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    test_user = User(
        email="test@email.com",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNhyZiBUpj2je",
        created_at=datetime.now()
    )
    session.add(test_user)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def api_key_manager():
    with patch.dict(os.environ, {'API_SALT': 'test_salt'}):
        return APIKeyManager()


@pytest.fixture
def background_tasks():
    return BackgroundTasks()


@pytest.fixture
def test_user(db_session):
    return db_session.query(User).filter_by(email="test@email.com").first()


def test_api_key_manager_initialization():
    with patch.dict(os.environ, {'API_SALT': 'test_salt'}):
        manager = APIKeyManager()
        assert manager.private_salt == 'test_salt'
        assert manager.key_prefix == 'sk_live_'


def test_api_key_manager_initialization_no_salt():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError):
            APIKeyManager()


def test_generate_key(api_key_manager):
    key = api_key_manager.generate_key("test@email.com")
    assert key.startswith("sk_live_")
    assert len(key) > len("sk_live_")


def test_save_key(api_key_manager, db_session, test_user):
    api_key = api_key_manager.save_key(test_user.id, db_session)

    # Verify key was saved
    saved_key = db_session.query(UserAPIKeys).filter_by(user_id=test_user.id).first()
    assert saved_key is not None
    assert saved_key.api_key == api_key
    assert saved_key.created_at is not None
    assert saved_key.updated_at is not None


def test_save_key_existing(api_key_manager, db_session, test_user):
    # First save
    first_key = api_key_manager.save_key(test_user.id, db_session)

    # Second save should return the same key
    second_key = api_key_manager.save_key(test_user.id, db_session)
    assert first_key == second_key


def test_save_key_invalid_user(api_key_manager, db_session):
    with pytest.raises(HTTPException) as exc_info:
        api_key_manager.save_key(999, db_session)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_old_key(api_key_manager, db_session, test_user):
    # Create multiple API keys with different timestamps
    key1 = UserAPIKeys(
        user_id=test_user.id,
        api_key="test_key_1",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    key2 = UserAPIKeys(
        user_id=test_user.id,
        api_key="test_key_2",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add_all([key1, key2])
    db_session.commit()

    # Test deletion with minimal delay
    await api_key_manager.delete_old_key(db_session, test_user.id, delay_minutes=0)

    # Verify only one key remains
    remaining_keys = db_session.query(UserAPIKeys).filter_by(user_id=test_user.id).all()
    assert len(remaining_keys) == 1


def test_reset_key(api_key_manager, db_session, test_user, background_tasks):
    auth_request = AuthRequest(email="test@email.com", password="test_password")
    new_key = api_key_manager.reset_key(auth_request, db_session, background_tasks)

    # Verify new key
    assert new_key is not None
    assert new_key.startswith("sk_live_")

    # Verify database record
    key_record = db_session.query(UserAPIKeys).filter_by(api_key=new_key).first()
    assert key_record is not None
    assert key_record.user_id == test_user.id
    assert key_record.created_at is not None
    assert key_record.updated_at is not None


def test_reset_key_invalid_user(api_key_manager, db_session, background_tasks):
    auth_request = AuthRequest(email="nonexistent@email.com", password="test_password")
    with pytest.raises(HTTPException) as exc_info:
        api_key_manager.reset_key(auth_request, db_session, background_tasks)
    assert exc_info.value.status_code == 404


def test_verify_api_key(db_session, test_user):
    # Create test API key
    api_key = "test_api_key_verify"
    key_record = UserAPIKeys(
        user_id=test_user.id,
        api_key=api_key,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(key_record)
    db_session.commit()

    # Verify key
    verified_user = verify_api_key(api_key, db_session)
    assert verified_user.id == test_user.id
    assert verified_user.email == test_user.email


def test_verify_api_key_invalid(db_session):
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key("invalid_key", db_session)
    assert exc_info.value.status_code == 401


def test_verify_api_key_no_user(db_session):
    # Create API key for non-existent user
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


def test_database_cascade_delete(db_session, test_user):
    # Create API key for user
    key_record = UserAPIKeys(
        user_id=test_user.id,
        api_key="test_cascade_key",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(key_record)
    db_session.commit()

    # Delete user and verify API key is also deleted
    db_session.delete(test_user)
    db_session.commit()

    # Verify API key was cascade deleted
    deleted_key = db_session.query(UserAPIKeys).filter_by(user_id=test_user.id).first()
    assert deleted_key is None