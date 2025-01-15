import unittest
from unittest.mock import MagicMock

from pydantic import ValidationError
from pydantic.v1 import EmailStr

from app.schemas.auth_schemas import AuthRequest, AuthResponse


class TestAuthModels(unittest.TestCase):
    def setUp(self):
        """
        Set up a temporary database simulation.
        """
        self.temp_db = {
            "users": [
                {"id": 1, "email": "user1@example.com", "password": "password123", "api_key": "key123"},
                {"id": 2, "email": "user2@example.com", "password": "password456", "api_key": "key456"},
            ]
        }

    def test_auth_request_valid(self):
        """
        Test valid AuthRequest model creation.
        """
        data = {"email": "user1@example.com", "password": "password123"}
        auth_request = AuthRequest(**data)
        self.assertEqual(auth_request.email, data["email"])
        self.assertEqual(auth_request.password, data["password"])

    def test_auth_request_invalid_email(self):
        """
        Test AuthRequest with invalid email.
        """
        data = {"email": "invalid_email", "password": "password123"}
        with self.assertRaises(ValidationError):
            AuthRequest(**data)

    def test_auth_response_valid(self):
        """
        Test valid AuthResponse model creation.
        """
        data = {"id": 1, "email": "user1@example.com", "api_key": "key123"}
        auth_response = AuthResponse(**data)
        self.assertEqual(auth_response.id, data["id"])
        self.assertEqual(auth_response.email, data["email"])
        self.assertEqual(auth_response.api_key, data["api_key"])

    def test_auth_service_authenticate(self):
        """
        Test authentication logic using MagicMock.
        """
        # Simulate an authentication function
        auth_service = MagicMock()

        def mock_authenticate(email, password):
            for user in self.temp_db["users"]:
                if user["email"] == email and user["password"] == password:
                    return AuthResponse(id=user["id"], email=EmailStr(user["email"]), api_key=user["api_key"])
            return None

        auth_service.authenticate = mock_authenticate

        response = auth_service.authenticate("user1@example.com", "password123")
        self.assertIsNotNone(response)
        self.assertEqual(response.id, 1)
        self.assertEqual(response.email, "user1@example.com")
        self.assertEqual(response.api_key, "key123")

        response = auth_service.authenticate("user1@example.com", "wrongpassword")
        self.assertIsNone(response)

    def test_auth_response_invalid(self):
        """
        Test AuthResponse with missing fields.
        """
        data = {"id": 1, "email": "user1@example.com"}
        with self.assertRaises(ValidationError):
            AuthResponse(**data)
