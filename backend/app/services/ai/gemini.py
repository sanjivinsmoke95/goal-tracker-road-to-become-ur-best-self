"""Google Gemini provider (the configured default when a key is present).

Imports the SDK lazily so a missing dependency or key never breaks the app —
the factory falls back to the stub. When active it produces the same shapes the
stub does, so nothing downstream changes.
"""

from __future__ import annotations

import json
import logging

from app.core.config import settings
from app.services.ai.base import LLMProvider
from app.services.ai.stub import StubProvider

logger = logging.getLogger(__name__)
_stub = StubProvider()


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self) -> None:
        self.available = False
        self._client = None
        if not settings.gemini_api_key:
            return
        try:
            from google import genai  # type: ignore

            self._client = genai.Client(api_key=settings.gemini_api_key)
            self.available = True
        except Exception as exc:  # noqa: BLE001 — degrade to stub, never crash
            logger.warning("Gemini unavailable (%s); falling back to the stub provider.", exc)

    def _json(self, prompt: str, fallback):
        if not self.available:
            return fallback
        try:
            resp = self._client.models.generate_content(model=settings.gemini_model, contents=prompt)
            text = (resp.text or "").strip().removeprefix("```json").removeprefix("```").removesuffix("```")
            return json.loads(text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gemini call failed (%s); using offline fallback.", exc)
            return fallback

    def _text(self, prompt: str, fallback: str) -> str:
        if not self.available:
            return fallback
        try:
            resp = self._client.models.generate_content(model=settings.gemini_model, contents=prompt)
            return (resp.text or fallback).strip()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gemini call failed (%s); using offline fallback.", exc)
            return fallback

    def explain_recommendation(self, ctx: dict) -> str:
        prompt = (
            "In 2 sentences, explain why this competitive-programming problem is a good pick. "
            f"Context: {json.dumps(ctx)}. Be encouraging and specific, not generic."
        )
        return self._text(prompt, _stub.explain_recommendation(ctx))

    def review_code(self, ctx: dict) -> dict:
        prompt = (
            "Review this solution. Return ONLY JSON with keys correctness, complexity{time,space}, "
            "strengths[], improvements[], mistakes[{mistake_type,note,severity}], summary. "
            f"Data: {json.dumps({k: ctx.get(k) for k in ('language', 'verdict', 'code')})}"
        )
        return self._json(prompt, _stub.review_code(ctx))

    def tutor_hint(self, ctx: dict) -> dict:
        prompt = (
            "Give progressive hints (do NOT reveal the full solution unless solution=true). "
            "Return ONLY JSON {hints:[...], solution: string|null}. "
            f"Data: {json.dumps(ctx)}"
        )
        return self._json(prompt, _stub.tutor_hint(ctx))

    def generate_plan(self, ctx: dict) -> list[dict]:
        prompt = (
            "Create a day-by-day learning plan. Return ONLY a JSON array of "
            "{day, tasks:[{category,title}]}. "
            f"Data: {json.dumps(ctx)}"
        )
        result = self._json(prompt, None)
        return result if isinstance(result, list) else _stub.generate_plan(ctx)

    def answer_with_context(self, question: str, context: list[dict]) -> str:
        if not context:
            return super().answer_with_context(question, context)
        blocks = "\n\n".join(
            f"[{i + 1}] {c['title']} ({c['source']})\n{c['content']}" for i, c in enumerate(context)
        )
        prompt = (
            "You are a precise programming tutor. Answer the question USING ONLY the "
            "documentation passages below. Be concise and concrete. If the passages do "
            "not cover it, say so honestly. Cite passages inline like [1], [2]. Do not "
            "invent APIs or URLs.\n\n"
            f"Question: {question}\n\nPassages:\n{blocks}"
        )
        # Deterministic retrieval answer is the fallback if the LLM call fails.
        return self._text(prompt, super().answer_with_context(question, context))
