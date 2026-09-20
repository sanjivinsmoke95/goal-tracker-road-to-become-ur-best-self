"""Neutral profile comparison between two consenting users.

Deterministic and transparent: it compares the same real metrics for both people
and buckets topics into strengths and growth areas. It never declares an overall
winner and never says one person is "better" — it reports who has more experience
where, and turns *your* growth areas into concrete suggested actions.
"""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Goal, PlatformAccount, TopicCompletion, User
from app.services import curriculum, goals_service, skill_engine
from app.services.adapters.leetcode import blended_rating, level_from_rating

_MARGIN = 15.0  # score gap (0–100) that counts as a real difference in experience


def _learning(db: Session, user: User) -> dict:
    done = {
        tid
        for (tid,) in db.execute(
            select(TopicCompletion.topic_id).where(TopicCompletion.user_id == user.id)
        ).all()
    }
    paths: dict[str, float] = {}
    total_topics = 0
    for pid, path in curriculum.PATHS.items():
        tids = [t["id"] for m in path["modules"] for t in m["topics"]]
        total_topics += len(tids)
        completed = sum(1 for t in tids if t in done)
        paths[pid] = round(100 * completed / len(tids), 1) if tids else 0.0
    overall = round(100 * len(done) / total_topics, 1) if total_topics else 0.0
    return {"overall_pct": overall, "paths": paths}


def _planner(db: Session, user: User, today: date) -> dict:
    cutoff = today - timedelta(days=14)
    goals = list(
        db.execute(
            select(Goal).where(Goal.user_id == user.id, Goal.date >= cutoff, Goal.date <= today)
        ).scalars()
    )
    total = len(goals)
    completed = sum(1 for g in goals if g.status == "completed")
    return {
        "completion_rate": round(100 * completed / total, 1) if total else 0.0,
        "streak": goals_service.compute_streak(goals_service.completed_dates(db, user), today),
    }


def metrics_for(db: Session, user: User, today: date | None = None) -> dict:
    today = today or date.today()
    cf = skill_engine.compute_for_user(db, user, platform="codeforces")

    lc_acc = db.execute(
        select(PlatformAccount).where(PlatformAccount.user_id == user.id, PlatformAccount.platform == "leetcode")
    ).scalar_one_or_none()
    lc_meta = (lc_acc.meta if lc_acc else None) or {}
    lc_solved = lc_meta.get("total", 0)
    lc_level = level_from_rating(blended_rating(lc_meta))

    topics = {
        tag: {"score": ts.score, "attempts": ts.attempts, "solved": ts.solved, "band": ts.band}
        for tag, ts in cf.topics.items()
        if ts.band != "insufficient_data" and ts.score is not None
    }
    return {
        "cf_rating": cf.estimated_rating,
        "cf_solved": cf.total_solved,
        "lc_solved": lc_solved,
        "lc_level": lc_level,
        "topics": topics,
        "learning": _learning(db, user),
        "planner": _planner(db, user, today),
    }


def compare(db: Session, me: User, friend: User, today: date | None = None) -> dict:
    mine = metrics_for(db, me, today)
    theirs = metrics_for(db, friend, today)

    my_t, fr_t = mine["topics"], theirs["topics"]
    your_strengths = sorted(t for t, v in my_t.items() if v["band"] == "strong")
    friend_strengths = sorted(t for t, v in fr_t.items() if v["band"] == "strong")
    shared_strengths = sorted(set(your_strengths) & set(friend_strengths))

    per_topic: list[dict] = []
    your_growth: list[dict] = []
    friend_growth: list[dict] = []
    shared_growth: list[str] = []
    for tag in sorted(set(my_t) & set(fr_t)):
        ms, fs = my_t[tag]["score"], fr_t[tag]["score"]
        per_topic.append({"topic": tag, "you": ms, "friend": fs})
        if fs - ms >= _MARGIN:
            your_growth.append({"topic": tag, "you": ms, "friend": fs, "gap": round(fs - ms, 1)})
        elif ms - fs >= _MARGIN:
            friend_growth.append({"topic": tag, "you": ms, "friend": fs, "gap": round(ms - fs, 1)})
        if ms < 50 and fs < 50:
            shared_growth.append(tag)

    your_growth.sort(key=lambda x: x["gap"], reverse=True)
    friend_growth.sort(key=lambda x: x["gap"], reverse=True)

    report = [_action_for(item) for item in your_growth[:3]]

    return {
        "you": mine,
        "friend": {**theirs, "display_name": friend.full_name or friend.email},
        "topic_comparison": per_topic,
        "your_strengths": your_strengths,
        "friend_strengths": friend_strengths,
        "shared_strengths": shared_strengths,
        "your_growth_areas": your_growth,
        "friend_growth_areas": friend_growth,
        "shared_growth_areas": shared_growth,
        "report": report,
    }


def _action_for(item: dict) -> dict:
    you = item["you"]
    if you < 35:
        action = f"Review the basics of {item['topic']} and solve 2 beginner problems at your current level."
    elif you < 55:
        action = f"Practice 3 {item['topic']} problems around your level to close the gap."
    else:
        action = f"Push {item['topic']} with 2 slightly harder problems — you're close."
    return {
        "topic": item["topic"],
        "your_success": item["you"],
        "friend_success": item["friend"],
        "suggested_action": action,
    }
