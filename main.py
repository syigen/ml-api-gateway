from fastapi import FastAPI

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.base import router as base_router
from app.api.v1.endpoints.monitor import router as monitoring_router
from app.api.v1.endpoints.reset_api_key import router as reset_api_key
from app.api.v1.endpoints.user_login import router as login_router
from app.db.database import Base, engine

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(base_router, prefix="/api/v1", tags=["base"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["user_authentication"])
app.include_router(monitoring_router, prefix="/api/v1/monitor", tags=["monitor"])
app.include_router(reset_api_key, prefix="/api/v1/user", tags=["reset_api_key"])
app.include_router(login_router, prefix="/api/v1/user", tags=["user_login"])

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
