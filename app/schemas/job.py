from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SkillItem(BaseModel):
    skill_name: str
    category: Optional[str] = "Technical"

    class Config:
        from_attributes = True

class JobBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=10)
    department: Optional[str] = "Engineering"
    location: Optional[str] = "Remote"
    employment_type: Optional[str] = "Full-time"
    min_experience_years: Optional[float] = Field(0.0, ge=0.0)
    required_education_level: Optional[str] = "Bachelor"
    is_active: Optional[bool] = True

class JobCreate(JobBase):
    required_skills: List[str] = []
    preferred_skills: List[str] = []

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    min_experience_years: Optional[float] = None
    required_education_level: Optional[str] = None
    is_active: Optional[bool] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None

class JobResponse(JobBase):
    id: int
    created_by_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    required_skills: List[SkillItem] = []
    preferred_skills: List[SkillItem] = []
    candidates_matched_count: Optional[int] = 0

    class Config:
        from_attributes = True
