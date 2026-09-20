"""Static code analysis: a deterministic first pass (complexity + findings) that
does NOT depend on an LLM, optionally enriched with an AI review and a
RAG-grounded answer to a free-form question.

The deterministic estimates are explicitly labelled as heuristics (INFERENCE),
never presented as ground truth — they are computed from the code's structure
(loop nesting, sorts, recursion, allocations), which is real signal without
running the code or calling a model.
"""

from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.services.ai import get_provider

_SORT_RE = re.compile(r"\b(sorted|sort|nlargest|nsmallest)\s*\(|\.sort\s*\(|std::sort", re.I)
_STRUCT_RE = re.compile(
    r"\b(list|dict|set|vector|map|unordered_map|unordered_set|deque|array|new\s+\w+\[)\b|[\[\{]", re.I
)
_PY_COMMENT = re.compile(r"#.*$", re.M)
_C_COMMENT = re.compile(r"//.*$|/\*.*?\*/", re.M | re.S)
_STRING = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'")


def _strip_noise(code: str, language: str) -> str:
    code = _STRING.sub('""', code)
    code = (_PY_COMMENT if language == "python" else _C_COMMENT).sub("", code)
    return code


def max_loop_nesting(code: str, language: str) -> int:
    """Deepest nesting of for/while loops. Indentation-based for Python, brace-based
    for C-like languages. Braceless single-statement loops are not counted (a known,
    acceptable limitation of a static heuristic)."""
    code = _strip_noise(code, language)
    if language == "python":
        active: list[int] = []
        deepest = 0
        for raw in code.splitlines():
            stripped = raw.lstrip()
            if not stripped:
                continue
            indent = len(raw) - len(stripped)
            while active and indent <= active[-1]:
                active.pop()
            if re.match(r"(for|while)\b", stripped):
                active.append(indent)
                deepest = max(deepest, len(active))
        return deepest
    # Brace languages.
    pending = False
    stack: list[bool] = []
    deepest = 0
    for tok in re.finditer(r"\bfor\b|\bwhile\b|\{|\}", code):
        t = tok.group()
        if t in ("for", "while"):
            pending = True
        elif t == "{":
            stack.append(pending)
            pending = False
            deepest = max(deepest, sum(1 for x in stack if x))
        elif t == "}" and stack:
            stack.pop()
    return deepest


def has_recursion(code: str, language: str) -> bool:
    code = _strip_noise(code, language)
    if language == "python":
        names = re.findall(r"def\s+(\w+)\s*\(", code)
    else:
        names = re.findall(r"\b\w+\s+(\w+)\s*\([^;]*\)\s*\{", code)
    for name in set(names):
        # Called somewhere other than its own definition line.
        calls = len(re.findall(rf"\b{name}\s*\(", code))
        if calls >= 2:
            return True
    return False


def estimate_complexity(code: str, language: str) -> dict:
    nesting = max_loop_nesting(code, language)
    sorts = bool(_SORT_RE.search(_strip_noise(code, language)))
    recursion = has_recursion(code, language)
    allocs = bool(_STRUCT_RE.search(_strip_noise(code, language)))

    reasons: list[str] = []
    if nesting >= 2:
        time = f"O(n^{nesting})"
        reasons.append(f"{nesting} nested loops")
    elif nesting == 1 and sorts:
        time = "O(n log n)"
        reasons.append("a single loop plus a sort (the sort dominates)")
    elif sorts and nesting == 0:
        time = "O(n log n)"
        reasons.append("a sort with no dominating loop")
    elif nesting == 1:
        time = "O(n)"
        reasons.append("a single loop")
    elif recursion:
        time = "O(?) — recursive"
        reasons.append("recursion whose cost depends on the recurrence (add memoization if subproblems repeat)")
    else:
        time = "O(1)"
        reasons.append("no loops detected")

    if recursion and nesting < 2:
        space = "O(depth) — recursion stack"
    elif allocs:
        space = "O(n) — stores data in a collection"
    else:
        space = "O(1)"

    return {
        "time": time,
        "space": space,
        "reason": "Estimated from " + ", ".join(reasons) + ".",
        "loop_nesting": nesting,
        "uses_sort": sorts,
        "uses_recursion": recursion,
        "estimate": True,  # this is a heuristic, not a proof
    }


def static_findings(code: str, language: str, constraints: str = "") -> list[dict]:
    findings: list[dict] = []
    clean = _strip_noise(code, language)
    nesting = max_loop_nesting(code, language)
    big_constraints = bool(re.search(r"10\s*\^\s*([5-9]|1[0-9])|1[eE]\+?0*[5-9]|[1-9]\d{5,}", constraints or ""))

    if nesting >= 2:
        sev = "high" if big_constraints else "medium"
        note = "Nested loops give quadratic-or-worse time"
        if big_constraints:
            note += " — with the stated constraints this will likely TLE. Consider hashing, sorting, two pointers, or a better data structure."
        else:
            note += ". Check it fits the constraints; if n can be large, look for a near-linear approach."
        findings.append({"type": "complexity", "severity": sev, "note": note})

    if language == "cpp":
        if re.search(r"\bint\b", clean) and "*" in clean and "long long" not in clean:
            findings.append({
                "type": "overflow",
                "severity": "high",
                "note": "Multiplying int values can overflow (>2.1e9). Use long long for products/sums that can grow.",
            })
        if "endl" in clean:
            findings.append({
                "type": "io_performance",
                "severity": "low",
                "note": "endl flushes the buffer every call; prefer '\\n' and add ios::sync_with_stdio(false) for fast IO.",
            })
    if language == "python":
        if re.search(r"for .+:\s*\n\s*.*input\(", code):
            findings.append({
                "type": "io_performance",
                "severity": "medium",
                "note": "Calling input() inside a loop is slow; read all input once via sys.stdin for large cases.",
            })
        if re.search(r"\+\s*str\(|\bstr\b.*\+.*in\b", code) and "join" not in code and nesting >= 1:
            findings.append({
                "type": "efficiency",
                "severity": "low",
                "note": "Building a string with repeated + in a loop is O(n^2); collect parts in a list and ''.join() them.",
            })
    if has_recursion(code, language) and "memo" not in clean.lower() and "cache" not in clean.lower():
        findings.append({
            "type": "algorithm",
            "severity": "medium",
            "note": "Recursion without memoization can recompute subproblems exponentially. If subproblems repeat, memoize or use bottom-up DP.",
        })
    return findings


def analyze(db: Session, payload: dict) -> dict:
    """Full analysis: deterministic complexity + findings, an AI review, and — when
    a question is asked — a RAG-grounded answer with citations."""
    language = (payload.get("language") or "python").lower()
    code = payload.get("code") or ""
    constraints = payload.get("constraints") or ""
    verdict = payload.get("verdict") or ""
    question = (payload.get("question") or "").strip()

    complexity = estimate_complexity(code, language)
    findings = static_findings(code, language, constraints)

    provider = get_provider()
    review = provider.review_code(
        {"language": language, "code": code, "verdict": verdict,
         "problem": payload.get("problem_statement", ""), "constraints": constraints}
    )

    result = {
        "complexity": complexity,
        "findings": findings,
        "review": review,
        "answer": None,
        "sources": [],
        "llm": provider.name if getattr(provider, "available", False) and provider.name != "stub" else "heuristic",
    }

    if question:
        from app.services.rag import store as rag_store

        # Self-heal the index on a fresh DB, then retrieve documentation relevant
        # to the question and let the provider answer using both the retrieved
        # docs and the user's code as context.
        if rag_store.status(db)["indexed_chunks"] == 0:
            rag_store.reindex(db)
        hits = rag_store.retrieve(db, f"{question} {constraints}", k=4, topic="dsa")
        context = hits + [{
            "title": "Your code", "source": "submission", "url": "",
            "content": f"Language: {language}. Verdict: {verdict or 'unknown'}. "
                       f"Estimated {complexity['time']} time. Code:\n{code[:3000]}",
            "score": 1.0,
        }]
        result["answer"] = provider.answer_with_context(question, context)
        result["sources"] = [
            {"title": h["title"], "source": h["source"], "url": h["url"], "score": h["score"]} for h in hits
        ]
    return result
