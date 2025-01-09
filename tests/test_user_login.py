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
    """
        Test case to verify that invalid email format results in a validation error.

        This test submits a login request with an invalid email format and expects a
        422 Unprocessable Entity response, with a `detail` field in the returned JSON.

        Args:
            client (TestClient): The fixture providing the test client.
            test_db: The fixture providing the test database session.
    """
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
    """
        Test case to verify that missing required fields in the login request raises a validation error.

        This test submits an empty request body and expects a 422 Unprocessable Entity response.

        Args:
            client (TestClient): The fixture providing the test client.
            test_db: The fixture providing the test database session.
    """
    response = client.post(
        "api/v1/auth/login",
        json={}
    )
    assert response.status_code == 422
