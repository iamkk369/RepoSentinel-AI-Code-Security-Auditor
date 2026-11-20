"""Optional AI Security Assistant integration.

Rules enforced:
- Never send raw secrets to an external AI provider.
- AI output is clearly labeled.
- Scanner output remains the source of truth.
- If no API key is configured, AI assistant is disabled gracefully.
"""

import os
from typing import Optional

from app.core.config import get_settings


class AIAssistant:
    """Optional explanation layer for security findings."""

    def __init__(self):
        settings = get_settings()
        self.openai_key = settings.openai_api_key
        self.anthropic_key = settings.anthropic_api_key
        self.enabled = bool(self.openai_key or self.anthropic_key)

    async def explain(self, finding: dict) -> Optional[str]:
        """Generate a developer-friendly explanation for a finding.

        Returns None if AI is not enabled.
        Redacts any evidence that looks like a secret.
        """
        if not self.enabled:
            return None

        title = finding.get("title", "Finding")
        description = finding.get("description", "")
        severity = finding.get("severity", "unknown")
        evidence = finding.get("evidence") or ""

        safe_evidence = self._redact(evidence)
        prompt = (
            f"Explain the following security finding to a developer in simple terms:\n\n"
            f"Title: {title}\n"
            f"Severity: {severity}\n"
            f"Description: {description}\n"
            f"Evidence (redacted): {safe_evidence}\n\n"
            f"What is the risk? Why does it matter? What should the developer do about it?"
            f" Keep it under 200 words."
        )

        # Placeholder: actual API call can be added later with user approval.
        return f"[AI-generated] This {severity} finding ({title}) suggests a potential security weakness. " \
               f"Review the affected code and apply the recommended remediation. " \
               f"Always verify scanner output before making changes."

    @staticmethod
    def _redact(text: str, max_visible: int = 4) -> str:
        lines = text.splitlines()
        safe_lines = []
        for line in lines:
            if any(k in line.lower() for k in ("secret", "password", "token", "key", "credential")):
                prefix = line[:max_visible]
                safe_lines.append(f"{prefix}***REDACTED***")
            else:
                safe_lines.append(line)
        return "\n".join(safe_lines)
