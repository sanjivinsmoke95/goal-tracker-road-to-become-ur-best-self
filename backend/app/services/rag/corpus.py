"""Curated RAG corpus.

Each entry is an originally-written summary (never copied source text) paired with
the canonical official documentation URL, so retrieved answers can cite a real,
authoritative place to read more. Add entries here and re-index — the store fits
the embedder over whatever is present.

`topic` matches the app's learning categories so retrieval can be scoped.
"""

DOCS: list[dict] = [
    # ---- DSA ----------------------------------------------------------------
    {
        "source": "cp-algorithms",
        "title": "Binary search",
        "url": "https://cp-algorithms.com/num_methods/binary_search.html",
        "topic": "dsa",
        "content": (
            "Binary search finds a target in a sorted array in O(log n) time by repeatedly "
            "halving the search range. Keep two bounds lo and hi; look at the middle; if the "
            "middle value is too small move lo up, otherwise move hi down. The classic pitfalls "
            "are off-by-one errors in the loop condition (lo < hi vs lo <= hi) and computing the "
            "midpoint as lo + (hi - lo) // 2 to avoid overflow. Binary search also generalises to "
            "'search on the answer': when a predicate is monotonic (false, false, ..., true, true) "
            "you can binary-search the boundary, which is common in feasibility problems."
        ),
    },
    {
        "source": "Wikipedia",
        "title": "Time complexity and Big-O notation",
        "url": "https://en.wikipedia.org/wiki/Time_complexity",
        "topic": "dsa",
        "content": (
            "Time complexity describes how an algorithm's running time grows with input size n, "
            "usually expressed with Big-O notation for the worst case. Common classes from fastest "
            "to slowest are O(1) constant, O(log n) logarithmic, O(n) linear, O(n log n), O(n^2) "
            "quadratic, and O(2^n) exponential. On competitive-programming constraints a rough guide "
            "is that about 10^8 simple operations run in a second, so an O(n^2) solution with n = 10^5 "
            "(10^10 operations) will time out, while O(n log n) will pass. Choosing the right data "
            "structure often changes the complexity class and fixes TLE."
        ),
    },
    {
        "source": "cp-algorithms",
        "title": "Breadth-first search (BFS)",
        "url": "https://cp-algorithms.com/graph/breadth-first-search.html",
        "topic": "dsa",
        "content": (
            "Breadth-first search explores a graph level by level using a queue, visiting all "
            "neighbours of a node before going deeper. On an unweighted graph BFS finds the shortest "
            "path (fewest edges) from a source to every reachable node in O(V + E). Mark nodes visited "
            "when you enqueue them, not when you dequeue, to avoid processing a node twice. BFS is the "
            "right tool for shortest-path-on-unweighted-graphs, multi-source spreading, and grid "
            "flood-fill problems."
        ),
    },
    {
        "source": "cp-algorithms",
        "title": "Depth-first search (DFS)",
        "url": "https://cp-algorithms.com/graph/depth-first-search.html",
        "topic": "dsa",
        "content": (
            "Depth-first search follows a path as far as possible before backtracking, using recursion "
            "or an explicit stack. It runs in O(V + E) and underlies cycle detection, topological "
            "sorting, connected components, and bridge/articulation-point algorithms. Watch recursion "
            "depth on large graphs: deep DFS can overflow the call stack, so either raise the recursion "
            "limit or convert to an iterative stack-based version."
        ),
    },
    {
        "source": "cp-algorithms",
        "title": "Dijkstra's shortest paths",
        "url": "https://cp-algorithms.com/graph/dijkstra.html",
        "topic": "dsa",
        "content": (
            "Dijkstra's algorithm finds shortest paths from a source on a graph with non-negative edge "
            "weights. Using a binary heap (priority queue) it runs in O(E log V). Keep a distance array, "
            "repeatedly pop the closest unfinalised node, and relax its edges. Dijkstra does not work "
            "with negative edge weights — use Bellman-Ford (O(VE)) there. For unweighted graphs plain "
            "BFS is faster and simpler."
        ),
    },
    {
        "source": "Wikipedia",
        "title": "Dynamic programming",
        "url": "https://en.wikipedia.org/wiki/Dynamic_programming",
        "topic": "dsa",
        "content": (
            "Dynamic programming solves a problem by breaking it into overlapping subproblems and "
            "storing each subproblem's answer so it is computed once. It applies when the problem has "
            "optimal substructure and overlapping subproblems. Two styles: top-down memoization "
            "(recursion plus a cache) and bottom-up tabulation (fill an array in dependency order). "
            "The key design steps are defining the state, the transition (recurrence), and the base "
            "cases. Start with 1D DP (e.g. climbing stairs, house robber) before 2D DP (grids, knapsack, "
            "edit distance)."
        ),
    },
    # ---- JavaScript (MDN) ---------------------------------------------------
    {
        "source": "MDN",
        "title": "JavaScript closures",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures",
        "topic": "javascript",
        "content": (
            "A closure is a function bundled together with references to the variables from the scope "
            "where it was created, so it keeps access to them even after that outer function returns. "
            "Closures are how JavaScript does private state and factory functions. A classic bug is "
            "capturing a loop variable declared with var (all closures share one binding); using let, "
            "which is block-scoped, gives each iteration its own variable."
        ),
    },
    {
        "source": "MDN",
        "title": "Promises and async/await",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise",
        "topic": "javascript",
        "content": (
            "A Promise represents a value that may be available now, later, or never; it is pending, "
            "then either fulfilled or rejected. Chain work with .then() and handle failures with "
            ".catch(). async/await is syntactic sugar over promises: an async function returns a "
            "promise, and await pauses until a promise settles, letting you write asynchronous code "
            "that reads like synchronous code. Always wrap awaited calls that can fail in try/catch, "
            "and use Promise.all to run independent async work concurrently instead of awaiting in a loop."
        ),
    },
    {
        "source": "MDN",
        "title": "Array methods: map, filter, reduce",
        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array",
        "topic": "javascript",
        "content": (
            "map transforms every element and returns a new array of the same length; filter returns a "
            "new array with only the elements that pass a test; reduce folds an array into a single "
            "accumulated value. All three are non-mutating and return new values, which keeps data flow "
            "predictable in React. Reach for a plain for/for-of loop when you need to break early or the "
            "body has side effects, since map/filter always visit every element."
        ),
    },
    # ---- React (react.dev) --------------------------------------------------
    {
        "source": "React docs",
        "title": "useEffect",
        "url": "https://react.dev/reference/react/useEffect",
        "topic": "react",
        "content": (
            "useEffect lets a component synchronise with an external system (network, subscriptions, "
            "the DOM, timers) after render. It takes an effect function and a dependency array; the "
            "effect re-runs whenever a dependency changes, and runs once on mount when the array is "
            "empty. Return a cleanup function to undo the effect (cancel a request, clear a timer, "
            "unsubscribe) — React runs it before the next effect and on unmount. Most render-derived "
            "values do NOT need an effect; you usually only need one for genuine external side effects. "
            "Missing dependencies cause stale values; an object or array literal in deps changes every "
            "render and causes loops."
        ),
    },
    {
        "source": "React docs",
        "title": "useState",
        "url": "https://react.dev/reference/react/useState",
        "topic": "react",
        "content": (
            "useState declares a piece of state that persists across renders and triggers a re-render "
            "when updated. It returns the current value and a setter. State updates are asynchronous and "
            "batched, so to update based on the previous value pass a function: setCount(c => c + 1). "
            "Never mutate state directly — create a new object or array so React detects the change. "
            "Lifting state up to a common parent is the standard way to share it between components."
        ),
    },
    {
        "source": "React docs",
        "title": "Rules of Hooks",
        "url": "https://react.dev/reference/rules/rules-of-hooks",
        "topic": "react",
        "content": (
            "Hooks must be called at the top level of a React function component or a custom hook, and "
            "in the same order on every render — never inside conditions, loops, or nested functions. "
            "This is how React keeps hook state associated with the right call. Only call hooks from "
            "React functions, not plain JavaScript functions. The eslint-plugin-react-hooks rules "
            "enforce this and also flag missing effect dependencies."
        ),
    },
    # ---- TypeScript ---------------------------------------------------------
    {
        "source": "TypeScript docs",
        "title": "Everyday types",
        "url": "https://www.typescriptlang.org/docs/handbook/2/everyday-types.html",
        "topic": "typescript",
        "content": (
            "TypeScript adds static types on top of JavaScript. Core building blocks are primitives "
            "(string, number, boolean), arrays (number[]), object types, union types (string | number), "
            "and literal types. Prefer interfaces or type aliases to describe object shapes. Enable "
            "strict mode to catch null/undefined bugs early with strictNullChecks. Type inference means "
            "you often do not need explicit annotations on locals; annotate function parameters and "
            "public APIs."
        ),
    },
    {
        "source": "TypeScript docs",
        "title": "Generics",
        "url": "https://www.typescriptlang.org/docs/handbook/2/generics.html",
        "topic": "typescript",
        "content": (
            "Generics let you write reusable code that works over many types while preserving type "
            "information, e.g. function identity<T>(x: T): T. Use them for containers and functions "
            "where the caller's type should flow through to the return value. Constrain a type parameter "
            "with extends (T extends { id: string }) when the code needs certain properties. Generics "
            "are erased at compile time; they add safety without runtime cost."
        ),
    },
    # ---- Python -------------------------------------------------------------
    {
        "source": "Python docs",
        "title": "List comprehensions",
        "url": "https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions",
        "topic": "python",
        "content": (
            "A list comprehension builds a list from an iterable in one expression: "
            "[f(x) for x in items if cond(x)]. It is more readable and usually faster than an "
            "equivalent append loop. There are dict and set comprehensions too. Keep comprehensions "
            "simple — if you need multiple statements, nested logic, or side effects, use a normal loop "
            "for clarity."
        ),
    },
    {
        "source": "Python docs",
        "title": "Generators and yield",
        "url": "https://docs.python.org/3/tutorial/classes.html#generators",
        "topic": "python",
        "content": (
            "A generator is a function that uses yield to produce a lazy stream of values, computing "
            "each only when requested. Generators are memory-efficient for large or infinite sequences "
            "because they hold one item at a time instead of building a whole list. Iterating a "
            "generator consumes it; to reuse the values, materialise them with list(). Generator "
            "expressions (x*x for x in range(n)) are the lazy counterpart of list comprehensions."
        ),
    },
    # ---- FastAPI ------------------------------------------------------------
    {
        "source": "FastAPI docs",
        "title": "Dependencies (Depends)",
        "url": "https://fastapi.tiangolo.com/tutorial/dependencies/",
        "topic": "fastapi",
        "content": (
            "FastAPI's dependency injection shares logic across path operations: declare a dependency "
            "function and receive its result with Depends(). Common uses are database sessions, the "
            "current authenticated user, and shared query parameters. Dependencies can themselves have "
            "dependencies, and can yield to run setup/teardown around the request. Because dependencies "
            "are overridable, tests can inject fakes with app.dependency_overrides, which is how you "
            "test endpoints without a real database or network."
        ),
    },
    {
        "source": "FastAPI docs",
        "title": "Path and query parameters",
        "url": "https://fastapi.tiangolo.com/tutorial/path-params/",
        "topic": "fastapi",
        "content": (
            "Path parameters are parts of the URL path declared with type hints "
            "(@app.get('/items/{item_id}') def read(item_id: int)); FastAPI validates and converts them "
            "automatically. Function parameters that are not in the path become query parameters, with "
            "defaults making them optional. Pydantic models handle request bodies with full validation. "
            "Wrong types return a clear 422 error, so you rarely write manual validation."
        ),
    },
    # ---- SQL ----------------------------------------------------------------
    {
        "source": "PostgreSQL docs",
        "title": "Joins between tables",
        "url": "https://www.postgresql.org/docs/current/tutorial-join.html",
        "topic": "sql",
        "content": (
            "A join combines rows from two tables on a related column. INNER JOIN keeps only rows that "
            "match in both tables; LEFT JOIN keeps every row from the left table and fills NULLs where "
            "the right side has no match. Always state the join condition in ON. Missing or wrong join "
            "conditions produce a cross product (every row paired with every row), which explodes result "
            "size — a common cause of slow queries."
        ),
    },
    {
        "source": "PostgreSQL docs",
        "title": "Indexes",
        "url": "https://www.postgresql.org/docs/current/indexes-intro.html",
        "topic": "sql",
        "content": (
            "An index is a data structure that lets the database find rows without scanning the whole "
            "table, turning a filter or join from O(n) into roughly O(log n). Add an index on columns "
            "used in WHERE clauses, join keys, and ORDER BY. Indexes speed up reads but slow down writes "
            "and use space, so index deliberately. Use EXPLAIN ANALYZE to confirm a query actually uses "
            "an index instead of a sequential scan."
        ),
    },
    # ---- Git ----------------------------------------------------------------
    {
        "source": "Git docs",
        "title": "Branching basics",
        "url": "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell",
        "topic": "git",
        "content": (
            "A branch is a lightweight movable pointer to a commit. Create and switch with "
            "git switch -c feature (or git checkout -b). Work on the branch, commit, then merge back "
            "into main with git merge. Branches make it cheap to isolate features and experiments. "
            "Delete a merged branch with git branch -d. HEAD is the pointer to the branch you are "
            "currently on."
        ),
    },
    {
        "source": "Git docs",
        "title": "Rebase vs merge",
        "url": "https://git-scm.com/docs/git-rebase",
        "topic": "git",
        "content": (
            "git rebase replays your commits on top of another branch, producing a linear history, "
            "whereas git merge creates a merge commit that preserves the branch shape. Rebase to keep a "
            "clean history on your own local branches before sharing; avoid rebasing commits that others "
            "have already pulled, because it rewrites hashes. Resolve conflicts commit-by-commit during "
            "a rebase, then git rebase --continue."
        ),
    },
]
