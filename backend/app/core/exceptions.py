"""Custom application exceptions."""


class RepoSentinelException(Exception):
    """Base application exception."""

    pass


class GitHubAPIException(RepoSentinelException):
    """Raised when GitHub API returns an error."""

    pass


class ScannerException(RepoSentinelException):
    """Raised when a scanner fails."""

    pass


class ScanTimeoutException(ScannerException):
    """Raised when a scan exceeds its time limit."""

    pass
