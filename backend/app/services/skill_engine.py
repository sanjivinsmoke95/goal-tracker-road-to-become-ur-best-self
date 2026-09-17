"""The skill engine — deterministic, statistical, no LLM.

Turns a user's real submissions into an estimated solving level, per-topic
scores, and Strong / Developing / Needs-reinforcement / Insufficient-data
classifications. Recent activity is weighted more heavily than old activity.
Everything here is a pure function of the submission data, so it is fully
unit-testable and never invents a score.

This implements the DATA → INFERENCE contract: the inputs are facts (what you
submitted); the outputs are clearly-labelled estimates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

RECENT_DAYS = 120
MIN_TOPIC_ATTEMPTS = 3
# Codeforces ratings roughly span 800..3500; we normalise into 0..1 for scoring.
RATING_FLOOR, RATING_CEIL = 800, 2600


@dataclass
class SubmissionData:
    problem_id: str
    verdict: str
    problem_rating: int | None
    problem_tags: list[str]
    submitted_at: datetime


@dataclass
class TopicScore:
    tag: str
    attempts: int
    solved: int
    score: float | None
    band: str  # strong | developing | needs_reinforcement | insufficient_data


@dataclass
class SkillProfile:
    estimated_rating: int | None
    confidence: float
    recommended_range: tuple[int, int] | None
    recent_success_rate: float | None
    average_attempts: float | None
    average_problem_rating: float | None
    total_solved: int
    total_attempts: int
    topics: dict[str, TopicScore] = field(default_factory=dict)

    @property
    def strengths(self) -> list[str]:
        return [t.tag for t in _sorted(self.topics) if t.band == "strong"]

    @property
    def reinforce(self) -> list[str]:
        return [t.tag for t in _sorted(self.topics) if t.band == "needs_reinforcement"]


def _sorted(topics: dict[str, TopicScore]) -> list[TopicScore]:
    return sorted(topics.values(), key=lambda t: (t.score is None, -(t.score or 0)))


def _norm_rating(r: int | None) -> float:
    if r is None:
        return 0.5
    return max(0.0, min(1.0, (r - RATING_FLOOR) / (RATING_CEIL - RATING_FLOOR)))


def _percentile(values: list[int], pct: float) -> int:
    """Nearest-rank percentile."""
    if not values:
        return 0
    ordered = sorted(values)
    k = max(0, min(len(ordered) - 1, round(pct / 100 * (len(ordered) - 1))))
    return ordered[k]


def _as_aware(dt: datetime) -> datetime:
    """SQLite returns naive datetimes; treat those as UTC so comparisons work."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _band(score: float) -> str:
    if score >= 68:
        return "strong"
    if score >= 45:
        return "developing"
    return "needs_reinforcement"


def build_profile(subs: list[SubmissionData], now: datetime | None = None) -> SkillProfile:
    now = _as_aware(now or datetime.now(timezone.utc))
    cutoff = now - timedelta(days=RECENT_DAYS)
    recent = [s for s in subs if _as_aware(s.submitted_at) >= cutoff] or subs  # all-time if sparse

    # Per-problem aggregation (recent window).
    attempts_by_problem: dict[str, int] = {}
    solved_problems: set[str] = set()
    rating_of: dict[str, int | None] = {}
    for s in recent:
        attempts_by_problem[s.problem_id] = attempts_by_problem.get(s.problem_id, 0) + 1
        rating_of[s.problem_id] = s.problem_rating
        if s.verdict == "OK":
            solved_problems.add(s.problem_id)

    total_attempts = len(attempts_by_problem)
    total_solved = len(solved_problems)
    recent_success_rate = (total_solved / total_attempts) if total_attempts else None
    average_attempts = (
        sum(attempts_by_problem.values()) / total_attempts if total_attempts else None
    )
    solved_ratings = [rating_of[p] for p in solved_problems if rating_of.get(p) is not None]
    average_problem_rating = (sum(solved_ratings) / len(solved_ratings)) if solved_ratings else None

    # Estimated solving level: the 70th percentile of recently-solved ratings,
    # softened downward when recent failures cluster. Rounded to nearest 100.
    estimated_rating: int | None = None
    recommended_range: tuple[int, int] | None = None
    confidence = 0.0
    if solved_ratings:
        est = _percentile(solved_ratings, 70)
        # Soften by recent failure pressure.
        if recent_success_rate is not None and recent_success_rate < 0.4:
            est -= 100
        estimated_rating = int(round(est / 100.0) * 100)
        recommended_range = (max(RATING_FLOOR, estimated_rating - 100), estimated_rating + 100)
        confidence = round(min(1.0, len(solved_ratings) / 20.0), 2)

    # Per-topic scores.
    topics: dict[str, TopicScore] = {}
    tag_attempts: dict[str, set[str]] = {}
    tag_solved: dict[str, set[str]] = {}
    tag_diff: dict[str, list[float]] = {}
    for s in recent:
        for tag in s.problem_tags or []:
            tag_attempts.setdefault(tag, set()).add(s.problem_id)
            if s.verdict == "OK":
                tag_solved.setdefault(tag, set()).add(s.problem_id)
                tag_diff.setdefault(tag, []).append(_norm_rating(s.problem_rating))

    for tag, probs in tag_attempts.items():
        attempts = len(probs)
        solved = len(tag_solved.get(tag, set()))
        if attempts < MIN_TOPIC_ATTEMPTS:
            topics[tag] = TopicScore(tag, attempts, solved, None, "insufficient_data")
            continue
        success = solved / attempts
        diff = sum(tag_diff.get(tag, [])) / len(tag_diff[tag]) if tag_diff.get(tag) else 0.4
        score = max(0.0, min(100.0, success * 70 + diff * 30))
        topics[tag] = TopicScore(tag, attempts, solved, round(score, 1), _band(score))

    return SkillProfile(
        estimated_rating=estimated_rating,
        confidence=confidence,
        recommended_range=recommended_range,
        recent_success_rate=round(recent_success_rate, 3) if recent_success_rate is not None else None,
        average_attempts=round(average_attempts, 2) if average_attempts is not None else None,
        average_problem_rating=round(average_problem_rating, 1) if average_problem_rating is not None else None,
        total_solved=total_solved,
        total_attempts=total_attempts,
        topics=topics,
    )


# ---- DB-facing wrapper ----

def load_submissions(db, user, platform: str | None = None) -> list[SubmissionData]:
    from sqlalchemy import select

    from app.models import Submission

    stmt = select(Submission).where(Submission.user_id == user.id)
    if platform:
        stmt = stmt.where(Submission.platform == platform)
    rows = db.execute(stmt).scalars()
    return [
        SubmissionData(
            problem_id=s.problem_id or s.external_id,
            verdict=s.verdict,
            problem_rating=s.problem_rating,
            problem_tags=s.problem_tags or [],
            submitted_at=s.submitted_at,
        )
        for s in rows
    ]


def compute_for_user(db, user, platform: str | None = None, now: datetime | None = None) -> SkillProfile:
    return build_profile(load_submissions(db, user, platform), now)
