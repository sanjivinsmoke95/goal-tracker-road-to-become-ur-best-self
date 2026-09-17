from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConnectRequest(BaseModel):
    handle: str = Field(min_length=1, max_length=120)


class CodeforcesProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    handle: str
    rating: int | None
    max_rating: int | None
    rank: str | None
    max_rank: str | None
    avatar: str | None
    last_synced_at: datetime | None


class SyncResult(BaseModel):
    last_synced_at: str
    new_submissions: int
    new_solved: int


class ProblemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform: str
    external_id: str
    name: str
    rating: int | None
    difficulty: str | None
    tags: list[str]
    url: str


class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    platform: str
    external_id: str
    problem_id: str | None
    verdict: str
    language: str
    submitted_at: datetime
    problem_rating: int | None
    problem_tags: list[str]
    source_available: bool
