import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.schemas.user import UserCreate
from app.services.user_service import create_user, get_password_hash

# Test Database Setup
db_url = "sqlite:///:memory:"
engine = create_engine(db_url)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture
def sample_user():
    return UserCreate(
        email="Dileepa@gmail.com",
        password="Sadeepa@2004"
    )

@pytest.fixture
def duplicate_user():
    return UserCreate(
        email="Dileepa@gmail.com",
        password="Sadeepa@2004"
    )

# Tests
def test_get_password_hash():
    password = "testpassword"
    hashed_password = get_password_hash(password)

    assert hashed_password is not None
    assert hashed_password != password
    assert len(hashed_password) > 0

def test_create_user_success(db_session, sample_user):
    user = create_user(sample_user, db_session)

    assert user.email == sample_user.email
    assert user.hashed_password != sample_user.password

def test_create_user_duplicate_email(db_session, sample_user, duplicate_user):
    with pytest.raises(ValueError, match="Email already registered."):
        create_user(duplicate_user, db_session)
