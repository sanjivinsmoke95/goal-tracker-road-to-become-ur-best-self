"""Per-user preferences: personalization inputs for recommendations/planning,
plus the comparison-consent flag."""

from typing import Any

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class UserPreferences(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(80), default="")

    # Personalization used by recommendations and the planner.
    daily_hours: Mapped[float] = mapped_column(default=2.0, nullable=False)
    daily_problems: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    target_cf_rating: Mapped[int | None] = mapped_column(Integer)
    target_lc_solved: Mapped[int | None] = mapped_column(Integer)
    desired_difficulty: Mapped[str] = mapped_column(String(16), default="balanced")  # weakness|current|challenge|balanced
    technologies: Mapped[list[Any]] = mapped_column(JSON, default=list)
    goals: Mapped[str] = mapped_column(Text, default="")

    # Privacy: the accepting side can still refuse to be compared.
    allow_comparison: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
