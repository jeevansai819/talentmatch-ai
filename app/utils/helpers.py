import re
import os
import uuid
from typing import Optional, List, Tuple
from datetime import datetime

# Regex patterns for contact information
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+?\d{10,13}')
LINKEDIN_REGEX = re.compile(r'linkedin\.com/in/[a-zA-Z0-9_-]+', re.IGNORECASE)
GITHUB_REGEX = re.compile(r'github\.com/[a-zA-Z0-9_-]+', re.IGNORECASE)

YEAR_REGEX = re.compile(r'\b(19\d{2}|20\d{2})\b')
EXPERIENCE_YEARS_REGEX = re.compile(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)?', re.IGNORECASE)

def normalize_text(text: str) -> str:
    """Preprocess text: lowercasing, whitespace normalization, cleaning."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[^\w\s\+\#\.\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_email(text: str) -> Optional[str]:
    """Extract primary email address from text."""
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    """Extract primary phone number from text."""
    match = PHONE_REGEX.search(text)
    if match:
        raw = match.group(0).strip()
        # Clean up punctuation
        cleaned = re.sub(r'[^\d\+]', '', raw)
        return raw if len(cleaned) >= 10 else None
    return None

def extract_links(text: str) -> dict:
    """Extract LinkedIn and GitHub handles/URLs."""
    linkedin = LINKEDIN_REGEX.search(text)
    github = GITHUB_REGEX.search(text)
    return {
        "linkedin": f"https://{linkedin.group(0)}" if linkedin else None,
        "github": f"https://{github.group(0)}" if github else None
    }

def sanitize_filename(filename: str) -> str:
    """Create a safe unique stored filename while keeping original extension."""
    ext = os.path.splitext(filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    return safe_name

def format_file_size(size_bytes: int) -> str:
    """Format bytes into human-readable string (KB/MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def extract_experience_years_from_text(text: str) -> float:
    """
    Search for explicit experience statements (e.g. '5+ years of experience')
    or estimate total experience duration from date ranges (e.g., '2019 - 2024').
    """
    # 1. Check explicit declarations
    exp_matches = EXPERIENCE_YEARS_REGEX.findall(text)
    if exp_matches:
        try:
            values = [float(v) for v in exp_matches if float(v) < 45]
            if values:
                return max(values)
        except ValueError:
            pass

    # 2. Extract year spans
    years = [int(y) for y in YEAR_REGEX.findall(text)]
    valid_years = [y for y in years if 1980 <= y <= datetime.now().year]
    if len(valid_years) >= 2:
        span = max(valid_years) - min(valid_years)
        if 0 < span <= 40:
            return float(span)

    return 0.0
