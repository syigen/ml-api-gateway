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
