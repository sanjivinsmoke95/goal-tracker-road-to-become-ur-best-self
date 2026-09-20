from app.services.rag import store as rag_store
from app.services.rag.embeddings import TfidfEmbedder, cosine, tokenize
from app.services.rag.store import chunk_text
from tests.conftest import register_and_login


# --- Pure embedding / chunking logic --------------------------------------
def test_tokenize_drops_stopwords_and_keeps_symbols():
    toks = tokenize("The useEffect hook in C++ and React.js")
    assert "useeffect" in toks
    assert "c++" in toks
    assert "the" not in toks and "and" not in toks and "in" not in toks


def test_tfidf_is_deterministic_and_normalized():
    corpus = ["binary search sorted array", "dynamic programming subproblems", "react hooks useeffect"]
    e = TfidfEmbedder().fit(corpus)
    v1 = e.embed("binary search array")
    v2 = e.embed("binary search array")
    assert v1 == v2  # deterministic
    # A vector's cosine with itself is ~1 (L2-normalized).
    assert abs(cosine(v1, v1) - 1.0) < 1e-9
    # Unrelated query shares no vocabulary → orthogonal.
    assert cosine(v1, e.embed("react hooks")) == 0.0


def test_chunk_text_splits_long_text():
    one = chunk_text("Short sentence.")
    assert one == ["Short sentence."]
    long = "This is a sentence. " * 120  # well over the size threshold
    chunks = chunk_text(long, size=300)
    assert len(chunks) > 1
    assert all(len(c) <= 420 for c in chunks)  # size + overlap slack


# --- Retrieval over the real corpus ---------------------------------------
def test_reindex_and_retrieve_finds_relevant_doc(client):
    # Use a DB session directly through the app override.
    from app.db import get_db
    from app.main import app

    db = next(app.dependency_overrides[get_db]())
    n = rag_store.reindex(db)
    assert n >= len(__import__("app.services.rag.corpus", fromlist=["DOCS"]).DOCS)

    hits = rag_store.retrieve(db, "how does the useEffect cleanup function work in react", k=3)
    assert hits, "expected at least one retrieved chunk"
    assert hits[0]["title"] == "useEffect"
    assert "react.dev" in hits[0]["url"]

    # Topic scoping restricts the corpus.
    dsa = rag_store.retrieve(db, "shortest path", k=3, topic="dsa")
    assert dsa and all(h["topic"] == "dsa" for h in dsa)


# --- API ------------------------------------------------------------------
def test_rag_ask_returns_answer_with_sources(client):
    h = register_and_login(client)
    r = client.post("/rag/ask", json={"question": "why is my solution O(n^2) and timing out?"}, headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["answer"]
    assert body["sources"], "answer must cite retrieved sources"
    assert all(s["url"].startswith("http") for s in body["sources"])
    # Keyless test env → retrieval-only mode, still grounded in real docs.
    assert body["grounded"] is True
    assert body["llm"] == "retrieval-only"


def test_rag_status_reports_index(client):
    h = register_and_login(client)
    client.post("/rag/ask", json={"question": "binary search"}, headers=h)  # triggers self-heal index
    st = client.get("/rag/status", headers=h).json()
    assert st["indexed_chunks"] > 0
    assert "dsa" in st["topics"] and "react" in st["topics"]
    assert st["embedder"] == "tfidf"


def test_rag_requires_auth(client):
    assert client.post("/rag/ask", json={"question": "x"}).status_code in (401, 403)
