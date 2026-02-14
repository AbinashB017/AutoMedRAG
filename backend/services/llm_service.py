from backend.utils.config import NVIDIA_MODEL, NVIDIA_API_KEY

# Try to import langchain with fallback
try:
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
    from langchain_core.messages import HumanMessage
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    ChatNVIDIA = None
    HumanMessage = None

# Initialize LLM lazily
_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        if not HAS_LANGCHAIN:
            raise ImportError("langchain-nvidia-ai-endpoints not installed")
        if not NVIDIA_API_KEY:
            raise ValueError("NVIDIA_API_KEY not configured")
        _llm = ChatNVIDIA(model=NVIDIA_MODEL)
    return _llm

def generate_answer(query, papers):
    """
    Generate an answer using LLM based on query and papers.
    Falls back to summary if LLM is not available.
    """
    if not papers:
        return "No papers available to generate answer."
    
    # If LLM is available, use it
    if HAS_LANGCHAIN:
        try:
            llm = _get_llm()
            
            context = "\n\n".join(
                [f"Title: {p.get('title', 'Unknown')}\nAbstract: {p.get('abstract', 'N/A')}" 
                 for p in papers]
            )

            prompt = f"""You are a clinical evidence assistant.
Answer ONLY using provided abstracts.
Cite paper titles in brackets.
If insufficient evidence, say so.

Question:
{query}

Abstracts:
{context}
"""

            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"LLM generation failed: {e}, using fallback summary")
    
    # Fallback: Return a structured summary
    answer = f"Based on the retrieved medical literature regarding '{query}':\n\n"
    
    for i, paper in enumerate(papers, 1):
        title = paper.get('title', 'Unknown')
        abstract = paper.get('abstract', 'No abstract available')
        score = paper.get('rerank_score', paper.get('hybrid_score', 0))
        
        answer += f"{i}. [{title}]\n"
        answer += f"   {abstract[:300]}...\n"
        if score > 0:
            answer += f"   (Relevance Score: {score:.3f})\n\n"
    
    answer += "\nNote: For detailed analysis, please consult with medical professionals."
    return answer
