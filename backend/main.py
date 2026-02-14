from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import QueryRequest, QueryResponse, ReportSummaryResponse, ReportQuestionRequest, ReportQuestionResponse, ReportExplanationRequest, ReportExplanationResponse
from backend.services.pubmed_service import fetch_pubmed
from backend.services.retrieval_service import hybrid_retrieve
from backend.services.reranker_service import rerank
from backend.services.llm_service import generate_answer
from backend.services.report_parser_service import extract_report_text, extract_key_sections
from backend.services.report_summarizer_service import summarize_report, answer_report_question, explain_medical_term

app = FastAPI(title="AutoMedRAG API", description="Medical Document Retrieval and Analysis System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "AutoMedRAG API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Retrieve and analyze medical papers for a given question.
    
    - Fetches relevant papers from PubMed
    - Performs hybrid retrieval (semantic + keyword)
    - Re-ranks results for relevance
    - Generates an evidence-based answer
    - Supports conversation history for contextual understanding
    """
    try:
        # Build context from conversation history
        context = ""
        if request.history and len(request.history) > 0:
            # Get last 2 exchanges for context
            recent_history = request.history[-4:]  # Last 2 Q&A pairs
            for msg in recent_history:
                if msg.role == "user":
                    context += f"Previous question: {msg.content}\n"
                else:
                    context += f"Previous answer: {msg.content}\n"
        
        # Enhance the question with context if available
        enhanced_question = request.question
        if context:
            enhanced_question = f"Context: {context}\nNew question: {request.question}"
        
        # Fetch papers from PubMed (use original question for API)
        papers = fetch_pubmed(request.question)
        
        if not papers:
            return QueryResponse(
                answer="No relevant papers found for your query.",
                papers=[]
            )
        
        # Hybrid retrieval (use enhanced question for better matching)
        retrieved = hybrid_retrieve(enhanced_question, papers)
        
        if not retrieved:
            return QueryResponse(
                answer="No relevant results after retrieval.",
                papers=[]
            )
        
        # Re-rank papers (use enhanced question)
        top_papers = rerank(enhanced_question, retrieved)
        
        # Generate answer using LLM (use original question but with context awareness)
        answer = generate_answer(enhanced_question, top_papers)
        
        return QueryResponse(
            answer=answer,
            papers=top_papers
        )
    except Exception as e:
        return QueryResponse(
            answer=f"Error processing query: {str(e)}",
            papers=[]
        )


# Report-related endpoints
@app.post("/summarize-report")
async def summarize_medical_report(file: UploadFile = File(...)):
    """
    Upload a medical report and get AI-powered summary.
    Supports: PDF, DOCX, TXT
    """
    try:
        # Read file content
        content = await file.read()
        
        # Extract text from report
        report_text = extract_report_text(content, file.filename)
        
        # Summarize the report
        summary_result = summarize_report(report_text)
        
        # Extract key sections
        key_sections = extract_key_sections(report_text)
        
        return {
            "filename": file.filename,
            "summary": summary_result["summary"],
            "key_sections": key_sections,
            "report_text": report_text,  # Include the extracted text
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


@app.post("/report-question", response_model=ReportQuestionResponse)
async def ask_question_about_report(request: ReportQuestionRequest):
    """
    Ask a question about a medical report.
    The AI will answer based on the report content.
    """
    try:
        answer = answer_report_question(request.report_text, request.question)
        
        return ReportQuestionResponse(
            question=request.question,
            answer=answer
        )
    except Exception as e:
        return ReportQuestionResponse(
            question=request.question,
            answer=f"Error answering question: {str(e)}"
        )


@app.post("/explain-term", response_model=ReportExplanationResponse)
async def explain_medical_term_endpoint(request: ReportExplanationRequest):
    """
    Get an explanation of a medical term found in the report.
    Provides patient-friendly language.
    """
    try:
        explanation = explain_medical_term(request.report_text, request.term)
        
        return ReportExplanationResponse(
            term=request.term,
            explanation=explanation
        )
    except Exception as e:
        return ReportExplanationResponse(
            term=request.term,
            explanation=f"Error explaining term: {str(e)}"
        )

