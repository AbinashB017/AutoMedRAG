from pydantic import BaseModel
from typing import List

class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class QueryRequest(BaseModel):
    question: str
    history: List[ConversationMessage] | None = None

class Paper(BaseModel):
    title: str
    abstract: str
    hybrid_score: float | None = None
    rerank_score: float | None = None

class QueryResponse(BaseModel):
    answer: str
    papers: List[Paper]