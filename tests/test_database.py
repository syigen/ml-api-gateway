from fastapi import BackgroundTasks
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
import pytest
from unittest.mock import patch
import os

from app.core.security import APIKeyManager

SQLALCHEMY_DATABASE_URL = "sqlite:///./test-ml-safe-app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

@pytest.fixture(scope="session")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    test_key_user = User(
        email="user@email.com",
        hashed_password= pwd_context.hash("User@123"),
        created_at=datetime.now()
    )

    session.add(test_key_user)
    session.commit()

    user_api_key = UserAPIKeys(
        user_id=test_key_user.id,
        api_key="sk_live_22e4591b335d125f7d06b5b074bf23058a126145155f7f620eded7485e31bfe",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(user_api_key)
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
def test_key_user(db_session):
    return  db_session.query(User).filter_by(email="user@email.com").first()

