"""Gitleaks secret detection scanner."""

import asyncio
import json
import os
import subprocess

from app.core.exceptions import ScannerException


class GitleaksScanner:
    TIMEOUT = 120

    async def scan(self, repo_path: str) -> list[dict]:
        report_path = os.path.join(os.path.dirname(repo_path), "gitleaks_report.json")
        proc = await asyncio.create_subprocess_exec(
            "gitleaks",
            "detect",
            "--source", repo_path,
            "--report-format", "json",
            "--report-path", report_path,
            "--exit-code", "0",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            raise ScannerException("Gitleaks scan timed out")

        if not os.path.exists(report_path):
            return []

        with open(report_path) as f:
            try:
                findings = json.load(f)
            except json.JSONDecodeError:
                return []

        return self._normalize(findings)

    def _normalize(self, findings: list[dict]) -> list[dict]:
        results = []
        for f in findings:
            secret = f.get("Secret", "")
            redacted = secret[:4] + "***REDACTED***" if len(secret) > 4 else "***REDACTED***"
            results.append({
                "finding_id": f"gitleaks_{f.get('Fingerprint', f.get('StartLine', '0'))}_{f.get('File', 'unknown')}",
                "scanner": "gitleaks",
                "category": "secrets",
                "title": f"Exposed {f.get('Description', 'secret')}",
                "description": f"Detected potential secret: {f.get('Description', 'unknown')}. Value: {redacted}",
                "severity": self._severity(f.get("Description", "")),
                "affected_file": f.get("File"),
                "line_number": f.get("StartLine"),
                "vulnerability_id": None,
                "evidence": redacted,
                "remediation": "Remove the secret from the repository, rotate the credential, and use environment variables or a secrets manager.",
            })
        return results

    def _severity(self, description: str) -> str:
        desc = description.lower()
        if any(k in desc for k in ("private key", "aws_secret", "api_key")):
            return "critical"
        if any(k in desc for k in ("password", "token", "secret")):
            return "high"
        return "medium"
