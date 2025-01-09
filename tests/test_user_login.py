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
    """
        Fixture to provide a FastAPI TestClient for testing API endpoints.

        This fixture overrides the FastAPI dependency `get_db` with an in-memory SQLite database
        to isolate tests and ensure they do not affect the production database.
        Yields:
            TestClient: A test client to interact with the FastAPI app.
    """

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
    """
        Fixture for initializing and cleaning up the test database.

        Yields:
            Database session: A SQLAlchemy session connected to the in-memory SQLite database.
        Performs cleanup to delete test data after the test completes.
    """
    db = TestingSessionLocal()
    yield db
    db.query(Base.metadata.tables['users']).delete()  # Cleanup
    db.commit()


def test_invalid_login_user(client, test_db):
    """
        Test case to verify that login fails with invalid credentials.

        This test attempts to log in a user with incorrect credentials (email and/or password)
        and expects a 400 Bad Request response.

        Args:
            client (TestClient): The fixture providing the test client.
            test_db: The fixture providing the test database session.
    """
    response = client.post(
        "api/v1/user/login",
        json={
            "email": "testuser@example.com",
            "password": "Password123"
        }
    )
    assert response.status_code == 400
    data = response.json()


def test_login_user_invalid_email(client, test_db):
    """
        Test case to verify that invalid email format results in a validation error.

        This test submits a login request with an invalid email format and expects a
        422 Unprocessable Entity response, with a `detail` field in the returned JSON.

        Args:
            client (TestClient): The fixture providing the test client.
            test_db: The fixture providing the test database session.
    """
    response = client.post(
        "api/v1/user/login",
        json={
            "email": "invalidemail",
            "password": "Password1"
        }
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_login_user_missing_fields(client, test_db):
    """
        Test case to verify that missing required fields in the login request raises a validation error.

        This test submits an empty request body and expects a 422 Unprocessable Entity response.

        Args:
            client (TestClient): The fixture providing the test client.
            test_db: The fixture providing the test database session.
    """
    response = client.post(
        "api/v1/user/login",
        json={}
    )
    assert response.status_code == 422
