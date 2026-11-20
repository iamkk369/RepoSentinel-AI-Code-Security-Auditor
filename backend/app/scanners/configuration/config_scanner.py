"""Configuration security scanner — checks Docker, GitHub Actions, and env configs."""

import glob
import os
import re


class ConfigScanner:
    SEVERITY_HIGH = "high"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_LOW = "low"

    async def scan(self, repo_path: str) -> list[dict]:
        findings = []
        findings.extend(self._scan_docker(repo_path))
        findings.extend(self._scan_github_actions(repo_path))
        findings.extend(self._scan_env_files(repo_path))
        return findings

    def _scan_docker(self, repo_path: str) -> list[dict]:
        findings = []
        for dockerfile in glob.glob(os.path.join(repo_path, "**", "Dockerfile*"), recursive=True):
            with open(dockerfile) as f:
                content = f.read()
            lines = content.splitlines()
            for lineno, line in enumerate(lines, 1):
                stripped = line.strip().lower()
                if "user root" in stripped or (stripped.startswith("user") and "root" in stripped):
                    findings.append(self._make_finding(
                        "config", "docker_root_user",
                        "Container runs as root user",
                        "Running containers as root increases the attack surface. Use a non-root USER directive.",
                        self.SEVERITY_HIGH, dockerfile, lineno,
                        "Add a non-root USER directive before the CMD or ENTRYPOINT.",
                    ))
                if "--no-cache" in line and any(cmd in line.lower() for cmd in ("apk ", "apt ", "pip ", "npm ")):
                    findings.append(self._make_finding(
                        "config", "docker_layer_caching",
                        "Missing cleanup in Dockerfile layer",
                        "Package managers should clean caches in the same RUN layer to reduce image size.",
                        self.SEVERITY_LOW, dockerfile, lineno,
                        "Combine install and cleanup in a single RUN command.",
                    ))
        return findings

    def _scan_github_actions(self, repo_path: str) -> list[dict]:
        findings = []
        workflow_dir = os.path.join(repo_path, ".github", "workflows")
        if not os.path.isdir(workflow_dir):
            return findings
        for yml_file in glob.glob(os.path.join(workflow_dir, "*.y??ml")):
            with open(yml_file) as f:
                content = f.read()
            lines = content.splitlines()
            for lineno, line in enumerate(lines, 1):
                if re.search(r"permissions:\s*write-all", line, re.IGNORECASE):
                    findings.append(self._make_finding(
                        "config", "gha_write_all_permissions",
                        "Overly broad GitHub Actions permissions",
                        "Using `permissions: write-all` grants excessive write access to the workflow.",
                        self.SEVERITY_MEDIUM, yml_file, lineno,
                        "Use the minimum required permissions for each job.",
                    ))
                if "pull_request_target" in line and "actions/checkout" in content:
                    if "github.event.pull_request.head.sha" not in content:
                        findings.append(self._make_finding(
                            "config", "gha_unsafe_pr_target",
                            "Unsafe pull_request_target usage",
                            "pull_request_target runs in the base repo context and may expose secrets if the checked-out code is untrusted.",
                            self.SEVERITY_HIGH, yml_file, lineno,
                            "Ensure PR code is checked out by commit SHA, not ref.",
                        ))
                if "secrets." in line and "::" in line:
                    findings.append(self._make_finding(
                        "config", "gha_secret_in_log",
                        "Potential secret exposure in workflow log",
                        "Secrets may be printed to workflow logs if not handled carefully.",
                        self.SEVERITY_MEDIUM, yml_file, lineno,
                        "Avoid echoing secrets and use GitHub masking.",
                    ))
        return findings

    def _scan_env_files(self, repo_path: str) -> list[dict]:
        findings = []
        for env_file in glob.glob(os.path.join(repo_path, "**", ".env*"), recursive=True):
            if os.path.basename(env_file) == ".env.example":
                continue
            with open(env_file) as f:
                content = f.read()
            lines = content.splitlines()
            for lineno, line in enumerate(lines, 1):
                if re.search(r"^(AWS_SECRET_ACCESS_KEY|PRIVATE_KEY|SECRET_KEY|API_KEY|DATABASE_URL|PASSWORD)=.+", line, re.IGNORECASE):
                    findings.append(self._make_finding(
                        "config", "env_committed_secret",
                        "Sensitive value committed in environment file",
                        "Environment files containing secrets should never be committed to version control.",
                        self.SEVERITY_HIGH, env_file, lineno,
                        "Remove the file, rotate the secret, and add it to .gitignore. Use a secrets manager.",
                    ))
        return findings

    def _make_finding(self, scanner: str, rule: str, title: str, description: str,
                      severity: str, filepath: str, line: int, remediation: str) -> dict:
        return {
            "finding_id": f"config_{rule}_{os.path.basename(filepath)}_{line}",
            "scanner": scanner,
            "category": "configuration",
            "title": title,
            "description": description,
            "severity": severity,
            "affected_file": filepath,
            "line_number": line,
            "vulnerability_id": rule,
            "evidence": None,
            "remediation": remediation,
        }
