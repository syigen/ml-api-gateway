from fastapi import FastAPI
from app.api.v1.endpoints.base import router as base_router

app = FastAPI()

app.include_router(base_router, prefix="/api/v1", tags=["base"])
app.include_router(base_router, prefix="/core", tags=["monitoring"])


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
