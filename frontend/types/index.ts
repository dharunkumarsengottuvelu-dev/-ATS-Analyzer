export interface ContactInfo {
    email?: string;
    phone?: string;
    linkedin?: string;
    github?: string;
    portfolio?: string;
    address?: string;
}

export interface Experience {
    company: string;
    designation: string;
    duration: string;
    responsibilities: string[];
    achievements: string[];
}

export interface Education {
    degree: string;
    university: string;
    cgpa_or_percentage?: string;
    graduation_year?: string;
}

export interface Project {
    title: string;
    description: string;
    technologies: string[];
}

export interface ParsedResume {
    raw_text: string;
    contact_info: ContactInfo;
    category?: string;
    summary?: string;
    skills: string[];
    experience: Experience[];
    education: Education[];
    projects: Project[];
    certifications: string[];
    languages: string[];
}

export interface UploadResponse {
    status: string;
    message: string;
    filename: string;
    parsed_data: ParsedResume;
    resume_id?: number;
}

export interface MatchMetrics {
    semantic_match_percentage: number;
    keyword_coverage_percentage: number;
    matched_skills: string[];
    missing_skills: string[];
}

export interface AnalyzeResponse {
    status: string;
    metrics: MatchMetrics;
    extracted_resume_skills: string[];
    analysis_id?: number;
}

export interface ReportRequestPayload {
    filename: string;
    resume_text: string;
    job_description: string;
    resume_data: ParsedResume;
    metrics: MatchMetrics;
    analysis_id?: number;
}

export interface ReportResponse {
    status: string;
    message: string;
    job_id: string;
}

export interface ReportStatus {
    status: 'pending' | 'processing' | 'completed' | 'failed';
    message: string;
    pdf_url?: string;
    ats_score?: number;
    llm_feedback?: string;
    execution_time?: number;
    error?: string;
}
