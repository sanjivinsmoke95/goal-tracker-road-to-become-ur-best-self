"""User creation and authentication — the only business logic auth needs."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import User


def get_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email.lower())).scalar_one_or_none()


def create_user(db: Session, email: str, password: str, full_name: str = "") -> User:
    user = User(email=email.lower(), hashed_password=hash_password(password), full_name=full_name)
    db.add(user)
    db.flush()  # populate id without ending the request transaction
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
