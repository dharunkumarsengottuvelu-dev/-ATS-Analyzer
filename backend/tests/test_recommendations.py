import pytest
import pandas as pd
from backend.ai.recommendation.cleaner import DataCleaner
from backend.ai.recommendation.feature_extractor import FeatureExtractor

def test_cleaner_normalizes_skills():
    cleaner = DataCleaner()
    
    df = pd.DataFrame({
        "job_title": ["Frontend Dev"],
        "company_name": ["Acme"],
        "job_description": ["Need JS and React"],
        "required_skills": ["js, reactjs, html"],
        "experience_required": ["2 years"],
        "location": ["Remote"]
    })
    
    cleaned_df = cleaner.clean(df)
    
    skills = cleaned_df.iloc[0]["required_skills"]
    assert "JavaScript" in skills
    assert "React" in skills
    assert "html" in skills  # Keeps original case from input if not an alias

def test_feature_extractor_extracts_experience():
    extractor = FeatureExtractor()
    
    df = pd.DataFrame({
        "job_title": ["Dev"],
        "company_name": ["Acme"],
        "job_description": [""],
        "required_skills": [""],
        "experience_required": ["3-5 years"],
        "location": ["Remote"]
    })
    
    feat_df = extractor.extract_features(df)
    
    assert feat_df.iloc[0]["experience_years"] == 3.0

def test_resume_feature_extraction():
    extractor = FeatureExtractor()
    
    resume_data = {
        "title": "Software Engineer",
        "skills": ["JavaScript", "Python"],
        "total_experience": "5.5 years"
    }
    
    res = extractor.extract_resume_features(resume_data)
    
    assert res["experience_years"] == 5.0
    assert "javascript" in res["skill_list"]
    assert "python" in res["skill_list"]
    assert "Software Engineer" in res["semantic_content"]
