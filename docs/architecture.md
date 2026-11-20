# RepoSentinel Architecture

## Overview

RepoSentinel is a security intelligence platform that scans GitHub repositories for:
- Exposed secrets (Gitleaks)
- Vulnerable dependencies (OSV.dev)
- Insecure code patterns (Semgrep SAST)
- Configuration risks (Docker, GitHub Actions)

## System Components

```
┌─────────────────┐     HTTP API     ┌─────────────────┐
│  React Frontend │ ◄──────────────► │  FastAPI Backend│
│   (Vite + TS)   │                   │  (SQLite/PG)    │
└─────────────────┘                   └────────┬────────┘
                                                │
           ┌────────────────────────────────────┼────────────────┐
           │                                    │                │
           ▼                                    ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Gitleaks │    │   OSV    │    │ Semgrep  │    │ Config   │
    │ (secrets)│    │ (deps)   │    │ (SAST)   │    │ (files)  │
    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

## Scanning Flow

1. User triggers scan from frontend.
2. Backend clones repo to temp directory (shallow clone, timeout).
3. Four scanners run in parallel (`asyncio.gather`).
4. Findings normalized, deduplicated, and stored in DB.
5. Dashboard metrics and finding lists are updated.

## Security Model

- GitHub OAuth tokens stored in DB (encrypted at rest in production).
- Secrets redacted in logs, API responses, and storage.
- No execution of repository code during scanning.
- Subprocess timeouts prevent resource exhaustion.
- Path traversal is prevented (all file ops within temp dir).
- AI assistant never receives raw secret values.

## Database

SQLite for development, PostgreSQL for production.

| Table | Purpose |
|-------|---------|
| `users` | GitHub OAuth users |
| `repositories` | Linked repositories |
| `scans` | Scan jobs and status |
| `findings` | Security findings (deduplicated) |
| `scan_findings` | Junction table |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/auth/login` | Get GitHub OAuth URL |
| POST | `/api/v1/auth/callback` | Exchange code for token |
| GET | `/api/v1/auth/me` | Current user |
| GET | `/api/v1/repos` | List repositories |
| POST | `/api/v1/repos/{owner}/{name}/add` | Add repository |
| POST | `/api/v1/scans` | Trigger scan |
| GET | `/api/v1/scans/{id}` | Scan status |
| GET | `/api/v1/findings` | List findings (filterable) |
| GET | `/api/v1/dashboard/metrics` | Dashboard metrics |
| GET | `/api/v1/reports/scan/{id}/json` | JSON report |
| GET | `/api/v1/reports/scan/{id}/csv` | CSV report |
