from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import QueryRequest, QueryResponse
from backend.services.pubmed_service import fetch_pubmed
from backend.services.retrieval_service import hybrid_retrieve
from backend.services.reranker_service import rerank
from backend.services.llm_service import generate_answer

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
    """
    try:
        # Fetch papers from PubMed
        papers = fetch_pubmed(request.question)
        
        if not papers:
            return QueryResponse(
                answer="No relevant papers found for your query.",
                papers=[]
            )
        
        # Hybrid retrieval
        retrieved = hybrid_retrieve(request.question, papers)
        
        if not retrieved:
            return QueryResponse(
                answer="No relevant results after retrieval.",
                papers=[]
            )
        
        # Re-rank papers
        top_papers = rerank(request.question, retrieved)
        
        # Generate answer using LLM
        answer = generate_answer(request.question, top_papers)
        
        return QueryResponse(
            answer=answer,
            papers=top_papers
        )
    except Exception as e:
        return QueryResponse(
            answer=f"Error processing query: {str(e)}",
            papers=[]
        )
