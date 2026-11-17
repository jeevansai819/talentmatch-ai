from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    email = Column(String(255), index=True, nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    total_experience_years = Column(Float, default=0.0, nullable=False)
    highest_education_level = Column(String(100), default="Unavailable", nullable=False)
    current_status = Column(String(50), default="New", index=True, nullable=False)
    linkedin_url = Column(String(255), nullable=True)
    github_url = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    education_records = relationship("CandidateEducation", back_populates="candidate", cascade="all, delete-orphan")
    experience_records = relationship("CandidateExperience", back_populates="candidate", cascade="all, delete-orphan")
    match_results = relationship("MatchResult", back_populates="candidate", cascade="all, delete-orphan")
    notes = relationship("RecruiterNote", back_populates="candidate", cascade="all, delete-orphan")
    status_history = relationship("ApplicationStatusHistory", back_populates="candidate", cascade="all, delete-orphan")
    shortlist_entries = relationship("ShortlistCandidate", back_populates="candidate", cascade="all, delete-orphan")
