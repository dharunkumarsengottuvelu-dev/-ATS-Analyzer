import os
import sys
import json
import random
from sqlalchemy.orm import Session
from backend.database.session import SessionLocal, engine, Base
from backend.models.job import Job
from typing import List

# Setup sys path so we can run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Base.metadata.create_all(bind=engine)

def seed_jobs():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Job).count() > 0:
            print("Jobs already seeded. Skipping.")
            return

        roles = [
            ("Software Engineer", ["Python", "Java", "C++", "SQL", "Git", "REST API", "Docker"]),
            ("Full Stack Developer", ["React", "Node.js", "TypeScript", "Express", "MongoDB", "SQL", "AWS"]),
            ("Frontend Developer", ["React", "Vue", "Angular", "HTML", "CSS", "JavaScript", "TypeScript"]),
            ("Backend Developer", ["Python", "Django", "FastAPI", "Go", "PostgreSQL", "Redis", "Kafka"]),
            ("Python Developer", ["Python", "Django", "Flask", "Pandas", "Pytest", "SQL", "AWS"]),
            ("Java Developer", ["Java", "Spring Boot", "Hibernate", "SQL", "Kafka", "AWS", "Microservices"]),
            ("React Developer", ["React", "Redux", "Next.js", "TypeScript", "Tailwind CSS", "Jest", "HTML"]),
            ("Node.js Developer", ["Node.js", "Express", "NestJS", "TypeScript", "MongoDB", "Redis", "Docker"]),
            ("AI Engineer", ["Python", "PyTorch", "TensorFlow", "NLP", "LLMs", "LangChain", "Vector Databases"]),
            ("ML Engineer", ["Python", "Scikit-learn", "TensorFlow", "MLflow", "AWS SageMaker", "SQL", "Pandas"]),
            ("Data Analyst", ["SQL", "Excel", "Tableau", "Power BI", "Python", "Pandas", "Statistics"]),
            ("Data Scientist", ["Python", "R", "SQL", "Machine Learning", "Statistics", "Data Visualization", "Jupyter"]),
            ("DevOps Engineer", ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD", "Linux", "Bash", "Python"]),
            ("Cloud Engineer", ["AWS", "Azure", "GCP", "Terraform", "Kubernetes", "Linux", "Networking"]),
            ("Cyber Security Engineer", ["Security", "Network Security", "Penetration Testing", "Python", "Linux", "SIEM", "Cryptography"]),
            ("UI/UX Designer", ["Figma", "Sketch", "Adobe XD", "Wireframing", "Prototyping", "User Research", "HTML/CSS"])
        ]

        companies = ["Google", "Meta", "Amazon", "Netflix", "Apple", "Microsoft", "Stripe", "Airbnb", "Uber", "Lyft", "Twitter", "Snap", "Spotify", "Dropbox", "Slack", "Atlassian", "Twilio", "Zoom", "Snowflake", "Databricks", "Palantir", "Coinbase", "Robinhood", "Instacart", "DoorDash", "Pinterest", "Reddit", "Discord", "GitHub", "GitLab"]
        
        locations = ["San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX", "London, UK", "Remote", "Toronto, Canada", "Berlin, Germany", "Sydney, Australia", "Bangalore, India", "Singapore", "Dublin, Ireland", "Chicago, IL", "Boston, MA", "Los Angeles, CA"]
        
        levels = [
            ("Entry Level", "0-2 years", "$70,000 - $100,000"),
            ("Mid Level", "2-5 years", "$100,000 - $150,000"),
            ("Senior Level", "5-8 years", "$150,000 - $220,000"),
            ("Staff Level", "8+ years", "$200,000 - $300,000")
        ]

        jobs_to_create = []

        for i in range(500):
            role_title, all_skills = random.choice(roles)
            company = random.choice(companies)
            location = random.choice(locations)
            level_name, experience, salary = random.choice(levels)
            
            # Pick a subset of skills
            k = random.randint(3, len(all_skills))
            required_skills = random.sample(all_skills, k)

            title = f"{level_name} {role_title}" if level_name != "Mid Level" else role_title

            desc = f"We are looking for a highly skilled {title} to join our team at {company}. You will be responsible for developing cutting edge solutions and working with modern tech stacks. Location: {location}. Experience required: {experience}."

            job = Job(
                title=title,
                company=company,
                location=location,
                experience=experience,
                salary=salary,
                description=desc,
                required_skills=json.dumps(required_skills),
                job_type=random.choice(["Full-time", "Full-time", "Full-time", "Contract", "Part-time"]),
                apply_link=f"https://example.com/careers/{company.lower()}/job/{i}"
            )
            jobs_to_create.append(job)

        db.bulk_save_objects(jobs_to_create)
        db.commit()
        print(f"Successfully seeded {len(jobs_to_create)} jobs.")

    except Exception as e:
        print(f"Error seeding jobs: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_jobs()
