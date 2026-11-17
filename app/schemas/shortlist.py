from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ShortlistCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    job_id: int
    description: Optional[str] = None

class ShortlistAddCandidate(BaseModel):
    candidate_id: int
    notes: Optional[str] = None

class ShortlistCandidateItem(BaseModel):
    candidate_id: int
    candidate_name: str
    candidate_email: Optional[str] = None
    candidate_phone: Optional[str] = None
    match_score: Optional[float] = None
    match_tier: Optional[str] = None
    experience_years: float = 0.0
    education: str = "Unavailable"
    status: str = "Shortlisted"
    notes: Optional[str] = None
    added_at: datetime

    class Config:
        from_attributes = True

class ShortlistResponse(BaseModel):
    id: int
    name: str
    job_id: int
    job_title: str
    description: Optional[str]
    candidates_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ShortlistDetailResponse(ShortlistResponse):
    candidates: List[ShortlistCandidateItem] = []

    class Config:
        from_attributes = True
