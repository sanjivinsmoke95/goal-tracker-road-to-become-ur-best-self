"""Static learning catalogue (Milestone 8).

Content is code, not database rows — it is authored, versioned, and identical
for everyone. Only a user's *progress* is stored per account. Every topic links
to official documentation (never invented URLs).
"""

from __future__ import annotations


def _topic(tid, title, theory, example, exercise, docs):
    return {"id": tid, "title": title, "theory": theory, "example": example, "exercise": exercise, "docs": docs}


REACT = {
    "id": "react",
    "title": "React",
    "modules": [
        {
            "id": "react-foundations",
            "title": "Foundations",
            "topics": [
                _topic(
                    "react-jsx", "JSX",
                    "JSX lets you write markup inside JavaScript. It compiles to React.createElement calls. "
                    "Expressions go in braces; components must return a single root element.",
                    "const el = <h1>Hello, {name}</h1>;",
                    "Render a <ul> with three <li> items built from an array using .map().",
                    [{"title": "React — Writing markup with JSX", "url": "https://react.dev/learn/writing-markup-with-jsx", "source": "react.dev"}],
                ),
                _topic(
                    "react-components", "Components & Props",
                    "Components are functions that return JSX. Props pass data down as read-only inputs.",
                    "function Greeting({ name }) { return <p>Hi {name}</p>; }",
                    "Write a <Card title description> component and render two cards.",
                    [{"title": "React — Passing props to a component", "url": "https://react.dev/learn/passing-props-to-a-component", "source": "react.dev"}],
                ),
                _topic(
                    "react-usestate", "useState",
                    "useState adds local state to a function component. It returns the current value and a setter; "
                    "calling the setter re-renders the component with the new value.",
                    "const [count, setCount] = useState(0);\n<button onClick={() => setCount(count + 1)}>{count}</button>",
                    "Build a counter with + and − buttons that never goes below 0.",
                    [{"title": "React — useState", "url": "https://react.dev/reference/react/useState", "source": "react.dev"}],
                ),
                _topic(
                    "react-useeffect", "useEffect",
                    "useEffect runs side effects after render (data fetching, subscriptions). The dependency array "
                    "controls when it re-runs; return a cleanup function to undo the effect.",
                    "useEffect(() => {\n  const id = setInterval(tick, 1000);\n  return () => clearInterval(id);\n}, []);",
                    "Fetch and display the current time, updating every second, with cleanup.",
                    [{"title": "React — useEffect", "url": "https://react.dev/reference/react/useEffect", "source": "react.dev"}],
                ),
            ],
        },
        {
            "id": "react-data",
            "title": "Data & Routing",
            "topics": [
                _topic(
                    "react-forms", "Forms",
                    "Controlled inputs bind value to state and update it onChange, keeping React the source of truth.",
                    "<input value={q} onChange={e => setQ(e.target.value)} />",
                    "Build a search box that filters a list as you type.",
                    [{"title": "MDN — HTML forms", "url": "https://developer.mozilla.org/en-US/docs/Learn/Forms", "source": "MDN"}],
                ),
                _topic(
                    "react-routing", "Routing",
                    "React Router maps URLs to components with <Routes>/<Route> and navigates via <Link>.",
                    "<Routes><Route path=\"/about\" element={<About/>} /></Routes>",
                    "Add a two-page app (Home, About) with a nav bar using <Link>.",
                    [{"title": "React Router — Tutorial", "url": "https://reactrouter.com/en/main/start/tutorial", "source": "reactrouter.com"}],
                ),
            ],
        },
    ],
}

BACKEND = {
    "id": "backend",
    "title": "Backend",
    "modules": [
        {
            "id": "backend-web",
            "title": "The Web",
            "topics": [
                _topic(
                    "be-http", "HTTP",
                    "HTTP is a request/response protocol. A request has a method (GET/POST/…), path, headers and body; "
                    "a response has a status code, headers and body.",
                    "GET /users/1 HTTP/1.1\nHost: api.example.com",
                    "List the meanings of status codes 200, 201, 400, 401, 404, 500.",
                    [{"title": "MDN — HTTP overview", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview", "source": "MDN"}],
                ),
                _topic(
                    "be-rest", "REST APIs",
                    "REST models resources as URLs and uses HTTP methods for actions: GET (read), POST (create), "
                    "PUT/PATCH (update), DELETE. Responses are usually JSON.",
                    "POST /goals   {\"title\": \"Solve CF problem\"}  → 201 Created",
                    "Design REST endpoints for a to-do list (CRUD).",
                    [{"title": "MDN — REST glossary", "url": "https://developer.mozilla.org/en-US/docs/Glossary/REST", "source": "MDN"}],
                ),
                _topic(
                    "be-fastapi", "FastAPI basics",
                    "FastAPI builds typed APIs from Python type hints, with automatic validation (Pydantic) and docs.",
                    "@app.get('/health')\ndef health(): return {'status': 'ok'}",
                    "Add a POST endpoint that validates a body with a Pydantic model.",
                    [{"title": "FastAPI — First steps", "url": "https://fastapi.tiangolo.com/tutorial/first-steps/", "source": "fastapi.tiangolo.com"}],
                ),
            ],
        },
        {
            "id": "backend-data",
            "title": "Data & Auth",
            "topics": [
                _topic(
                    "be-postgres", "PostgreSQL",
                    "A relational database stores rows in typed tables. SQL queries read/write data; indexes speed reads; "
                    "foreign keys enforce relationships.",
                    "SELECT title FROM goals WHERE user_id = $1 ORDER BY created_at;",
                    "Write SQL to count completed goals per day for one user.",
                    [{"title": "PostgreSQL — Tutorial", "url": "https://www.postgresql.org/docs/current/tutorial.html", "source": "postgresql.org"}],
                ),
                _topic(
                    "be-jwt", "Auth & JWT",
                    "A JWT is a signed token carrying claims (e.g. the user id). The server verifies the signature to "
                    "authenticate requests without server-side sessions.",
                    "Authorization: Bearer <header>.<payload>.<signature>",
                    "Explain why the token is signed but not encrypted, and what that implies.",
                    [{"title": "jwt.io — Introduction to JWT", "url": "https://jwt.io/introduction", "source": "jwt.io"}],
                ),
            ],
        },
    ],
}

PATHS = {p["id"]: p for p in [REACT, BACKEND]}


def all_paths() -> list[dict]:
    # Summaries (no heavy content) for the index.
    return [
        {
            "id": p["id"],
            "title": p["title"],
            "modules": [
                {"id": m["id"], "title": m["title"], "topics": [{"id": t["id"], "title": t["title"]} for t in m["topics"]]}
                for m in p["modules"]
            ],
            "topic_count": sum(len(m["topics"]) for m in p["modules"]),
        }
        for p in PATHS.values()
    ]


def get_topic(topic_id: str) -> dict | None:
    for p in PATHS.values():
        for m in p["modules"]:
            for t in m["topics"]:
                if t["id"] == topic_id:
                    return {**t, "path": p["id"], "module": m["id"]}
    return None


def all_topic_ids() -> list[str]:
    return [t["id"] for p in PATHS.values() for m in p["modules"] for t in m["topics"]]
