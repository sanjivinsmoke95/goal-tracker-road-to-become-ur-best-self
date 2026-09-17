"""Adaptive Learning OS — API entrypoint.

Run:   uvicorn app.main:app --reload
Docs:  http://localhost:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, dashboard, goals
from app.core.config import settings
from app.core.logging import configure_logging
from app.db import Base, engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    logger.info("Starting %s (%s)", settings.app_name, settings.environment)
    # Dev convenience: ensure tables exist. Production uses Alembic migrations.
    if settings.environment == "development":
        Base.metadata.create_all(bind=engine)
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


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
