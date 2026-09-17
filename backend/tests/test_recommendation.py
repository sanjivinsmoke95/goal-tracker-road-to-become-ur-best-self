from datetime import datetime, timezone

from app.services.recommendation_engine import Candidate, RecoContext, adapted_target, rank
from app.services.skill_engine import SubmissionData, build_profile

NOW = datetime(2026, 9, 17, tzinfo=timezone.utc)


def _profile(rating, struggling):
    # Strong at greedy; when struggling, many failed dp attempts drag the
    # success rate below 0.4 (and make dp a weak topic).
    n_ok = 3 if struggling else 15
    subs = [SubmissionData(f"p{i}", "OK", rating, ["greedy"], NOW) for i in range(n_ok)]
    if struggling:
        subs += [SubmissionData(f"f{i}", "WRONG_ANSWER", rating + 200, ["dp"], NOW) for i in range(12)]
    return build_profile(subs, NOW)


def test_adapted_target_rises_when_succeeding():
    p = _profile(900, struggling=False)
    assert adapted_target(p) == p.estimated_rating + 100


def test_adapted_target_falls_when_struggling():
    p = _profile(900, struggling=True)
    assert p.recent_success_rate is not None and p.recent_success_rate < 0.4
    assert adapted_target(p) <= (p.estimated_rating or 900)


def test_difficulty_fit_prefers_target_rating():
    p = _profile(900, struggling=False)  # target becomes 1000
    target = adapted_target(p)
    cands = [
        Candidate("easy", target - 300, ["greedy"]),
        Candidate("fit", target, ["greedy"]),
        Candidate("hard", target + 400, ["greedy"]),
    ]
    ranked = rank(cands, p)
    assert ranked[0]["id"] == "fit"


def test_excessive_difficulty_penalised():
    p = _profile(900, struggling=False)
    target = adapted_target(p)
    r = rank([Candidate("way_too_hard", target + 500, ["dp"])], p)[0]
    assert "excessive_difficulty" in r["penalties"]


def test_weak_topic_boosts_relevance():
    # dp is a weak topic in this profile; a dp problem at-target should beat a
    # strong-topic problem at-target on topic relevance.
    p = _profile(900, struggling=True)  # creates dp failures -> weak/dev dp
    target = adapted_target(p)
    cands = [Candidate("greedy_at", target, ["greedy"]), Candidate("dp_at", target, ["dp"])]
    ranked = rank(cands, p)
    dp = next(c for c in ranked if c["id"] == "dp_at")
    greedy = next(c for c in ranked if c["id"] == "greedy_at")
    assert dp["components"]["topic_relevance"] >= greedy["components"]["topic_relevance"]
