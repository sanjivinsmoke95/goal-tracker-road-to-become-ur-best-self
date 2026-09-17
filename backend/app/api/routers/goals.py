"""Daily goals API (Milestone 2)."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import Goal, User
from app.schemas.goal import GoalCreate, GoalRead, GoalUpdate, StreakSummary
from app.services import goals_service

router = APIRouter(prefix="/goals", tags=["goals"])


def _today() -> date:
    return date.today()


def _owned(db: Session, user: User, goal_id: str) -> Goal:
    goal = goals_service.get_goal(db, user, goal_id)
    if not goal:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Goal not found.")
    return goal


@router.get("", response_model=list[GoalRead])
def list_goals(
    date_on: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Goal]:
    return goals_service.list_goals(db, user, date_on or _today())


@router.get("/streak", response_model=StreakSummary)
def get_streak(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return goals_service.streak_summary(db, user, _today())


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Goal:
    return goals_service.create_goal(db, user, payload.model_dump(), _today())


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(
    goal_id: str,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Goal:
    goal = _owned(db, user, goal_id)
    changes = payload.model_dump(exclude_unset=True)
    return goals_service.update_goal(db, goal, changes)


@router.post("/{goal_id}/complete", response_model=GoalRead)
def complete_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Goal:
    """Toggle completion — checking the box completes it, unchecking reopens it."""
    goal = _owned(db, user, goal_id)
    return goals_service.toggle_complete(db, goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    goal = _owned(db, user, goal_id)
    goals_service.delete_goal(db, goal)
