"""Deterministic stand-in provider — the app is fully usable with no API key.

Its output is templated from real inputs (score breakdowns, code heuristics),
so it is honest and useful, just not as fluent as a real model. Swapping in
Gemini upgrades the prose; the app's behaviour does not otherwise change.
"""

from __future__ import annotations

from app.services.ai.base import LLMProvider

_MISTAKE_HEURISTICS = [
    ("unnecessary_on2", "for", "Nested loops detected — check whether the complexity can be reduced.", "medium"),
    ("integer_overflow", "int ", "Using 32-bit int with multiplication can overflow — consider 64-bit.", "high"),
    ("io_performance", "endl", "endl flushes every call — prefer '\\n' in tight loops.", "low"),
]


def _detect(code: str, language: str) -> list[dict]:
    found: list[dict] = []
    low = code.lower()
    # nested loop → O(n^2) flag
    if low.count("for") >= 2 and "for" in low:
        found.append({"mistake_type": "unnecessary_on2", "note": _MISTAKE_HEURISTICS[0][2], "severity": "medium"})
    if language.startswith("GNU C++") or "c++" in language.lower():
        if " int " in code and "*" in code and "long long" not in code:
            found.append({"mistake_type": "integer_overflow", "note": _MISTAKE_HEURISTICS[1][2], "severity": "high"})
        if "endl" in code:
            found.append({"mistake_type": "io_performance", "note": _MISTAKE_HEURISTICS[2][2], "severity": "low"})
    return found


class StubProvider(LLMProvider):
    name = "stub"
    available = True

    def explain_recommendation(self, ctx: dict) -> str:
        pr = ctx.get("problem_rating")
        target = ctx.get("target_rating")
        tags = ctx.get("tags", [])
        reason = ctx.get("top_reason", "difficulty fit")
        bits = []
        if target and pr:
            delta = pr - target
            if delta > 0:
                bits.append(f"a {delta}-point step up from your current level (~{target})")
            elif delta < 0:
                bits.append(f"a reinforcement pick just below your level (~{target})")
            else:
                bits.append(f"right at your estimated level (~{target})")
        if tags:
            bits.append("topics: " + ", ".join(tags[:3]))
        if reason:
            bits.append(f"selected mainly for {reason}")
        return "Recommended because it is " + "; ".join(bits) + "."

    def review_code(self, ctx: dict) -> dict:
        code = ctx.get("code", "") or ""
        language = ctx.get("language", "")
        verdict = ctx.get("verdict", "")
        mistakes = _detect(code, language)
        strengths = []
        if verdict == "OK":
            strengths.append("Accepted solution — the core approach works.")
        if len(code.splitlines()) < 60:
            strengths.append("Concise implementation.")
        improvements = [m["note"] for m in mistakes] or ["No automated issues detected by the offline reviewer."]
        return {
            "correctness": "Accepted" if verdict == "OK" else (verdict or "Unknown"),
            "complexity": {"time": "not analysed offline", "space": "not analysed offline"},
            "strengths": strengths or ["Solution submitted."],
            "improvements": improvements,
            "mistakes": mistakes,
            "summary": "Offline heuristic review. Configure a Gemini key for full algorithmic analysis.",
        }

    def tutor_hint(self, ctx: dict) -> dict:
        tags = ctx.get("tags", []) or ["the problem"]
        level = ctx.get("level", 1)
        hints = [
            f"Start by restating what is being asked and the constraints — they often hint at the intended complexity.",
            f"This problem is tagged {', '.join(tags[:2])}. What invariant or quantity stays useful as you scan the input?",
            f"Consider the smallest cases by hand; the pattern you see usually generalises to the {tags[0]} idea.",
        ]
        return {"hints": hints[: max(1, min(3, level))], "solution": None}

    def generate_plan(self, ctx: dict) -> list[dict]:
        days = int(ctx.get("duration_days", 30))
        react = ["JSX", "Components", "Props", "State", "useState", "useEffect", "Forms", "Routing", "Context", "Custom Hooks"]
        backend = ["HTTP", "REST", "FastAPI basics", "Databases", "PostgreSQL", "Auth & JWT", "Caching", "Background jobs", "Testing", "Deployment"]
        out = []
        for d in range(days):
            out.append({
                "day": d + 1,
                "tasks": [
                    {"category": "cf", "title": "Solve 2 Codeforces problems at your recommended level"},
                    {"category": "react", "title": f"React — {react[d % len(react)]}"},
                    {"category": "backend", "title": f"Backend — {backend[d % len(backend)]}"},
                ],
            })
        return out
