"""Friends + consent-gated profile comparison."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import User
from app.schemas.social import (
    FriendRequestCreate,
    FriendRequestRead,
    PendingRequests,
    UserMini,
)
from app.services import comparison_service, friend_service, preferences_service

router = APIRouter(prefix="/friends", tags=["friends"])


@router.get("", response_model=list[UserMini])
def list_friends(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[User]:
    return friend_service.list_friends(db, user)


@router.get("/pending", response_model=PendingRequests)
def pending(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    return friend_service.pending(db, user)


@router.post("/request", response_model=FriendRequestRead, status_code=status.HTTP_201_CREATED)
def send_request(
    payload: FriendRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    target = friend_service.find_user_by_email(db, payload.email)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No user with that email.")
    try:
        return friend_service.send_request(db, user, target)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.post("/{friendship_id}/accept", response_model=FriendRequestRead)
def accept(friendship_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return friend_service.respond(db, user, friendship_id, accept=True)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.post("/{friendship_id}/decline", response_model=FriendRequestRead)
def decline(friendship_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        return friend_service.respond(db, user, friendship_id, accept=False)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.delete("/{other_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(other_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> None:
    friend_service.remove(db, user, other_id)


@router.get("/{friend_id}/compare")
def compare(friend_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    if not friend_service.are_friends(db, user.id, friend_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only compare with an accepted friend.")
    friend = db.get(User, friend_id)
    if not friend:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Friend not found.")
    # Privacy: the friend must allow being compared.
    if not preferences_service.get_or_create(db, friend).allow_comparison:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This friend has turned off profile comparison.")
    return comparison_service.compare(db, user, friend)
