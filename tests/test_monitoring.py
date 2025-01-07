import time
import requests
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
ENDPOINT = "http://127.0.0.1:8000"


def test_can_get_response_usage():
    response = requests.get(ENDPOINT + "/core/response-usage")

    start_time = time.time()
    response = requests.get(ENDPOINT + "/core/response")
    end_time = time.time()
    response_time = end_time - start_time

    print(f"/response called successfully. Response Time: {response_time:.4f} seconds")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "This is the /response endpoint."


def test_can_get_response():
    response = requests.get(ENDPOINT + "/core/response")
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "This is the /response endpoint."


def test_error_handling():
    response = client.get("/nonexistent")
    assert response.status_code == 404

# if __name__ == "__main__":
#     test_can_get_response_usage()
#     test_can_get_response()
