from pydantic import BaseModel
from typing import List, Optional

class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class QueryRequest(BaseModel):
    question: str
    history: Optional[List[ConversationMessage]] = None

class Paper(BaseModel):
    title: str
    abstract: str
    hybrid_score: Optional[float] = None
    rerank_score: Optional[float] = None

class QueryResponse(BaseModel):
    answer: str
    papers: List[Paper]