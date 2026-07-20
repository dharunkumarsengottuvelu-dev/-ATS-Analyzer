# ATS Resume Analyzer

## Project Overview
ATS Resume Analyzer is an AI-powered Offline Applicant Tracking System designed to evaluate resumes against Job Descriptions (JD) securely and privately. 

## Architecture
The application runs locally without internet dependencies using an offline LLM (Llama 3.2 via Ollama) for analysis, a FastAPI backend, and a Next.js frontend dashboard.

## Technology Stack
- **Frontend**: Next.js, React, Tailwind CSS
- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: PostgreSQL / SQLite (Local)
- **AI/ML**: Ollama (Llama 3.2), HuggingFace SentenceTransformers
- **Deployment**: Docker, Docker Compose, Nginx

## Folder Structure
```
/frontend    - Next.js UI Dashboard (Owner: SUTHEESHWARAN)
/backend     - FastAPI application (Owner: dharunkumarsengottuvelu-dev)
/database    - SQL schemas & migrations (Owner: gowthamganesan103-cmyk)
/docker      - Container configs (Owner: ha-rish632)
/ai-model    - Local models & embeddings (Owner: dharunkumarsengottuvelu-dev)
```

## Installation & Development

### 1. Database
Set up PostgreSQL and configure the connection string in your environment variables.

### 2. AI Model (Ollama)
Ensure Ollama is installed locally and the Llama 3.2 model is pulled:
`ollama run llama3.2`

### 3. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Docker Running
To run the full stack via Docker:
```bash
docker-compose up --build
```

## Contributing
Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on branching strategies, git workflows, and commit conventions.

## License
MIT License

