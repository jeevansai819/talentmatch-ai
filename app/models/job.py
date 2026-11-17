from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=False)
    department = Column(String(100), nullable=True)
    location = Column(String(255), default="Remote", nullable=False)
    employment_type = Column(String(50), default="Full-time", nullable=False)
    min_experience_years = Column(Float, default=0.0, nullable=False)
    required_education_level = Column(String(100), default="Bachelor", nullable=False)
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    created_by = relationship("User", back_populates="jobs")
    required_skills = relationship("JobRequiredSkill", back_populates="job", cascade="all, delete-orphan")
    preferred_skills = relationship("JobPreferredSkill", back_populates="job", cascade="all, delete-orphan")
    match_results = relationship("MatchResult", back_populates="job", cascade="all, delete-orphan")
    shortlists = relationship("Shortlist", back_populates="job", cascade="all, delete-orphan")
