import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.skill import CandidateSkill
from app.models.education import CandidateEducation
from app.models.experience import CandidateExperience
from app.models.audit import ApplicationStatusHistory
from app.schemas.resume import MultiUploadResponse, ResumeUploadResult, ResumeResponse
from app.services.pdf_extractor import PDFExtractor, PDFExtractionError
from app.services.resume_parser import resume_parser
from app.utils.helpers import sanitize_filename

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

@router.post("/upload", response_model=MultiUploadResponse)
async def upload_resumes(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and automatically process multiple candidate resumes in PDF format.
    Validates file format, extracts text via PyMuPDF, parses structured information,
    and stores records in the database.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files were provided for upload."
        )

    results: List[ResumeUploadResult] = []
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    for upload_file in files:
        orig_name = upload_file.filename or "unknown.pdf"
        
        # 1. Extension check
        ext = os.path.splitext(orig_name)[1].lower()
        if ext != ".pdf":
            results.append(ResumeUploadResult(
                filename=orig_name,
                status="failed",
                message="Only PDF files are supported. Please upload valid .pdf documents."
            ))
            continue

        # 2. Save temporary/permanent file
        safe_name = sanitize_filename(orig_name)
        file_path = os.path.join(settings.UPLOAD_DIR, safe_name)

        try:
            # Read and validate size
            contents = await upload_file.read()
            file_size = len(contents)

            if file_size > max_bytes:
                results.append(ResumeUploadResult(
                    filename=orig_name,
                    status="failed",
                    message=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
                ))
                continue

            if file_size == 0:
                results.append(ResumeUploadResult(
                    filename=orig_name,
                    status="failed",
                    message="The uploaded file is empty (0 bytes)."
                ))
                continue

            with open(file_path, "wb") as f:
                f.write(contents)

        except Exception as e:
            results.append(ResumeUploadResult(
                filename=orig_name,
                status="failed",
                message=f"Error saving file: {str(e)}"
            ))
            continue

        # 3. Extract text using PyMuPDF
        try:
            extracted_text, page_count = PDFExtractor.extract_text(file_path)
        except PDFExtractionError as e:
            # Clean up invalid file
            if os.path.exists(file_path):
                os.remove(file_path)
            results.append(ResumeUploadResult(
                filename=orig_name,
                status="failed",
                message=str(e)
            ))
            continue
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            results.append(ResumeUploadResult(
                filename=orig_name,
                status="failed",
                message=f"PDF extraction error: {str(e)}"
            ))
            continue

        # 4. Parse Resume Information
        try:
            parsed = resume_parser.parse(extracted_text)
            
            # Check duplicate candidate by email
            candidate = None
            if parsed.get("email"):
                candidate = db.query(Candidate).filter(Candidate.email == parsed["email"].lower()).first()

            if not candidate:
                candidate = Candidate(
                    name=parsed.get("name") or "Candidate",
                    email=parsed.get("email").lower() if parsed.get("email") else None,
                    phone=parsed.get("phone"),
                    location=parsed.get("location"),
                    total_experience_years=parsed.get("total_experience_years", 0.0),
                    highest_education_level=parsed.get("highest_education_level", "Unavailable"),
                    current_status="New",
                    linkedin_url=parsed.get("linkedin_url"),
                    github_url=parsed.get("github_url"),
                    summary=parsed.get("summary")
                )
                db.add(candidate)
                db.flush()

                # Record status history
                db.add(ApplicationStatusHistory(
                    candidate_id=candidate.id,
                    old_status=None,
                    new_status="New",
                    changed_by_id=current_user.id,
                    comment="Candidate profile initialized from resume upload."
                ))
            else:
                # Update existing candidate record if needed
                if parsed.get("total_experience_years", 0) > candidate.total_experience_years:
                    candidate.total_experience_years = parsed["total_experience_years"]
                if candidate.highest_education_level == "Unavailable" and parsed.get("highest_education_level"):
                    candidate.highest_education_level = parsed["highest_education_level"]

            # Save Resume record
            resume_record = Resume(
                candidate_id=candidate.id,
                filename=safe_name,
                original_filename=orig_name,
                file_size=file_size,
                mime_type="application/pdf",
                file_path=file_path,
                raw_text=extracted_text,
                parsed_successfully=True
            )
            db.add(resume_record)
            db.flush()

            # Store Extracted Skills
            existing_skill_names = {s.skill_name.lower() for s in candidate.skills}
            for s_info in parsed.get("skills", []):
                if s_info["skill_name"].lower() not in existing_skill_names:
                    db.add(CandidateSkill(
                        candidate_id=candidate.id,
                        skill_name=s_info["skill_name"],
                        category=s_info["category"],
                        confidence_score=s_info.get("confidence_score", 1.0)
                    ))
                    existing_skill_names.add(s_info["skill_name"].lower())

            # Store Education Records
            for edu in parsed.get("education", []):
                db.add(CandidateEducation(
                    candidate_id=candidate.id,
                    degree=edu["degree"],
                    field_of_study=edu.get("field_of_study"),
                    institution=edu.get("institution"),
                    graduation_year=edu.get("graduation_year")
                ))

            # Store Experience Records
            for exp in parsed.get("experience", []):
                db.add(CandidateExperience(
                    candidate_id=candidate.id,
                    title=exp["title"],
                    company=exp.get("company"),
                    duration_years=exp.get("duration_years", 0.0),
                    is_current=exp.get("is_current", False)
                ))

            db.commit()

            results.append(ResumeUploadResult(
                filename=orig_name,
                status="success",
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                message="Resume parsed and candidate profile created successfully.",
                extracted_skills_count=len(parsed.get("skills", [])),
                experience_years=candidate.total_experience_years
            ))

        except Exception as e:
            db.rollback()
            results.append(ResumeUploadResult(
                filename=orig_name,
                status="failed",
                message=f"Parsing error: {str(e)}"
            ))

    successful = sum(1 for r in results if r.status == "success")
    failed = sum(1 for r in results if r.status == "failed")

    return MultiUploadResponse(
        total_uploaded=len(files),
        successful_count=successful,
        failed_count=failed,
        results=results
    )

@router.get("", response_model=List[ResumeResponse])
def list_resumes(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all uploaded resume records."""
    return db.query(Resume).order_by(Resume.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{id}", response_model=ResumeResponse)
def get_resume(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch resume details."""
    resume = db.query(Resume).filter(Resume.id == id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume record not found.")
    return resume

@router.get("/{id}/download")
def download_resume(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Download the original uploaded PDF resume."""
    resume = db.query(Resume).filter(Resume.id == id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume record not found.")

    if not os.path.exists(resume.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file missing from storage.")

    return FileResponse(
        path=resume.file_path,
        media_type="application/pdf",
        filename=resume.original_filename
    )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a resume file and record."""
    resume = db.query(Resume).filter(Resume.id == id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume record not found.")

    if os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except OSError:
            pass

    db.delete(resume)
    db.commit()
    return None
