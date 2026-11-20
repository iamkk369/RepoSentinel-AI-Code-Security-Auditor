"""OSV.dev dependency vulnerability scanner."""

import glob
import json
import os

import httpx

from app.core.exceptions import ScannerException


class OSVScanner:
    SUPPORTED_FILES = {
        "requirements.txt": "PyPI",
        "package-lock.json": "npm",
        "package.json": "npm",
        "poetry.lock": "PyPI",
        "pyproject.toml": "PyPI",
    }
    OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"
    SEVERITY_MAP = {"CRITICAL": "critical", "HIGH": "high", "MODERATE": "medium", "LOW": "low"}

    async def scan(self, repo_path: str) -> list[dict]:
        packages = []
        for pattern, ecosystem in self.SUPPORTED_FILES.items():
            for filepath in glob.glob(os.path.join(repo_path, "**", pattern), recursive=True):
                pkgs = self._parse_manifest(filepath, ecosystem)
                packages.extend(pkgs)

        if not packages:
            return []

        return await self._query_osv(packages)

    def _parse_manifest(self, filepath: str, ecosystem: str) -> list[dict]:
        packages = []
        filename = os.path.basename(filepath)
        if filename == "requirements.txt":
            with open(filepath) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split("==")
                    if len(parts) == 2:
                        packages.append({"name": parts[0].strip(), "version": parts[1].strip(), "ecosystem": ecosystem})
        elif filename in ("package-lock.json",):
            with open(filepath) as f:
                data = json.load(f)
            deps = data.get("packages", {}).get("", {}).get("dependencies", {})
            for name, version in deps.items():
                clean = version.lstrip("^~>=<")
                packages.append({"name": name, "version": clean, "ecosystem": ecosystem})
        elif filename == "pyproject.toml":
            # Simplified: grab deps from [project] dependencies
            try:
                import tomllib
                with open(filepath, "rb") as f:
                    data = tomllib.load(f)
                deps = data.get("project", {}).get("dependencies", [])
                for dep in deps:
                    # "requests>=2.0"
                    name = dep.split("[")[0].split(">=")[0].split("==")[0].split("<")[0].strip()
                    version = "0.0.0"
                    for sep in (">=", "==", "~="):
                        if sep in dep:
                            version = dep.split(sep)[1].split(",")[0].split(";")[0].strip()
                            break
                    packages.append({"name": name, "version": version, "ecosystem": ecosystem})
            except Exception:
                pass
        return packages

    async def _query_osv(self, packages: list[dict]) -> list[dict]:
        queries = [{"package": {"name": p["name"], "ecosystem": p["ecosystem"]}, "version": p["version"]} for p in packages]
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.OSV_BATCH_URL, json={"queries": queries})
            if resp.status_code != 200:
                raise ScannerException(f"OSV API error: {resp.status_code}")
            data = resp.json()

        results = data.get("results", [])
        findings = []
        for idx, result in enumerate(results):
            pkg = packages[idx]
            for v in result.get("vulns", []):
                aliases = v.get("aliases", [])
                cve = next((a for a in aliases if a.startswith("CVE-")), aliases[0] if aliases else v.get("id"))
                severity = self._extract_severity(v)
                findings.append({
                    "finding_id": f"osv_{v['id']}_{pkg['name']}",
                    "scanner": "osv",
                    "category": "dependency_vulnerability",
                    "title": f"Vulnerable dependency: {pkg['name']}@{pkg['version']}",
                    "description": v.get("details", "No details available.")[:500],
                    "severity": severity,
                    "affected_file": f"{pkg['name']}@{pkg['version']}",
                    "line_number": None,
                    "vulnerability_id": cve,
                    "evidence": f"Package: {pkg['name']} {pkg['version']} - {v.get('id')}",
                    "remediation": v.get("affected", [{}])[0].get("ranges", [{}])[0].get("events", [{}])[-1].get("fixed", "Check OSV advisory for patched version."),
                })
        return findings

    def _extract_severity(self, vuln: dict) -> str:
        for s in vuln.get("severity", []):
            if s.get("type") == "CVSS_V3":
                score = s.get("score", "0.0")
                try:
                    val = float(score)
                    if val >= 9.0:
                        return "critical"
                    if val >= 7.0:
                        return "high"
                    if val >= 4.0:
                        return "medium"
                    return "low"
                except ValueError:
                    pass
        return "medium"
