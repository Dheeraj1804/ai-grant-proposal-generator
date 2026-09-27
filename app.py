
import streamlit as st
import pdfplumber
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.prompts import PromptTemplate


# ==========================================
# 1. ENVIRONMENT SETUP
# ==========================================

# Load .env from the same directory as this app.py file
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

api_key = os.getenv("OPENROUTER_API_KEY")

st.set_page_config(
    page_title="AI Grant Proposal Generator",
    page_icon="📄",
    layout="wide"
)

st.title("AI Research Grant Proposal Generator & Evaluator")
st.write(
    "Generate, evaluate, and refine research grant proposals "
    "using AI and rule-based scoring."
)

if not api_key or not api_key.strip():
    st.error(
        "OpenRouter API key not found. "
        f"Expected .env file at: {ENV_PATH}. "
        "Check that the file is named .env (not .env.txt) and contains "
        "OPENROUTER_API_KEY=your_actual_key"
    )
    st.stop()

client = OpenAI(
    api_key=api_key.strip(),
    base_url="https://openrouter.ai/api/v1"
)


# ==========================================
# 2. REUSABLE AI RESPONSE FUNCTION
# ==========================================



def get_ai_response(messages, max_tokens=2000):

    try:
        response = client.chat.completions.create(
            # Try a non-reasoning chat model
            model="openai/gpt-4o-mini",

            messages=messages,

            # Output token limit
            max_tokens=max_tokens,

            # Ask for direct text output rather than extended reasoning
            temperature=0.4
        )

        if not response.choices:
            st.error("OpenRouter returned no response choices.")
            st.stop()

        choice = response.choices[0]
        content = choice.message.content

        # Check for empty response
        if not isinstance(content, str) or not content.strip():

            st.error(
                "The AI returned empty content. "
                "The response may have reached its token limit."
            )

            st.write("Model:", response.model)
            st.write("Finish reason:", choice.finish_reason)

            if response.usage:
                st.write(
                    "Completion tokens:",
                    response.usage.completion_tokens
                )

                st.write(
                    "Reasoning tokens:",
                    getattr(
                        response.usage.completion_tokens_details,
                        "reasoning_tokens",
                        None
                    )
                )

            st.stop()

        return content.strip()

    except Exception as e:
        st.error(f"OpenRouter API request failed: {e}")
        st.stop()

# ==========================================
# 3. PDF TEXT EXTRACTION
# ==========================================

def extract_text_from_pdf(uploaded_pdf):
    """
    Extracts readable text from an uploaded PDF.
    """

    extracted_text = ""

    try:
        with pdfplumber.open(uploaded_pdf) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    extracted_text += page_text + "\n"

    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        st.stop()

    return extracted_text.strip()


# ==========================================
# 4. RULE-BASED SCORING ENGINE
# ==========================================

def rule_based_score(proposal):
    """
    Preliminary heuristic score based on proposal content.
    This is not an official funder evaluation.
    """

    if not isinstance(proposal, str) or not proposal.strip():
        return 0, ["Proposal is empty. Scoring skipped."]

    text = proposal.lower()

    score = 0
    explanation = []

    if "methodology" in text:
        score += 20
        explanation.append("Methodology section present (+20)")

    if "impact" in text:
        score += 20
        explanation.append("Impact section present (+20)")

    if len(text) > 1500:
        score += 20
        explanation.append("Detailed proposal length (+20)")

    if "budget" in text:
        score += 20
        explanation.append("Budget discussion included (+20)")

    if "timeline" in text:
        score += 20
        explanation.append("Timeline included (+20)")

    return score, explanation


# ==========================================
# 5. USER INPUTS
# ==========================================

st.subheader("Grant Proposal Details")

uploaded_file = st.file_uploader(
    "Upload Grant Guideline PDF",
    type=["pdf"]
)

research_topic = st.text_input(
    "Enter Research Topic"
)

objectives = st.text_area(
    "Enter Research Objectives"
)


# ==========================================
# 6. MAIN WORKFLOW
# ==========================================

if st.button("Generate Proposal", type="primary"):

    # --------------------------------------
    # INPUT VALIDATION
    # --------------------------------------

    if uploaded_file is None:
        st.warning("Please upload a grant guideline PDF.")
        st.stop()

    if not research_topic.strip():
        st.warning("Please enter a research topic.")
        st.stop()

    if not objectives.strip():
        st.warning("Please enter research objectives.")
        st.stop()

    # --------------------------------------
    # EXTRACT PDF TEXT
    # --------------------------------------

    with st.spinner("Extracting grant guideline text..."):
        guideline_text = extract_text_from_pdf(uploaded_file)

    if not guideline_text:
        st.error(
            "No readable text found in the PDF. "
            "Please upload a text-based PDF. "
            "Scanned PDFs may require OCR."
        )
        st.stop()

    st.success("Grant guidelines extracted successfully.")

    # ======================================
    # AGENT 1: GUIDELINE INGESTION
    # ======================================

    st.subheader("Step 1: Guideline Analysis")

    with st.spinner("Analyzing grant guidelines..."):

        constraints = get_ai_response(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a grant guideline analysis assistant. "
                        "Extract eligibility requirements, funding limits, "
                        "evaluation criteria, deadlines, and key constraints. "
                        "Be concise and use bullet points. "
                        "Do not invent missing information."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Analyze these grant guidelines:\n\n"
                        + guideline_text[:6000]
                    )
                }
            ],
            max_tokens=1500
        )

    st.write(constraints)

    # ======================================
    # AGENT 2: PROPOSAL DRAFTING
    # ======================================

    st.subheader("Step 2: Proposal Generation")

    proposal_template = PromptTemplate(
        input_variables=[
            "topic",
            "objectives",
            "constraints"
        ],
        template="""
You are an expert research grant proposal writer.

Prepare a structured research proposal using the information below.

Grant Guidelines and Constraints:
{constraints}

Research Topic:
{topic}

Research Objectives:
{objectives}

Include the following sections:

1. Title
2. Abstract
3. Problem Statement
4. Research Objectives
5. Methodology
6. Expected Outcomes
7. Impact
8. Budget
9. Timeline

Instructions:
- Align the proposal with the grant constraints.
- Do not invent eligibility requirements or funding limits.
- Clearly identify assumptions where information is missing.
- Keep the proposal professional, clear, and well-structured.
"""
    )

    formatted_prompt = proposal_template.format(
        topic=research_topic,
        objectives=objectives,
        constraints=constraints
    )

    with st.spinner("Generating research proposal..."):

        proposal = get_ai_response(
            [
                {
                    "role": "system",
                    "content": (
                        "You are an expert research proposal drafting agent."
                    )
                },
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ],
            max_tokens=3000
        )

    if not proposal:
        st.error("Proposal generation failed. No proposal was returned.")
        st.stop()

    st.success("Proposal generated successfully.")

    with st.expander("View Generated Proposal", expanded=True):
        st.markdown(proposal)

    # ======================================
    # AGENT 3: PROPOSAL EVALUATION
    # ======================================

    st.subheader("Step 3: Proposal Evaluation")

    with st.spinner("Evaluating proposal..."):

        evaluation = get_ai_response(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a research grant proposal evaluator. "
                        "Evaluate clarity, feasibility, methodology, "
                        "expected impact, alignment with guidelines, "
                        "and missing information. "
                        "Provide constructive feedback. "
                        "Do not claim to represent an official funder."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Grant constraints:\n"
                        + constraints[:3000]
                        + "\n\nProposal to evaluate:\n"
                        + proposal[:10000]
                    )
                }
            ],
            max_tokens=1500
        )

    st.markdown("### AI Evaluation Feedback")
    st.write(evaluation)

    # ======================================
    # RULE-BASED SCORING
    # ======================================

    st.subheader("Step 4: Rule-Based Scoring")

    score, score_explanation = rule_based_score(proposal)

    st.metric(
        label="Preliminary Rule-Based Score",
        value=f"{score}/100"
    )

    st.caption(
        "This score checks for selected keywords and proposal length. "
        "It is a simple heuristic, not a validated grant assessment."
    )

    if score_explanation:
        for item in score_explanation:
            st.write(f"- {item}")

    # ======================================
    # AGENT 4: PROPOSAL REFINEMENT
    # ======================================

    st.subheader("Step 5: Proposal Refinement")

    with st.spinner("Refining proposal based on evaluation..."):

        refined_proposal = get_ai_response(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a research proposal refinement agent. "
                        "Improve the proposal using the evaluator's feedback. "
                        "Preserve factual accuracy. "
                        "Do not invent grant requirements, data, or results. "
                        "Clearly flag missing information or assumptions."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        "Original Proposal:\n"
                        + proposal[:10000]
                        + "\n\nEvaluation Feedback:\n"
                        + evaluation[:4000]
                        + "\n\nPlease provide the refined proposal."
                    )
                }
            ],
            max_tokens=3000
        )

    if not refined_proposal:
        st.error("Refinement failed. No refined proposal was returned.")
        st.stop()

    st.success("Proposal refinement completed.")

    with st.expander("View Refined Proposal", expanded=True):
        st.markdown(refined_proposal)

    # ======================================
    # FINAL SUMMARY
    # ======================================

    st.subheader("Workflow Completed")

    st.write(
        "The proposal has been generated, evaluated, "
        "scored using preliminary rules, and refined."
    )

    st.download_button(
        label="Download Refined Proposal",
        data=refined_proposal,
        file_name="refined_grant_proposal.txt",
        mime="text/plain"
    )