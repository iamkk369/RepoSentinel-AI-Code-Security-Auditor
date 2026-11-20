"""Risk analysis engine — severity mapping and deduplication."""

import hashlib


SEVERITY_ORDER = {"critical": 5, "high": 4, "medium": 3, "low": 2, "informational": 1}


class RiskEngine:
    """
    Deterministic risk analysis.

    - Normalizes severity strings.
    - Generates stable finding IDs for deduplication.
    - Merges duplicate findings across scanners.
    """

    @staticmethod
    def normalize_severity(severity: str) -> str:
        s = severity.lower().strip()
        if s in SEVERITY_ORDER:
            return s
        mapping = {
            "error": "high",
            "warning": "medium",
            "info": "informational",
            "important": "high",
            "moderate": "medium",
        }
        return mapping.get(s, "medium")

    @staticmethod
    def compute_finding_id(finding: dict) -> str:
        """Generate a stable finding ID from scanner, category, file, line, and title."""
        key = (
            f"{finding.get('scanner', 'unknown')}:"
            f"{finding.get('category', 'unknown')}:"
            f"{finding.get('affected_file', 'none')}:"
            f"{finding.get('line_number', 0)}:"
            f"{finding.get('title', 'unknown')}"
        )
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    @classmethod
    def deduplicate(cls, findings: list[dict]) -> list[dict]:
        """Deduplicate findings by stable ID, keeping highest severity."""
        seen: dict[str, dict] = {}
        for f in findings:
            fid = f.get("finding_id")
            if not fid:
                fid = cls.compute_finding_id(f)
                f["finding_id"] = fid
            existing = seen.get(fid)
            if existing:
                existing_sev = SEVERITY_ORDER.get(cls.normalize_severity(existing["severity"]), 0)
                new_sev = SEVERITY_ORDER.get(cls.normalize_severity(f["severity"]), 0)
                if new_sev > existing_sev:
                    f.setdefault("scanners", []).append(existing["scanner"])
                    seen[fid] = f
                else:
                    existing.setdefault("scanners", []).append(f["scanner"])
            else:
                seen[fid] = f
        return list(seen.values())

    @staticmethod
    def severity_score(severity: str) -> int:
        return SEVERITY_ORDER.get(severity.lower().strip(), 0)
