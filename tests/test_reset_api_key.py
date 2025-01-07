from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.db.models import User
from app.schemas.schemas import AuthRequest
from main import app


def test_reset_api_key():

    client = TestClient(app)

    user = User(id=1, email="test@email.com")
    login_data = AuthRequest(email="test@email.com", password="test_password")

    with patch("app.api.v1.deps.validate_api_key", return_value=user):
        with patch("app.db.database.get_db", return_value=MagicMock(spec=Session)):
            with patch("app.core.security.APIKeyManager.reset_key", return_value="new_generated_key"):

                response = client.post(
                    "/api/v1/user/reset-api-key",
                    json=login_data.model_dump(),
                    headers={"x-api-key": "new_generated_key"}
                )

                assert response.status_code == 401
