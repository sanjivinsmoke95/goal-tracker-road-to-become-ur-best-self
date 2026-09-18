"""Daily planner API: the day view, routines, bulk entry, and missed carry-over.

Individual task actions (check off, edit, delete) stay on the existing /goals
router — a planner task *is* a goal. This router adds the day-planner layer on
top: recurring routines, bulk/paste entry, and the missed-task triage.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import Goal, Routine, User
from app.schemas.goal import GoalRead
from app.schemas.planner import (
    BulkTasks,
    DayPlan,
    MissedResponse,
    PasteTasks,
    RoutineCreate,
    RoutineRead,
    RoutineUpdate,
)
from app.services import planner_service

router = APIRouter(prefix="/planner", tags=["planner"])


def _today() -> date:
    return date.today()


# --- Day view -------------------------------------------------------------
@router.get("/day", response_model=DayPlan)
def get_day(
    date_on: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return planner_service.day_plan(db, user, date_on or _today(), _today())


# --- Bulk / paste entry ---------------------------------------------------
@router.post("/tasks/bulk", response_model=list[GoalRead], status_code=status.HTTP_201_CREATED)
def add_bulk(
    payload: BulkTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Goal]:
    items = [t.model_dump() for t in payload.tasks]
    return planner_service.bulk_create(db, user, items, payload.date or _today(), source="upload")


@router.post("/tasks/paste", response_model=list[GoalRead], status_code=status.HTTP_201_CREATED)
def add_paste(
    payload: PasteTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Goal]:
    items = planner_service.parse_paste(payload.text)
    return planner_service.bulk_create(db, user, items, payload.date or _today(), source="upload")


# --- Missed carry-over ----------------------------------------------------
@router.get("/missed", response_model=MissedResponse)
def get_missed(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return {"tasks": planner_service.missed_tasks(db, user, _today())}


def _owned_goal(db: Session, user: User, goal_id: str) -> Goal:
    goal = db.get(Goal, goal_id)
    if not goal or goal.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found.")
    return goal


@router.post("/missed/{goal_id}/move", response_model=GoalRead)
def move_missed(
    goal_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Goal:
    return planner_service.move_to_today(db, _owned_goal(db, user, goal_id), _today())


@router.post("/missed/{goal_id}/dismiss", response_model=GoalRead)
def dismiss_missed(
    goal_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Goal:
    return planner_service.dismiss(db, _owned_goal(db, user, goal_id))


# --- Routines -------------------------------------------------------------
def _owned_routine(db: Session, user: User, routine_id: str) -> Routine:
    routine = planner_service.get_routine(db, user, routine_id)
    if not routine:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Routine not found.")
    return routine


@router.get("/routines", response_model=list[RoutineRead])
def list_routines(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Routine]:
    return planner_service.list_routines(db, user)


@router.post("/routines", response_model=RoutineRead, status_code=status.HTTP_201_CREATED)
def create_routine(
    payload: RoutineCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Routine:
    return planner_service.create_routine(db, user, payload.model_dump())


@router.patch("/routines/{routine_id}", response_model=RoutineRead)
def update_routine(
    routine_id: str,
    payload: RoutineUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Routine:
    routine = _owned_routine(db, user, routine_id)
    return planner_service.update_routine(db, routine, payload.model_dump(exclude_unset=True))


@router.delete("/routines/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine(
    routine_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    planner_service.delete_routine(db, _owned_routine(db, user, routine_id))
