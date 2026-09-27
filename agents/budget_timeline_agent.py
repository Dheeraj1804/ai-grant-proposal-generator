"""Build a transparent draft budget and milestone plan."""
import json
from utils.llm_client import ask_llm

def create_budget_timeline(idea: str, duration: str, budget_cap: str,
                           currency: str, constraints: str) -> str:
    system = """Create a planning proposal with two sections: itemized budget and timeline.
For each budget row include item, quantity/assumption, unit cost, total, justification.
Show arithmetic and subtotal/total. If values are unknown, label estimates as placeholders.
Never claim costs are verified. Timeline should include phase, start/end month, deliverable,
dependency. Check total against cap if supplied; flag any overage. Output Markdown tables."""
    user = f"""Project: {idea}
Duration: {duration or 'Not specified'}
Budget cap: {budget_cap or 'Not specified'}
Currency: {currency or 'Not specified'}
Guideline constraints: {constraints or 'Not supplied'}"""
    return ask_llm(system, user, max_tokens=3000)

def validate_budget_inputs(budget_cap: str, duration: str) -> list:
    issues = []
    if budget_cap.strip():
        try:
            if float(budget_cap) <= 0:
                issues.append("Budget cap should be greater than zero.")
        except ValueError:
            issues.append("Budget cap must be numeric (without currency symbols).")
    if duration.strip() and len(duration.strip()) < 2:
        issues.append("Please provide a clearer project duration.")
    return issues
