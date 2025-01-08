from fastapi import APIRouter
from app.core.monitoring import  timeit
import asyncio
from fastapi.testclient import TestClient
import threading


router = APIRouter()

response_time_data = {}

@router.get("/response", tags=["Response"])
@timeit
async def get_responses():
    await asyncio.sleep(1)
    return {"message": "This is the /response endpoint."}



@router.get("/response-usage", tags=["ResponseUsage"])
@timeit
def trigger_response_usage():
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

