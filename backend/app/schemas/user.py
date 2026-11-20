"""User schemas."""

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str | None = None
    avatar_url: str | None = None


class UserCreate(UserBase):
    github_id: int
    access_token: str | None = None


class UserResponse(UserBase):
    id: int
    github_id: int

    class Config:
        from_attributes = True
