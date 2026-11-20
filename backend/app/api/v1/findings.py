"""Finding router."""

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import DBDep
from app.models.finding import Finding
from app.schemas.finding import FindingResponse

router = APIRouter()


@router.get("", response_model=list[FindingResponse])
async def list_findings(
    db: DBDep,
    repository_id: int | None = None,
    scan_id: int | None = None,
    severity: str | None = Query(None),
    category: str | None = Query(None),
    scanner: str | None = Query(None),
    skip: int = 0,
    limit: int = 100,
) -> list:
    query = db.query(Finding)

    if scan_id:
        query = query.join(Finding.scan_findings).filter(Finding.scan_findings.any(scan_id=scan_id))
    if repository_id:
        from app.models.scan import Scan
        query = query.join(Finding.scan_findings).join(Scan).filter(Scan.repository_id == repository_id)
    if severity:
        query = query.filter(Finding.severity == severity)
    if category:
        query = query.filter(Finding.category == category)
    if scanner:
        query = query.filter(Finding.scanner == scanner)

    return query.offset(skip).limit(limit).all()


@router.get("/{finding_id}", response_model=FindingResponse)
async def get_finding(finding_id: int, db: DBDep) -> Finding:
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding
