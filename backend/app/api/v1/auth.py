"""Authentication router — GitHub OAuth."""

from fastapi import APIRouter, HTTPException

from app.api.deps import DBDep
from app.core.config import get_settings
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.github_service import GitHubService

router = APIRouter()


@router.get("/login")
async def login() -> dict:
    settings = get_settings()
    return {
        "auth_url": (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={settings.github_client_id}"
            f"&redirect_uri={settings.github_redirect_uri}"
            f"&scope=repo read:user"
        )
    }


@router.post("/callback")
async def callback(code: str, db: DBDep) -> dict:
    gh = GitHubService()
    token_data = await gh.exchange_code(code)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to obtain access token")

    gh_user = GitHubService(access_token)
    user_data = await gh_user.get_user()

    db_user = db.query(User).filter(User.github_id == user_data["id"]).first()
    if not db_user:
        db_user = User(
            github_id=user_data["id"],
            username=user_data["login"],
            email=user_data.get("email"),
            avatar_url=user_data.get("avatar_url"),
            access_token=access_token,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    else:
        db_user.access_token = access_token
        db.commit()

    token = create_access_token({"sub": str(db_user.github_id), "username": db_user.username})
    return {"access_token": token, "token_type": "bearer", "user": UserResponse.model_validate(db_user)}


@router.get("/me", response_model=UserResponse)
async def me(user: dict, db: DBDep) -> User:
    db_user = db.query(User).filter(User.github_id == int(user["sub"])).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
