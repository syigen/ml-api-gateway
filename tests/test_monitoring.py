import time

import requests
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
ENDPOINT = "http://127.0.0.1:8000"


def test_can_get_response_usage():
    """
    Test the /api/v1/monitor/response-usage endpoint.

    This test verifies:
    1. The /response-usage endpoint returns a 200 status code and correct response message.
    2. The /response endpoint can be triggered subsequently and its response time is calculated.
    """

    response = requests.get(ENDPOINT + "/api/v1/monitor/response-usage")
    assert response.status_code == 200
    print(f"/response-usage Status Code: {response.status_code}")
    print(f"/response-usage Body: {response.text}")
    response_data = response.json()
    assert response_data["message"] == "Response usage calculation triggered."

    start_time = time.time()
    response = requests.get(ENDPOINT + "/api/v1/monitor/response")
    end_time = time.time()
    response_time = end_time - start_time

    print(f"/response called successfully. Response Time: {response_time:.4f} seconds")
    print(f"/response Status Code: {response.status_code}")
    print(f"/response Body: {response.text}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "This is the /response endpoint."


def test_can_get_response():
    """
    Test the /api/v1/monitor/response endpoint.

    This test ensures:
    1. The endpoint is accessible and returns a 200 status code.
    2. The response body contains the expected message.
    """

    response = requests.get(ENDPOINT + "/api/v1/monitor/response")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "This is the /response endpoint."


def test_error_handling():
    """
    Test error handling for a non-existent endpoint.

    This test verifies:
    1. Accessing a non-existent endpoint returns a 404 status code.
    2. The response contains appropriate error information.
    """

    response = client.get("/nonexistent")
    print(f"Error Handling Status Code: {response.status_code}")
    print(f"Error Handling Body: {response.text}")
    assert response.status_code == 404
