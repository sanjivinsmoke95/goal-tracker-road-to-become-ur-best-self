"""Daily snapshots of the computed skill profile — the series behind Progress."""

from datetime import date as date_type
from typing import Any

from sqlalchemy import JSON, Date, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class SkillSnapshot(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "skill_snapshots"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_skill_snapshot_day"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    date: Mapped[date_type] = mapped_column(Date, index=True, nullable=False)
    estimated_rating: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    recent_success_rate: Mapped[float | None] = mapped_column(Float)
    total_solved: Mapped[int] = mapped_column(Integer, default=0)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    topics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    platform: Mapped[str] = mapped_column(String(16), default="codeforces")
