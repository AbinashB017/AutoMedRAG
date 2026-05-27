"""
Report Summarization Service - AI-powered report analysis
Uses the NVIDIA LLM (via query_llm) to create summaries and explanations.
"""
from backend.services.llm_service import query_llm, answer_report_question


def summarize_report(report_text: str) -> dict:
    """
    Summarize a medical report using AI.
    Returns a dict with 'summary' and 'full_text'.
    """
    truncated = report_text[:5000]  # Limit to first 5000 chars to keep prompt manageable

    prompt = f"""You are a clinical medical assistant.
Analyze the following medical report and provide a structured response with these sections:

1. SUMMARY — A brief 2-3 sentence overview of the report.
2. KEY FINDINGS — List the main diagnoses, important test results, and clinical concerns.
3. NEXT STEPS — Recommended follow-up actions for the patient.
4. ALERTS — Any critical values or urgent items that need immediate attention.

Medical Report:
{truncated}

Provide a clear, patient-friendly response."""

    result = query_llm(prompt)

    if not result:
        # Fallback: basic extraction if LLM unavailable
        result = (
            "AI summarization is currently unavailable (LLM not configured).\n"
            "Please ensure NVIDIA_API_KEY is set and required packages are installed.\n\n"
            f"Report preview:\n{report_text[:500]}..."
        )

    return {
        "summary": result,
        "full_text": report_text
    }


def explain_medical_term(report_text: str, term: str) -> str:
    """
    Explain a medical term found in the report in simple language.
    """
    truncated = report_text[:4000]

    prompt = f"""You are a medical assistant helping a patient understand their report.
Explain the medical term '{term}' in simple, easy-to-understand language.
Use context from the medical report below if it helps clarify the meaning.
Keep the explanation under 150 words and avoid jargon.

Medical Report:
{truncated}

Explanation of '{term}':"""

    result = query_llm(prompt)

    if not result:
        return (
            f"Unable to explain '{term}' — LLM is currently unavailable.\n"
            "Please ensure NVIDIA_API_KEY is configured and required packages are installed."
        )

    return result


def answer_report_question_service(question: str, report_text: str) -> str:
    """
    Answer a user question about their medical report.
    Delegates to llm_service.answer_report_question which tries LLM first,
    then falls back to keyword extraction.
    """
    return answer_report_question(question, report_text)


def get_action_items(report_text: str) -> list:
    """
    Extract actionable items from the report.
    """
    truncated = report_text[:4000]

    prompt = f"""From this medical report, extract all action items for the patient.
List things like:
- Medications to take (name, dose, frequency)
- Follow-up appointments needed
- Tests or lab work to get done
- Lifestyle changes recommended
- Warning signs to watch for and when to seek urgent care

Medical Report:
{truncated}

List action items in bullet points:"""

    result = query_llm(prompt)

    if not result:
        return ["Action item extraction unavailable — LLM not configured."]

    return [line for line in result.split("\n") if line.strip()]
