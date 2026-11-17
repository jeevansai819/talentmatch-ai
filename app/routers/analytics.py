from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.skill import CandidateSkill
from app.models.matching import MatchResult
from app.models.shortlist import ShortlistCandidate
from app.schemas.analytics import DashboardAnalyticsResponse

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/dashboard", response_model=DashboardAnalyticsResponse)
def get_dashboard_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compute real-time statistical analytics and distributions derived directly
    from current database records.
    """
    # 1. High-Level Metrics
    total_resumes = db.query(Resume).count()
    total_active_jobs = db.query(Job).filter(Job.is_active == True).count()
    total_candidates = db.query(Candidate).count()
    total_shortlisted = db.query(ShortlistCandidate).count()

    avg_score_raw = db.query(func.avg(MatchResult.overall_score)).scalar()
    avg_score = round(float(avg_score_raw), 1) if avg_score_raw is not None else 0.0

    # 2. Most Common Candidate Skills (Top 15)
    skills_query = (
        db.query(
            CandidateSkill.skill_name,
            CandidateSkill.category,
            func.count(CandidateSkill.id).label("total")
        )
        .group_by(CandidateSkill.skill_name, CandidateSkill.category)
        .order_by(desc("total"))
        .limit(15)
        .all()
    )
    skills_distribution = [
        {"skill": row[0], "category": row[1], "count": int(row[2])}
        for row in skills_query
    ]

    # 3. Experience Distribution Brackets
    exp_0_2 = db.query(Candidate).filter(Candidate.total_experience_years < 3.0).count()
    exp_3_5 = db.query(Candidate).filter(Candidate.total_experience_years >= 3.0, Candidate.total_experience_years < 6.0).count()
    exp_6_8 = db.query(Candidate).filter(Candidate.total_experience_years >= 6.0, Candidate.total_experience_years < 9.0).count()
    exp_9_plus = db.query(Candidate).filter(Candidate.total_experience_years >= 9.0).count()

    experience_distribution = [
        {"label": "0 - 2 Years (Junior)", "count": exp_0_2},
        {"label": "3 - 5 Years (Mid-level)", "count": exp_3_5},
        {"label": "6 - 8 Years (Senior)", "count": exp_6_8},
        {"label": "9+ Years (Lead / Staff)", "count": exp_9_plus}
    ]

    # 4. Education Distribution
    edu_query = (
        db.query(
            Candidate.highest_education_level,
            func.count(Candidate.id).label("total")
        )
        .group_by(Candidate.highest_education_level)
        .order_by(desc("total"))
        .all()
    )
    education_distribution = [
        {"label": row[0] or "Unavailable", "count": int(row[1])}
        for row in edu_query
    ]

    # 5. Match Score Distribution
    m_exc = db.query(MatchResult).filter(MatchResult.overall_score >= 90.0).count()
    m_str = db.query(MatchResult).filter(MatchResult.overall_score >= 75.0, MatchResult.overall_score < 90.0).count()
    m_mod = db.query(MatchResult).filter(MatchResult.overall_score >= 60.0, MatchResult.overall_score < 75.0).count()
    m_low = db.query(MatchResult).filter(MatchResult.overall_score < 60.0).count()

    match_score_distribution = [
        {"label": "90–100% (Excellent)", "count": m_exc},
        {"label": "75–89% (Strong)", "count": m_str},
        {"label": "60–74% (Moderate)", "count": m_mod},
        {"label": "< 60% (Low)", "count": m_low}
    ]

    # 6. Candidate Recruitment Status Distribution
    status_query = (
        db.query(Candidate.current_status, func.count(Candidate.id).label("total"))
        .group_by(Candidate.current_status)
        .all()
    )
    status_distribution = [
        {"label": row[0], "count": int(row[1])}
        for row in status_query
    ]

    # 7. Recent Upload Activity (Last 7 Days)
    today = datetime.now().date()
    activity = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        cnt = db.query(Resume).filter(Resume.created_at >= day_start, Resume.created_at <= day_end).count()
        activity.append({
            "date": day.strftime("%b %d"),
            "count": cnt
        })

    return {
        "total_resumes": total_resumes,
        "total_active_jobs": total_active_jobs,
        "total_candidates": total_candidates,
        "total_shortlisted": total_shortlisted,
        "average_matching_score": avg_score,
        "skills_distribution": skills_distribution,
        "experience_distribution": experience_distribution,
        "education_distribution": education_distribution,
        "match_score_distribution": match_score_distribution,
        "recent_activity": activity,
        "status_distribution": status_distribution
    }
