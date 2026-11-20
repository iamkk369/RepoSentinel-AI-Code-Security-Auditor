"""Scan schemas."""

from datetime import datetime

from pydantic import BaseModel


class ScanBase(BaseModel):
    repository_id: int
    branch: str = "main"


class ScanCreate(ScanBase):
    pass


class ScanResponse(BaseModel):
    id: int
    repository_id: int
    status: str
    branch: str
    commit_sha: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    total_findings: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
