"""Embedders. Every embedding is a normalized sparse map so cosine similarity is
one code path regardless of provider.

- TfidfEmbedder (default, keyless, deterministic): classic TF-IDF over the corpus
  vocabulary. Real information-retrieval, no network, no API key. Fitted params
  (vocab + idf) persist so a query embeds into the same space as the documents.
- GeminiEmbedder (optional): dense semantic vectors via google-genai, exposed as
  {str(index): value} so the same cosine works. Falls back to TF-IDF when no key.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable

# Small, deliberately conservative stopword list — enough to cut noise without
# needing an NLP dependency.
_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "is", "are", "was", "were",
    "be", "been", "it", "its", "this", "that", "these", "those", "for", "on",
    "with", "as", "at", "by", "from", "into", "if", "then", "else", "so", "than",
    "you", "your", "we", "they", "he", "she", "them", "but", "not", "no", "do",
    "does", "can", "will", "would", "should", "how", "what", "when", "which",
    "where", "why", "who", "there", "here", "about", "using", "use", "used",
}

_TOKEN_RE = re.compile(r"[a-zA-Z0-9+#.]+")


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokens (keeping c++, c#, .net-ish forms), no stopwords."""
    out: list[str] = []
    for raw in _TOKEN_RE.findall((text or "").lower()):
        tok = raw.strip(".")
        if len(tok) >= 2 and tok not in _STOP:
            out.append(tok)
    return out


def _l2_normalize(vec: dict[str, float]) -> dict[str, float]:
    norm = math.sqrt(sum(v * v for v in vec.values()))
    if norm == 0:
        return {}
    return {k: v / norm for k, v in vec.items()}


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    """Dot product of two already-L2-normalized sparse vectors = cosine similarity."""
    if len(a) > len(b):
        a, b = b, a
    return sum(w * b.get(k, 0.0) for k, w in a.items())


class TfidfEmbedder:
    name = "tfidf"

    def __init__(self, idf: dict[str, float] | None = None):
        self.idf: dict[str, float] = idf or {}

    def fit(self, corpus: Iterable[str]) -> "TfidfEmbedder":
        docs = [tokenize(t) for t in corpus]
        n = len(docs) or 1
        df: Counter[str] = Counter()
        for toks in docs:
            for term in set(toks):
                df[term] += 1
        # Smoothed idf so a term in every doc still contributes a little.
        self.idf = {term: math.log((1 + n) / (1 + dfi)) + 1.0 for term, dfi in df.items()}
        return self

    def embed(self, text: str) -> dict[str, float]:
        toks = tokenize(text)
        if not toks:
            return {}
        tf = Counter(toks)
        total = len(toks)
        vec: dict[str, float] = {}
        for term, count in tf.items():
            idf = self.idf.get(term)
            if idf is None:
                continue  # out-of-vocabulary at query time → ignored
            vec[term] = (count / total) * idf
        return _l2_normalize(vec)

    def embed_many(self, texts: list[str]) -> list[dict[str, float]]:
        return [self.embed(t) for t in texts]

    def to_meta(self) -> dict:
        return {"embedder": self.name, "idf": self.idf}

    @classmethod
    def from_meta(cls, data: dict) -> "TfidfEmbedder":
        return cls(idf=data.get("idf") or {})


class GeminiEmbedder:
    """Dense semantic embeddings via google-genai. Optional; needs GEMINI_API_KEY."""

    name = "gemini"

    def __init__(self, model: str = "text-embedding-004"):
        self.model = model
        self.available = False
        self._client = None
        try:
            from app.core.config import settings

            if settings.gemini_api_key:
                from google import genai  # lazy: only if the dep + key exist

                self._client = genai.Client(api_key=settings.gemini_api_key)
                self.available = True
        except Exception:  # pragma: no cover - depends on optional dep/key
            self.available = False

    def _dense(self, text: str) -> dict[str, float]:
        resp = self._client.models.embed_content(model=self.model, contents=text)
        values = resp.embeddings[0].values
        return _l2_normalize({str(i): float(v) for i, v in enumerate(values)})

    def fit(self, corpus: Iterable[str]) -> "GeminiEmbedder":
        return self  # no corpus fitting needed for a pretrained embedder

    def embed(self, text: str) -> dict[str, float]:
        if not text.strip():
            return {}
        return self._dense(text)

    def embed_many(self, texts: list[str]) -> list[dict[str, float]]:
        return [self.embed(t) for t in texts]

    def to_meta(self) -> dict:
        return {"embedder": self.name, "model": self.model}

    @classmethod
    def from_meta(cls, data: dict) -> "GeminiEmbedder":
        return cls(model=data.get("model", "text-embedding-004"))
