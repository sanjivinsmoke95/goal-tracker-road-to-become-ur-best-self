from pydantic import BaseModel, Field


class RagQuery(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    topic: str | None = None
    k: int = Field(default=4, ge=1, le=8)


class RagSource(BaseModel):
    title: str
    source: str
    url: str
    score: float


class RagAnswer(BaseModel):
    answer: str
    sources: list[RagSource]
    grounded: bool
    llm: str


class RagStatus(BaseModel):
    indexed_chunks: int
    topics: list[str]
    embedder: str | None
