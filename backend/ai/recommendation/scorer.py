import pandas as pd
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Scorer:
    def __init__(self, model_trainer):
        self.model_trainer = model_trainer

    def score_candidates(
        self, 
        resume_features: Dict[str, Any], 
        candidate_metadatas: List[Dict[str, Any]], 
        candidate_distances: List[float],
        candidate_ids: List[str]
    ) -> List[Dict[str, Any]]:
        
        if not candidate_metadatas:
            return []
            
        resume_skills = set(resume_features.get("skill_list", []))
        resume_exp = resume_features.get("experience_years", 0.0)
        
        feature_rows = []
        detailed_results = []
        
        for i, meta in enumerate(candidate_metadatas):
            job_id = candidate_ids[i]
            # distance is (1 - cosine_similarity). So similarity = 1 - distance
            semantic_sim = 1.0 - candidate_distances[i]
            
            job_skills_str = meta.get("required_skills", "")
            job_skills = set([s.strip().lower() for s in job_skills_str.split(",") if s.strip()])
            
            job_exp = meta.get("experience_years", 0.0)
            
            # Calculate explicit features
            overlap_skills = resume_skills.intersection(job_skills)
            missing_skills = job_skills.difference(resume_skills)
            
            skill_overlap_count = len(overlap_skills)
            skill_overlap_ratio = skill_overlap_count / len(job_skills) if len(job_skills) > 0 else 1.0
            
            exp_diff = resume_exp - job_exp
            
            # Prepare row for XGBoost prediction
            feature_rows.append({
                "job_id": job_id,
                "skill_overlap_ratio": skill_overlap_ratio,
                "skill_overlap_count": skill_overlap_count,
                "semantic_similarity": semantic_sim,
                "experience_diff": exp_diff
            })
            
            # Prepare output metadata
            detailed_results.append({
                "job_id": job_id,
                "company_name": meta.get("company_name", "Unknown"),
                "job_title": meta.get("job_title", "Unknown"),
                "location": meta.get("location", "Remote"),
                "experience_required": job_exp,
                "semantic_similarity": float(semantic_sim),
                "matched_skills": list(overlap_skills),
                "missing_skills": list(missing_skills),
                "ats_compatibility_score": round(skill_overlap_ratio * 100, 2),
            })
            
        # Predict using XGBoost
        df_features = pd.DataFrame(feature_rows)
        xgb_scores = self.model_trainer.predict(df_features)
        
        # Combine scores and rank
        for i, result in enumerate(detailed_results):
            # Scale score to 0-100%
            conf_score = max(0.0, min(100.0, float(xgb_scores[i]) * 100))
            result["confidence_score"] = round(conf_score, 2)
            result["match_percentage"] = round(conf_score, 2) # Equivalent in this context
            
            # Generate Learning Recommendations
            missing = result["missing_skills"]
            if missing:
                result["learning_recommendations"] = [
                    f"Consider taking a course on {skill.title()} to improve your chances."
                    for skill in missing[:3]
                ]
            else:
                result["learning_recommendations"] = ["Your skills perfectly align with this role!"]
                
        # Sort by confidence_score descending
        ranked_results = sorted(detailed_results, key=lambda x: x["confidence_score"], reverse=True)
        
        # Add ranking position
        for i, res in enumerate(ranked_results):
            res["ranking_position"] = i + 1
            res["why_recommended"] = f"Strong semantic match ({round(res['semantic_similarity']*100)}%) with {len(res['matched_skills'])} matching skills."
            
        return ranked_results
