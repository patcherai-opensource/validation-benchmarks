from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class QuestionBase(BaseModel):
    question: str

class QuestionCreate(QuestionBase):
    answer: Optional[str] = None

class Question(QuestionBase):
    id: int
    answer: Optional[str] = None
    created_at: datetime
    status: str

    class Config:
        orm_mode = True
