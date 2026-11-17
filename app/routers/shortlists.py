from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job
from app.models.candidate import Candidate
from app.models.matching import MatchResult
from app.models.shortlist import Shortlist, ShortlistCandidate
from app.models.audit import ApplicationStatusHistory
from app.schemas.shortlist import (
    ShortlistCreate,
    ShortlistAddCandidate,
    ShortlistResponse,
    ShortlistDetailResponse,
    ShortlistCandidateItem
)
from app.services.report_generator import report_generator

router = APIRouter(prefix="/api/shortlists", tags=["Shortlists"])

@router.post("", response_model=ShortlistResponse, status_code=status.HTTP_201_CREATED)
def create_shortlist(
    shortlist_in: ShortlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new candidate shortlist for a specific job."""
    job = db.query(Job).filter(Job.id == shortlist_in.job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target job not found.")

    new_shortlist = Shortlist(
        name=shortlist_in.name.strip(),
        job_id=job.id,
        description=shortlist_in.description.strip() if shortlist_in.description else None,
        created_by_id=current_user.id
    )
    db.add(new_shortlist)
    db.commit()
    db.refresh(new_shortlist)

    return {
        "id": new_shortlist.id,
        "name": new_shortlist.name,
        "job_id": new_shortlist.job_id,
        "job_title": job.title,
        "description": new_shortlist.description,
        "candidates_count": 0,
        "created_at": new_shortlist.created_at,
        "updated_at": new_shortlist.updated_at
    }

@router.get("", response_model=List[ShortlistResponse])
def get_shortlists(
    job_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all shortlists, optionally filtered by job."""
    query = db.query(Shortlist)
    if job_id:
        query = query.filter(Shortlist.job_id == job_id)

    shortlists = query.order_by(Shortlist.created_at.desc()).all()
    results = []
    for s in shortlists:
        results.append({
            "id": s.id,
            "name": s.name,
            "job_id": s.job_id,
            "job_title": s.job.title if s.job else "Unknown Role",
            "description": s.description,
            "candidates_count": len(s.candidates),
            "created_at": s.created_at,
            "updated_at": s.updated_at
        })
    return results

@router.get("/{id}", response_model=ShortlistDetailResponse)
def get_shortlist_detail(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch complete shortlist details and candidate members."""
    shortlist = db.query(Shortlist).filter(Shortlist.id == id).first()
    if not shortlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortlist not found.")

    cand_items = []
    for entry in shortlist.candidates:
        c = entry.candidate
        # Look up match score if exists
        match_rec = db.query(MatchResult).filter(
            MatchResult.job_id == shortlist.job_id,
            MatchResult.candidate_id == c.id
        ).first()

        cand_items.append({
            "candidate_id": c.id,
            "candidate_name": c.name,
            "candidate_email": c.email,
            "candidate_phone": c.phone,
            "match_score": match_rec.overall_score if match_rec else None,
            "match_tier": match_rec.match_tier if match_rec else None,
            "experience_years": c.total_experience_years,
            "education": c.highest_education_level,
            "status": c.current_status,
            "notes": entry.notes,
            "added_at": entry.added_at
        })

    return {
        "id": shortlist.id,
        "name": shortlist.name,
        "job_id": shortlist.job_id,
        "job_title": shortlist.job.title if shortlist.job else "Unknown Role",
        "description": shortlist.description,
        "candidates_count": len(cand_items),
        "created_at": shortlist.created_at,
        "updated_at": shortlist.updated_at,
        "candidates": cand_items
    }

@router.post("/{id}/candidates")
def add_candidate_to_shortlist(
    id: int,
    item: ShortlistAddCandidate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a candidate to a shortlist and optionally update their status to 'Shortlisted'."""
    shortlist = db.query(Shortlist).filter(Shortlist.id == id).first()
    if not shortlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortlist not found.")

    candidate = db.query(Candidate).filter(Candidate.id == item.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found.")

    # Check if candidate is already in shortlist
    existing = db.query(ShortlistCandidate).filter(
        ShortlistCandidate.shortlist_id == shortlist.id,
        ShortlistCandidate.candidate_id == candidate.id
    ).first()

    if existing:
        if item.notes:
            existing.notes = item.notes
            db.commit()
        return {"message": "Candidate is already present in this shortlist."}

    entry = ShortlistCandidate(
        shortlist_id=shortlist.id,
        candidate_id=candidate.id,
        notes=item.notes
    )
    db.add(entry)

    # Automatically set status to Shortlisted if currently New or Under Review
    if candidate.current_status in ["New", "Under Review"]:
        old_status = candidate.current_status
        candidate.current_status = "Shortlisted"
        db.add(ApplicationStatusHistory(
            candidate_id=candidate.id,
            old_status=old_status,
            new_status="Shortlisted",
            changed_by_id=current_user.id,
            comment=f"Candidate added to shortlist '{shortlist.name}'"
        ))

    db.commit()
    return {"message": f"Successfully added {candidate.name} to shortlist '{shortlist.name}'."}

@router.delete("/{id}/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_candidate_from_shortlist(
    id: int,
    candidate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove candidate from a shortlist."""
    entry = db.query(ShortlistCandidate).filter(
        ShortlistCandidate.shortlist_id == id,
        ShortlistCandidate.candidate_id == candidate_id
    ).first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate entry not found in shortlist.")

    db.delete(entry)
    db.commit()
    return None

@router.get("/{id}/export/csv")
def export_shortlist_csv(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Export shortlisted candidates as a CSV file."""
    shortlist = db.query(Shortlist).filter(Shortlist.id == id).first()
    if not shortlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortlist not found.")

    candidates_export = []
    for entry in shortlist.candidates:
        c = entry.candidate
        match_rec = db.query(MatchResult).filter(
            MatchResult.job_id == shortlist.job_id,
            MatchResult.candidate_id == c.id
        ).first()

        candidates_export.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "match_score": match_rec.overall_score if match_rec else "N/A",
            "match_tier": match_rec.match_tier if match_rec else "N/A",
            "experience_years": c.total_experience_years,
            "education": c.highest_education_level,
            "status": c.current_status,
            "notes": entry.notes
        })

    csv_data = report_generator.generate_shortlist_csv(
        shortlist_name=shortlist.name,
        job_title=shortlist.job.title if shortlist.job else "Role",
        candidates=candidates_export
    )

    safe_name = "".join(c for c in shortlist.name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"Shortlist_{safe_name}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shortlist(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a shortlist."""
    shortlist = db.query(Shortlist).filter(Shortlist.id == id).first()
    if not shortlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortlist not found.")
    db.delete(shortlist)
    db.commit()
    return None
