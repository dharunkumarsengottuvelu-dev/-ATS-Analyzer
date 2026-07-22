import re
from backend.schemas.resume import ContactInfo, ParsedResume
from backend.ai.parser.classifier import predict_resume_category

def extract_contact_info(text: str) -> ContactInfo:
    """
    Extracts basic contact information using Regex.
    (Will be enhanced with NLP later).
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
    github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+'
    
    email_match = re.search(email_pattern, text)
    phone_match = re.search(phone_pattern, text)
    linkedin_match = re.search(linkedin_pattern, text)
    github_match = re.search(github_pattern, text)
    
    return ContactInfo(
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
        linkedin=linkedin_match.group(0) if linkedin_match else None,
        github=github_match.group(0) if github_match else None,
        portfolio=None,
        address=None
    )

def parse_resume(text: str) -> ParsedResume:
    """
    Orchestrates the parsing of resume text into structured data.
    """
    contact_info = extract_contact_info(text)
    
    # Predict resume category
    category = predict_resume_category(text)
    
    # Placeholder for full NLP extraction (Phase 3/4)
    return ParsedResume(
        raw_text=text,
        contact_info=contact_info,
        category=category,
        summary=None,
        skills=[],
        experience=[],
        education=[],
        projects=[],
        certifications=[],
        languages=[]
    )
