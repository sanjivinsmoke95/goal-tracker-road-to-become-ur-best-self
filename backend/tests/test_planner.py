from datetime import date, timedelta

from app.services import planner_service
from app.services.planner_service import parse_paste
from tests.conftest import register_and_login


# --- Pure parsing / scheduling logic --------------------------------------
def test_parse_paste_extracts_category_and_priority():
    items = parse_paste(
        """
        Solve 2 LeetCode mediums
        lc: Two Sum follow-up
        [high] Revise segment trees
        - cf | Div 2 virtual
        \t
        """
    )
    titles = [i["title"] for i in items]
    assert "Solve 2 LeetCode mediums" in titles
    assert {"title": "Two Sum follow-up", "category": "lc", "priority": "medium", "estimated_minutes": 0} in items
    high = next(i for i in items if i["title"] == "Revise segment trees")
    assert high["priority"] == "high"
    cf = next(i for i in items if i["title"] == "Div 2 virtual")
    assert cf["category"] == "cf"
    assert len(items) == 4  # blank lines dropped


class _R:
    def __init__(self, frequency, days, active=True):
        self.frequency, self.days_of_week, self.active = frequency, days, active


def test_applies_on_by_frequency():
    monday = date(2026, 9, 21)  # a Monday
    saturday = date(2026, 9, 26)
    assert planner_service.applies_on(_R("daily", []), saturday)
    assert planner_service.applies_on(_R("weekdays", []), monday)
    assert not planner_service.applies_on(_R("weekdays", []), saturday)
    assert planner_service.applies_on(_R("custom", [5]), saturday)  # Sat=5
    assert not planner_service.applies_on(_R("custom", [0]), saturday)
    assert not planner_service.applies_on(_R("daily", [], active=False), monday)


# --- Bulk / paste API -----------------------------------------------------
def test_bulk_add_shows_up_in_day(client):
    h = register_and_login(client)
    r = client.post("/planner/tasks/bulk", json={"tasks": [
        {"title": "Read FastAPI docs", "category": "backend"},
        {"title": "1 CF problem", "category": "cf", "priority": "high"},
    ]}, headers=h)
    assert r.status_code == 201
    assert {t["source"] for t in r.json()} == {"upload"}

    day = client.get("/planner/day", headers=h).json()
    assert day["total"] == 2
    assert day["completed"] == 0
    assert {t["title"] for t in day["tasks"]} == {"Read FastAPI docs", "1 CF problem"}


def test_paste_endpoint_parses_lines(client):
    h = register_and_login(client)
    r = client.post("/planner/tasks/paste", json={"text": "lc: Two Sum\n[high] segment trees"}, headers=h)
    assert r.status_code == 201
    made = r.json()
    assert len(made) == 2
    assert {m["category"] for m in made} == {"lc", "other"}


# --- Routines -------------------------------------------------------------
def test_daily_routine_materializes_once_per_day(client):
    h = register_and_login(client)
    client.post("/planner/routines", json={
        "title": "Solve 1 LeetCode", "category": "lc", "frequency": "daily",
    }, headers=h)

    # First open of the day creates the task…
    day1 = client.get("/planner/day", headers=h).json()
    routine_tasks = [t for t in day1["tasks"] if t["source"] == "routine"]
    assert len(routine_tasks) == 1
    assert routine_tasks[0]["title"] == "Solve 1 LeetCode"

    # …opening again does NOT duplicate it.
    day2 = client.get("/planner/day", headers=h).json()
    assert len([t for t in day2["tasks"] if t["source"] == "routine"]) == 1


def test_routine_does_not_fabricate_past_days(client):
    h = register_and_login(client)
    client.post("/planner/routines", json={"title": "Daily thing", "frequency": "daily"}, headers=h)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    day = client.get(f"/planner/day?date={yesterday}", headers=h).json()
    assert day["total"] == 0  # nothing materialised for the past


def test_delete_routine_keeps_its_task_but_cuts_link(client):
    h = register_and_login(client)
    rid = client.post("/planner/routines", json={"title": "Stretch", "frequency": "daily"}, headers=h).json()["id"]
    client.get("/planner/day", headers=h)  # materialise
    client.delete(f"/planner/routines/{rid}", headers=h)

    day = client.get("/planner/day", headers=h).json()
    stretch = [t for t in day["tasks"] if t["title"] == "Stretch"]
    assert len(stretch) == 1  # task survives
    assert stretch[0]["routine_id"] is None  # link cut → won't be re-created either


# --- Missed carry-over ----------------------------------------------------
def test_missed_move_and_dismiss(client):
    h = register_and_login(client)
    today = date.today()
    y = (today - timedelta(days=1)).isoformat()
    # Two tasks left open yesterday.
    g1 = client.post("/goals", json={"title": "Unfinished A", "date": y}, headers=h).json()
    g2 = client.post("/goals", json={"title": "Unfinished B", "date": y}, headers=h).json()

    missed = client.get("/planner/missed", headers=h).json()["tasks"]
    assert {m["title"] for m in missed} == {"Unfinished A", "Unfinished B"}

    # Move A to today; dismiss B.
    moved = client.post(f"/planner/missed/{g1['id']}/move", headers=h).json()
    assert moved["date"] == today.isoformat()
    assert moved["source"] == "carried"
    assert moved["carried_from"] == y

    dismissed = client.post(f"/planner/missed/{g2['id']}/dismiss", headers=h).json()
    assert dismissed["status"] == "skipped"

    # Neither is "missed" any more: A is today, B is skipped.
    assert client.get("/planner/missed", headers=h).json()["tasks"] == []
    day = client.get("/planner/day", headers=h).json()
    assert "Unfinished A" in {t["title"] for t in day["tasks"]}


def test_planner_is_per_user(client):
    h1 = register_and_login(client, email="a@example.com")
    h2 = register_and_login(client, email="b@example.com")
    client.post("/planner/tasks/bulk", json={"tasks": [{"title": "A's task"}]}, headers=h1)
    assert client.get("/planner/day", headers=h2).json()["total"] == 0
