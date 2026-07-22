from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import List, Dict, Any

from backend.database.session import get_db
from backend.models.analysis import Analysis
from backend.models.resume import Resume
from backend.api.v1.routes.deps import get_current_user
from backend.models.user import User

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total Resumes
    total_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    
    # Analyses stats
    analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).all()
    total_analyses = len(analyses)
    
    today = date.today()
    todays_analyses = sum(1 for a in analyses if a.created_at and a.created_at.date() == today)
    
    avg_score = 0.0
    max_score = 0.0
    min_score = 0.0
    
    if total_analyses > 0:
        scores = [a.ats_score for a in analyses]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        
    return {
        "total_resumes": total_resumes,
        "total_analyses": total_analyses,
        "todays_analyses": todays_analyses,
        "average_score": round(avg_score, 1),
        "highest_score": round(max_score, 1),
        "lowest_score": round(min_score, 1)
    }

@router.get("/charts")
def get_charts_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).all()
    
    # 1. Score Distribution (Pie/Bar)
    distribution = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for a in analyses:
        score = a.ats_score
        if score <= 20: distribution["0-20"] += 1
        elif score <= 40: distribution["21-40"] += 1
        elif score <= 60: distribution["41-60"] += 1
        elif score <= 80: distribution["61-80"] += 1
        else: distribution["81-100"] += 1
        
    # 2. Skill Frequencies
    skill_counts = {}
    for a in analyses:
        if a.matched_skills and isinstance(a.matched_skills, list):
            for skill in a.matched_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
                
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "score_distribution": distribution,
        "top_skills": [{"skill": k, "count": v} for k, v in top_skills]
    }
