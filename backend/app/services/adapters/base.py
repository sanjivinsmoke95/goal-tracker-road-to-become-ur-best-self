"""The platform-agnostic contract every integration implements.

Everything above the adapter (sync, skill engine, recommendations) speaks only
these normalized shapes, so it never cares whether data came from Codeforces,
LeetCode, or a manual import.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NormalizedProblem:
    platform: str
    external_id: str  # "1520B" (cf) or a slug (lc)
    name: str = ""
    contest_id: int | None = None
    index: str | None = None
    rating: int | None = None
    difficulty: str | None = None
    tags: list[str] = field(default_factory=list)
    url: str = ""

    @property
    def pk(self) -> str:
        return f"{self.platform[:2]}:{self.external_id}"


@dataclass
class NormalizedSubmission:
    external_id: str
    verdict: str
    language: str
    submitted_at: datetime
    problem: NormalizedProblem
    source_code: str | None = None


@dataclass
class NormalizedProfile:
    handle: str
    rating: int | None = None
    max_rating: int | None = None
    rank: str | None = None
    max_rank: str | None = None
    avatar: str | None = None


class PlatformAdapter(abc.ABC):
    platform: str

    @abc.abstractmethod
    def fetch_profile(self, handle: str) -> NormalizedProfile: ...

    @abc.abstractmethod
    def fetch_submissions(self, handle: str) -> list[NormalizedSubmission]: ...
