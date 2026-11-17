from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.models.matching import MatchResult
from app.models.candidate import Candidate
from app.models.job import Job

class RankingService:
    """Service to rank, filter, compare, and paginate candidate match results."""

    @staticmethod
    def get_job_rankings(
        db: Session,
        job_id: int,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        tier: Optional[str] = None,
        min_experience: Optional[float] = None,
        required_skill: Optional[str] = None,
        sort_by: str = "score_desc",
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Retrieve candidates ranked for a specific job with flexible filters."""
        query = db.query(MatchResult).filter(MatchResult.job_id == job_id)

        if min_score is not None:
            query = query.filter(MatchResult.overall_score >= min_score)
        if max_score is not None:
            query = query.filter(MatchResult.overall_score <= max_score)
        if tier:
            query = query.filter(MatchResult.match_tier == tier)

        # Candidate-level joins for filtering
        if min_experience is not None or required_skill:
            query = query.join(Candidate, MatchResult.candidate_id == Candidate.id)
            if min_experience is not None:
                query = query.filter(Candidate.total_experience_years >= min_experience)

        # Sorting
        if sort_by == "score_asc":
            query = query.order_by(asc(MatchResult.overall_score))
        elif sort_by == "experience_desc":
            query = query.join(Candidate, MatchResult.candidate_id == Candidate.id).order_by(desc(Candidate.total_experience_years))
        elif sort_by == "name_asc":
            query = query.join(Candidate, MatchResult.candidate_id == Candidate.id).order_by(asc(Candidate.name))
        else:  # Default: score_desc
            query = query.order_by(desc(MatchResult.overall_score))

        total_count = query.count()
        results = query.offset(skip).limit(limit).all()

        rankings = []
        for idx, item in enumerate(results, start=skip + 1):
            cand = item.candidate
            rankings.append({
                "rank": idx,
                "match_id": item.id,
                "candidate_id": cand.id,
                "candidate_name": cand.name,
                "candidate_email": cand.email,
                "candidate_phone": cand.phone,
                "overall_score": item.overall_score,
                "match_tier": item.match_tier,
                "total_experience_years": cand.total_experience_years,
                "highest_education_level": cand.highest_education_level,
                "current_status": cand.current_status,
                "matched_required_skills": item.explanation_report.get("skills_analysis", {}).get("matched_required_skills", []),
                "missing_required_skills": item.explanation_report.get("skills_analysis", {}).get("missing_required_skills", []),
                "created_at": item.created_at.strftime("%Y-%m-%d %H:%M")
            })

        return {
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "rankings": rankings
        }

    @staticmethod
    def compare_candidates(db: Session, job_id: int, candidate_ids: List[int]) -> Dict[str, Any]:
        """Side-by-side comparative analysis of selected candidates for a job."""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"error": "Job not found"}

        matches = db.query(MatchResult).filter(
            MatchResult.job_id == job_id,
            MatchResult.candidate_id.in_(candidate_ids)
        ).all()

        comparisons = []
        for m in matches:
            c = m.candidate
            rep = m.explanation_report
            comparisons.append({
                "candidate_id": c.id,
                "name": c.name,
                "overall_score": m.overall_score,
                "match_tier": m.match_tier,
                "scores": rep.get("score_breakdown", {}),
                "experience_years": c.total_experience_years,
                "education": c.highest_education_level,
                "matched_required_skills": rep.get("skills_analysis", {}).get("matched_required_skills", []),
                "missing_required_skills": rep.get("skills_analysis", {}).get("missing_required_skills", []),
                "matched_preferred_skills": rep.get("skills_analysis", {}).get("matched_preferred_skills", []),
                "strengths": rep.get("strengths", []),
                "potential_gaps": rep.get("potential_gaps", []),
                "current_status": c.current_status
            })

        return {
            "job_id": job.id,
            "job_title": job.title,
            "min_experience_years": job.min_experience_years,
            "required_education_level": job.required_education_level,
            "candidates": comparisons
        }

ranking_service = RankingService()
