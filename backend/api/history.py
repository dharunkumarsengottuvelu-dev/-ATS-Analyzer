from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from pydantic import BaseModel
from datetime import datetime
from collections import defaultdict

from backend.database.session import get_db
from backend.models.analysis import Analysis
from backend.models.resume import Resume
from backend.models.job import JobDescription
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(
    prefix="/history",
    tags=["History"]
)

class HistoryItem(BaseModel):
    id: int
    resume_filename: str
    job_title: str
    ats_score: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[HistoryItem])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(None, description="Search by resume name or job title"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    order: str = Query("desc", description="Sort order (asc or desc)")
):
    query = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    
    if search:
        # Join with Resume and JobDescription for searching
        query = query.join(Resume, Analysis.resume_id == Resume.id) \
                     .outerjoin(JobDescription, Analysis.job_id == JobDescription.id) \
                     .filter(
                         (Resume.filename.ilike(f"%{search}%")) |
                         (JobDescription.title.ilike(f"%{search}%"))
                     )
                     
    if order == "desc":
        if sort_by == "ats_score":
            query = query.order_by(desc(Analysis.ats_score))
        else:
            query = query.order_by(desc(Analysis.created_at))
    else:
        if sort_by == "ats_score":
            query = query.order_by(Analysis.ats_score)
        else:
            query = query.order_by(Analysis.created_at)

    analyses = query.offset(skip).limit(limit).all()
    
    results = []
    for a in analyses:
        resume = db.query(Resume).filter(Resume.id == a.resume_id).first()
        job = db.query(JobDescription).filter(JobDescription.id == a.job_id).first()
        
        results.append(HistoryItem(
            id=a.id,
            resume_filename=resume.filename if resume else "Unknown",
            job_title=job.title if job and job.title else "Job Description",
            ats_score=a.ats_score,
            status=a.status,
            created_at=a.created_at or datetime.now()
        ))
        
    return results

@router.delete("/{analysis_id}")
def delete_history_item(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id, 
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    db.delete(analysis)
    db.commit()
    return {"status": "success", "message": "History item deleted"}

@router.get("/analytics")
def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).all()
    total_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).count()
    total_analyses = len(analyses)
    
    avg_score = 0.0
    if total_analyses > 0:
        avg_score = sum(a.ats_score for a in analyses) / total_analyses
        
    trend = defaultdict(list)
    for a in analyses:
        if a.created_at:
            day_str = a.created_at.strftime("%Y-%m-%d")
            trend[day_str].append(a.ats_score)
        
    trend_data = []
    for day, scores in sorted(trend.items()):
        trend_data.append({
            "date": day,
            "average_score": sum(scores)/len(scores),
            "count": len(scores)
        })
        
    return {
        "total_resumes": total_resumes,
        "total_analyses": total_analyses,
        "average_score": round(avg_score, 1),
        "trend": trend_data
    }
