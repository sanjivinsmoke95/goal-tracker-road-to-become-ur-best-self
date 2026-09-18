"""Schemas for the daily planner: routines, bulk task upload, and the day view."""

from datetime import date as date_type
from datetime import time as time_type
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.goal import Category, GoalRead, Priority

Frequency = Literal["daily", "weekdays", "custom"]


class RoutineBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    category: Category = "other"
    priority: Priority = "medium"
    estimated_minutes: int = Field(default=0, ge=0, le=24 * 60)
    frequency: Frequency = "daily"
    days_of_week: list[int] = Field(default_factory=list)
    at_time: time_type | None = None
    active: bool = True

    @field_validator("days_of_week")
    @classmethod
    def _valid_days(cls, v: list[int]) -> list[int]:
        return sorted({d for d in v if 0 <= d <= 6})


class RoutineCreate(RoutineBase):
    pass


class RoutineUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    category: Category | None = None
    priority: Priority | None = None
    estimated_minutes: int | None = Field(default=None, ge=0, le=24 * 60)
    frequency: Frequency | None = None
    days_of_week: list[int] | None = None
    at_time: time_type | None = None
    active: bool | None = None


class RoutineRead(RoutineBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class BulkTaskItem(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: Category = "other"
    priority: Priority = "medium"
    estimated_minutes: int = Field(default=0, ge=0, le=24 * 60)


class BulkTasks(BaseModel):
    """Add many tasks to one day at once — the paste / checklist-upload path."""
    date: date_type | None = None  # defaults to today
    tasks: list[BulkTaskItem] = Field(default_factory=list, max_length=200)


class PasteTasks(BaseModel):
    """Free-text paste: one task per line, optional 'category: title' prefix."""
    date: date_type | None = None
    text: str = Field(default="", max_length=20000)


class DayPlan(BaseModel):
    date: date_type
    tasks: list[GoalRead]
    total: int
    completed: int
    streak: int


class MissedResponse(BaseModel):
    tasks: list[GoalRead]
