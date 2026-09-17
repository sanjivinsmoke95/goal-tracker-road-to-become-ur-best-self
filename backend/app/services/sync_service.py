"""Pull a platform's data through its adapter and persist it.

Adapter-injected: the network lives entirely in the adapter, so this service
(and its tests) run against a fake adapter with canned data.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CodeforcesProfile, PlatformAccount, Problem, Submission, User
from app.services.adapters.base import NormalizedProblem, PlatformAdapter


def _upsert_problem(db: Session, np: NormalizedProblem, cache: dict[str, Problem]) -> Problem:
    # A per-sync cache: with autoflush disabled, db.get() cannot see rows added
    # earlier in this same transaction, so a problem present in both the corpus
    # and the submissions would be inserted twice. The cache dedups it.
    prob = cache.get(np.pk) or db.get(Problem, np.pk)
    if prob is None:
        prob = Problem(id=np.pk, platform=np.platform, external_id=np.external_id)
        db.add(prob)
    cache[np.pk] = prob
    # Don't clobber existing richer data with nulls — a code-less LeetCode
    # submission must not wipe the seeded difficulty/rating for that problem.
    prob.contest_id = np.contest_id if np.contest_id is not None else prob.contest_id
    prob.index = np.index or prob.index
    prob.name = np.name or prob.name
    prob.rating = np.rating if np.rating is not None else prob.rating
    prob.difficulty = np.difficulty if np.difficulty is not None else prob.difficulty
    prob.tags = np.tags or prob.tags
    prob.url = np.url or prob.url
    return prob


def _reset_platform_submissions(db: Session, user: User, platform: str) -> None:
    from sqlalchemy import delete

    from app.models import DailyProblem

    db.execute(delete(Submission).where(Submission.user_id == user.id, Submission.platform == platform))
    db.execute(delete(DailyProblem).where(DailyProblem.user_id == user.id, DailyProblem.platform == platform))
    db.flush()


def sync_codeforces(db: Session, user: User, handle: str, adapter: PlatformAdapter) -> dict:
    now = datetime.now(timezone.utc)

    # Profile
    profile_data = adapter.fetch_profile(handle)
    profile = db.execute(
        select(CodeforcesProfile).where(CodeforcesProfile.user_id == user.id)
    ).scalar_one_or_none()

    # Switching to a different handle must not merge two people's history —
    # wipe the previous handle's submissions first.
    if profile is not None and profile.handle.lower() != profile_data.handle.lower():
        _reset_platform_submissions(db, user, "codeforces")

    if profile is None:
        profile = CodeforcesProfile(user_id=user.id, handle=handle)
        db.add(profile)
    profile.handle = profile_data.handle
    profile.rating = profile_data.rating
    profile.max_rating = profile_data.max_rating
    profile.rank = profile_data.rank
    profile.max_rank = profile_data.max_rank
    profile.avatar = profile_data.avatar
    profile.last_synced_at = now

    account = db.execute(
        select(PlatformAccount).where(
            PlatformAccount.user_id == user.id, PlatformAccount.platform == "codeforces"
        )
    ).scalar_one_or_none()
    if account is None:
        account = PlatformAccount(user_id=user.id, platform="codeforces", handle=handle)
        db.add(account)
    account.handle = handle
    account.last_synced_at = now

    # Existing state
    existing_ids = set(
        db.execute(
            select(Submission.external_id).where(
                Submission.user_id == user.id, Submission.platform == "codeforces"
            )
        ).scalars()
    )
    solved_before = set(
        db.execute(
            select(Submission.problem_id).where(
                Submission.user_id == user.id, Submission.platform == "codeforces", Submission.verdict == "OK"
            )
        ).scalars()
    )

    problem_cache: dict[str, Problem] = {}

    # Ingest the full problem set once so recommendations have unsolved
    # candidates (guarded — the fake adapter in tests may not provide it).
    if hasattr(adapter, "fetch_problemset"):
        try:
            for np in adapter.fetch_problemset():
                _upsert_problem(db, np, problem_cache)
        except Exception:  # noqa: BLE001 — corpus ingest is best-effort
            pass

    new_submissions = 0
    newly_solved: set[str] = set()

    for ns in adapter.fetch_submissions(handle):
        prob = _upsert_problem(db, ns.problem, problem_cache)
        if ns.external_id in existing_ids:
            continue
        db.add(
            Submission(
                user_id=user.id,
                platform="codeforces",
                external_id=ns.external_id,
                problem_id=prob.id,
                verdict=ns.verdict,
                language=ns.language,
                submitted_at=ns.submitted_at,
                problem_rating=ns.problem.rating,
                problem_tags=ns.problem.tags,
                source_available=ns.source_code is not None,
                source_code=ns.source_code,
            )
        )
        existing_ids.add(ns.external_id)
        new_submissions += 1
        if ns.verdict == "OK" and prob.id not in solved_before:
            newly_solved.add(prob.id)

    db.flush()

    # Refresh the skill snapshot from the newly-synced data.
    from app.services import skills_service

    skills_service.snapshot_today(db, user)

    return {
        "last_synced_at": now.isoformat(),
        "new_submissions": new_submissions,
        "new_solved": len(newly_solved),
    }


def _get_or_create_account(db: Session, user: User, platform: str, handle: str, now: datetime) -> PlatformAccount:
    acc = db.execute(
        select(PlatformAccount).where(PlatformAccount.user_id == user.id, PlatformAccount.platform == platform)
    ).scalar_one_or_none()
    if acc is None:
        acc = PlatformAccount(user_id=user.id, platform=platform, handle=handle)
        db.add(acc)
    acc.handle = handle
    acc.last_synced_at = now
    return acc


def _ingest_submissions(db: Session, user: User, platform: str, subs, cache: dict[str, Problem]) -> dict:
    existing_ids = set(
        db.execute(
            select(Submission.external_id).where(
                Submission.user_id == user.id, Submission.platform == platform
            )
        ).scalars()
    )
    solved_before = set(
        db.execute(
            select(Submission.problem_id).where(
                Submission.user_id == user.id, Submission.platform == platform, Submission.verdict == "OK"
            )
        ).scalars()
    )
    new_submissions, newly_solved = 0, set()
    for ns in subs:
        prob = _upsert_problem(db, ns.problem, cache)
        if ns.external_id in existing_ids:
            continue
        db.add(
            Submission(
                user_id=user.id, platform=platform, external_id=ns.external_id, problem_id=prob.id,
                verdict=ns.verdict, language=ns.language, submitted_at=ns.submitted_at,
                problem_rating=prob.rating, problem_tags=prob.tags or [],
                source_available=ns.source_code is not None, source_code=ns.source_code,
            )
        )
        existing_ids.add(ns.external_id)
        new_submissions += 1
        if ns.verdict == "OK" and prob.id not in solved_before:
            newly_solved.add(prob.id)
    return {"new_submissions": new_submissions, "new_solved": len(newly_solved)}


def sync_leetcode(db: Session, user: User, handle: str, adapter: PlatformAdapter) -> dict:
    from app.services import skills_service
    from app.services.leetcode_seed import SEED

    now = datetime.now(timezone.utc)
    adapter.fetch_profile(handle)  # validates the handle exists
    existing = db.execute(
        select(PlatformAccount).where(PlatformAccount.user_id == user.id, PlatformAccount.platform == "leetcode")
    ).scalar_one_or_none()
    if existing is not None and existing.handle.lower() != handle.lower():
        _reset_platform_submissions(db, user, "leetcode")
    account = _get_or_create_account(db, user, "leetcode", handle, now)

    # Solved counts by difficulty — reliable even when the recent-AC list is empty.
    if hasattr(adapter, "fetch_stats"):
        try:
            account.meta = adapter.fetch_stats(handle)
        except Exception:  # noqa: BLE001
            pass

    cache: dict[str, Problem] = {}
    for np in SEED:  # ensure a real candidate corpus exists
        _upsert_problem(db, np, cache)

    result = _ingest_submissions(db, user, "leetcode", adapter.fetch_submissions(handle), cache)
    db.flush()
    skills_service.snapshot_today(db, user)
    return {"last_synced_at": now.isoformat(), **result}


def import_leetcode_solved(db: Session, user: User, items: list[dict]) -> dict:
    """Manual import fallback: a list of {slug,title,difficulty,tags}."""
    from datetime import datetime as _dt

    from app.services.adapters.leetcode import lc_problem
    from app.services.leetcode_seed import SEED

    now = datetime.now(timezone.utc)
    _get_or_create_account(db, user, "leetcode", user.email.split("@")[0], now)
    cache: dict[str, Problem] = {}
    for np in SEED:
        _upsert_problem(db, np, cache)
    subs = []

    from app.services.adapters.base import NormalizedSubmission

    for i, it in enumerate(items):
        np = lc_problem(it["slug"], it.get("title", it["slug"]), it.get("difficulty", "Medium"), it.get("tags", []))
        subs.append(NormalizedSubmission(f"import-{it['slug']}-{i}", "OK", "", now, np))
    result = _ingest_submissions(db, user, "leetcode", subs, cache)
    db.flush()
    from app.services import skills_service

    skills_service.snapshot_today(db, user)
    return {"last_synced_at": now.isoformat(), **result}
