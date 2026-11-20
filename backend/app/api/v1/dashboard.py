"""Dashboard router — aggregates metrics."""

from sqlalchemy import func

from fastapi import APIRouter

from app.api.deps import DBDep, UserDep
from app.models.finding import Finding
from app.models.repository import Repository
from app.models.scan import Scan
from app.models.finding import ScanFinding
from app.models.user import User

router = APIRouter()


@router.get("/metrics")
async def dashboard_metrics(user: UserDep, db: DBDep) -> dict:
    db_user = db.query(User).filter(User.github_id == int(user["sub"])).first()
    if not db_user:
        return {}

    repo_count = db.query(Repository).filter(Repository.user_id == db_user.id).count()
    scan_count = (
        db.query(Scan)
        .join(Repository)
        .filter(Repository.user_id == db_user.id)
        .count()
    )

    severity_counts = (
        db.query(Finding.severity, func.count(Finding.id))
        .join(ScanFinding)
        .join(Scan)
        .join(Repository)
        .filter(Repository.user_id == db_user.id)
        .group_by(Finding.severity)
        .all()
    )

    category_counts = (
        db.query(Finding.category, func.count(Finding.id))
        .join(ScanFinding)
        .join(Scan)
        .join(Repository)
        .filter(Repository.user_id == db_user.id)
        .group_by(Finding.category)
        .all()
    )

    recent_scans = (
        db.query(Scan)
        .join(Repository)
        .filter(Repository.user_id == db_user.id)
        .order_by(Scan.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_repositories": repo_count,
        "total_scans": scan_count,
        "severity_distribution": {s: c for s, c in severity_counts},
        "category_distribution": {c: n for c, n in category_counts},
        "recent_scans": [
            {
                "id": s.id,
                "repository_id": s.repository_id,
                "status": s.status,
                "total_findings": s.total_findings,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in recent_scans
        ],
    }
