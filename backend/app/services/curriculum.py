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

DSA = {
    "id": "dsa",
    "title": "DSA",
    "modules": [
        {
            "id": "dsa-core",
            "title": "Core techniques",
            "topics": [
                _topic(
                    "dsa-complexity", "Big-O & complexity",
                    "Big-O describes how running time grows with input size n. Know the ladder: O(1), "
                    "O(log n), O(n), O(n log n), O(n^2), O(2^n). Rule of thumb: ~10^8 simple ops per second, "
                    "so O(n^2) with n=10^5 will TLE while O(n log n) passes.",
                    "# n = 10^5 → O(n^2) ≈ 10^10 ops → too slow\nfor i in range(n):\n    for j in range(n):\n        ...",
                    "Given n ≤ 2·10^5, decide whether an O(n^2) or O(n log n) approach is required.",
                    [{"title": "Time complexity", "url": "https://en.wikipedia.org/wiki/Time_complexity", "source": "Wikipedia"}],
                ),
                _topic(
                    "dsa-binary-search", "Binary search",
                    "On a sorted array, halve the search range each step for O(log n). Generalises to "
                    "'binary search on the answer' when a predicate is monotonic (false…false,true…true).",
                    "lo, hi = 0, len(a)-1\nwhile lo <= hi:\n    mid = (lo+hi)//2\n    if a[mid] == x: return mid\n    if a[mid] < x: lo = mid+1\n    else: hi = mid-1",
                    "Find the first index where a[i] >= x (lower_bound) without using library bisect.",
                    [{"title": "Binary search", "url": "https://cp-algorithms.com/num_methods/binary_search.html", "source": "cp-algorithms"}],
                ),
                _topic(
                    "dsa-graphs", "BFS & DFS",
                    "BFS explores level by level with a queue and gives shortest paths on unweighted graphs "
                    "in O(V+E); DFS goes deep with recursion/stack and powers cycle detection and topological "
                    "sort. Mark visited on enqueue (BFS) to avoid reprocessing.",
                    "from collections import deque\nq = deque([src]); seen = {src}\nwhile q:\n    u = q.popleft()\n    for v in adj[u]:\n        if v not in seen: seen.add(v); q.append(v)",
                    "Count connected components in an undirected graph using BFS or DFS.",
                    [{"title": "Breadth-first search", "url": "https://cp-algorithms.com/graph/breadth-first-search.html", "source": "cp-algorithms"}],
                ),
                _topic(
                    "dsa-dp", "Dynamic programming",
                    "DP solves problems with overlapping subproblems and optimal substructure by storing each "
                    "subproblem's answer once. Define the state, the transition, and base cases. Start with 1D "
                    "(climbing stairs, house robber) before 2D (grids, knapsack, edit distance).",
                    "dp = [0]*(n+1); dp[1] = 1\nfor i in range(2, n+1):\n    dp[i] = dp[i-1] + dp[i-2]",
                    "Compute the number of ways to climb n stairs taking 1 or 2 steps (bottom-up).",
                    [{"title": "Dynamic programming", "url": "https://en.wikipedia.org/wiki/Dynamic_programming", "source": "Wikipedia"}],
                ),
            ],
        },
    ],
}

JAVASCRIPT = {
    "id": "javascript",
    "title": "JavaScript",
    "modules": [
        {
            "id": "js-core",
            "title": "Language essentials",
            "topics": [
                _topic(
                    "js-closures", "Closures",
                    "A closure is a function plus references to variables from where it was defined, so it "
                    "keeps access to them after the outer function returns. Basis of private state. Use let "
                    "(block-scoped) in loops to avoid the shared-var capture bug.",
                    "function counter(){ let n = 0; return () => ++n; }\nconst next = counter(); next(); // 1",
                    "Write makeAdder(x) that returns a function adding x to its argument.",
                    [{"title": "MDN — Closures", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures", "source": "MDN"}],
                ),
                _topic(
                    "js-async", "Promises & async/await",
                    "A Promise is a value available now, later, or never (pending → fulfilled/rejected). async "
                    "functions return promises; await pauses until one settles. Use Promise.all for independent "
                    "work; wrap awaits that can fail in try/catch.",
                    "async function load(){\n  try { const r = await fetch(url); return await r.json(); }\n  catch(e){ console.error(e); }\n}",
                    "Fetch two URLs concurrently with Promise.all and log both results.",
                    [{"title": "MDN — Promise", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise", "source": "MDN"}],
                ),
                _topic(
                    "js-arrays", "map / filter / reduce",
                    "map transforms each element (same length); filter keeps elements passing a test; reduce "
                    "folds to a single value. All are non-mutating. Use a plain loop when you need to break early.",
                    "const evens = nums.filter(n => n % 2 === 0);\nconst sum = nums.reduce((a, b) => a + b, 0);",
                    "From an array of {name, price}, compute the total price with reduce.",
                    [{"title": "MDN — Array", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array", "source": "MDN"}],
                ),
            ],
        },
    ],
}

TYPESCRIPT = {
    "id": "typescript",
    "title": "TypeScript",
    "modules": [
        {
            "id": "ts-core",
            "title": "Types",
            "topics": [
                _topic(
                    "ts-types", "Everyday types",
                    "TypeScript adds static types over JavaScript: primitives, arrays (number[]), object types, "
                    "unions (string | number), and literals. Turn on strict mode for null-safety; annotate "
                    "function parameters and public APIs, and let inference handle locals.",
                    "type User = { id: string; age?: number };\nfunction greet(u: User): string { return `Hi ${u.id}`; }",
                    "Type a function that takes (string | number) and returns its string length or value.",
                    [{"title": "TypeScript — Everyday types", "url": "https://www.typescriptlang.org/docs/handbook/2/everyday-types.html", "source": "TypeScript"}],
                ),
                _topic(
                    "ts-generics", "Generics",
                    "Generics write reusable code over many types while preserving type info: function id<T>(x: T): T. "
                    "Constrain with extends when you need certain properties. Erased at compile time — safety with "
                    "no runtime cost.",
                    "function first<T>(xs: T[]): T | undefined { return xs[0]; }",
                    "Write a generic wrapInArray<T>(x: T): T[] and use it with two different types.",
                    [{"title": "TypeScript — Generics", "url": "https://www.typescriptlang.org/docs/handbook/2/generics.html", "source": "TypeScript"}],
                ),
            ],
        },
    ],
}

PYTHON = {
    "id": "python",
    "title": "Python",
    "modules": [
        {
            "id": "py-core",
            "title": "Pythonic essentials",
            "topics": [
                _topic(
                    "py-comprehensions", "Comprehensions",
                    "A comprehension builds a collection in one expression: [f(x) for x in items if cond(x)]. "
                    "There are dict and set versions too. Keep them simple; use a loop when logic gets complex.",
                    "squares = [x*x for x in range(10) if x % 2 == 0]",
                    "Build a dict mapping each word in a list to its length using a dict comprehension.",
                    [{"title": "Python — List comprehensions", "url": "https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions", "source": "Python docs"}],
                ),
                _topic(
                    "py-generators", "Generators & yield",
                    "A generator uses yield to produce a lazy stream, computing each value on demand — memory "
                    "efficient for large/infinite sequences. Iterating consumes it; materialise with list() to reuse.",
                    "def firstn(n):\n    i = 0\n    while i < n:\n        yield i; i += 1",
                    "Write a generator that yields the Fibonacci numbers up to a limit.",
                    [{"title": "Python — Generators", "url": "https://docs.python.org/3/tutorial/classes.html#generators", "source": "Python docs"}],
                ),
            ],
        },
    ],
}

SQL = {
    "id": "sql",
    "title": "SQL",
    "modules": [
        {
            "id": "sql-core",
            "title": "Querying",
            "topics": [
                _topic(
                    "sql-joins", "Joins",
                    "A join combines rows from two tables on a related column. INNER JOIN keeps only matches; "
                    "LEFT JOIN keeps all left rows (NULLs where no match). Always specify the ON condition or you "
                    "get a cartesian explosion.",
                    "SELECT u.name, o.total\nFROM users u\nJOIN orders o ON o.user_id = u.id;",
                    "Write a query listing every user and their order count, including users with zero orders.",
                    [{"title": "PostgreSQL — Joins", "url": "https://www.postgresql.org/docs/current/tutorial-join.html", "source": "PostgreSQL"}],
                ),
                _topic(
                    "sql-indexes", "Indexes",
                    "An index lets the DB find rows without scanning the whole table, turning a filter/join from "
                    "O(n) into ~O(log n). Index WHERE columns, join keys, and ORDER BY. They cost write speed and "
                    "space — use EXPLAIN ANALYZE to confirm one is used.",
                    "CREATE INDEX idx_orders_user ON orders(user_id);\nEXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 7;",
                    "Add an index that speeds up a query filtering orders by status and date.",
                    [{"title": "PostgreSQL — Indexes", "url": "https://www.postgresql.org/docs/current/indexes-intro.html", "source": "PostgreSQL"}],
                ),
            ],
        },
    ],
}

GIT = {
    "id": "git",
    "title": "Git",
    "modules": [
        {
            "id": "git-core",
            "title": "Everyday Git",
            "topics": [
                _topic(
                    "git-branching", "Branching",
                    "A branch is a movable pointer to a commit. Create/switch with git switch -c feature, commit, "
                    "then merge back into main. Branches make features and experiments cheap to isolate; HEAD "
                    "points at your current branch.",
                    "git switch -c feature\n# ...commit work...\ngit switch main\ngit merge feature",
                    "Create a branch, make a commit, and merge it back into main.",
                    [{"title": "Git — Branching in a nutshell", "url": "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell", "source": "Git docs"}],
                ),
                _topic(
                    "git-rebase", "Rebase vs merge",
                    "git rebase replays your commits for a linear history; git merge preserves branch shape with a "
                    "merge commit. Rebase local branches before sharing; never rebase commits others have pulled "
                    "(it rewrites hashes).",
                    "git switch feature\ngit rebase main   # replay feature on top of main",
                    "Rebase a feature branch onto an updated main and resolve any conflict.",
                    [{"title": "Git — git-rebase", "url": "https://git-scm.com/docs/git-rebase", "source": "Git docs"}],
                ),
            ],
        },
    ],
}

PATHS = {p["id"]: p for p in [DSA, JAVASCRIPT, TYPESCRIPT, REACT, BACKEND, PYTHON, SQL, GIT]}


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
