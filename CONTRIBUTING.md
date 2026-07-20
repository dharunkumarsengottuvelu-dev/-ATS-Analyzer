# Contributing to ATS Resume Analyzer

We use a strict branching and code review strategy to maintain high code quality and prevent regressions.

## Branch Strategy & Ownership
The repository uses a component-based branching strategy:
- `main` - Protected. Production-ready code.
- `develop` - Protected. Integration branch for all features.
- `frontend` - UI/Next.js components (Owner: SUTHEESHWARAN)
- `backend` - FastAPI/APIs (Owner: dharunkumarsengottuvelu-dev)
- `database` - SQL/Schema (Owner: gowthamganesan103-cmyk)
- `docker` - Deployment (Owner: ha-rish632)
- `ai-model` - AI/LLM integrations (Owner: dharunkumarsengottuvelu-dev)

## Git Workflow
1. **Never commit directly to `main` or `develop`.**
2. Always checkout your designated branch: `git checkout frontend`
3. If creating a specific feature, branch off your component branch: `git checkout -b frontend/dashboard-fix`
4. Push to your branch and open a Pull Request against `develop`.

## Commit Convention
We strictly follow [Conventional Commits](https://www.conventionalcommits.org/).
Every commit must be prefixed with a type:
- `feat(frontend): add responsive navbar`
- `feat(database): add migration for users table`
- `fix(api): resolve 500 error on upload`
- `docs: update readme instructions`
- `refactor: clean up semantic matching`
- `style: format python files`
- `perf: optimize embedding load time`
- `test: add unit tests for parsing`
- `chore: update dependencies`

## Pull Requests & Review Process
1. Push your branch to GitHub.
2. Open a Pull Request targeting the `develop` branch.
3. Ensure all CI/CD status checks pass.
4. Request a review from the relevant component owner.
5. Once approved, the PR can be merged into `develop`.

## Coding Standards
- **Python**: PEP-8 compliance, use type hints, write docstrings.
- **TypeScript**: Strict mode enabled, no `any` types, use functional React components.
- **SQL**: Use clear migration scripts, avoid raw queries in application code where possible.
