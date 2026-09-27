"""Extract readable text and summarize a grant guideline."""
import io
import pdfplumber
from utils.llm_client import ask_llm

def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from all pages. Scanned PDFs may require OCR separately."""
    pages = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for number, page in enumerate(pdf.pages, start=1):
            pages.append(f"\n--- PAGE {number} ---\n{page.extract_text() or ''}")
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("No selectable text found. This may be a scanned PDF.")
    return text

def clean_guideline_text(text: str) -> str:
    lines = [line.strip() for line in text.replace("\x00", "").splitlines()]
    return "\n".join(line for line in lines if line)

def identify_guideline_sections(text: str) -> dict:
    """Quick keyword-based section locator; useful even before LLM extraction."""
    keywords = {
        "eligibility": ["eligible", "eligibility", "applicant"],
        "funding": ["budget", "funding", "maximum award", "grant amount"],
        "timeline": ["deadline", "duration", "months", "project period"],
        "submission": ["submit", "submission", "required documents"],
        "evaluation": ["evaluation", "scoring", "selection criteria"],
    }
    lower = text.lower()
    return {section: [word for word in terms if word in lower]
            for section, terms in keywords.items()}

def extract_constraints(guideline_text: str) -> str:
    text = clean_guideline_text(guideline_text)
    if len(text) < 100:
        raise ValueError("Guideline text is too short to analyze.")
    system = """You are a grant-compliance analyst. Extract only requirements supported
by the supplied guideline. Never invent a deadline, cap, or eligibility rule.
Mark missing or ambiguous information as NOT SPECIFIED / NEEDS HUMAN REVIEW.
Return clear headings: Program Summary, Eligibility, Funding/Budget Limits,
Deadlines, Project Duration, Required Sections/Documents, Restrictions,
Evaluation Criteria, Ambiguities, Source Evidence (short quotes/page markers)."""
    return ask_llm(system, f"Analyze this guideline:\n\n{text[:26000]}", max_tokens=3500)
