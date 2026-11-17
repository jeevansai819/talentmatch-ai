from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.job import SkillItem

class EducationItem(BaseModel):
    id: Optional[int] = None
    degree: str
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    graduation_year: Optional[int] = None

    class Config:
        from_attributes = True

class ExperienceItem(BaseModel):
    id: Optional[int] = None
    title: str
    company: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    duration_years: float = 0.0
    is_current: bool = False
    description: Optional[str] = None

    class Config:
        from_attributes = True

class NoteItem(BaseModel):
    id: int
    content: str
    author_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class StatusHistoryItem(BaseModel):
    id: int
    old_status: Optional[str]
    new_status: str
    changed_by_name: Optional[str]
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class CandidateResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    total_experience_years: float = 0.0
    highest_education_level: str = "Unavailable"
    current_status: str = "New"
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    created_at: datetime
    skills: List[SkillItem] = []

    class Config:
        from_attributes = True

class CandidateDetailResponse(CandidateResponse):
    summary: Optional[str] = None
    education_records: List[EducationItem] = []
    experience_records: List[ExperienceItem] = []
    notes: List[NoteItem] = []
    status_history: List[StatusHistoryItem] = []
    resume_id: Optional[int] = None
    resume_filename: Optional[str] = None

    class Config:
        from_attributes = True

class CandidateStatusUpdate(BaseModel):
    status: str
    comment: Optional[str] = None

class CandidateNoteCreate(BaseModel):
    content: str
