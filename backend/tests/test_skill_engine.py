from datetime import datetime, timezone

from app.services.skill_engine import SubmissionData, build_profile

NOW = datetime(2026, 9, 17, tzinfo=timezone.utc)


def sub(pid, verdict, rating, tags, day=17):
    return SubmissionData(pid, verdict, rating, tags, datetime(2026, 9, day, tzinfo=timezone.utc))


def test_empty_profile_is_insufficient():
    p = build_profile([], NOW)
    assert p.estimated_rating is None
    assert p.confidence == 0.0
    assert p.total_solved == 0
    assert p.topics == {}


def test_estimated_rating_tracks_solved_ratings():
    subs = [sub(f"cf:{i}", "OK", 800 + (i % 3) * 100, ["greedy"]) for i in range(15)]
    subs += [sub("cf:hard", "OK", 1000, ["dp"])]
    p = build_profile(subs, NOW)
    # 70th percentile of {800,900,1000} spread → ~900-1000, rounded to 100s.
    assert p.estimated_rating in (900, 1000)
    assert p.recommended_range == (p.estimated_rating - 100, p.estimated_rating + 100)
    assert p.confidence > 0


def test_repeated_failures_soften_estimate():
    # Solves only low, fails high repeatedly → low success rate softens estimate.
    subs = [sub(f"cf:s{i}", "OK", 800, ["impl"]) for i in range(3)]
    subs += [sub(f"cf:f{i}", "WRONG_ANSWER", 1200, ["dp"]) for i in range(8)]
    p = build_profile(subs, NOW)
    assert p.recent_success_rate is not None and p.recent_success_rate < 0.4
    assert p.estimated_rating is not None
    assert p.estimated_rating <= 800  # softened down from the 800 solves


def test_topic_bands_strong_and_reinforce():
    subs = [sub(f"cf:g{i}", "OK", 1100, ["greedy"]) for i in range(5)]  # strong
    subs += [sub("cf:d1", "WRONG_ANSWER", 1400, ["dp"])]
    subs += [sub("cf:d2", "WRONG_ANSWER", 1400, ["dp"])]
    subs += [sub("cf:d3", "OK", 900, ["dp"])]  # dp: 1/3 solved → needs reinforcement
    p = build_profile(subs, NOW)
    assert p.topics["greedy"].band == "strong"
    assert "greedy" in p.strengths
    assert p.topics["dp"].band == "needs_reinforcement"
    assert "dp" in p.reinforce


def test_insufficient_data_topic_not_labelled_weak():
    subs = [sub("cf:a", "WRONG_ANSWER", 1500, ["graphs"])]  # only 1 attempt
    p = build_profile(subs, NOW)
    assert p.topics["graphs"].band == "insufficient_data"
    # Not counted as a weakness despite the failure.
    assert "graphs" not in p.reinforce
