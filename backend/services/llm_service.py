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

def answer_report_question(query: str, report_text: str) -> str:
    """
    Answer a question about a medical report.
    Does NOT require papers - works directly with report text.
    Uses extraction logic by default for reliability.
    """
    if not report_text or not query:
        return "Please provide both a report and a question."
    
    print(f"\n[DEBUG] ===== ANSWER_REPORT_QUESTION =====")
    print(f"[DEBUG] Query: '{query}'")
    print(f"[DEBUG] Report text length: {len(report_text) if report_text else 0}")
    print(f"[DEBUG] Report text preview: {report_text[:300] if report_text else 'EMPTY'}")
    print(f"[DEBUG] =====================================\n")
    
    # Use extraction logic for reliability (skip LLM for now)
    query_lower = query.lower()
    report_lower = report_text.lower()
    
    if any(word in query_lower for word in ['allerg']):
        print(f"[DEBUG] Detected allergy question")
        lines = report_text.split('\n')
        
        # Find allergy section
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if 'allerg' in line_lower:
                print(f"[DEBUG] Found allergy keyword at line {i}: '{line}'")
                # Get allergy lines  
                allergy_lines = []
                for j in range(i, min(i+3, len(lines))):
                    stripped = lines[j].strip()
                    if stripped:
                        allergy_lines.append(stripped)
                        print(f"[DEBUG] Adding allergy line: '{stripped}'")
                
                if allergy_lines:
                    result = "Allergies in your report:\n" + "\n".join(allergy_lines)
                    print(f"[DEBUG] Returning: {result}")
                    return result
        
        print(f"[DEBUG] No allergies found in report")
        return "No allergy information found in your report."
    
    elif any(word in query_lower for word in ['medication', 'medicine', 'drug', 'med']):
        print(f"[DEBUG] Detected medication question")
        lines = report_text.split('\n')
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in ['medication', 'drug', 'medicine']):
                med_lines = []
                for j in range(i, min(i+5, len(lines))):
                    stripped = lines[j].strip()
                    if stripped and not any(x in stripped.lower() for x in ['vital', 'diagnosis', 'procedure']):
                        med_lines.append(stripped)
                
                if med_lines:
                    return "Medications in your report:\n" + "\n".join(med_lines)
        return "No medication information found in your report."
    
    elif any(word in query_lower for word in ['diagnosis']):
        print(f"[DEBUG] Detected diagnosis question")
        lines = report_text.split('\n')
        for i, line in enumerate(lines):
            if 'diagnosis' in line.lower():
                diag_lines = []
                for j in range(i, min(i+5, len(lines))):
                    stripped = lines[j].strip()
                    if stripped and not any(x in stripped.lower() for x in ['vital', 'medication']):
                        diag_lines.append(stripped)
                
                if diag_lines:
                    return "Diagnoses in your report:\n" + "\n".join(diag_lines)
        return "No diagnosis information found in your report."
    
    elif any(word in query_lower for word in ['vital', 'blood pressure', 'heart rate']):
        print(f"[DEBUG] Detected vital signs question")
        lines = report_text.split('\n')
        for i, line in enumerate(lines):
            if 'vital' in line.lower():
                vital_lines = []
                for j in range(i, min(i+6, len(lines))):
                    stripped = lines[j].strip()
                    if stripped and not any(x in stripped.lower() for x in ['diagnosis', 'medication']):
                        vital_lines.append(stripped)
                
                if vital_lines:
                    return "Vital Signs in your report:\n" + "\n".join(vital_lines)
        return "No vital signs information found in your report."
    
    else:
        print(f"[DEBUG] Generic search - no specific handler for: {query_lower}")
        return f"Unable to find specific information about '{query}' in your report. Try asking about:\n- Allergies\n- Medications\n- Diagnoses\n- Vital signs"