import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "TalentMatch AI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "talentmatch-production-secret-key-must-be-changed-in-production-use"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = "sqlite:///./talentmatch.db"

    # Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]

    # AI & NLP
    SPACY_MODEL: str = "en_core_web_sm"

    # Configurable Scoring Weights (Default to 40/20/20/10/10)
    WEIGHT_REQUIRED_SKILLS: float = 40.0
    WEIGHT_PREFERRED_SKILLS: float = 20.0
    WEIGHT_EXPERIENCE: float = 20.0
    WEIGHT_EDUCATION: float = 10.0
    WEIGHT_TEXT_SIMILARITY: float = 10.0

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
