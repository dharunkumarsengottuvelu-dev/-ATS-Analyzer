# ATS Resume Analyzer

## Project Overview
ATS Resume Analyzer is an AI-powered Offline Applicant Tracking System designed to evaluate resumes against Job Descriptions (JD) securely and privately. The system uses local LLMs and embeddings to ensure candidate data never leaves your environment.

## Architecture & Design
The application has recently undergone a major **Enterprise Architecture Refactoring**. It follows Clean Architecture principles, ensuring that business logic, data access, and routing are strictly decoupled. 
- **Frontend**: Built with Next.js, React, and Tailwind CSS using a **Feature-Based Architecture**.
- **Backend**: Built with Python, FastAPI, and SQLAlchemy using a **Service-Repository Pattern**.
- **AI/ML**: Powered by Llama 3.2 (via Ollama), HuggingFace SentenceTransformers, PyMuPDF, and XGBoost.
- **Database**: SQLite (Local defaults) with SQLAlchemy ORM.

## Project Structure

### Backend (`/backend`)
```
/backend
├── /ai             # AI/ML modules (parser, embeddings, scoring, recommendation)
├── /api            # Versioned API routes (e.g., /api/v1/routes)
├── /core           # Centralized configuration, logging, and security
├── /database       # Session management and database setup
├── /models         # SQLAlchemy database models
├── /repositories   # Data Access Layer (CRUD operations)
├── /schemas        # Pydantic validation schemas
└── /services       # Core Business Logic
```

### Frontend (`/frontend`)
```
/frontend
├── /app            # Next.js App Router (Pages, Layouts)
├── /components     # UI components divided by responsibility
│   ├── /features   # Complex business components (e.g., AnalysisPanel, FileUpload)
│   ├── /layout     # Layout wrappers (e.g., Sidebar, NetworkMonitor)
│   └── /ui         # Reusable basic components (Buttons, Inputs)
├── /services       # API Integration logic
├── /store          # Zustand state management
├── /types          # TypeScript type definitions
└── /utils          # Helper functions and constants
```

## Installation & Development

### 1. Database
The system uses SQLite by default (stored at `backend/ats.db`). If using PostgreSQL, configure the `DATABASE_URL` in your backend environment variables or `.env` file.

### 2. AI Model (Ollama)
Ensure Ollama is installed locally and the Llama 3.2 model is pulled:
```bash
ollama run llama3.2
```

### 3. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Docker Deployment
To run the full stack via Docker:
```bash
docker-compose up --build
```

## Contributing
Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on branching strategies, git workflows, and commit conventions.

## License
MIT License
