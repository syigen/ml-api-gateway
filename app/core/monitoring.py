import time
import httpx
from fastapi import APIRouter

router = APIRouter()


@router.get("/response", tags=["Response"])
async def get_responses():
    return {"message": "This is the /response endpoint."}


@router.get("/response-usage", tags=["ResponseUsage"])
async def log_response_usage():

    response_api_url = "http://localhost:8000/api/v1/response"

    start_time = time.time()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(response_api_url, timeout=10.0)
            end_time = time.time()

            response_time = end_time - start_time

            print(f"Response time for /response: {response_time:.4f} seconds")

            return {
                "message": "Logged response time successfully",
                "response_time": response_time,
                "status_code": response.status_code
            }
        except httpx.RequestError as e:

            print(f"Failed to call /response: {e}")
            return {"message": "Failed to call /response", "error": str(e)}

#print()
