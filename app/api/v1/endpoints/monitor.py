import asyncio
import threading

from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.core.monitoring import timeit

router = APIRouter()

response_time_data = {}


@router.get("/response", tags=["Response"])
@timeit
async def get_responses():
    """
        Handles GET requests to the /response endpoint.
        Simulates a delay of 1 second before returning a response.
    """
    await asyncio.sleep(1)
    return {"message": "This is the /response endpoint."}


@router.get("/response-usage", tags=["ResponseUsage"])
@timeit
def trigger_response_usage():
    """
    Triggers the calculation of response time for the /response endpoint.
    Spawns a separate thread to make a request to /response and measure the response time.
    The calculated response time is stored in the response_time_data dictionary.
    """

    @timeit
    def measure_response_time():
        with TestClient(router) as client:
            response = client.get("/response")
            response_time = response.elapsed.total_seconds()
            response_time_data["/response"] = response_time
            print(f"Response time for /response: {response_time:.4f} seconds")

    thread = threading.Thread(target=measure_response_time)
    thread.start()

    return {"message": "Response usage calculation triggered."}
