from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job
from app.models.skill import JobRequiredSkill, JobPreferredSkill
from app.models.matching import MatchResult
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.services.skill_extractor import skill_extractor
from app.utils.constants import CANONICAL_SKILL_MAP

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new job posting with required and preferred skills."""
    new_job = Job(
        title=job_in.title.strip(),
        description=job_in.description.strip(),
        department=job_in.department.strip() if job_in.department else "General",
        location=job_in.location.strip() if job_in.location else "Remote",
        employment_type=job_in.employment_type if job_in.employment_type else "Full-time",
        min_experience_years=float(job_in.min_experience_years or 0.0),
        required_education_level=job_in.required_education_level or "Bachelor",
        is_active=job_in.is_active if job_in.is_active is not None else True,
        created_by_id=current_user.id
    )
    db.add(new_job)
    db.flush()

    # Normalize and attach required skills
    req_skills = skill_extractor.normalize_skill_list(job_in.required_skills)
    for s_name in req_skills:
        cat = CANONICAL_SKILL_MAP.get(s_name.lower(), {}).get("category", "Technical")
        db.add(JobRequiredSkill(job_id=new_job.id, skill_name=s_name, category=cat))

    # Normalize and attach preferred skills
    pref_skills = skill_extractor.normalize_skill_list(job_in.preferred_skills)
    for s_name in pref_skills:
        cat = CANONICAL_SKILL_MAP.get(s_name.lower(), {}).get("category", "Technical")
        db.add(JobPreferredSkill(job_id=new_job.id, skill_name=s_name, category=cat))

    db.commit()
    db.refresh(new_job)
    return new_job

@router.get("", response_model=List[JobResponse])
def get_jobs(
    is_active: Optional[bool] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all job postings with optional filters."""
    query = db.query(Job)
    if is_active is not None:
        query = query.filter(Job.is_active == is_active)
    if department:
        query = query.filter(Job.department.ilike(f"%{department}%"))
    if search:
        query = query.filter(Job.title.ilike(f"%{search}%") | Job.description.ilike(f"%{search}%"))

    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    # Annotate candidates matched count
    for j in jobs:
        j.candidates_matched_count = db.query(MatchResult).filter(MatchResult.job_id == j.id).count()

    return jobs

@router.get("/{id}", response_model=JobResponse)
def get_job(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch details of an individual job posting."""
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")
    job.candidates_matched_count = db.query(MatchResult).filter(MatchResult.job_id == job.id).count()
    return job

@router.put("/{id}", response_model=JobResponse)
def update_job(
    id: int,
    job_in: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update job posting details and skill criteria."""
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")

    update_dict = job_in.model_dump(exclude_unset=True)

    # Handle skills separately
    if "required_skills" in update_dict:
        db.query(JobRequiredSkill).filter(JobRequiredSkill.job_id == job.id).delete()
        req_skills = skill_extractor.normalize_skill_list(update_dict.pop("required_skills"))
        for s_name in req_skills:
            cat = CANONICAL_SKILL_MAP.get(s_name.lower(), {}).get("category", "Technical")
            db.add(JobRequiredSkill(job_id=job.id, skill_name=s_name, category=cat))

    if "preferred_skills" in update_dict:
        db.query(JobPreferredSkill).filter(JobPreferredSkill.job_id == job.id).delete()
        pref_skills = skill_extractor.normalize_skill_list(update_dict.pop("preferred_skills"))
        for s_name in pref_skills:
            cat = CANONICAL_SKILL_MAP.get(s_name.lower(), {}).get("category", "Technical")
            db.add(JobPreferredSkill(job_id=job.id, skill_name=s_name, category=cat))

    for field, value in update_dict.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    job.candidates_matched_count = db.query(MatchResult).filter(MatchResult.job_id == job.id).count()
    return job

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a job posting and its associated matches."""
    job = db.query(Job).filter(Job.id == id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")
    db.delete(job)
    db.commit()
    return None
