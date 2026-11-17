from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.matching import MatchResult
from app.schemas.matching import MatchingRunRequest, MatchResultResponse, CandidateComparisonRequest
from app.services.matching_engine import matching_engine
from app.services.ranking_service import ranking_service
from app.services.report_generator import report_generator

router = APIRouter(prefix="/api/matching", tags=["Matching"])

@router.post("/{job_id}/run")
def run_job_matching(
    job_id: int,
    request: Optional[MatchingRunRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute AI/NLP resume screening and matching engine for a job description.
    Compares candidates against job requirements across skills, experience, education,
    and semantic similarity.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")

    # Prepare job data dict
    job_data = {
        "title": job.title,
        "description": job.description,
        "required_skills": [s.skill_name for s in job.required_skills],
        "preferred_skills": [s.skill_name for s in job.preferred_skills],
        "min_experience_years": job.min_experience_years,
        "required_education_level": job.required_education_level
    }

    # Fetch candidates
    cand_query = db.query(Candidate)
    if request and request.candidate_ids:
        cand_query = cand_query.filter(Candidate.id.in_(request.candidate_ids))
    candidates = cand_query.all()

    if not candidates:
        return {
            "message": "No candidates available for screening. Upload resumes first.",
            "processed_count": 0,
            "job_id": job.id
        }

    # Custom weights if provided
    weights = None
    if request and request.weights:
        weights = {
            "required_skills": request.weights.required_skills,
            "preferred_skills": request.weights.preferred_skills,
            "experience": request.weights.experience,
            "education": request.weights.education,
            "text_similarity": request.weights.text_similarity
        }

    processed_count = 0
    for cand in candidates:
        # Get candidate latest resume text
        latest_resume = db.query(Resume).filter(Resume.candidate_id == cand.id).order_by(Resume.created_at.desc()).first()
        raw_text = latest_resume.raw_text if latest_resume else ""

        cand_data = {
            "skills": [{"skill_name": s.skill_name, "category": s.category} for s in cand.skills],
            "total_experience_years": cand.total_experience_years,
            "highest_education_level": cand.highest_education_level,
            "raw_text": raw_text
        }

        # Calculate scores & explainable breakdown
        match_output = matching_engine.calculate_match(
            candidate_data=cand_data,
            job_data=job_data,
            weights=weights
        )

        # Check existing match record for this job & candidate
        match_rec = db.query(MatchResult).filter(
            MatchResult.job_id == job.id,
            MatchResult.candidate_id == cand.id
        ).first()

        if not match_rec:
            match_rec = MatchResult(
                job_id=job.id,
                candidate_id=cand.id,
                overall_score=match_output["overall_score"],
                required_skills_score=match_output["required_skills_score"],
                preferred_skills_score=match_output["preferred_skills_score"],
                experience_score=match_output["experience_score"],
                education_score=match_output["education_score"],
                text_similarity_score=match_output["text_similarity_score"],
                match_tier=match_output["match_tier"],
                explanation_report=match_output["explanation_report"]
            )
            db.add(match_rec)
        else:
            match_rec.overall_score = match_output["overall_score"]
            match_rec.required_skills_score = match_output["required_skills_score"]
            match_rec.preferred_skills_score = match_output["preferred_skills_score"]
            match_rec.experience_score = match_output["experience_score"]
            match_rec.education_score = match_output["education_score"]
            match_rec.text_similarity_score = match_output["text_similarity_score"]
            match_rec.match_tier = match_output["match_tier"]
            match_rec.explanation_report = match_output["explanation_report"]

        processed_count += 1

    db.commit()

    return {
        "message": f"Successfully processed matching for {processed_count} candidates.",
        "processed_count": processed_count,
        "job_id": job.id,
        "job_title": job.title
    }

@router.get("/{job_id}/results")
def get_job_ranking_results(
    job_id: int,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    tier: Optional[str] = None,
    min_experience: Optional[float] = None,
    sort_by: str = "score_desc",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve ranked candidates for a job posting with filtering and pagination."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")

    results = ranking_service.get_job_rankings(
        db=db,
        job_id=job.id,
        min_score=min_score,
        max_score=max_score,
        tier=tier,
        min_experience=min_experience,
        sort_by=sort_by,
        skip=skip,
        limit=limit
    )
    results["job_title"] = job.title
    results["job_id"] = job.id
    return results

@router.get("/results/{id}", response_model=MatchResultResponse)
def get_match_result_detail(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch individual candidate-job matching explanation breakdown."""
    match_rec = db.query(MatchResult).filter(MatchResult.id == id).first()
    if not match_rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match result not found.")

    return {
        "id": match_rec.id,
        "job_id": match_rec.job_id,
        "candidate_id": match_rec.candidate_id,
        "candidate_name": match_rec.candidate.name if match_rec.candidate else "Candidate",
        "overall_score": match_rec.overall_score,
        "required_skills_score": match_rec.required_skills_score,
        "preferred_skills_score": match_rec.preferred_skills_score,
        "experience_score": match_rec.experience_score,
        "education_score": match_rec.education_score,
        "text_similarity_score": match_rec.text_similarity_score,
        "match_tier": match_rec.match_tier,
        "explanation_report": match_rec.explanation_report,
        "created_at": match_rec.created_at
    }

@router.post("/compare")
def compare_candidates_side_by_side(
    req: CandidateComparisonRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare up to 5 candidates side-by-side for a specific job."""
    comparison = ranking_service.compare_candidates(
        db=db,
        job_id=req.job_id,
        candidate_ids=req.candidate_ids
    )
    if "error" in comparison:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=comparison["error"])
    return comparison

@router.get("/{job_id}/export/pdf")
def export_screening_report_pdf(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate and download executive PDF screening report for a job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found.")

    rankings_data = ranking_service.get_job_rankings(db=db, job_id=job.id, limit=50)

    job_info = {
        "title": job.title,
        "department": job.department,
        "location": job.location,
        "employment_type": job.employment_type,
        "min_experience_years": job.min_experience_years,
        "required_education_level": job.required_education_level
    }

    pdf_bytes = report_generator.generate_screening_pdf(
        job_info=job_info,
        ranked_candidates=rankings_data.get("rankings", [])
    )

    safe_title = "".join(c for c in job.title if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"TalentMatch_Screening_{safe_title}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
