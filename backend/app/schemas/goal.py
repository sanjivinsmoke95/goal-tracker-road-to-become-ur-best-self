from datetime import date as date_type
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Category = Literal["cf", "lc", "react", "backend", "cs", "other"]
Priority = Literal["low", "medium", "high"]
Status = Literal["pending", "in_progress", "completed", "skipped"]


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    category: Category = "other"
    priority: Priority = "medium"
    estimated_minutes: int = Field(default=0, ge=0, le=24 * 60)
    date: date_type | None = None  # defaults to today server-side
    notes: str = Field(default="", max_length=4000)
    linked_type: Literal["problem", "topic"] | None = None
    linked_ref: str | None = Field(default=None, max_length=200)


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    category: Category | None = None
    priority: Priority | None = None
    estimated_minutes: int | None = Field(default=None, ge=0, le=24 * 60)
    date: date_type | None = None
    status: Status | None = None
    notes: str | None = Field(default=None, max_length=4000)


class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    category: Category
    priority: Priority
    estimated_minutes: int
    date: date_type
    status: Status
    completed_at: datetime | None
    notes: str
    source: str = "manual"
    routine_id: str | None = None
    carried_from: date_type | None = None
    linked_type: str | None
    linked_ref: str | None


class StreakSummary(BaseModel):
    streak: int
    today_total: int
    today_completed: int
