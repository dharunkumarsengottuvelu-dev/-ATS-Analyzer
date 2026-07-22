from backend.schemas.analysis import MatchMetrics

def calculate_ats_score(metrics: MatchMetrics, resume_data: dict) -> dict:
    """
    Calculates the final ATS score based on various weighted metrics.
    - Semantic Similarity (40%)
    - Keyword Coverage (40%)
    - Resume Completeness (20%)
    """
    semantic_weight = 0.4
    keyword_weight = 0.4
    completeness_weight = 0.2
    
    # 1. Semantic Score (0-100)
    semantic_score = metrics.semantic_match_percentage
    
    # 2. Keyword Coverage Score (0-100)
    keyword_score = metrics.keyword_coverage_percentage
    
    # 3. Completeness Score (0-100)
    # Check if key sections exist in the parsed resume data
    completeness_score = 0
    if resume_data.get("contact_info", {}).get("email"):
        completeness_score += 20
    if resume_data.get("contact_info", {}).get("phone"):
        completeness_score += 20
    if len(resume_data.get("experience", [])) > 0:
        completeness_score += 30
    if len(resume_data.get("education", [])) > 0:
        completeness_score += 20
    if len(resume_data.get("skills", [])) > 0:
        completeness_score += 10
        
    # Calculate weighted total
    final_score = (semantic_score * semantic_weight) + \
                  (keyword_score * keyword_weight) + \
                  (completeness_score * completeness_weight)
                  
    return {
        "overall_score": round(final_score, 2),
        "breakdown": {
            "semantic_score": round(semantic_score, 2),
            "keyword_score": round(keyword_score, 2),
            "completeness_score": round(completeness_score, 2)
        }
    }
