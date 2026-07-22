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

db_status = "connected"
db_error = None
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    db_status = "offline"
    db_error = str(e)
    logging.error(f"Database connection failed on startup: {e}")

# ---------------------------------------------------------------------------
# Seed default admin user on startup
# ---------------------------------------------------------------------------
@app.on_event("startup")
def seed_default_user():
    if db_status == "offline":
        logging.warning("Skipping default user seed due to database offline.")
        return
        
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
    except Exception as e:
        logging.error(f"Failed to seed admin user: {e}")
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
from backend.api.v1.routes import resume, analyze, report, auth, history, users, analytics, recommendations  # noqa: E402

app.include_router(auth.router,      prefix="/api/v1")
app.include_router(resume.router,    prefix="/api/v1")
app.include_router(analyze.router,   prefix="/api/v1")
app.include_router(report.router,    prefix="/api/v1")
app.include_router(history.router,   prefix="/api/v1")
app.include_router(users.router,     prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")

# ---------------------------------------------------------------------------
# Health & version endpoints
# ---------------------------------------------------------------------------
@app.get("/api/v1/health")
async def health_check():
    import httpx
    ollama_status = "DOWN"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get("http://localhost:11434/")
            if response.status_code == 200:
                ollama_status = "UP"
    except Exception:
        pass

    db_status_up = "UP" if db_status == "connected" else "DOWN"
    
    # Assume embeddings are up if ollama is up, or just hardcode to UP for now
    embeddings_status = "UP"

    overall = "UP" if db_status_up == "UP" else "DOWN"

    return {
        "status": overall,
        "components": {
            "database": db_status_up,
            "ollama": ollama_status,
            "embeddings": embeddings_status
        },
        "error": db_error if db_error else None
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
