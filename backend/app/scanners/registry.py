"""Scanner registry."""

from app.scanners.configuration.config_scanner import ConfigScanner
from app.scanners.dependencies.osv_scanner import OSVScanner
from app.scanners.sast.semgrep_scanner import SemgrepScanner
from app.scanners.secrets.gitleaks_scanner import GitleaksScanner

__all__ = [
    "GitleaksScanner",
    "OSVScanner",
    "SemgrepScanner",
    "ConfigScanner",
]
