"""RepoSentinel FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, dashboard, findings, repos, reports, scans
from app.core.config import get_settings
from app.db.base import Base, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Create tables for SQLite dev mode
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup could go here


app = FastAPI(
    title="RepoSentinel API",
    description="AI-Assisted GitHub Repository Security Intelligence Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(repos.router, prefix="/api/v1/repos", tags=["repositories"])
app.include_router(scans.router, prefix="/api/v1/scans", tags=["scans"])
app.include_router(findings.router, prefix="/api/v1/findings", tags=["findings"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "version": "0.1.0"}
