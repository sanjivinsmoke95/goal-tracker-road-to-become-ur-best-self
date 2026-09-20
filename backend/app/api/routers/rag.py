"""RAG API: ask questions grounded in the documentation corpus, with citations.

Retrieval is real and keyless (TF-IDF cosine); when GEMINI_API_KEY is set the
answer is LLM-synthesised over the retrieved passages, otherwise it returns the
most relevant passages directly. Either way `sources` are real official-doc links.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models import User
from app.schemas.rag import RagAnswer, RagQuery, RagStatus
from app.services.rag import store as rag_store

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/status", response_model=RagStatus)
def rag_status(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    return rag_store.status(db)


@router.post("/ask", response_model=RagAnswer)
def rag_ask(
    payload: RagQuery,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    # Self-heal: if the corpus was never indexed (fresh DB), index it now.
    if rag_store.status(db)["indexed_chunks"] == 0:
        rag_store.reindex(db)
    return rag_store.answer(db, payload.question, topic=payload.topic, k=payload.k)


@router.post("/reindex", response_model=RagStatus)
def rag_reindex(
    prefer_gemini: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    rag_store.reindex(db, prefer_gemini=prefer_gemini)
    return rag_store.status(db)
