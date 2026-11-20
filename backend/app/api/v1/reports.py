"""Reports router."""

import csv
import io
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import joinedload

from app.api.deps import DBDep, UserDep
from app.models.finding import Finding
from app.models.scan import Scan
from app.models.user import User

router = APIRouter()


@router.get("/scan/{scan_id}/json")
async def export_json(scan_id: int, user: UserDep, db: DBDep) -> StreamingResponse:
    db_user = db.query(User).filter(User.github_id == int(user["sub"])).first()
    scan = db.query(Scan).options(joinedload(Scan.repository)).filter(Scan.id == scan_id).first()
    if not scan or scan.repository.user_id != db_user.id:
        raise HTTPException(status_code=404, detail="Scan not found")

    findings = (
        db.query(Finding)
        .join(ScanFinding)
        .filter(ScanFinding.scan_id == scan_id)
        .all()
    )

    data = {
        "repository": {
            "full_name": scan.repository.full_name,
            "html_url": scan.repository.html_url,
        },
        "scan": {
            "id": scan.id,
            "status": scan.status,
            "started_at": scan.started_at.isoformat() if scan.started_at else None,
            "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        },
        "findings": [
            {
                "finding_id": f.finding_id,
                "scanner": f.scanner,
                "category": f.category,
                "title": f.title,
                "severity": f.severity,
                "affected_file": f.affected_file,
                "line_number": f.line_number,
                "vulnerability_id": f.vulnerability_id,
                "evidence": f.evidence,
                "remediation": f.remediation,
            }
            for f in findings
        ],
    }

    return StreamingResponse(
        io.BytesIO(json.dumps(data, indent=2).encode()),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}_report.json"},
    )


@router.get("/scan/{scan_id}/csv")
async def export_csv(scan_id: int, user: UserDep, db: DBDep) -> StreamingResponse:
    db_user = db.query(User).filter(User.github_id == int(user["sub"])).first()
    scan = db.query(Scan).options(joinedload(Scan.repository)).filter(Scan.id == scan_id).first()
    if not scan or scan.repository.user_id != db_user.id:
        raise HTTPException(status_code=404, detail="Scan not found")

    findings = (
        db.query(Finding)
        .join(ScanFinding)
        .filter(ScanFinding.scan_id == scan_id)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "finding_id", "scanner", "category", "title", "severity",
        "affected_file", "line_number", "vulnerability_id", "evidence", "remediation",
    ])
    for f in findings:
        writer.writerow([
            f.finding_id, f.scanner, f.category, f.title, f.severity,
            f.affected_file, f.line_number, f.vulnerability_id, f.evidence, f.remediation,
        ])

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=scan_{scan_id}_report.csv"},
    )
