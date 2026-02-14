"""
Report Summarization Service - AI-powered report analysis
Uses LLM to create summaries and explanations
"""
from backend.services.llm_service import generate_answer, answer_report_question


def summarize_report(report_text: str) -> dict:
    """
    Summarize a medical report using AI
    Returns: summary, key_findings, recommendations
    """
    
    # Create a summarization prompt
    summary_prompt = f"""Analyze this medical report and provide:
1. A brief 2-3 sentence summary
2. Key findings (list main diagnoses, test results, concerns)
3. Recommended next steps
4. Any important alerts or critical values

Medical Report:
{report_text[:5000]}  # Limit to first 5000 chars to save tokens

Provide structured response with clear sections."""
    
    summary_response = answer_report_question(summary_prompt, report_text)
    
    return {
        "summary": summary_response,
        "full_text": report_text
    }


def explain_medical_term(report_text: str, term: str) -> str:
    """
    Explain a medical term found in the report using LLM
    """
    
    explanation_prompt = f"""Based on this medical report, explain what '{term}' means in simple language.
Provide a clear explanation that a patient can understand.

Medical Report:
{report_text}

Explanation of '{term}'."""
    
    explanation = answer_report_question(explanation_prompt, report_text)
    return explanation


def answer_report_question(question: str, report_text: str) -> str:
    """
    Answer a user question about their medical report
    """
    
    qa_prompt = f"""Based on this medical report, please answer the following question:

Question: {question}

Medical Report:
{report_text}

Answer in clear, patient-friendly language."""
    
    # Use the new answer_report_question function from llm_service
    from backend.services.llm_service import answer_report_question as llm_answer
    answer = llm_answer(question, report_text)
    return answer


def get_action_items(report_text: str) -> list:
    """
    Extract actionable items from the report
    """
    
    action_prompt = f"""From this medical report, extract all action items for the patient.
List things like:
- Medications to take
- Follow-up appointments needed
- Tests to get done
- Lifestyle changes
- Warning signs to watch for

Medical Report:
{report_text}

List action items in bullet points."""
    
    action_items = answer_report_question(action_prompt, report_text)
    return action_items.split('\n')
