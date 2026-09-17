from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.platform import SubmissionRead
from app.schemas.recommendation import ProblemMini


class AnalyzeRequest(BaseModel):
    code: str | None = None
    language: str | None = None


class MistakeSummary(BaseModel):
    mistake_type: str
    frequency: int
    severity: str
    last_occurrence: datetime | None
    note: str


class SubmissionDetail(BaseModel):
    submission: SubmissionRead
    problem: ProblemMini | None
    analysis: dict[str, Any] | None
