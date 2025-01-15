from fastapi import APIRouter, Depends

from app.api.v1.deps import validate_api_key
from app.db.models import User

router = APIRouter()


@router.get("/")
async def root():
    return {"version": "1.0.0"}


@router.get("/protected-endpoint")
async def protected_endpoint(user: User = Depends(validate_api_key)):
    return {"message": f"Welcome {user.email}!"}
