import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# App creation
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Offline AI ATS Resume Analyzer API",
    description="Backend API for local AI ATS Resume Analyzer using Llama 3.2",
    version="1.0.0"
)

# ---------------------------------------------------------------------------
# Database setup (must happen before routers are attached)
# ---------------------------------------------------------------------------
from backend.database.session import engine, SessionLocal, get_db, Base  # noqa: E402
from backend.models import User, Resume, JobDescription, Analysis, Report, Settings, ActivityLog, Skill  # noqa: E402
from backend.core.security import get_password_hash  # noqa: E402

Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------------
# Seed default admin user on startup
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
from backend.api import resume, analyze, report, auth, history, users, analytics  # noqa: E402

app.include_router(auth.router,      prefix="/api/v1")
app.include_router(resume.router,    prefix="/api/v1")
app.include_router(analyze.router,   prefix="/api/v1")
app.include_router(report.router,    prefix="/api/v1")
app.include_router(history.router,   prefix="/api/v1")
app.include_router(users.router,     prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

# ---------------------------------------------------------------------------
# Health & version endpoints
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Logging middleware  (added first = innermost, runs after CORS)
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled error: {exc}")
        response = JSONResponse(
            status_code=500,
            content={"message": "An unexpected server error occurred.", "details": str(exc)},
        )
    process_time = time.time() - start_time
    logger.info(
        f"path={request.url.path} method={request.method} "
        f"status={response.status_code} duration={process_time:.3f}s"
    )
    return response

# ---------------------------------------------------------------------------
# CORS middleware — added LAST so it is the OUTERMOST middleware.
# This guarantees Access-Control-Allow-Origin is on EVERY response,
# including 4xx / 5xx error responses.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
