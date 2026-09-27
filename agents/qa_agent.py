"""Deterministic quality checks for proposal completeness and basic consistency."""
import re

REQUIRED_SECTIONS = [
    "Executive Summary", "Problem Statement", "Objectives", "Methodology",
    "Expected Outcomes", "Monitoring", "Risk", "Budget", "Timeline", "Sustainability"
]

def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))

def find_missing_sections(text: str, required_sections=None) -> list:
    required = required_sections or REQUIRED_SECTIONS
    lower = text.lower()
    return [section for section in required if section.lower() not in lower]

def find_placeholders(text: str) -> list:
    patterns = [r"\[NEEDS INPUT\]", r"\[INSERT[^\]]*\]", r"\bTBD\b", r"\bTODO\b"]
    found = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    return sorted(set(found), key=str.lower)

def check_budget_cap(text: str, cap: float | None) -> str:
    if cap is None:
        return "Not checked — no budget cap supplied."
    # Conservative: do not guess which currency amount is the final total.
    amounts = re.findall(r"(?:total\s*(?:requested\s*)?(?:budget|cost)?\s*[:\-]?\s*)"
                         r"(?:[$€£]\s*)?([\d,]+(?:\.\d{1,2})?)", text, re.I)
    if not amounts:
        return "Unclear — could not reliably identify a total budget. Review manually."
    total = float(amounts[-1].replace(",", ""))
    return f"Potential over-cap: {total:,.2f} > {cap:,.2f}" if total > cap else \
           f"Parsed total {total:,.2f} is within cap {cap:,.2f} (verify manually)."

def run_quality_checks(proposal: str, budget_cap: float | None = None,
                       required_sections=None) -> dict:
    missing = find_missing_sections(proposal, required_sections)
    placeholders = find_placeholders(proposal)
    wc = word_count(proposal)
    checks = [
        {"check": "Minimum length (500 words)", "status": "Pass" if wc >= 500 else "Review",
         "details": f"{wc} words"},
        {"check": "Required sections", "status": "Pass" if not missing else "Review",
         "details": "All found" if not missing else ", ".join(missing)},
        {"check": "Unresolved placeholders", "status": "Review" if placeholders else "Pass",
         "details": ", ".join(placeholders) if placeholders else "None detected"},
        {"check": "Budget cap", "status": "Review",
         "details": check_budget_cap(proposal, budget_cap)},
    ]
    return {"word_count": wc, "missing_sections": missing,
            "placeholders": placeholders, "checks": checks}

def format_quality_report(report: dict) -> str:
    lines = ["## Automated QA Report", f"- Word count: {report['word_count']}",
             f"- Missing sections: {', '.join(report['missing_sections']) or 'None detected'}",
             f"- Placeholders: {', '.join(report['placeholders']) or 'None detected'}",
             "", "| Check | Status | Details |", "|---|---|---|"]
    for item in report["checks"]:
        lines.append(f"| {item['check']} | {item['status']} | {item['details']} |")
    lines.append("\n*Automated checks are indicators only; manually verify all grant requirements.*")
    return "\n".join(lines)
