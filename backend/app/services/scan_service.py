"""Scan service — orchestrates repository cloning and scanner execution."""

import asyncio
import json
import os
import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.finding import Finding, ScanFinding
from app.models.scan import Scan
from app.scanners.configuration.config_scanner import ConfigScanner
from app.scanners.dependencies.osv_scanner import OSVScanner
from app.scanners.sast.semgrep_scanner import SemgrepScanner
from app.scanners.secrets.gitleaks_scanner import GitleaksScanner


class ScanService:
    MAX_REPO_SIZE_MB = 500
    CLONE_TIMEOUT = 120  # seconds

    def __init__(self, db: Session, github_token: str):
        self.db = db
        self.github_token = github_token

    async def run_scan(self, scan_id: int, repo_full_name: str, branch: str = "main") -> None:
        scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return

        scan.status = "running"
        scan.started_at = datetime.now(timezone.utc)
        self.db.commit()

        temp_dir = tempfile.mkdtemp(prefix="reposentinel_")
        try:
            repo_path = await self._clone_repo(temp_dir, repo_full_name, branch)
            all_findings = await self._run_scanners(repo_path)
            await self._persist_findings(scan_id, all_findings)

            scan.status = "completed"
            scan.completed_at = datetime.now(timezone.utc)
        except Exception as e:
            scan.status = "failed"
            scan.error_message = str(e)
            scan.completed_at = datetime.now(timezone.utc)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            self.db.commit()

    async def _clone_repo(self, temp_dir: str, repo_full_name: str, branch: str) -> str:
        repo_path = os.path.join(temp_dir, "repo")
        url = f"https://{self.github_token}@github.com/{repo_full_name}.git"
        proc = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth", "1", "--branch", branch, url, repo_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.CLONE_TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            raise RuntimeError("Repository clone timed out")
        if proc.returncode != 0:
            raise RuntimeError(f"Clone failed: {stderr.decode()}")
        return repo_path

    async def _run_scanners(self, repo_path: str) -> list[dict]:
        scanners = [
            GitleaksScanner(),
            OSVScanner(),
            SemgrepScanner(),
            ConfigScanner(),
        ]
        tasks = [scanner.scan(repo_path) for scanner in scanners]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        findings = []
        for result in results:
            if isinstance(result, Exception):
                continue
            findings.extend(result)
        return findings

    async def _persist_findings(self, scan_id: int, raw_findings: list[dict]) -> None:
        severity_map = {"critical": 0, "high": 0, "medium": 0, "low": 0, "informational": 0}

        for raw in raw_findings:
            fid = raw.get("finding_id") or str(uuid.uuid4())
            existing = self.db.query(Finding).filter(Finding.finding_id == fid).first()
            if not existing:
                finding = Finding(
                    finding_id=fid,
                    scanner=raw.get("scanner", "unknown"),
                    category=raw.get("category", "unknown"),
                    title=raw.get("title", "Unknown finding"),
                    description=raw.get("description", ""),
                    severity=raw.get("severity", "informational"),
                    affected_file=raw.get("affected_file"),
                    line_number=raw.get("line_number"),
                    vulnerability_id=raw.get("vulnerability_id"),
                    evidence=raw.get("evidence"),
                    remediation=raw.get("remediation"),
                )
                self.db.add(finding)
                self.db.commit()
                self.db.refresh(finding)
            else:
                finding = existing

            link = ScanFinding(scan_id=scan_id, finding_id=finding.id)
            self.db.add(link)

            sev = finding.severity.lower()
            if sev in severity_map:
                severity_map[sev] += 1

        self.db.commit()

        scan = self.db.query(Scan).filter(Scan.id == scan_id).first()
        scan.total_findings = sum(severity_map.values())
        scan.critical_count = severity_map["critical"]
        scan.high_count = severity_map["high"]
        scan.medium_count = severity_map["medium"]
        scan.low_count = severity_map["low"]
        scan.info_count = severity_map["informational"]
        self.db.commit()
