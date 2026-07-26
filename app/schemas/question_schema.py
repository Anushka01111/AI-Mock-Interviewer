from pydantic import BaseModel
from typing import Optional

class QuestionCreate(BaseModel):
    session_id: int
    question_text: str
    ideal_answer: Optional[str] = None

class QuestionUpdate(BaseModel):
    question_text: str

class QuestionResponse(BaseModel):
    question_id: int
    session_id: int
    question_text: str
    ideal_answer: Optional[str] = None

    class Config:
        from_attributes = True

