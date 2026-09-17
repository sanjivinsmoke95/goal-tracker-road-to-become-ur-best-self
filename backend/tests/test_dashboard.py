from tests.conftest import register_and_login


def test_dashboard_requires_auth(client):
    assert client.get("/dashboard").status_code in (401, 403)


def test_dashboard_returns_honest_empty_shell(client):
    headers = register_and_login(client)
    r = client.get("/dashboard", headers=headers)
    assert r.status_code == 200
    body = r.json()

    # No invented numbers: a fresh account has a zero streak and nothing connected.
    assert body["streak"] == 0
    assert body["platforms"]["codeforces"]["connected"] is False
    assert body["platforms"]["leetcode"]["connected"] is False
    assert body["problem_of_the_day"] == {"codeforces": None, "leetcode": None}
    assert body["today_goals"] == []

    # Skill snapshot is explicitly flagged as insufficient data, not faked.
    assert body["skill_snapshot"]["available"] is False
    assert body["skill_snapshot"]["estimated_cf_rating"] is None

    # The DATA / INFERENCE / RECOMMENDATION provenance contract is present.
    assert set(body["provenance"]) == {"data", "inference", "recommendation"}
