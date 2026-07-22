import pandas as pd
import logging
import re

logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self):
        # Common skill aliases
        self.skill_aliases = {
            "js": "JavaScript",
            "reactjs": "React",
            "node": "Node.js",
            "nodejs": "Node.js",
            "py": "Python",
            "sql server": "Microsoft SQL Server",
            "ts": "TypeScript",
            "aws": "Amazon Web Services",
            "gcp": "Google Cloud Platform",
            "k8s": "Kubernetes",
            "tf": "TensorFlow",
            "nlp": "Natural Language Processing",
            "ml": "Machine Learning",
            "ai": "Artificial Intelligence",
            "dl": "Deep Learning",
            "c#": "C#",
            "cpp": "C++",
            "c++": "C++",
            "golang": "Go",
            "rn": "React Native",
            "vuejs": "Vue.js",
            "vue": "Vue.js",
        }
        
        # Heuristics for standardizing column names
        self.column_mappings = {
            "title": "job_title",
            "job title": "job_title",
            "role": "job_title",
            "company": "company_name",
            "company name": "company_name",
            "employer": "company_name",
            "skills": "required_skills",
            "required skills": "required_skills",
            "key skills": "required_skills",
            "technologies": "required_skills",
            "description": "job_description",
            "job description": "job_description",
            "responsibilities": "responsibilities",
            "experience": "experience_required",
            "experience required": "experience_required",
            "salary": "salary_range",
            "salary range": "salary_range",
            "location": "location",
            "job location": "location",
            "industry": "industry",
            "domain": "industry",
            "category": "job_category",
            "preferred skills": "preferred_skills",
            "qualifications": "education",
            "education": "education",
            "employment type": "employment_type",
        }

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
            
        logger.info("Starting data cleaning...")
        
        # 1. Normalize Column Names
        df.columns = [str(col).lower().strip() for col in df.columns]
        df.rename(columns=self.column_mappings, inplace=True)
        
        # Ensure core columns exist, even if empty
        core_cols = ['job_title', 'company_name', 'job_description', 'required_skills', 'experience_required', 'location']
        for col in core_cols:
            if col not in df.columns:
                df[col] = ""
                
        # 2. Handle missing values
        df.fillna({
            "job_title": "Unknown Title",
            "company_name": "Unknown Company",
            "job_description": "",
            "required_skills": "",
            "experience_required": "0",
            "location": "Remote",
        }, inplace=True)
        
        # Fill remaining object columns with empty string
        for col in df.select_dtypes(include=['object', 'str']):
            df[col] = df[col].fillna("")
            
        # 3. Deduplication (based on Title, Company, Description)
        initial_len = len(df)
        df.drop_duplicates(subset=["job_title", "company_name", "job_description"], keep="first", inplace=True)
        logger.info(f"Removed {initial_len - len(df)} duplicate rows.")
        
        # 4. Remove invalid rows (empty title AND empty description)
        invalid_mask = (df["job_title"].str.strip() == "") & (df["job_description"].str.strip() == "")
        invalid_count = invalid_mask.sum()
        df = df[~invalid_mask]
        logger.info(f"Removed {invalid_count} invalid rows.")
        
        # 5. Normalize specific text fields
        df["job_title"] = df["job_title"].apply(self._clean_text)
        df["company_name"] = df["company_name"].apply(self._clean_text)
        
        # 6. Normalize skills
        df["required_skills"] = df["required_skills"].apply(self._normalize_skills)
        
        logger.info(f"Data cleaning completed. {len(df)} rows remaining.")
        return df

    def _clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        # Remove extra whitespace and special characters
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def _normalize_skills(self, skills_text: str) -> str:
        if not isinstance(skills_text, str) or not skills_text:
            return ""
            
        # Split by comma, pipe, or newline
        raw_skills = re.split(r'[,|\n]', skills_text)
        
        normalized_skills = []
        for skill in raw_skills:
            skill = skill.strip()
            if not skill:
                continue
                
            skill_lower = skill.lower()
            if skill_lower in self.skill_aliases:
                normalized_skills.append(self.skill_aliases[skill_lower])
            else:
                # Keep original case for non-aliases, just clean it
                normalized_skills.append(self._clean_text(skill))
                
        # Return as comma separated unique skills
        return ", ".join(sorted(list(set(normalized_skills))))
