"""The RAG pipeline over the database: chunk → embed → store → retrieve → answer.

Retrieval is cosine similarity in Python over the stored sparse embeddings —
correct and fast for a personal-scale corpus, and portable (no pgvector, works
on the SQLite test DB). The LLM only synthesises an answer from what retrieval
returns; it never chooses the facts.
"""

from __future__ import annotations

import re

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import RagDocument, RagMeta
from app.services.ai import get_provider
from app.services.rag.corpus import DOCS
from app.services.rag.embeddings import TfidfEmbedder, cosine

_META_ID = "index"


def chunk_text(text: str, size: int = 700, overlap: int = 100) -> list[str]:
    """Split into ~size-char chunks on sentence boundaries, with a little overlap.

    Most curated entries are a single chunk; longer sources split cleanly so a
    retrieved passage stays focused.
    """
    text = text.strip()
    if len(text) <= size:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    cur = ""
    for s in sentences:
        if cur and len(cur) + len(s) + 1 > size:
            chunks.append(cur.strip())
            cur = (cur[-overlap:] + " " + s) if overlap else s
        else:
            cur = f"{cur} {s}".strip()
    if cur.strip():
        chunks.append(cur.strip())
    return chunks


def _select_embedder(prefer_gemini: bool):
    if prefer_gemini:
        from app.services.rag.embeddings import GeminiEmbedder

        emb = GeminiEmbedder()
        if emb.available:
            return emb
    return TfidfEmbedder()


def reindex(db: Session, prefer_gemini: bool = False) -> int:
    """Rebuild the whole index from the corpus. Idempotent. Returns chunk count."""
    # Flatten corpus into (metadata-with-chunk-index, chunk_text) pairs.
    records: list[tuple[dict, str]] = []
    for doc in DOCS:
        for i, chunk in enumerate(chunk_text(doc["content"])):
            records.append(({**doc, "_chunk_index": i}, chunk))

    # Index the title *with* the body (title repeated for a light boost) so a
    # query naming the concept ranks that document's own page first, counteracting
    # TF-IDF's bias toward shorter documents. The stored content stays the body only.
    embed_texts = [f"{meta['title']}. {meta['title']}. {chunk}" for meta, chunk in records]
    embedder = _select_embedder(prefer_gemini)
    embedder.fit(embed_texts)
    vectors = embedder.embed_many(embed_texts)

    db.execute(delete(RagDocument))
    db.execute(delete(RagMeta))
    for (meta, chunk), vec in zip(records, vectors):
        db.add(
            RagDocument(
                source=meta["source"],
                title=meta["title"],
                url=meta.get("url", ""),
                topic=meta.get("topic", "general"),
                chunk_index=meta["_chunk_index"],
                content=chunk,
                embedding=vec,
            )
        )
    db.add(RagMeta(id=_META_ID, data=embedder.to_meta()))
    db.flush()
    return len(records)


def _load_embedder(db: Session):
    meta = db.get(RagMeta, _META_ID)
    if not meta:
        return None
    data = meta.data or {}
    if data.get("embedder") == "gemini":
        from app.services.rag.embeddings import GeminiEmbedder

        emb = GeminiEmbedder.from_meta(data)
        if emb.available:
            return emb
        return None  # indexed with gemini but key now gone → must re-index
    return TfidfEmbedder.from_meta(data)


def retrieve(db: Session, query: str, k: int = 4, topic: str | None = None) -> list[dict]:
    embedder = _load_embedder(db)
    if embedder is None:
        return []
    qvec = embedder.embed(query)
    if not qvec:
        return []
    stmt = select(RagDocument)
    if topic:
        stmt = stmt.where(RagDocument.topic == topic)
    scored: list[tuple[float, RagDocument]] = []
    for doc in db.execute(stmt).scalars():
        score = cosine(qvec, doc.embedding or {})
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda p: p[0], reverse=True)
    # Drop weak matches so citations stay relevant: keep the top hit, plus any
    # within a fraction of its score and above a small absolute floor.
    if scored:
        floor = max(0.03, scored[0][0] * 0.25)
        scored = [scored[0]] + [p for p in scored[1:] if p[0] >= floor]
    out = []
    for score, doc in scored[:k]:
        out.append(
            {
                "title": doc.title,
                "source": doc.source,
                "url": doc.url,
                "topic": doc.topic,
                "content": doc.content,
                "score": round(score, 4),
            }
        )
    return out


def answer(db: Session, question: str, topic: str | None = None, k: int = 4) -> dict:
    hits = retrieve(db, question, k=k, topic=topic)
    provider = get_provider()
    text = provider.answer_with_context(question, hits)
    # The stub is our keyless fallback: it returns retrieved passages verbatim,
    # so that is "retrieval-only". Only a real, available LLM counts as synthesis.
    is_real_llm = getattr(provider, "available", False) and provider.name != "stub"
    return {
        "answer": text,
        "sources": [{"title": h["title"], "source": h["source"], "url": h["url"], "score": h["score"]} for h in hits],
        "grounded": bool(hits),
        "llm": provider.name if is_real_llm else "retrieval-only",
    }


def status(db: Session) -> dict:
    count = db.execute(select(RagDocument)).scalars().all()
    meta = db.get(RagMeta, _META_ID)
    topics = sorted({d.topic for d in count})
    return {
        "indexed_chunks": len(count),
        "topics": topics,
        "embedder": (meta.data or {}).get("embedder") if meta else None,
    }
