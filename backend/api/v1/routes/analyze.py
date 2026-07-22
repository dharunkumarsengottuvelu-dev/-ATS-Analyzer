from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.analysis import AnalyzeRequest, AnalyzeResponse, MatchMetrics
from backend.ai.analyzer.skills import extract_skills, match_job_description
from backend.ai.embeddings.semantic import calculate_semantic_similarity
from backend.models.skill import Skill
from backend.models.analysis import Analysis
from backend.models.job import JobDescription
from backend.models.user import User
from backend.api.v1.routes.deps import get_current_user_optional

router = APIRouter(
    prefix="/analyze",
    tags=["Analysis"]
)

@router.post("/match", response_model=AnalyzeResponse)
def analyze_job_match(
    request: AnalyzeRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Analyzes a resume against a job description.
    Performs keyword matching, skill extraction, semantic similarity scoring,
    and stores the job description and analysis history in the database.
    """
    try:
        user_id = current_user.id if current_user else 1
        
        # 1. Fetch known skills from local DB (Using a hardcoded list for now as fallback if DB is empty)
        db_skills = db.query(Skill.name).all()
        known_skills = [s[0] for s in db_skills]
        if not known_skills:
            # Fallback list if DB isn't seeded yet
            known_skills = ["python", "java", "react", "next.js", "fastapi", "sql", "machine learning", "nlp", "docker", "aws"]
        
        # 2. Extract skills from Resume
        resume_extraction = extract_skills(request.resume_text, known_skills)
        resume_skills = resume_extraction["extracted"]
        
        # 3. Extract skills from Job Description
        jd_extraction = extract_skills(request.job_description, known_skills)
        jd_skills = jd_extraction["extracted"]
        
        # 4. Compare Skills
        match_results = match_job_description(resume_skills, jd_skills)
        
        # 5. Semantic Similarity
        semantic_score = calculate_semantic_similarity(request.resume_text, request.job_description)
        
        # 6. Save Job Description to DB
        db_job = JobDescription(
            user_id=user_id,
            title="Extracted Job Title", # Can be improved by parsing title later
            company="Unknown Company",
            description_text=request.job_description
        )
        db.add(db_job)
        db.flush() # flush to get job_id without committing yet
        
        # 7. Save Analysis to DB
        # Note: We need a resume_id. For now, since the frontend isn't sending resume_id in the request payload,
        # we'll fetch the latest resume uploaded by this user, OR we'll default to 1.
        # This will be fully fixed when we update the frontend payload.
        # But for now, just fetch the most recent resume for this user.
        from backend.models.resume import Resume
        recent_resume = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).first()
        resume_id = recent_resume.id if recent_resume else 1
        
        db_analysis = Analysis(
            user_id=user_id,
            resume_id=resume_id,
            job_id=db_job.id,
            ats_score=0.0, # Will be updated after report generation
            semantic_score=semantic_score,
            keyword_score=match_results["coverage_percentage"],
            matched_skills=match_results["matched_skills"],
            missing_skills=match_results["missing_skills"],
            status="completed"
        )
        db.add(db_analysis)
        db.commit()
        
        metrics = MatchMetrics(
            semantic_match_percentage=semantic_score,
            keyword_coverage_percentage=match_results["coverage_percentage"],
            matched_skills=match_results["matched_skills"],
            missing_skills=match_results["missing_skills"]
        )
        
        # Return analysis_id in response so we can link report generation
        return AnalyzeResponse(
            status="success",
            metrics=metrics,
            extracted_resume_skills=resume_skills,
            analysis_id=db_analysis.id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
