"""Repository schemas."""

from pydantic import BaseModel


class RepositoryBase(BaseModel):
    owner: str
    name: str
    full_name: str
    description: str | None = None
    html_url: str
    language: str | None = None
    visibility: str = "public"
    default_branch: str = "main"


class RepositoryCreate(RepositoryBase):
    github_id: int


class RepositoryResponse(RepositoryBase):
    id: int
    github_id: int

    class Config:
        from_attributes = True
