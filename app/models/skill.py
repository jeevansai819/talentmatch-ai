from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(100), index=True, nullable=False)
    category = Column(String(100), default="Technical", nullable=False)
    confidence_score = Column(Float, default=1.0, nullable=False)

    candidate = relationship("Candidate", back_populates="skills")

class JobRequiredSkill(Base):
    __tablename__ = "job_required_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(100), index=True, nullable=False)
    category = Column(String(100), default="Technical", nullable=False)

    job = relationship("Job", back_populates="required_skills")

class JobPreferredSkill(Base):
    __tablename__ = "job_preferred_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(100), index=True, nullable=False)
    category = Column(String(100), default="Technical", nullable=False)

    job = relationship("Job", back_populates="preferred_skills")
