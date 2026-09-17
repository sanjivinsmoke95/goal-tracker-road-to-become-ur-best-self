"""Analyse a submission through the AI layer and record any mistakes.

The review shape comes from the provider (stub or Gemini). Detected mistakes
are appended to the user's mistake history so recurring patterns surface over
time (Milestone 13).
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import MistakeOccurrence, Submission, User
from app.services.ai import get_provider


def analyze_submission(db: Session, user: User, submission: Submission, code_override: str | None = None) -> dict:
    code = code_override if code_override is not None else (submission.source_code or "")
    ctx = {
        "code": code,
        "language": submission.language,
        "verdict": submission.verdict,
        "problem_rating": submission.problem_rating,
        "tags": submission.problem_tags or [],
    }
    review = get_provider().review_code(ctx)

    if code_override is not None:
        submission.source_code = code_override
        submission.source_available = True
    submission.analysis_meta = review

    for m in review.get("mistakes", []) or []:
        db.add(
            MistakeOccurrence(
                user_id=user.id,
                mistake_type=m.get("mistake_type", "unknown"),
                note=m.get("note", ""),
                severity=m.get("severity", "medium"),
                platform=submission.platform,
                problem_id=submission.problem_id,
                submission_id=submission.id,
                occurred_at=datetime.now(timezone.utc),
            )
        )
    db.flush()
    return review


_SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}


def recurring_mistakes(db: Session, user: User) -> list[dict]:
    rows = list(db.execute(select(MistakeOccurrence).where(MistakeOccurrence.user_id == user.id)).scalars())
    agg: dict[str, dict] = {}
    for r in rows:
        a = agg.setdefault(
            r.mistake_type, {"mistake_type": r.mistake_type, "frequency": 0, "severity": "low", "last_occurrence": None, "note": r.note}
        )
        a["frequency"] += 1
        if _SEVERITY_ORDER.get(r.severity, 1) > _SEVERITY_ORDER.get(a["severity"], 0):
            a["severity"] = r.severity
        occ = r.occurred_at
        if a["last_occurrence"] is None or (occ and occ.replace(tzinfo=None) > a["last_occurrence"].replace(tzinfo=None)):
            a["last_occurrence"] = occ
            a["note"] = r.note
    return sorted(agg.values(), key=lambda x: x["frequency"], reverse=True)


def mistake_insight(db: Session, user: User) -> str | None:
    """A single, non-judgemental nudge based on the top recurring mistake."""
    top = recurring_mistakes(db, user)
    if not top or top[0]["frequency"] < 3:
        return None
    m = top[0]
    label = m["mistake_type"].replace("_", " ")
    return (
        f"You've hit '{label}' {m['frequency']} times recently. "
        "Today's practice includes a problem useful for reinforcing it."
    )


def count(db: Session, user: User) -> int:
    return db.execute(
        select(func.count()).select_from(MistakeOccurrence).where(MistakeOccurrence.user_id == user.id)
    ).scalar_one()
