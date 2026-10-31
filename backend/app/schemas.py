from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ---- Auth ----
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Resume ----
class ResumeOut(BaseModel):
    id: str
    filename: str
    target_role: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ---- Interview ----
class StartInterviewRequest(BaseModel):
    resume_id: Optional[str] = None
    target_role: str
    num_questions: int = 5


class QuestionOut(BaseModel):
    id: str
    order_index: int
    question_text: str
    category: Optional[str] = None

    class Config:
        from_attributes = True


class StartInterviewResponse(BaseModel):
    session_id: str
    questions: List[QuestionOut]


class SubmitAnswerRequest(BaseModel):
    question_id: str
    answer_text: str


class SubmitAnswerResponse(BaseModel):
    question_id: str
    technical_score: float
    communication_score: float
    feedback: str


class SessionSummary(BaseModel):
    session_id: str
    status: str
    overall_technical_score: Optional[float] = None
    overall_communication_score: Optional[float] = None
    report_path: Optional[str] = None
