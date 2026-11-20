"""Scan router."""

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.api.deps import DBDep, UserDep
from app.models.finding import Finding, ScanFinding
from app.models.scan import Scan
from app.models.user import User
from app.schemas.scan import ScanCreate, ScanResponse
from app.services.github_service import GitHubService
from app.services.scan_service import ScanService

router = APIRouter()


async def _run_scan(db: DBDep, scan_id: int, github_token: str, repo_full_name: str, branch: str) -> None:
    service = ScanService(db, github_token)
    await service.run_scan(scan_id, repo_full_name, branch)


@router.post("", response_model=ScanResponse)
async def trigger_scan(
    req: ScanCreate,
    background_tasks: BackgroundTasks,
    user: UserDep,
    db: DBDep,
) -> Scan:
    db_user = db.query(User).filter(User.github_id == int(user["sub"])).first()
    if not db_user or not db_user.access_token:
        raise HTTPException(status_code=401, detail="GitHub token not available")

    scan = Scan(
        repository_id=req.repository_id,
        status="pending",
        branch=req.branch,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    from app.models.repository import Repository
    repo = db.query(Repository).filter(Repository.id == req.repository_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    background_tasks.add_task(
        _run_scan, db, scan.id, db_user.access_token, repo.full_name, req.branch
    )

    return scan


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: int, db: DBDep) -> Scan:
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
