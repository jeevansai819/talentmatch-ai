import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Ensure all models are registered

# Import routers
from app.routers.auth import router as auth_router
from app.routers.resumes import router as resumes_router
from app.routers.jobs import router as jobs_router
from app.routers.candidates import router as candidates_router
from app.routers.matching import router as matching_router
from app.routers.shortlists import router as shortlists_router
from app.routers.analytics import router as analytics_router
from app.routers.web import router as web_router

# Initialize database schema on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TalentMatch AI",
    description="Enterprise-grade AI-Powered Resume Screening & Job Matching Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets
static_path = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_path):
    os.makedirs(static_path, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Mount API routers
app.include_router(auth_router)
app.include_router(resumes_router)
app.include_router(jobs_router)
app.include_router(candidates_router)
app.include_router(matching_router)
app.include_router(shortlists_router)
app.include_router(analytics_router)

# Mount Web View router
app.include_router(web_router)

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"detail": "API endpoint not found."})
    return JSONResponse(status_code=404, content={"detail": "Page not found."})

@app.get("/api/health", tags=["Health"])
def health_check():
    """Application health and status check."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
