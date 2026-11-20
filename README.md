# RepoSentinel — AI-Assisted GitHub Repository Security Intelligence Platform

RepoSentinel analyzes GitHub repositories to detect security weaknesses including exposed secrets, vulnerable dependencies, insecure coding patterns, and configuration risks.

## Features

- 🔐 **Secret Detection** — Gitleaks integration for API keys, tokens, credentials, and private keys
- 📦 **Dependency Vulnerability Scanner** — OSV.dev powered analysis of dependency manifests
- 🛡️ **Static Application Security Testing (SAST)** — Semgrep rules for insecure code patterns
- ⚙️ **Configuration Security** — Scan Dockerfiles, GitHub Actions, and compose files
- 📊 **Security Dashboard** — Clean, responsive React frontend with actionable metrics
- 📄 **Reports** — Export findings as JSON and CSV
- 🤖 **AI Security Assistant** *(optional)* — Explainable remediation guidance

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic
- **Frontend:** React, Vite, TypeScript
- **Database:** SQLite (development), PostgreSQL (production)
- **Security Tools:** Gitleaks, Semgrep, OSV.dev API

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Git
- Gitleaks
- Semgrep

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your GitHub OAuth app credentials
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Documentation

- [Architecture](./docs/architecture.md)
- [Security](./docs/security.md)
- [API](./docs/api.md)

## License

MIT
