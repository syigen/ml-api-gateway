import time
from fastapi import APIRouter
from fastapi.testclient import TestClient
import threading
from fastapi import FastAPI

app = FastAPI()
router = APIRouter()

response_time_data = {}

app.include_router(router)


@router.get("/response", tags=["Response"])
async def get_responses():
    return {"message": "This is the /response endpoint."}


@router.get("/response-usage", tags=["ResponseUsage"])
def trigger_response_usage():
    def measure_response_time():
        with TestClient(app) as client:
            start_time = time.time()

            response = client.get("/response")

            end_time = time.time()
            response_time = end_time - start_time

            response_time_data["/response"] = response_time
            print(f"Response time for /response: {response_time:.4f} seconds")


    thread = threading.Thread(target=measure_response_time)
    thread.start()

    return {"message": "Response usage calculation triggered."}
