from datetime import datetime, timezone

from app.api.deps import get_cf_adapter
from app.main import app
from app.services.adapters.base import NormalizedProblem, NormalizedProfile, NormalizedSubmission
from tests.conftest import register_and_login


def _sub(ext, rating, tags, verdict):
    return NormalizedSubmission(
        external_id=ext, verdict=verdict, language="c++",
        submitted_at=datetime.now(timezone.utc),
        problem=NormalizedProblem(platform="codeforces", external_id=ext, name=f"P{ext}",
                                  contest_id=int(ext[:-1]), index=ext[-1], rating=rating, tags=tags,
                                  url=f"https://codeforces.com/x/{ext}"),
    )


class _Fake:
    platform = "codeforces"

    def __init__(self, subs):
        self._subs = subs

    def fetch_profile(self, handle):
        return NormalizedProfile(handle=handle, rating=1400, max_rating=1500, rank="specialist", max_rank="specialist")

    def fetch_submissions(self, handle):
        return list(self._subs)


def _connect(client, headers, subs, handle):
    app.dependency_overrides[get_cf_adapter] = lambda: _Fake(subs)
    r = client.post("/platforms/codeforces/connect", json={"handle": handle}, headers=headers)
    assert r.status_code == 200


# A is strong in arrays, weak in binary search. B is the mirror image.
A_SUBS = (
    [_sub(f"{100+i}A", 1200, ["arrays"], "OK") for i in range(3)]
    + [_sub("200B", 1300, ["binary search"], "OK")]
    + [_sub(f"{210+i}B", 1300, ["binary search"], "WRONG_ANSWER") for i in range(3)]
)
B_SUBS = (
    [_sub(f"{300+i}A", 1300, ["binary search"], "OK") for i in range(3)]
    + [_sub("400B", 1200, ["arrays"], "OK")]
    + [_sub(f"{410+i}B", 1200, ["arrays"], "WRONG_ANSWER") for i in range(3)]
)


def _befriend(client, ha, hb):
    r = client.post("/friends/request", json={"email": "b@example.com"}, headers=ha)
    assert r.status_code == 201
    fid = r.json()["id"]
    assert client.post(f"/friends/{fid}/accept", headers=hb).status_code == 200
    return fid


def test_full_friend_compare_flow(client):
    ha = register_and_login(client, email="a@example.com")
    hb = register_and_login(client, email="b@example.com")
    _connect(client, ha, A_SUBS, "alice")
    _connect(client, hb, B_SUBS, "bob")

    # B's user id (for the compare endpoint).
    b_id = client.get("/auth/me", headers=hb).json()["id"]

    # Not friends yet → comparison is forbidden.
    assert client.get(f"/friends/{b_id}/compare", headers=ha).status_code == 403

    _befriend(client, ha, hb)
    assert {f["email"] for f in client.get("/friends", headers=ha).json()} == {"b@example.com"}

    cmp = client.get(f"/friends/{b_id}/compare", headers=ha).json()
    assert "arrays" in cmp["your_strengths"]
    assert "binary search" in cmp["friend_strengths"]
    # A is weaker at binary search → it's A's growth area, and A is stronger at arrays.
    assert "binary search" in {g["topic"] for g in cmp["your_growth_areas"]}
    assert "arrays" in {g["topic"] for g in cmp["friend_growth_areas"]}
    # Neutral report with concrete actions, no overall "winner".
    assert cmp["report"] and all("suggested_action" in r for r in cmp["report"])
    assert "winner" not in cmp


def test_comparison_respects_consent(client):
    ha = register_and_login(client, email="a@example.com")
    hb = register_and_login(client, email="b@example.com")
    _connect(client, ha, A_SUBS, "alice")
    _connect(client, hb, B_SUBS, "bob")
    b_id = client.get("/auth/me", headers=hb).json()["id"]
    _befriend(client, ha, hb)

    # B turns off comparison → A can no longer compare.
    assert client.put("/preferences", json={"allow_comparison": False}, headers=hb).status_code == 200
    assert client.get(f"/friends/{b_id}/compare", headers=ha).status_code == 403


def test_request_to_unknown_email_404(client):
    ha = register_and_login(client, email="a@example.com")
    assert client.post("/friends/request", json={"email": "nobody@example.com"}, headers=ha).status_code == 404


def test_mutual_request_auto_accepts(client):
    ha = register_and_login(client, email="a@example.com")
    hb = register_and_login(client, email="b@example.com")
    client.post("/friends/request", json={"email": "b@example.com"}, headers=ha)
    # B requesting A back should connect them immediately.
    r = client.post("/friends/request", json={"email": "a@example.com"}, headers=hb)
    assert r.json()["status"] == "accepted"


def test_preferences_get_and_update(client):
    h = register_and_login(client)
    prefs = client.get("/preferences", headers=h).json()
    assert prefs["allow_comparison"] is True and prefs["daily_problems"] == 2

    updated = client.put("/preferences", json={
        "target_cf_rating": 1600, "daily_problems": 4, "technologies": ["react", "python"],
        "desired_difficulty": "challenge",
    }, headers=h).json()
    assert updated["target_cf_rating"] == 1600
    assert updated["daily_problems"] == 4
    assert updated["technologies"] == ["react", "python"]
