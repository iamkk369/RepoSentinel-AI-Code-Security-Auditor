"""Finding schemas."""

from datetime import datetime

from pydantic import BaseModel


class FindingBase(BaseModel):
    scanner: str
    category: str
    title: str
    description: str
    severity: str
    affected_file: str | None = None
    line_number: int | None = None
    vulnerability_id: str | None = None
    evidence: str | None = None
    remediation: str | None = None
    ai_explanation: str | None = None


class FindingCreate(FindingBase):
    finding_id: str


class FindingResponse(FindingBase):
    id: int
    finding_id: str
    created_at: datetime

    class Config:
        from_attributes = True
