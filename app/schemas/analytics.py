from pydantic import BaseModel
from typing import List, Dict, Any

class SkillCount(BaseModel):
    skill: str
    category: str
    count: int

class DistributionBracket(BaseModel):
    label: str
    count: int

class TimeSeriesPoint(BaseModel):
    date: str
    count: int

class DashboardAnalyticsResponse(BaseModel):
    total_resumes: int
    total_active_jobs: int
    total_candidates: int
    total_shortlisted: int
    average_matching_score: float
    skills_distribution: List[SkillCount]
    experience_distribution: List[DistributionBracket]
    education_distribution: List[DistributionBracket]
    match_score_distribution: List[DistributionBracket]
    recent_activity: List[TimeSeriesPoint]
    status_distribution: List[DistributionBracket]
