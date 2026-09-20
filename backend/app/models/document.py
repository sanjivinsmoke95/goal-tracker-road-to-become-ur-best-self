"""RAG corpus storage.

A ``RagDocument`` is one *chunk* of a source document, with its retrieval
embedding stored alongside it. The embedding is a sparse map {term: weight}
(for the keyless TF-IDF embedder) or {index: value} (for a dense provider like
Gemini) — either way a JSON object, so this is portable across Postgres and the
SQLite test DB with no pgvector dependency. Cosine similarity is computed in
Python over the small personal corpus.

``RagMeta`` is a single row holding the fitted index parameters (vocabulary /
idf weights, the embedder name and dimension) so queries embed into the exact
same space the documents were indexed in.
"""

from typing import Any

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class RagDocument(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rag_documents"

    source: Mapped[str] = mapped_column(String(120), nullable=False)  # "MDN", "React docs"
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    url: Mapped[str] = mapped_column(String(500), default="")
    topic: Mapped[str] = mapped_column(String(48), index=True, default="general")

    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class RagMeta(Base):
    """Single-row (id='index') fitted-index parameters for the retriever."""

    __tablename__ = "rag_meta"

    id: Mapped[str] = mapped_column(String(24), primary_key=True, default="index")
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
