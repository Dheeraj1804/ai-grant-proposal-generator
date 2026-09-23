"""Revise a proposal using evaluation feedback and QA findings."""
from utils.llm_client import ask_llm

def refine_proposal(proposal: str, evaluation: str, qa_report: str,
                    constraints: str = "", preserve_facts: bool = True) -> str:
    fact_rule = ("Do not add unsupported facts, citations, partnerships, results, or costs. "
                 "Use [NEEDS INPUT] for missing facts.") if preserve_facts else \
                "Clearly label any assumptions and items requiring verification."
    system = f"""You are a grant proposal editor. Revise the draft using the review feedback.
Prioritize critical weaknesses, improve clarity and alignment, and retain useful content.
{fact_rule}
Return the complete revised proposal with clear headings. End with a short change log."""
    user = f"""GUIDELINE CONSTRAINTS:\n{constraints}\n\nEVALUATION:\n{evaluation}
\nQA FINDINGS:\n{qa_report}\n\nDRAFT:\n{proposal}"""
    return ask_llm(system, user, temperature=0.25, max_tokens=4500)

def compare_versions(original: str, revised: str) -> dict:
    """Simple local metrics; this does not determine whether revision is substantively better."""
    return {
        "original_words": len(original.split()),
        "revised_words": len(revised.split()),
        "word_change": len(revised.split()) - len(original.split()),
        "original_chars": len(original),
        "revised_chars": len(revised),
    }
