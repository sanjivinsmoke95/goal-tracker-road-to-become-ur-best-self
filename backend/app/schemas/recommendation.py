from datetime import date as date_type
from typing import Any

from pydantic import BaseModel


class ProblemMini(BaseModel):
    id: str
    platform: str
    name: str
    rating: int | None
    difficulty: str | None
    tags: list[str]
    url: str


class DailyProblemRead(BaseModel):
    platform: str
    date: date_type
    problem: ProblemMini | None
    target_rating: int | None
    score: float
    reason: dict[str, Any]
    explanation: str
    status: str


class ProblemOfTheDay(BaseModel):
    codeforces: DailyProblemRead | None
    leetcode: DailyProblemRead | None
