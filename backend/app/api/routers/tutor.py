"""AI Tutor — progressive hints, never instant solutions (Milestone 23)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import Problem, User
from app.services import analysis_service, skill_engine
from app.services.ai import get_provider

router = APIRouter(prefix="/tutor", tags=["tutor"])


class HintRequest(BaseModel):
    problem_id: str | None = None
    tags: list[str] = []
    level: int = 1  # 1..3, how many hints to reveal


class AskRequest(BaseModel):
    message: str
    problem_id: str | None = None
    reveal_solution: bool = False


def _tags(db: Session, problem_id: str | None, fallback: list[str]) -> list[str]:
    if problem_id:
        p = db.get(Problem, problem_id)
        if p:
            return p.tags or []
    return fallback


@router.post("/hint")
def hint(payload: HintRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    return get_provider().tutor_hint(
        {"tags": _tags(db, payload.problem_id, payload.tags), "level": max(1, min(3, payload.level))}
    )


@router.post("/ask")
def ask(payload: AskRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    profile = skill_engine.compute_for_user(db, user, platform="codeforces")
    ctx = {
        "message": payload.message,
        "tags": _tags(db, payload.problem_id, []),
        "level": 3 if payload.reveal_solution else 2,
        "estimated_rating": profile.estimated_rating,
        "reveal_solution": payload.reveal_solution,
    }
    return get_provider().tutor_hint(ctx)


@router.get("/insight")
def insight(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    msg = analysis_service.mistake_insight(db, user)
    if not msg:
        profile = skill_engine.compute_for_user(db, user, platform="codeforces")
        if profile.estimated_rating:
            msg = (
                f"Your estimated Codeforces level is ~{profile.estimated_rating}. "
                f"Keep the daily problem going to move it."
            )
        else:
            msg = "Connect Codeforces and solve a few problems to unlock personalised insights."
    return {"insight": msg}
