# RepoSentinel Security Documentation

## Security-First Design

This document covers the security considerations built into RepoSentinel.

## Token Handling

- GitHub OAuth tokens are never logged or exposed to the frontend.
- Access tokens are encrypted at rest in production environments.
- Tokens are refreshed on each login.

## Secret Detection & Handling

- Gitleaks discovers secrets but the backend immediately redacts values:
  - Only the first 4 characters are visible in evidence.
  - Values are marked `***REDACTED***` before storage.
- Raw secret values are never sent to the AI assistant.
- Secret values are never returned in API responses or reports.

## Scanning Safety

- Repositories are cloned to temporary directories.
- Shallow clones (`--depth 1`) reduce disk and time requirements.
- Clone timeout: 120 seconds. Scan timeout: 180 seconds.
- After scanning, the temp directory is deleted.
- No repository code is executed.
- No dependencies are installed from the scanned repository.
- No build scripts are run.

## Path Traversal Protection

All file paths during scanning are resolved relative to the cloned repo root. No `../` escapes are permitted.

## Subprocess Security

Scanner subprocesses run with explicit timeouts. If a scanner hangs, it is killed automatically.

## AI Assistant Safety

- AI features are optional and disabled when no API key is configured.
- Evidence is redacted before being sent to any AI provider.
- AI output is clearly labeled as `[AI-generated]`.
- AI never overrides scanner findings.
- AI never creates commits, pull requests, or modifies source code.

## Rate Limiting

GitHub API usage follows rate limits. The app surfaces rate limit errors to users.

## Known Limitations

- This is an MVP. Some advanced security features (e.g., SBOM generation, container image scanning, differential scanning) are out of scope.
- False positives from SAST rules are expected. Users should triage findings.
- OSV.dev data coverage varies by ecosystem.
