"""
Report Parser Service - Extract text from medical reports
Supports: PDF, DOCX, TXT
"""
import io
from pypdf import PdfReader
from docx import Document


def parse_pdf(file_content: bytes) -> str:
    """Extract text from PDF"""
    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Error parsing PDF: {e}")


def parse_docx(file_content: bytes) -> str:
    """Extract text from DOCX"""
    try:
        doc = Document(io.BytesIO(file_content))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Error parsing DOCX: {e}")


def parse_txt(file_content: bytes) -> str:
    """Extract text from TXT"""
    try:
        return file_content.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Error parsing TXT: {e}")


def extract_report_text(file_content: bytes, filename: str) -> str:
    """
    Extract text from any supported report format
    Automatically detects file type from filename
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return parse_pdf(file_content)
    elif filename_lower.endswith('.docx') or filename_lower.endswith('.doc'):
        return parse_docx(file_content)
    elif filename_lower.endswith('.txt'):
        return parse_txt(file_content)
    else:
        raise ValueError(f"Unsupported file format. Supported: PDF, DOCX, TXT")


def extract_key_sections(text: str) -> dict:
    """
    Extract key medical information from report text
    Looks for common sections and patterns with plain-language explanations
    """
    text_lower = text.lower()
    
    sections = {
        "diagnoses": [],
        "medications": [],
        "procedures": [],
        "allergies": [],
        "vital_signs": []
    }
    
    lines = text.split('\n')
    
    # Extract diagnoses
    for i, line in enumerate(lines):
        if 'diagnosis' in line.lower() or 'medical condition' in line.lower():
            for j in range(i+1, min(i+8, len(lines))):
                stripped = lines[j].strip()
                if stripped and not any(x in stripped.lower() for x in ['medication', 'allergy', 'vital', 'procedure']):
                    if len(stripped) > 3:
                        sections["diagnoses"].append(stripped)
                if 'medication' in lines[j].lower():
                    break
    
    # Extract medications
    for i, line in enumerate(lines):
        if 'medication' in line.lower() or 'drug' in line.lower():
            for j in range(i+1, min(i+8, len(lines))):
                stripped = lines[j].strip()
                if stripped and not any(x in stripped.lower() for x in ['diagnosis', 'allergy', 'vital', 'procedure']):
                    if len(stripped) > 3:
                        sections["medications"].append(stripped)
                if any(x in lines[j].lower() for x in ['diagnosis', 'allergy', 'vital', 'procedure']):
                    break
    
    # Extract allergies - be very aggressive with better matching
    allergies = extract_allergies(text)
    sections["allergies"] = allergies
    
    # Extract procedures
    for i, line in enumerate(lines):
        if 'procedure' in line.lower() or 'surgery' in line.lower() or 'test' in line.lower():
            for j in range(i+1, min(i+6, len(lines))):
                stripped = lines[j].strip()
                if stripped and not any(x in stripped.lower() for x in ['diagnosis', 'medication', 'allergy']):
                    if len(stripped) > 3:
                        sections["procedures"].append(stripped)
                if any(x in lines[j].lower() for x in ['diagnosis', 'medication', 'allergy']):
                    break
    
    # Extract vital signs
    for i, line in enumerate(lines):
        if 'vital' in line.lower():
            for j in range(i, min(i+7, len(lines))):
                stripped = lines[j].strip()
                if stripped and not any(x in stripped.lower() for x in ['diagnosis', 'medication']):
                    if len(stripped) > 3:
                        sections["vital_signs"].append(stripped)
    
    # Remove duplicates and limit to top entries
    for key in sections:
        sections[key] = list(set(sections[key]))[:6]
    
    return sections


def extract_allergies(text: str) -> list:
    """
    Specifically extract allergies from report text with multiple matching strategies
    """
    allergies = set()
    text_lower = text.lower()
    lines = text.split('\n')
    
    # Keyword patterns for allergies
    allergy_keywords = ['penicillin', 'aspirin', 'ibuprofen', 'sulfa', 'latex', 'peanut', 
                        'tree nut', 'shellfish', 'egg', 'milk', 'gluten', 'morphine',
                        'codeine', 'sulfonamide', 'ace inhibitor', 'beta blocker']
    
    # Strategy 1: Look for lines containing 'allergy' or 'allergies'
    for i, line in enumerate(lines):
        if 'allerg' in line.lower():
            # Get this line and next 3 lines
            for j in range(i, min(i+4, len(lines))):
                text_segment = lines[j].strip()
                if text_segment and len(text_segment) > 2 and text_segment.lower() != 'allergies:' and text_segment.lower() != 'allergy':
                    allergies.add(text_segment)
    
    # Strategy 2: Search for known allergens in the text
    for allergen in allergy_keywords:
        if allergen in text_lower:
            # Find the context around this allergen
            for line in lines:
                if allergen in line.lower() and len(line.strip()) > 0:
                    allergies.add(line.strip())
    
    # Strategy 3: Look for NKDA (No Known Drug Allergy) or similar
    if 'nkda' in text_lower or 'no known allergy' in text_lower or 'nka' in text_lower:
        allergies.add("No known allergies reported")
    
    # Filter out noise and return
    clean_allergies = []
    for allergy in allergies:
        # Remove header-only lines
        if allergy.lower() not in ['allergy:', 'allergies:', 'drug allergy:', 'allergies:']:
            clean_allergies.append(allergy)
    
    return sorted(list(set(clean_allergies)))[:6]  # Return top 6 unique allergies
