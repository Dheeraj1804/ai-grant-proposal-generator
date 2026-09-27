"""Generate a structured proposal draft."""
from langchain_core.prompts import PromptTemplate
from utils.llm_client import ask_llm

PROPOSAL_PROMPT = PromptTemplate.from_template("""
Create a grant proposal draft using the project details and grant requirements below.
Do not fabricate institutional approvals, partnerships, citations, or measured results.
Use [NEEDS INPUT] where essential information is missing.
Include: Title, Executive Summary, Problem Statement, Need/Evidence, Goals,
SMART Objectives, Methodology/Work Packages, Innovation, Expected Outcomes/Impact,
Monitoring & Evaluation, Risk Mitigation, Sustainability, Budget Narrative,
Timeline/Milestones, Team/Capabilities, and References/Supporting Evidence.
Align wording to the grant criteria while clearly labeling assumptions.

PROJECT IDEA: {idea}
ORGANIZATION / APPLICANT: {organization}
TARGET POPULATION: {population}
PROJECT DURATION: {duration}
KNOWN RESOURCES: {resources}
GUIDELINE CONSTRAINTS:
{constraints}
""")

def generate_proposal(idea: str, organization: str, population: str, duration: str,
                      resources: str, constraints: str) -> str:
    if not idea.strip():
        raise ValueError("Enter a project idea.")
    prompt = PROPOSAL_PROMPT.format(
        idea=idea, organization=organization or "[NEEDS INPUT]",
        population=population or "[NEEDS INPUT]", duration=duration or "[NEEDS INPUT]",
        resources=resources or "[NEEDS INPUT]", constraints=constraints or "Not supplied"
    )
    return ask_llm(
        "You are an experienced grant-writing assistant. Produce a useful first draft, not a guarantee of funding.",
        prompt, temperature=0.35, max_tokens=4500
    )
