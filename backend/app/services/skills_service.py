"""Serialisation of the skill profile + daily snapshotting for history."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SkillSnapshot, User
from app.services import skill_engine
from app.services.skill_engine import SkillProfile


def profile_to_dict(p: SkillProfile) -> dict:
    return {
        "estimated_rating": p.estimated_rating,
        "confidence": p.confidence,
        "recommended_range": list(p.recommended_range) if p.recommended_range else None,
        "recent_success_rate": p.recent_success_rate,
        "average_attempts": p.average_attempts,
        "average_problem_rating": p.average_problem_rating,
        "total_solved": p.total_solved,
        "total_attempts": p.total_attempts,
        "strengths": p.strengths,
        "reinforce": p.reinforce,
        "topics": [
            {"tag": t.tag, "attempts": t.attempts, "solved": t.solved, "score": t.score, "band": t.band}
            for t in sorted(p.topics.values(), key=lambda t: (t.score is None, -(t.score or 0)))
        ],
    }


def snapshot_today(db: Session, user: User, on_date: date | None = None) -> SkillSnapshot:
    on_date = on_date or date.today()
    p = skill_engine.compute_for_user(db, user)
    row = db.execute(
        select(SkillSnapshot).where(SkillSnapshot.user_id == user.id, SkillSnapshot.date == on_date)
    ).scalar_one_or_none()
    if row is None:
        row = SkillSnapshot(user_id=user.id, date=on_date)
        db.add(row)
    row.estimated_rating = p.estimated_rating
    row.confidence = p.confidence
    row.recent_success_rate = p.recent_success_rate
    row.total_solved = p.total_solved
    row.total_attempts = p.total_attempts
    row.topics = {
        t.tag: {"score": t.score, "band": t.band, "attempts": t.attempts, "solved": t.solved}
        for t in p.topics.values()
    }
    db.flush()
    return row
