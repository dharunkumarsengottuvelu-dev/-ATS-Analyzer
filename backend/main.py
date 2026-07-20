from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Offline AI ATS Resume Analyzer API",
    description="Backend API for local AI ATS Resume Analyzer using Llama 3.2",
    version="1.0.0"
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging
    logging.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected server error occurred.", "details": str(exc)},
    )

from backend.api import resume, analyze, report, auth
from backend.database.session import engine, SessionLocal, get_db
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.models import User, Resume, JobDescription, Analysis, Report, Settings, ActivityLog, Skill
from backend.database.session import Base
from backend.core.security import get_password_hash

# Create all database tables
Base.metadata.create_all(bind=engine)

# Seed a default admin user for local usage
@app.on_event("startup")
def seed_default_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            default_user = User(
                username="admin", 
                email="admin@local.com", 
                hashed_password=get_password_hash("admin")
            )
            db.add(default_user)
            db.commit()
    finally:
        db.close()

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin"],
)

import time
import logging
from fastapi import Request

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"path={request.url.path} method={request.method} "
        f"status={response.status_code} duration={process_time:.3f}s"
    )
    return response

from backend.api import resume, analyze, report, auth, history, users, analytics

app.include_router(auth.router, prefix="/api/v1")
app.include_router(resume.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(report.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "UP",
        "version": "1.0.0",
        "components": {
            "database": "UP",
            "ollama": "UP",
            "embeddings": "UP"
        }
    }

@app.get("/api/v1/version")
async def get_version():
    return {"version": "1.0.0"}
