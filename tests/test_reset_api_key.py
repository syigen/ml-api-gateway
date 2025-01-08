import pytest
from fastapi.testclient import TestClient

from app.db.database import get_db
from main import app
from .test_database import db_session, test_key_user, UserAPIKeys, TestingSessionLocal


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


def test_reset_api_key(db_session, test_key_user, client):
    retrieved_api_key = db_session.query(UserAPIKeys).filter_by(user_id=test_key_user.id).first()
    assert retrieved_api_key, "API key not found for the user in the database"
    print(f"Retrieved API Key: {retrieved_api_key.api_key}")

    login_data = {
        "email": test_key_user.email,
        "password": "User@123"
    }

    response = client.post(
        "api/v1/user/reset-api-key",
        json=login_data,
        headers={
            "x-api-key": retrieved_api_key.api_key,
            'Content-Type': 'application/json'
        }
    )

    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["email"] == test_key_user.email
    assert response_data["api_key"] != retrieved_api_key.api_key
    assert response_data["message"] == "Your previous API key will expire in 5 minutes."

    new_api_key = response_data["api_key"]
    new_key_record = db_session.query(UserAPIKeys).filter_by(api_key=new_api_key).first()
    assert new_key_record, "New API key not found in the database"
    assert new_key_record.user_id == test_key_user.id

    db_session.delete(new_key_record)
    db_session.delete(test_key_user)
    db_session.commit()
