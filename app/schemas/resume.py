from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ResumeResponse(BaseModel):
    id: int
    candidate_id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    parsed_successfully: bool
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeUploadResult(BaseModel):
    filename: str
    status: str  # "success" or "failed"
    candidate_id: Optional[int] = None
    candidate_name: Optional[str] = None
    message: str
    extracted_skills_count: int = 0
    experience_years: float = 0.0

class MultiUploadResponse(BaseModel):
    total_uploaded: int
    successful_count: int
    failed_count: int
    results: List[ResumeUploadResult]
