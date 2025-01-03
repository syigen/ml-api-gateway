from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import models
from app.models import Response, ResponseUsage
from app.db.database import SessionLocal, engine
import time

router = APIRouter()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ResponseModel(BaseModel):
    content: str
    extra_metadata: str


class ResponseUsageModel(BaseModel):
    response_id: str
    usage_count: int
    total_response_time: float


@router.get("/response", tags=["Response"])
def get_responses(request: Request, db: Session = Depends(get_db)):
    start_time = time.time()
    responses = db.query(Response).all()
    end_time = time.time()

    response_time = end_time - start_time
    print(f"Endpoint '/response': Response Time = {response_time:.4f} seconds")
    log_response_time(response_time, "GET /response", db)

    return responses


@router.get("/response-usage", tags=["ResponseUsage"])
def get_response_usage(db: Session = Depends(get_db)):
    usages = db.query(ResponseUsage).all()

    usage_list = [
        {
            "response_id": usage.response_id,
            "usage_count": usage.usage_count,
            "total_response_time": usage.total_response_time
        }
        for usage in usages
    ]

    return usage_list


@router.post("/response", tags=["Response"])
def create_response(response: ResponseModel, db: Session = Depends(get_db)):
    start_time = time.time()
    db_response = Response(content=response.content, extra_metadata=response.extra_metadata)
    db.add(db_response)
    db.commit()
    end_time = time.time()

    response_time = end_time - start_time
    print(f"Endpoint '/response': Response Time = {response_time:.4f} seconds")
    log_response_time(response_time, "POST /response", db)

    return db_response


def log_response_time(response_time: float, endpoint: str, db: Session):
    usage = db.query(ResponseUsage).filter(ResponseUsage.response_id == endpoint).first()

    if usage:
        usage.total_response_time += response_time
        usage.usage_count += 1
    else:

        usage = ResponseUsage(
            response_id=endpoint,
            usage_count=1,
            total_response_time=response_time
        )
        db.add(usage)

    db.commit()
