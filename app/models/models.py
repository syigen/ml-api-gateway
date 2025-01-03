from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models import Base

class Response(Base):
    __tablename__ = "responses"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    extra_metadata = Column(String, nullable=True)

class ResponseUsage(Base):
    __tablename__ = "response_usage"
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=False)
    usage_count = Column(Integer, nullable=False)
    response = relationship("Response", back_populates="usage")
    total_response_time = Column(Float, default=0.0)

Response.usage = relationship("ResponseUsage", back_populates="response")