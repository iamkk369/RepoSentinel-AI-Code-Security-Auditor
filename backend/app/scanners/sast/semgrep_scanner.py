"""Semgrep SAST scanner."""

import asyncio
import json
import os
import subprocess

from app.core.exceptions import ScannerException


class SemgrepScanner:
    TIMEOUT = 180
    DEFAULT_CONFIG = "p/security-audit"

    async def scan(self, repo_path: str) -> list[dict]:
        report_path = os.path.join(os.path.dirname(repo_path), "semgrep_report.json")
        proc = await asyncio.create_subprocess_exec(
            "semgrep",
            "--config", self.DEFAULT_CONFIG,
            repo_path,
            "--json",
            "--output", report_path,
            "--quiet",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            raise ScannerException("Semgrep scan timed out")

        if not os.path.exists(report_path):
            return []

        with open(report_path) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return []

        return self._normalize(data.get("results", []))

    def _normalize(self, results: list[dict]) -> list[dict]:
        findings = []
        for r in results:
            severity = r.get("extra", {}).get("metadata", {}).get("severity", "medium")
            findings.append({
                "finding_id": f"semgrep_{r.get('check_id', 'unknown')}_{r.get('path', 'x')}_{r.get('start', {}).get('line', 0)}",
                "scanner": "semgrep",
                "category": "sast",
                "title": r.get("check_id", "Semgrep finding"),
                "description": r.get("extra", {}).get("message", "No message provided."),
                "severity": self._severity(severity),
                "affected_file": r.get("path"),
                "line_number": r.get("start", {}).get("line"),
                "vulnerability_id": r.get("check_id"),
                "evidence": r.get("extra", {}).get("lines", "").strip()[:500],
                "remediation": "Review the flagged code pattern and refactor to mitigate the identified risk. See Semgrep rule documentation for details.",
            })
        return findings

    def _severity(self, semgrep_severity: str) -> str:
        mapping = {
            "ERROR": "high",
            "WARNING": "medium",
            "INFO": "low",
        }
        return mapping.get(semgrep_severity.upper(), "medium")
