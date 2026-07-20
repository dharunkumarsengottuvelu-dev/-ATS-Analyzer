from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description: str

class MatchMetrics(BaseModel):
    semantic_match_percentage: float
    keyword_coverage_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]

class AnalyzeResponse(BaseModel):
    status: str
    metrics: MatchMetrics
    extracted_resume_skills: List[str]
    analysis_id: Optional[int] = None
