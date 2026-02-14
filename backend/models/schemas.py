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


# Report-related schemas
class ReportSummaryResponse(BaseModel):
    summary: str
    key_findings: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    action_items: Optional[List[str]] = None


class ReportQuestionRequest(BaseModel):
    question: str
    report_text: str


class ReportQuestionResponse(BaseModel):
    question: str
    answer: str


class ReportExplanationRequest(BaseModel):
    term: str
    report_text: str


class ReportExplanationResponse(BaseModel):
    term: str
    explanation: str