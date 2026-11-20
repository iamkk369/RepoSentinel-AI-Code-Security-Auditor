"""Repository router."""

from fastapi import APIRouter, HTTPException

from app.api.deps import DBDep, UserDep
from app.core.exceptions import GitHubAPIException
from app.models.repository import Repository
from app.models.user import User
from app.schemas.repository import RepositoryCreate, RepositoryResponse
from app.services.github_service import GitHubService

router = APIRouter()


@router.get("", response_model=list[RepositoryResponse])
async def list_repos(user: UserDep, db: DBDep) -> list:
    db_user = db.query(User).filter(User.github_id == int(user["sub"])).first()
    if not db_user or not db_user.access_token:
        raise HTTPException(status_code=401, detail="GitHub token not available")

    gh = GitHubService(db_user.access_token)
    try:
        gh_repos = await gh.list_repos()
    except GitHubAPIException as e:
        raise HTTPException(status_code=502, detail=str(e))

    result = []
    for r in gh_repos:
        db_repo = db.query(Repository).filter(Repository.github_id == r["id"]).first()
        if not db_repo:
            db_repo = Repository(
                github_id=r["id"],
                owner=r["owner"]["login"],
                name=r["name"],
                full_name=r["full_name"],
                description=r.get("description"),
                html_url=r["html_url"],
                language=r.get("language"),
                visibility=r.get("visibility", "public"),
                default_branch=r.get("default_branch", "main"),
                user_id=db_user.id,
            )
            db.add(db_repo)
            db.commit()
            db.refresh(db_repo)
        result.append(db_repo)
    return result


@router.post("/{owner}/{name}/add", response_model=RepositoryResponse)
async def add_repo(owner: str, name: str, user: UserDep, db: DBDep) -> Repository:
    db_user = db.query(User).filter(User.github_id == int(user["sub"])).first()
    if not db_user or not db_user.access_token:
        raise HTTPException(status_code=401, detail="GitHub token not available")

    gh = GitHubService(db_user.access_token)
    try:
        r = await gh.get_repo(owner, name)
    except GitHubAPIException as e:
        raise HTTPException(status_code=404, detail=str(e))

    db_repo = db.query(Repository).filter(Repository.github_id == r["id"]).first()
    if not db_repo:
        db_repo = Repository(
            github_id=r["id"],
            owner=r["owner"]["login"],
            name=r["name"],
            full_name=r["full_name"],
            description=r.get("description"),
            html_url=r["html_url"],
            language=r.get("language"),
            visibility=r.get("visibility", "public"),
            default_branch=r.get("default_branch", "main"),
            user_id=db_user.id,
        )
        db.add(db_repo)
        db.commit()
        db.refresh(db_repo)
    return db_repo
