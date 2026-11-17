from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Weighted and component scores (0 - 100)
    overall_score = Column(Float, nullable=False, index=True)
    required_skills_score = Column(Float, default=0.0, nullable=False)
    preferred_skills_score = Column(Float, default=0.0, nullable=False)
    experience_score = Column(Float, default=0.0, nullable=False)
    education_score = Column(Float, default=0.0, nullable=False)
    text_similarity_score = Column(Float, default=0.0, nullable=False)
    
    match_tier = Column(String(50), nullable=False)  # Excellent, Strong, Moderate, Low
    explanation_report = Column(JSON, nullable=False)  # Structured explanation breakdown
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    job = relationship("Job", back_populates="match_results")
    candidate = relationship("Candidate", back_populates="match_results")
