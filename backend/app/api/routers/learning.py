"""Learning paths, topics, and completion (Milestone 8)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import TopicCompletion, User
from app.services import curriculum

router = APIRouter(prefix="/learning", tags=["learning"])


def _completed(db: Session, user: User) -> set[str]:
    return set(
        db.execute(select(TopicCompletion.topic_id).where(TopicCompletion.user_id == user.id)).scalars()
    )


@router.get("/paths")
def paths(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    done = _completed(db, user)
    return {"paths": curriculum.all_paths(), "completed": sorted(done), "completed_count": len(done),
            "total": len(curriculum.all_topic_ids())}


@router.get("/topics/{topic_id}")
def topic(topic_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    t = curriculum.get_topic(topic_id)
    if not t:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found.")
    return {**t, "completed": topic_id in _completed(db, user)}


@router.post("/topics/{topic_id}/complete")
def complete(topic_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    if not curriculum.get_topic(topic_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Topic not found.")
    existing = db.execute(
        select(TopicCompletion).where(TopicCompletion.user_id == user.id, TopicCompletion.topic_id == topic_id)
    ).scalar_one_or_none()
    if existing:
        db.delete(existing)  # toggle off
        db.flush()
        return {"topic_id": topic_id, "completed": False}
    db.add(TopicCompletion(user_id=user.id, topic_id=topic_id))
    db.flush()
    return {"topic_id": topic_id, "completed": True}
