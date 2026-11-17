from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.matching import MatchResult
from app.models.shortlist import Shortlist
from app.models.resume import Resume
from app.core.config import settings

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)

@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request, db: Session = Depends(get_db)):
    """Render public SaaS marketing landing page."""
    user = get_current_user_optional(request.cookies.get("access_token"), db)
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={"user": user, "app_name": settings.APP_NAME}
    )

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    """Render recruiter login page."""
    user = get_current_user_optional(request.cookies.get("access_token"), db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"app_name": settings.APP_NAME}
    )

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    """Render recruiter registration page."""
    user = get_current_user_optional(request.cookies.get("access_token"), db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"app_name": settings.APP_NAME}
    )

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    """Render main recruiter dashboard with high-level statistics and recent jobs/candidates."""
    total_resumes = db.query(Resume).count()
    total_jobs = db.query(Job).filter(Job.is_active == True).count()
    total_candidates = db.query(Candidate).count()
    recent_jobs = db.query(Job).order_by(Job.created_at.desc()).limit(5).all()
    recent_candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).limit(6).all()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "app_name": settings.APP_NAME,
            "total_resumes": total_resumes,
            "total_jobs": total_jobs,
            "total_candidates": total_candidates,
            "recent_jobs": recent_jobs,
            "recent_candidates": recent_candidates
        }
    )

@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, db: Session = Depends(get_db)):
    """Render drag-and-drop multiple PDF resume upload interface."""
    recent_resumes = db.query(Resume).order_by(Resume.created_at.desc()).limit(10).all()
    return templates.TemplateResponse(
        request=request,
        name="resume_upload.html",
        context={
            "app_name": settings.APP_NAME,
            "recent_resumes": recent_resumes,
            "max_size_mb": settings.MAX_UPLOAD_SIZE_MB
        }
    )

@router.get("/jobs", response_class=HTMLResponse)
def jobs_page(request: Request, db: Session = Depends(get_db)):
    """Render job management page (create, edit, view jobs)."""
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="job_management.html",
        context={
            "app_name": settings.APP_NAME,
            "jobs": jobs
        }
    )

@router.get("/candidates", response_class=HTMLResponse)
def candidates_page(request: Request, db: Session = Depends(get_db)):
    """Render candidate directory and management page."""
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="candidate_management.html",
        context={
            "app_name": settings.APP_NAME,
            "candidates": candidates
        }
    )

@router.get("/ranking", response_class=HTMLResponse)
def ranking_page(request: Request, job_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Render candidate ranking and screening dashboard."""
    jobs = db.query(Job).filter(Job.is_active == True).order_by(Job.created_at.desc()).all()
    selected_job = None
    if job_id:
        selected_job = db.query(Job).filter(Job.id == job_id).first()
    elif jobs:
        selected_job = jobs[0]

    return templates.TemplateResponse(
        request=request,
        name="candidate_ranking.html",
        context={
            "app_name": settings.APP_NAME,
            "jobs": jobs,
            "selected_job": selected_job
        }
    )

@router.get("/candidates/{id}", response_class=HTMLResponse)
def candidate_profile_page(id: int, request: Request, db: Session = Depends(get_db)):
    """Render comprehensive individual candidate profile and matching history."""
    candidate = db.query(Candidate).filter(Candidate.id == id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    latest_resume = db.query(Resume).filter(Resume.candidate_id == candidate.id).order_by(Resume.created_at.desc()).first()
    match_history = db.query(MatchResult).filter(MatchResult.candidate_id == candidate.id).order_by(MatchResult.overall_score.desc()).all()
    jobs = db.query(Job).filter(Job.is_active == True).all()
    shortlists = db.query(Shortlist).all()

    return templates.TemplateResponse(
        request=request,
        name="candidate_profile.html",
        context={
            "app_name": settings.APP_NAME,
            "candidate": candidate,
            "latest_resume": latest_resume,
            "match_history": match_history,
            "jobs": jobs,
            "shortlists": shortlists
        }
    )

@router.get("/shortlists", response_class=HTMLResponse)
def shortlists_page(request: Request, db: Session = Depends(get_db)):
    """Render shortlist management and export center."""
    shortlists = db.query(Shortlist).order_by(Shortlist.created_at.desc()).all()
    jobs = db.query(Job).filter(Job.is_active == True).all()
    return templates.TemplateResponse(
        request=request,
        name="shortlist_management.html",
        context={
            "app_name": settings.APP_NAME,
            "shortlists": shortlists,
            "jobs": jobs
        }
    )

@router.get("/analytics", response_class=HTMLResponse)
def analytics_page(request: Request, db: Session = Depends(get_db)):
    """Render executive analytics and data visualization dashboard."""
    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context={"app_name": settings.APP_NAME}
    )

@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db)):
    """Render platform configuration, scoring weights, and account settings."""
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "app_name": settings.APP_NAME,
            "weights": {
                "required_skills": settings.WEIGHT_REQUIRED_SKILLS,
                "preferred_skills": settings.WEIGHT_PREFERRED_SKILLS,
                "experience": settings.WEIGHT_EXPERIENCE,
                "education": settings.WEIGHT_EDUCATION,
                "text_similarity": settings.WEIGHT_TEXT_SIMILARITY
            }
        }
    )
