"""Selects the AI provider from configuration, degrading to the stub safely."""

from __future__ import annotations

import logging
from functools import lru_cache

from app.core.config import settings
from app.services.ai.base import LLMProvider
from app.services.ai.stub import StubProvider

logger = logging.getLogger(__name__)


@lru_cache
def get_provider() -> LLMProvider:
    choice = (settings.ai_provider or "stub").lower()
    if choice == "gemini":
        from app.services.ai.gemini import GeminiProvider

        provider = GeminiProvider()
        if provider.available:
            return provider
        logger.info("AI_PROVIDER=gemini but no working key; using the stub provider.")
    elif choice == "openai_compatible":
        # Reserved: an OpenAI-compatible provider slots in here identically.
        logger.info("openai_compatible not built yet; using the stub provider.")
    return StubProvider()
