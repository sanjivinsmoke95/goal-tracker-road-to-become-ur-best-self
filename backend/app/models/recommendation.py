"""The daily Problem of the Day, one row per user/platform/day (idempotent)."""

from datetime import date as date_type
from typing import Any

from sqlalchemy import JSON, Date, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class DailyProblem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "daily_problems"
    __table_args__ = (UniqueConstraint("user_id", "platform", "date", name="uq_daily_problem"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(16), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, index=True, nullable=False)
    problem_id: Mapped[str | None] = mapped_column(ForeignKey("problems.id"))
    target_rating: Mapped[int | None] = mapped_column(Integer)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    reason: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    explanation: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(16), default="assigned")  # assigned|solved|skipped
