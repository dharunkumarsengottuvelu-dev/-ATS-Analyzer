import spacy
from rapidfuzz import process, fuzz
from typing import List, Dict, Any

# Load English tokenizer, tagger, parser and NER
# Note: Requires running `python -m spacy download en_core_web_sm`
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spacy model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_skills(resume_text: str, known_skills: List[str], threshold: int = 85) -> Dict[str, Any]:
    """
    Extracts skills from the resume text by matching tokens and noun chunks 
    against a known list of skills using RapidFuzz.
    """
    doc = nlp(resume_text.lower())
    
    # Extract potential skill phrases (noun chunks and distinct tokens)
    potential_skills = set()
    for chunk in doc.noun_chunks:
        potential_skills.add(chunk.text)
    
    for token in doc:
        if not token.is_stop and not token.is_punct:
            potential_skills.add(token.text)
            
    matched_skills = set()
    for candidate in potential_skills:
        # Match candidate against known skills
        match = process.extractOne(candidate, known_skills, scorer=fuzz.WRatio)
        if match:
            matched_skill, score, _ = match
            if score >= threshold:
                matched_skills.add(matched_skill)
                
    return {
        "extracted": list(matched_skills)
    }

def match_job_description(resume_skills: List[str], jd_skills: List[str]) -> Dict[str, Any]:
    """
    Compares resume skills with JD skills.
    """
    resume_set = set([s.lower() for s in resume_skills])
    jd_set = set([s.lower() for s in jd_skills])
    
    matched = resume_set.intersection(jd_set)
    missing = jd_set.difference(resume_set)
    
    coverage = (len(matched) / len(jd_set)) * 100 if jd_set else 100.0
    
    return {
        "coverage_percentage": round(coverage, 2),
        "matched_skills": list(matched),
        "missing_skills": list(missing)
    }
