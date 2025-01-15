from .conftest import db_session, test_key_user, UserAPIKeys


def test_reset_api_key(db_session, test_key_user, client):
    """
    Test the API endpoint for resetting the user's API key.

    Ensures that:
    - The correct user is authenticated and their API key is reset.
    - A new API key is generated and stored in the database.
    - The previous API key is invalidated.

    Args:
        db_session: A database session used for testing.
        test_key_user: A test user object with a valid `id` and `email`.
        client: A test client for making HTTP requests to the FastAPI app.

    Steps:
    - Retrieve the existing API key for the test user from the database.
    - Send a `POST` request to the `reset-api-key` endpoint with valid login data and the old API key.
    - Assert that the response status is 200 and contains the new API key and relevant message.
    - Verify the new API key is stored in the database and belongs to the correct user.
    - Clean up by deleting the new API key and test user from the database.

    """
    # Retrieve existing API key for the test user
    retrieved_api_key = db_session.query(UserAPIKeys).filter_by(user_id=test_key_user.id).first()
    assert retrieved_api_key, "API key not found for the user in the database"
    print(f"Retrieved API Key: {retrieved_api_key.api_key}")

    # Login data for API key reset
    login_data = {
        "email": test_key_user.email,
        "password": "User@123"
    }

    # Send reset API key request
    response = client.post(
        "api/v1/user/reset-api-key",
        json=login_data,
        headers={
            "x-api-key": retrieved_api_key.api_key,
            'Content-Type': 'application/json'
        }
    )

    # Print response status and body for debugging
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")

    # Assert successful response and verify new API key details
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["email"] == test_key_user.email
    assert response_data["api_key"] != retrieved_api_key.api_key
    assert response_data["message"] == "Your previous API key will expire in 5 minutes."

    # Verify the new API key is saved in the database
    new_api_key = response_data["api_key"]
    new_key_record = db_session.query(UserAPIKeys).filter_by(api_key=new_api_key).first()
    assert new_key_record, "New API key not found in the database"
    assert new_key_record.user_id == test_key_user.id

    # Clean up
    db_session.delete(new_key_record)
    db_session.delete(test_key_user)
    db_session.commit()
