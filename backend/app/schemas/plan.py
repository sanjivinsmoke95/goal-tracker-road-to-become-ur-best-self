from datetime import date as date_type
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PlanDayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    day_number: int
    date: date_type
    tasks: list[Any]


class LearningPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    goal: str
    duration_days: int
    hours_per_day: int
    start_date: date_type
    source: str
    status: str
    days: list[PlanDayRead]


class GenerateRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=500)
    duration_days: int = Field(default=30, ge=1, le=365)
    hours_per_day: int = Field(default=2, ge=1, le=16)


class DayUpdate(BaseModel):
    tasks: list[Any]
