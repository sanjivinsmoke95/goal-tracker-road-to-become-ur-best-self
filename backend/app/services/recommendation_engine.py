"""Problem-of-the-Day recommendation — deterministic candidate scoring.

The LLM never picks the problem. This module scores unsolved candidates with a
configurable weighted formula and difficulty adaptation, and hands the winner
(plus its score breakdown) to the AI layer only to phrase the *explanation*.

    candidate_score = w.difficulty·difficulty_fit
                    + w.topic·topic_relevance
                    + w.novelty·novelty
                    + w.spaced·spaced_repetition
                    + w.recent·recent_performance_fit
                    + w.plan·learning_goal_alignment
                    − recently_seen_penalty − excessive_difficulty_penalty
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.services.skill_engine import SkillProfile

DEFAULT_WEIGHTS = {
    "difficulty": 0.40,
    "topic": 0.20,
    "novelty": 0.15,
    "spaced": 0.10,
    "recent": 0.10,
    "plan": 0.05,
}
RECENTLY_SEEN_PENALTY = 0.30
EXCESSIVE_DIFFICULTY_PENALTY = 0.50
DIFFICULTY_SIGMA = 200.0


@dataclass
class Candidate:
    id: str
    rating: int | None
    tags: list[str] = field(default_factory=list)


@dataclass
class RecoContext:
    recent_problem_ids: set[str] = field(default_factory=set)  # attempted very recently
    tag_last_seen_days: dict[str, int] = field(default_factory=dict)  # tag -> days since last attempt
    goal_tags: set[str] = field(default_factory=set)  # today's goal categories/tags
    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))


def adapted_target(profile: SkillProfile) -> int:
    """The difficulty we aim at today — shifts with recent performance."""
    base = profile.estimated_rating or 900
    r = profile.recent_success_rate
    if r is not None:
        if r >= 0.7:
            base += 100  # solving comfortably → nudge up
        elif r < 0.4:
            base -= 100  # struggling → ease off and reinforce
    return max(800, base)


def _difficulty_fit(rating: int | None, target: int) -> float:
    if rating is None:
        return 0.3
    return math.exp(-(((rating - target) / DIFFICULTY_SIGMA) ** 2))


def _topic_relevance(tags: list[str], profile: SkillProfile) -> float:
    if not tags:
        return 0.3
    best = 0.0
    for t in tags:
        ts = profile.topics.get(t)
        if ts is None:
            best = max(best, 0.55)  # never practised — worth exposure
        elif ts.band == "needs_reinforcement":
            best = max(best, 1.0)
        elif ts.band == "developing":
            best = max(best, 0.75)
        elif ts.band == "insufficient_data":
            best = max(best, 0.6)
        else:  # strong
            best = max(best, 0.4)
    return best


def _novelty(tags: list[str], profile: SkillProfile) -> float:
    if not tags:
        return 0.0
    unseen = sum(1 for t in tags if t not in profile.topics)
    return unseen / len(tags)


def _spaced(tags: list[str], ctx: RecoContext) -> float:
    if not tags:
        return 0.0
    # Older last-seen → higher score (saturating at ~30 days).
    scores = [min(1.0, ctx.tag_last_seen_days.get(t, 30) / 30.0) for t in tags]
    return sum(scores) / len(scores)


def _recent_perf_fit(rating: int | None, target: int, profile: SkillProfile) -> float:
    if rating is None or profile.recent_success_rate is None:
        return 0.5
    # Doing well → reward harder-than-target; struggling → reward easier.
    if profile.recent_success_rate >= 0.7:
        return 1.0 if rating >= target else 0.5
    if profile.recent_success_rate < 0.4:
        return 1.0 if rating <= target else 0.4
    return 0.7


def _plan_alignment(tags: list[str], ctx: RecoContext) -> float:
    if not ctx.goal_tags or not tags:
        return 0.0
    return 1.0 if any(t in ctx.goal_tags for t in tags) else 0.0


def score_candidate(c: Candidate, profile: SkillProfile, target: int, ctx: RecoContext) -> dict:
    w = ctx.weights
    comp = {
        "difficulty_fit": _difficulty_fit(c.rating, target),
        "topic_relevance": _topic_relevance(c.tags, profile),
        "novelty": _novelty(c.tags, profile),
        "spaced_repetition": _spaced(c.tags, ctx),
        "recent_performance_fit": _recent_perf_fit(c.rating, target, profile),
        "learning_goal_alignment": _plan_alignment(c.tags, ctx),
    }
    score = (
        w["difficulty"] * comp["difficulty_fit"]
        + w["topic"] * comp["topic_relevance"]
        + w["novelty"] * comp["novelty"]
        + w["spaced"] * comp["spaced_repetition"]
        + w["recent"] * comp["recent_performance_fit"]
        + w["plan"] * comp["learning_goal_alignment"]
    )
    penalties = {}
    if c.id in ctx.recent_problem_ids:
        penalties["recently_seen"] = RECENTLY_SEEN_PENALTY
        score -= RECENTLY_SEEN_PENALTY
    if c.rating is not None and c.rating > target + 300:
        penalties["excessive_difficulty"] = EXCESSIVE_DIFFICULTY_PENALTY
        score -= EXCESSIVE_DIFFICULTY_PENALTY

    top_reason = max(comp, key=comp.get).replace("_", " ")
    return {"id": c.id, "score": round(score, 4), "components": comp, "penalties": penalties, "top_reason": top_reason}


def rank(candidates: list[Candidate], profile: SkillProfile, ctx: RecoContext | None = None) -> list[dict]:
    ctx = ctx or RecoContext()
    target = adapted_target(profile)
    scored = [score_candidate(c, profile, target, ctx) for c in candidates]
    scored.sort(key=lambda s: s["score"], reverse=True)
    return scored
