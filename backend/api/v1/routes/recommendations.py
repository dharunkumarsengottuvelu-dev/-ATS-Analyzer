from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.ai.recommendation.engine import get_recommendation_engine

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

class ResumeData(BaseModel):
    title: Optional[str] = ""
    summary: Optional[str] = ""
    skills: List[str] = []
    total_experience: Optional[float] = 0.0

class MatchResponse(BaseModel):
    job_id: str
    company_name: str
    job_title: str
    location: str
    experience_required: float
    semantic_similarity: float
    matched_skills: List[str]
    missing_skills: List[str]
    ats_compatibility_score: float
    confidence_score: float
    match_percentage: float
    ranking_position: int
    why_recommended: str
    learning_recommendations: List[str]

@router.post("/train", summary="Train the AI Job Recommendation Engine")
async def train_recommendation_engine(background_tasks: BackgroundTasks):
    """
    Triggers the training pipeline in the background. 
    It will load data, clean it, generate embeddings, and train the XGBoost model.
    """
    def run_pipeline():
        engine = get_recommendation_engine()
        engine.run_training_pipeline()
        
    background_tasks.add_task(run_pipeline)
    
    return {"status": "processing", "message": "Training pipeline started in the background."}

@router.post("/match", response_model=List[MatchResponse], summary="Get Top Job Recommendations for a Resume")
async def match_resume_to_jobs(resume_data: ResumeData):
    """
    Accepts parsed resume features and returns the Top 10 recommended jobs.
    Uses Semantic Search (ChromaDB) and an XGBoost Ranking Model.
    """
    try:
        engine = get_recommendation_engine()
        results = engine.recommend_jobs(resume_data.dict(), top_n=10)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
