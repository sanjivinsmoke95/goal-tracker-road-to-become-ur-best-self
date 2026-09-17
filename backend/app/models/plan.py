"""Learning plans: uploaded or AI-generated, then adapted to real progress."""

from datetime import date as date_type
from typing import Any

from sqlalchemy import JSON, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class UploadedPlan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "uploaded_plans"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), default="")
    raw_rows: Mapped[list[Any]] = mapped_column(JSON, default=list)


class LearningPlan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "learning_plans"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), default="Learning Plan")
    goal: Mapped[str] = mapped_column(String(500), default="")
    duration_days: Mapped[int] = mapped_column(Integer, default=30)
    hours_per_day: Mapped[int] = mapped_column(Integer, default=2)
    start_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(String(16), default="generated")  # generated | upload
    status: Mapped[str] = mapped_column(String(16), default="active")

    days: Mapped[list["PlanDay"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan", order_by="PlanDay.day_number"
    )


class PlanDay(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "plan_days"

    plan_id: Mapped[str] = mapped_column(ForeignKey("learning_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    # [{"category": "cf", "title": "...", "done": false}]
    tasks: Mapped[list[Any]] = mapped_column(JSON, default=list)

    plan: Mapped["LearningPlan"] = relationship(back_populates="days")
