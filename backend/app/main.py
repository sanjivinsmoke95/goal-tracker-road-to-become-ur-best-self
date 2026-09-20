"""Adaptive Learning OS — API entrypoint.

Run:   uvicorn app.main:app --reload
Docs:  http://localhost:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import (
    analysis, auth, code, codeforces, dashboard, goals, learning,
    leetcode, planner, plans, progress, rag, recommendations, skills, tutor,
)
from app.core.config import settings
from app.core.logging import configure_logging
from app.db import Base, engine

logger = logging.getLogger(__name__)


def _ensure_rag_index() -> None:
    """Index the documentation corpus once, so the AI Tutor's docs Q&A works out
    of the box on a fresh database. Cheap and keyless (TF-IDF)."""
    try:
        from sqlalchemy.orm import Session

        from app.services.rag import store as rag_store

        with Session(engine) as db:
            if rag_store.status(db)["indexed_chunks"] == 0:
                n = rag_store.reindex(db)
                db.commit()
                logger.info("RAG corpus indexed: %d chunks", n)
    except Exception as exc:  # noqa: BLE001 — never block startup on the index
        logger.warning("RAG auto-index skipped: %s", exc)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    logger.info("Starting %s (%s)", settings.app_name, settings.environment)
    # Dev convenience: ensure tables exist. Production uses Alembic migrations.
    if settings.environment == "development":
        Base.metadata.create_all(bind=engine)
        _ensure_rag_index()
    yield
    logger.info("Shutting down")


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(goals.router)
app.include_router(planner.router)
app.include_router(rag.router)
app.include_router(codeforces.platforms)
app.include_router(codeforces.cf)
app.include_router(skills.router)
app.include_router(recommendations.router)
app.include_router(analysis.router)
app.include_router(learning.router)
app.include_router(leetcode.platforms)
app.include_router(leetcode.lc)
app.include_router(plans.router)
app.include_router(code.router)
app.include_router(tutor.router)
app.include_router(progress.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
