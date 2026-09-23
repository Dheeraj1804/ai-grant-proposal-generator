"""Turn extracted guideline text into a structured checklist and validate a draft."""
import json
from utils.llm_client import ask_llm

def extract_constraint_checklist(guideline_text: str) -> dict:
    system = """Return valid JSON only, with keys:
eligibility (array), required_sections (array), required_documents (array),
budget_cap (number or null), currency (string or null), deadline (string or null),
project_duration (string or null), restrictions (array), evaluation_criteria (array),
uncertainties (array). Do not infer missing values; use null/empty arrays."""
    raw = ask_llm(system, guideline_text[:22000], max_tokens=2500)
    try:
        return json.loads(raw.replace("```json", "").replace("```", "").strip())
    except json.JSONDecodeError:
        return {"parse_error": "Model did not return valid JSON", "raw_response": raw}

def validate_constraint_data(data: dict) -> list:
    issues = []
    if not isinstance(data, dict):
        return ["Constraint data must be a JSON object."]
    for key in ("eligibility", "required_sections", "required_documents",
                "restrictions", "evaluation_criteria", "uncertainties"):
        if key in data and not isinstance(data[key], list):
            issues.append(f"'{key}' should be a list.")
    cap = data.get("budget_cap")
    if cap is not None and (not isinstance(cap, (int, float)) or cap <= 0):
        issues.append("'budget_cap' must be a positive number or null.")
    return issues

def check_proposal_against_constraints(proposal: str, constraints: dict) -> str:
    system = """Compare the proposal to the supplied constraint checklist.
Create a table with requirement, evidence found, status (Pass/Partial/Fail/Unclear),
and recommended action. Do not claim legal or funding compliance; flag human review."""
    return ask_llm(system, f"CONSTRAINTS:\n{constraints}\n\nPROPOSAL:\n{proposal}", max_tokens=3000)
