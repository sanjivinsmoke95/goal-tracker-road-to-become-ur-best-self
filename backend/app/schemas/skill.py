from datetime import date as date_type

from pydantic import BaseModel


class TopicScoreRead(BaseModel):
    tag: str
    attempts: int
    solved: int
    score: float | None
    band: str


class SkillProfileRead(BaseModel):
    estimated_rating: int | None
    confidence: float
    recommended_range: list[int] | None
    recent_success_rate: float | None
    average_attempts: float | None
    average_problem_rating: float | None
    total_solved: int
    total_attempts: int
    strengths: list[str]
    reinforce: list[str]
    topics: list[TopicScoreRead]
    # Honesty flag: false when there isn't enough data to estimate anything.
    available: bool


class SkillHistoryPoint(BaseModel):
    date: date_type
    estimated_rating: int | None
    confidence: float
    total_solved: int
