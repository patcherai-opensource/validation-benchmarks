from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)  # User-submitted question text - stored as-is
    answer = Column(Text, nullable=True)  # Admin response
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="open")  # open, answered, closed
