import pytest
from fastapi.testclient import TestClient
from main import app
from app.db.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    yield db
    db.query(Base.metadata.tables['users']).delete()  # Cleanup
    db.commit()

def test_invalid_login_user(client, test_db):
    response = client.post(
        "api/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "Password123"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

def test_login_user_invalid_email(client, test_db):
    response = client.post(
        "api/v1/auth/login",
        json={
            "email": "invalidemail",
            "password": "Password1"
        }
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_login_user_missing_fields(client, test_db):
    response = client.post(
        "api/v1/auth/login",
        json={}
    )
    assert response.status_code == 422