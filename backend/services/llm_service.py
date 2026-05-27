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


def query_llm(prompt: str) -> str:
    """
    Send any prompt directly to the NVIDIA LLM and return the response string.
    Returns None if LLM is unavailable or the call fails.
    """
    if not HAS_LANGCHAIN or not NVIDIA_API_KEY:
        return None
    try:
        llm = _get_llm()
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        print(f"LLM query failed: {e}")
        return None


def generate_answer(query: str, papers: list) -> str:
    """
    Generate an evidence-based answer using LLM from retrieved paper abstracts.
    Falls back to a structured text summary when LLM is unavailable.
    """
    if not papers:
        return "No papers available to generate an answer."

    # Build context from paper titles + abstracts
    context = "\n\n".join(
        [f"Title: {p.get('title', 'Unknown')}\nAbstract: {p.get('abstract', 'N/A')}"
         for p in papers]
    )

    prompt = f"""You are a clinical evidence assistant.
Answer the question using ONLY the information in the provided abstracts below.
Cite the paper titles in square brackets when you use their information.
If the abstracts do not contain enough information, say so clearly — do NOT invent facts.

Question:
{query}

Abstracts:
{context}
"""

    result = query_llm(prompt)
    if result:
        return result

    # Fallback: structured plain-text summary (no LLM)
    answer = f"Based on the retrieved medical literature regarding '{query}':\n\n"
    for i, paper in enumerate(papers, 1):
        title = paper.get("title", "Unknown")
        abstract = paper.get("abstract", "No abstract available")
        score = paper.get("rerank_score", paper.get("hybrid_score", 0))
        answer += f"{i}. [{title}]\n"
        answer += f"   {abstract[:300]}...\n"
        if score > 0:
            answer += f"   (Relevance Score: {score:.3f})\n\n"
    answer += "\nNote: For detailed analysis, please consult with a qualified medical professional."
    return answer


def answer_report_question(query: str, report_text: str) -> str:
    """
    Answer a question about a medical report.
    Tries the NVIDIA LLM first (handles any question type).
    Falls back to keyword extraction for the 4 most common question types
    if the LLM is unavailable.
    """
    if not report_text or not query:
        return "Please provide both a report and a question."

    # ── LLM path (primary) ──────────────────────────────────────────────────
    if HAS_LANGCHAIN and NVIDIA_API_KEY:
        prompt = f"""You are a medical report assistant.
Answer the following question based ONLY on the content of the provided medical report.
Be accurate, clear, and use patient-friendly language.
If the specific information is not present in the report, say so honestly — do NOT guess.

Question: {query}

Medical Report:
{report_text[:6000]}

Answer:"""
        result = query_llm(prompt)
        if result:
            return result

    # ── Keyword-extraction fallback (when LLM is unavailable) ───────────────
    return _keyword_extract_from_report(query, report_text)


def _keyword_extract_from_report(query: str, report_text: str) -> str:
    """
    Simple keyword-based extractor used as a last-resort fallback when the LLM
    is not available. Handles 4 common question types.
    """
    query_lower = query.lower()
    lines = report_text.split("\n")

    if any(word in query_lower for word in ["allerg"]):
        for i, line in enumerate(lines):
            if "allerg" in line.lower():
                allergy_lines = [lines[j].strip() for j in range(i, min(i + 3, len(lines))) if lines[j].strip()]
                if allergy_lines:
                    return "Allergies in your report:\n" + "\n".join(allergy_lines)
        return "No allergy information found in your report."

    elif any(word in query_lower for word in ["medication", "medicine", "drug", "med"]):
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in ["medication", "drug", "medicine"]):
                med_lines = [
                    lines[j].strip() for j in range(i, min(i + 5, len(lines)))
                    if lines[j].strip() and not any(x in lines[j].lower() for x in ["vital", "diagnosis", "procedure"])
                ]
                if med_lines:
                    return "Medications in your report:\n" + "\n".join(med_lines)
        return "No medication information found in your report."

    elif "diagnosis" in query_lower:
        for i, line in enumerate(lines):
            if "diagnosis" in line.lower():
                diag_lines = [
                    lines[j].strip() for j in range(i, min(i + 5, len(lines)))
                    if lines[j].strip() and not any(x in lines[j].lower() for x in ["vital", "medication"])
                ]
                if diag_lines:
                    return "Diagnoses in your report:\n" + "\n".join(diag_lines)
        return "No diagnosis information found in your report."

    elif any(word in query_lower for word in ["vital", "blood pressure", "heart rate"]):
        for i, line in enumerate(lines):
            if "vital" in line.lower():
                vital_lines = [
                    lines[j].strip() for j in range(i, min(i + 6, len(lines)))
                    if lines[j].strip() and not any(x in lines[j].lower() for x in ["diagnosis", "medication"])
                ]
                if vital_lines:
                    return "Vital Signs in your report:\n" + "\n".join(vital_lines)
        return "No vital signs information found in your report."

    else:
        return (
            f"LLM is currently unavailable. Unable to answer '{query}' without AI assistance.\n"
            "Please check that NVIDIA_API_KEY is set and the required packages are installed."
        )