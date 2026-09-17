"""Declarative base + shared mixins.

Milestone 1 keeps every column type portable (String/Boolean/DateTime/Integer)
so the test suite can run against SQLite with no Postgres. Later milestones that
need JSONB / pgvector will add a Postgres-only test fixture.
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def new_uuid() -> str:
    return str(uuid4())


class UUIDMixin:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
