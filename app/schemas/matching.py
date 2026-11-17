from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class MatchingWeights(BaseModel):
    required_skills: float = Field(40.0, ge=0.0, le=100.0)
    preferred_skills: float = Field(20.0, ge=0.0, le=100.0)
    experience: float = Field(20.0, ge=0.0, le=100.0)
    education: float = Field(10.0, ge=0.0, le=100.0)
    text_similarity: float = Field(10.0, ge=0.0, le=100.0)

class MatchingRunRequest(BaseModel):
    weights: Optional[MatchingWeights] = None
    candidate_ids: Optional[List[int]] = None  # None means all candidates

class MatchResultResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    candidate_name: str
    overall_score: float
    required_skills_score: float
    preferred_skills_score: float
    experience_score: float
    education_score: float
    text_similarity_score: float
    match_tier: str
    explanation_report: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class CandidateComparisonRequest(BaseModel):
    job_id: int
    candidate_ids: List[int] = Field(..., min_length=2, max_length=5)
