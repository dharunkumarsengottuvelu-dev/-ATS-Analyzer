import pandas as pd
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class FeatureExtractor:
    def __init__(self):
        pass

    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
            
        logger.info("Extracting features from cleaned data...")
        
        # 1. Extract numerical experience required
        df["experience_years"] = df["experience_required"].apply(self._extract_experience_years)
        
        # 2. Extract skill count
        df["skill_count"] = df["required_skills"].apply(lambda x: len(x.split(',')) if x else 0)
        
        # 3. Create a combined semantic text for embedding
        df["semantic_content"] = df.apply(self._create_semantic_text, axis=1)
        
        # 4. Generate unique Job ID if not present
        if "id" not in df.columns and "job_id" not in df.columns:
            df["job_id"] = [f"JOB_{i}" for i in range(len(df))]
        elif "id" in df.columns:
             df["job_id"] = df["id"].astype(str)
            
        logger.info("Feature extraction completed.")
        return df

    def extract_resume_features(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts features from a parsed resume dictionary to match the job dataset format.
        """
        skills = resume_data.get("skills", [])
        if isinstance(skills, list):
            skills_str = ", ".join(skills)
        else:
            skills_str = str(skills)
            
        experience_years = self._extract_experience_years(str(resume_data.get("total_experience", "0")))
        
        # Create semantic text for resume
        components = [
            f"Title: {resume_data.get('title', 'Professional')}",
            f"Skills: {skills_str}",
            f"Experience: {resume_data.get('summary', '')}",
        ]
        semantic_content = " | ".join(c for c in components if c)
        
        return {
            "skills": skills_str,
            "skill_list": [s.strip().lower() for s in skills_str.split(",") if s.strip()],
            "experience_years": experience_years,
            "semantic_content": semantic_content
        }

    def _extract_experience_years(self, exp_text: str) -> float:
        if not isinstance(exp_text, str):
            return 0.0
            
        # Look for numbers (e.g., "5 years", "3-5 yrs", "2+")
        matches = re.findall(r'(\d+)', str(exp_text))
        if not matches:
            return 0.0
            
        # If range like 3-5, take the minimum required (3)
        numbers = [float(m) for m in matches]
        return min(numbers)

    def _create_semantic_text(self, row: pd.Series) -> str:
        """
        Combines multiple fields into a single string for SentenceTransformer embeddings.
        """
        components = []
        if pd.notna(row.get("job_title")) and row["job_title"]:
            components.append(f"Title: {row['job_title']}")
            
        if pd.notna(row.get("required_skills")) and row["required_skills"]:
            components.append(f"Skills: {row['required_skills']}")
            
        if pd.notna(row.get("industry")) and row["industry"]:
            components.append(f"Industry: {row['industry']}")
            
        if pd.notna(row.get("job_description")) and row["job_description"]:
            # Truncate description to avoid excessively long embeddings, focus on first 1000 chars
            desc = str(row['job_description'])[:1000]
            components.append(f"Description: {desc}")
            
        return " | ".join(components)
