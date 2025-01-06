from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"version": "1.0.0"}

