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

    def answer_with_context(self, question: str, context: list[dict]) -> str:
        """Answer a question grounded in retrieved documentation chunks.

        The default is deterministic and keyless: it returns the most relevant
        retrieved passage(s) verbatim from the corpus (which are our own concise
        summaries), so the answer is real retrieval even with no LLM configured.
        A real LLM provider overrides this to synthesise across the chunks.
        Sources are returned separately by the RAG service, not embedded here.
        """
        if not context:
            return "I don't have any indexed documentation matching that yet."
        top = context[0]
        parts = [top["content"].strip()]
        if len(context) > 1:
            second = context[1]
            sentence = second["content"].strip().split(". ")[0].rstrip(".")
            parts.append(f"Related — {second['title']} ({second['source']}): {sentence}.")
        return "\n\n".join(parts)
