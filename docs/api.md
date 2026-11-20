# RepoSentinel API Documentation

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

Obtain a token by completing the GitHub OAuth flow:
1. GET `/api/v1/auth/login` — returns the GitHub OAuth URL.
2. User authorizes on GitHub.
3. POST `/api/v1/auth/callback?code=<code>` — returns `access_token`.

## Endpoints

### Health
- `GET /health` — Returns `{ "status": "ok" }`

### Repositories
- `GET /api/v1/repos` — List user's linked repos (synced from GitHub)
- `POST /api/v1/repos/{owner}/{name}/add` — Add a specific repository

### Scans
- `POST /api/v1/scans` — Trigger a scan
  - Body: `{ "repository_id": 1, "branch": "main" }`
- `GET /api/v1/scans/{id}` — Get scan status and summary

### Findings
- `GET /api/v1/findings` — List findings
  - Query params: `severity`, `category`, `scanner`, `repository_id`, `scan_id`, `skip`, `limit`

### Reports
- `GET /api/v1/reports/scan/{scan_id}/json` — Download JSON report
- `GET /api/v1/reports/scan/{scan_id}/csv` — Download CSV report

### Dashboard
- `GET /api/v1/dashboard/metrics` — Aggregate metrics for the current user
