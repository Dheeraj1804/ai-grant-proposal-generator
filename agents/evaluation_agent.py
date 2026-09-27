"""Rubric-based proposal review. Scores are AI-generated estimates, not official."""
import json
from utils.llm_client import ask_llm

RUBRIC = {
    "Need and Significance": "Problem importance, evidence, and target population clarity",
    "Innovation": "Distinctiveness and rationale versus existing approaches",
    "Methodology and Feasibility": "Work plan, methods, resources, risks, realistic scope",
    "Impact and Evaluation": "Outcomes, measurable indicators, evaluation plan",
    "Budget and Timeline": "Justification, arithmetic transparency, milestone realism",
    "Clarity and Guideline Alignment": "Organization, completeness, and response to stated criteria",
}

def evaluate_proposal(proposal: str, constraints: str = "") -> str:
    rubric_text = "\n".join(f"- {k}: {v} (0–5 points)" for k, v in RUBRIC.items())
    system = """Review the proposal fairly. Give each criterion 0–5 points, where
0=absent and 5=strongly addressed. Return a Markdown score table, total out of 30,
strengths, critical weaknesses, missing evidence, compliance questions, and prioritized
recommendations. Cite proposal section names as evidence. Do not invent facts. State that
this is an AI-assisted preliminary review, not an official funder score."""
    return ask_llm(system, f"RUBRIC:\n{rubric_text}\n\nGUIDELINES:\n{constraints}\n\nPROPOSAL:\n{proposal}", max_tokens=3000)

def parse_scores(evaluation_text: str) -> dict:
    """Optional best-effort structured score extraction; never treat as authoritative."""
    system = """Extract scores from this evaluation into JSON: {criterion: score}.
Use only explicitly stated scores. Return JSON only; if unavailable return {}."""
    raw = ask_llm(system, evaluation_text, max_tokens=1000)
    try:
        return json.loads(raw.replace("```json", "").replace("```", "").strip())
    except json.JSONDecodeError:
        return {"parse_error": "Could not parse scores", "raw_response": raw}
