from tests.conftest import register_and_login


def test_learning_paths_and_topic(client):
    h = register_and_login(client)
    paths = client.get("/learning/paths", headers=h).json()
    ids = {p["id"] for p in paths["paths"]}
    # Core paths plus the expanded catalogue (DSA, JS, TS, Python, SQL, Git).
    assert {"react", "backend", "dsa", "javascript", "typescript", "python", "sql", "git"} <= ids
    assert paths["total"] > 0

    t = client.get("/learning/topics/react-usestate", headers=h).json()
    assert t["title"] == "useState"
    assert t["docs"][0]["url"].startswith("https://react.dev")
    assert t["completed"] is False


def test_complete_topic_toggles_and_counts(client):
    h = register_and_login(client)
    r = client.post("/learning/topics/react-jsx/complete", headers=h).json()
    assert r["completed"] is True
    assert client.get("/learning/paths", headers=h).json()["completed_count"] == 1
    # toggle off
    r = client.post("/learning/topics/react-jsx/complete", headers=h).json()
    assert r["completed"] is False


def test_unknown_topic_404(client):
    h = register_and_login(client)
    assert client.get("/learning/topics/nope", headers=h).status_code == 404


def test_code_run_python(client):
    h = register_and_login(client)
    r = client.post("/code/run", json={"language": "python", "code": "print(2 + 40)"}, headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["stdout"].strip() == "42"
    assert body["timed_out"] is False


def test_code_run_unsupported_language(client):
    h = register_and_login(client)
    assert client.post("/code/run", json={"language": "brainfuck", "code": ""}, headers=h).status_code == 422


def test_tutor_hint_is_progressive(client):
    h = register_and_login(client)
    r = client.post("/tutor/hint", json={"tags": ["dp"], "level": 2}, headers=h).json()
    assert 1 <= len(r["hints"]) <= 2
    assert r["solution"] is None  # never reveals the full solution by default


def test_progress_endpoint(client):
    h = register_and_login(client)
    for r in ("daily", "weekly", "monthly"):
        body = client.get(f"/progress?range={r}", headers=h).json()
        assert body["range"] == r
        assert "goals_completed" in body["totals"]
        assert len(body["series"]) >= 1
