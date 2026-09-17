"""Skill analysis API (Milestone 4)."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import SkillSnapshot, User
from app.schemas.skill import SkillHistoryPoint, SkillProfileRead
from app.services import skill_engine, skills_service

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=SkillProfileRead)
def get_skills(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    p = skill_engine.compute_for_user(db, user)
    data = skills_service.profile_to_dict(p)
    data["available"] = p.estimated_rating is not None or bool(p.topics)
    return data


@router.get("/history", response_model=list[SkillHistoryPoint])
def get_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[SkillSnapshot]:
    return list(
        db.execute(
            select(SkillSnapshot).where(SkillSnapshot.user_id == user.id).order_by(SkillSnapshot.date)
        ).scalars()
    )
