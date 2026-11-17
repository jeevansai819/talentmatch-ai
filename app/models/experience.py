from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class CandidateExperience(Base):
    __tablename__ = "candidate_experience"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    company = Column(String(255), nullable=True)
    title = Column(String(255), nullable=False)
    start_year = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    duration_years = Column(Float, default=0.0, nullable=False)
    is_current = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="experience_records")
