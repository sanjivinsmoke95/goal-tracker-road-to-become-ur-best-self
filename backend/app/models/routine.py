"""Recurring routines — the templates that auto-fill each day's planner.

A routine is not itself a task; it is a rule ("every weekday: solve 1 LeetCode
problem"). When the planner opens a day, each active routine whose weekday set
includes that day materialises into a real Goal for the day — deduped, so a
routine never doubles up. The generated Goals are ordinary tasks after that:
you check them off, and completing them feeds the same streak as everything else.
"""

from datetime import time
from typing import Any

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin

# "daily" / "weekdays" / "custom" is just a UI label; days_of_week is the truth.
FREQUENCIES = ("daily", "weekdays", "custom")


class Routine(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "routines"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(24), default="other", nullable=False)
    priority: Mapped[str] = mapped_column(String(12), default="medium", nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    frequency: Mapped[str] = mapped_column(String(12), default="daily", nullable=False)
    # ISO weekday indices, Monday=0 … Sunday=6. A day materialises the routine
    # when its weekday is in this list.
    days_of_week: Mapped[list[Any]] = mapped_column(JSON, default=list)

    # Optional preferred time-of-day, purely for ordering/labels in the UI.
    at_time: Mapped[time | None] = mapped_column(Time)

    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
