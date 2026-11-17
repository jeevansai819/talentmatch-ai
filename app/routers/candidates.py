from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.candidate import Candidate
from app.models.note import RecruiterNote
from app.models.audit import ApplicationStatusHistory
from app.models.resume import Resume
from app.schemas.candidate import (
    CandidateResponse,
    CandidateDetailResponse,
    CandidateStatusUpdate,
    CandidateNoteCreate
)
from app.utils.constants import APPLICATION_STATUSES

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])

@router.get("", response_model=List[CandidateResponse])
def get_candidates(
    status_filter: Optional[str] = Query(None, alias="status"),
    min_experience: Optional[float] = None,
    education: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve list of candidate profiles with optional filtering and search."""
    query = db.query(Candidate)

    if status_filter:
        query = query.filter(Candidate.current_status == status_filter)
    if min_experience is not None:
        query = query.filter(Candidate.total_experience_years >= min_experience)
    if education:
        query = query.filter(Candidate.highest_education_level.ilike(f"%{education}%"))
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            Candidate.name.ilike(search_fmt) |
            Candidate.email.ilike(search_fmt) |
            Candidate.location.ilike(search_fmt)
        )

    return query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{id}", response_model=CandidateDetailResponse)
def get_candidate(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch complete candidate dossier including education, experience, notes, and audit log."""
    candidate = db.query(Candidate).filter(Candidate.id == id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found.")

    latest_resume = db.query(Resume).filter(Resume.candidate_id == candidate.id).order_by(Resume.created_at.desc()).first()

    # Format notes with author name
    notes_list = []
    for n in candidate.notes:
        notes_list.append({
            "id": n.id,
            "content": n.content,
            "author_name": n.author.full_name if n.author else "Recruiter",
            "created_at": n.created_at
        })

    # Format status history with author name
    history_list = []
    for h in candidate.status_history:
        history_list.append({
            "id": h.id,
            "old_status": h.old_status,
            "new_status": h.new_status,
            "changed_by_name": h.changed_by.full_name if h.changed_by else "System",
            "comment": h.comment,
            "created_at": h.created_at
        })

    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "location": candidate.location,
        "total_experience_years": candidate.total_experience_years,
        "highest_education_level": candidate.highest_education_level,
        "current_status": candidate.current_status,
        "linkedin_url": candidate.linkedin_url,
        "github_url": candidate.github_url,
        "summary": candidate.summary,
        "created_at": candidate.created_at,
        "skills": candidate.skills,
        "education_records": candidate.education_records,
        "experience_records": candidate.experience_records,
        "notes": notes_list,
        "status_history": history_list,
        "resume_id": latest_resume.id if latest_resume else None,
        "resume_filename": latest_resume.original_filename if latest_resume else None
    }

@router.put("/{id}/status")
def update_candidate_status(
    id: int,
    status_update: CandidateStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update candidate recruitment lifecycle status and record audit entry."""
    candidate = db.query(Candidate).filter(Candidate.id == id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found.")

    if status_update.status not in APPLICATION_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{status_update.status}'. Allowed: {', '.join(APPLICATION_STATUSES)}"
        )

    old_status = candidate.current_status
    candidate.current_status = status_update.status

    audit_entry = ApplicationStatusHistory(
        candidate_id=candidate.id,
        old_status=old_status,
        new_status=status_update.status,
        changed_by_id=current_user.id,
        comment=status_update.comment or f"Status changed from {old_status} to {status_update.status}"
    )
    db.add(audit_entry)
    db.commit()

    return {"message": "Candidate status updated successfully.", "status": candidate.current_status}

@router.post("/{id}/notes")
def add_candidate_note(
    id: int,
    note_in: CandidateNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a confidential recruiter note to candidate profile."""
    candidate = db.query(Candidate).filter(Candidate.id == id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found.")

    if not note_in.content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Note content cannot be empty.")

    new_note = RecruiterNote(
        candidate_id=candidate.id,
        user_id=current_user.id,
        content=note_in.content.strip()
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return {
        "id": new_note.id,
        "content": new_note.content,
        "author_name": current_user.full_name,
        "created_at": new_note.created_at
    }

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a candidate profile and associated records."""
    candidate = db.query(Candidate).filter(Candidate.id == id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found.")
    db.delete(candidate)
    db.commit()
    return None
