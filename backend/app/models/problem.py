"""Unified problem corpus (Codeforces + LeetCode) and the user's submissions."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class Problem(Base, TimestampMixin):
    """One problem, platform-agnostic. Primary key is a stable synthetic id
    like `cf:1520B` so submissions and recommendations reference it directly.
    Tags are stored as a JSON array (portable across Postgres/SQLite)."""

    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # e.g. "cf:1520B"
    platform: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    external_id: Mapped[str] = mapped_column(String(48), index=True, nullable=False)  # "1520B"
    contest_id: Mapped[int | None] = mapped_column(Integer)
    index: Mapped[str | None] = mapped_column(String(8))
    name: Mapped[str] = mapped_column(String(300), default="")
    rating: Mapped[int | None] = mapped_column(Integer, index=True)  # CF numeric rating
    difficulty: Mapped[str | None] = mapped_column(String(16))  # LC Easy/Medium/Hard
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    url: Mapped[str] = mapped_column(String(300), default="")


class Submission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "submissions"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    external_id: Mapped[str] = mapped_column(String(48), index=True, nullable=False)  # CF submission id
    problem_id: Mapped[str | None] = mapped_column(ForeignKey("problems.id"), index=True)

    verdict: Mapped[str] = mapped_column(String(32), default="")  # OK, WRONG_ANSWER, TIME_LIMIT_EXCEEDED...
    language: Mapped[str] = mapped_column(String(48), default="")
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)

    # Denormalised for fast skill queries without a join.
    problem_rating: Mapped[int | None] = mapped_column(Integer)
    problem_tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    # The CF public API does not return source; this stays null unless supplied.
    source_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_code: Mapped[str | None] = mapped_column(Text)
    analysis_meta: Mapped[dict[str, Any] | None] = mapped_column(JSON)  # set by M6
