from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    address: Optional[str] = None

class Experience(BaseModel):
    company: str
    designation: str
    duration: str
    responsibilities: List[str]
    achievements: List[str]

class Education(BaseModel):
    degree: str
    university: str
    cgpa_or_percentage: Optional[str] = None
    graduation_year: Optional[str] = None

class Project(BaseModel):
    title: str
    description: str
    technologies: List[str]

class ParsedResume(BaseModel):
    raw_text: str
    contact_info: ContactInfo
    category: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    certifications: List[str] = []
    languages: List[str] = []

class UploadResponse(BaseModel):
    status: str
    message: str
    filename: str
    parsed_data: ParsedResume
    resume_id: Optional[int] = None
