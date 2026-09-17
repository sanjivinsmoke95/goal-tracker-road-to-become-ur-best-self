"""The swappable AI provider contract.

The application depends only on this interface, never on a concrete model, so
the provider can change via one env var. Determinism lives elsewhere (the skill
and recommendation engines); the LLM only explains, reviews, tutors, and drafts
plans.
"""

from __future__ import annotations

import abc


class LLMProvider(abc.ABC):
    name: str = "base"
    available: bool = False

    @abc.abstractmethod
    def explain_recommendation(self, ctx: dict) -> str:
        """Why this problem was chosen, given the deterministic score breakdown."""

    @abc.abstractmethod
    def review_code(self, ctx: dict) -> dict:
        """Return {correctness, complexity, strengths[], improvements[], mistakes[], summary}."""

    @abc.abstractmethod
    def tutor_hint(self, ctx: dict) -> dict:
        """Return {hints: [str,...], solution: str|None}. Progressive, not instant."""

    @abc.abstractmethod
    def generate_plan(self, ctx: dict) -> list[dict]:
        """Return a list of day dicts for a learning plan."""
