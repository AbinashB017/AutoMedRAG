from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    question: str

class Paper(BaseModel):
    title: str
    abstract: str
    hybrid_score: float | None = None
    rerank_score: float | None = None

class QueryResponse(BaseModel):
    answer: str
    papers: List[Paper]
