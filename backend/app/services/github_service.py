"""GitHub API service wrapper."""

import httpx

from app.core.config import get_settings
from app.core.exceptions import GitHubAPIException


class GitHubService:
    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: str | None = None):
        self.access_token = access_token
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if access_token:
            self.headers["Authorization"] = f"Bearer {access_token}"

    async def exchange_code(self, code: str) -> dict:
        settings = get_settings()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": settings.github_client_id,
                    "client_secret": settings.github_client_secret,
                    "code": code,
                    "redirect_uri": settings.github_redirect_uri,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            if "error" in data:
                raise GitHubAPIException(f"OAuth error: {data['error_description']}")
            return data

    async def get_user(self) -> dict:
        return await self._get("/user")

    async def list_repos(self, page: int = 1, per_page: int = 30) -> list:
        return await self._get(
            "/user/repos",
            params={"page": page, "per_page": per_page, "sort": "updated"},
        )

    async def get_repo(self, owner: str, repo: str) -> dict:
        return await self._get(f"/repos/{owner}/{repo}")

    async def _get(self, path: str, params: dict | None = None) -> dict | list:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}{path}",
                headers=self.headers,
                params=params,
            )
            if resp.status_code == 401:
                raise GitHubAPIException("Unauthorized: invalid or expired token")
            if resp.status_code == 403:
                raise GitHubAPIException("Rate limit or insufficient permissions")
            if resp.status_code == 404:
                raise GitHubAPIException("Resource not found")
            resp.raise_for_status()
            return resp.json()
