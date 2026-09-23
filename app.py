import streamlit as st
from agents.guideline_agent import extract_pdf_text, extract_constraints
from agents.constraint_agent import extract_constraint_checklist, validate_constraint_data
from agents.proposal_agent import generate_proposal
from agents.budget_timeline_agent import create_budget_timeline, validate_budget_inputs
from agents.evaluation_agent import evaluate_proposal
from agents.qa_agent import run_quality_checks, format_quality_report
from agents.refinement_agent import refine_proposal, compare_versions

st.set_page_config(page_title="AI Grant Proposal Generator", layout="wide")
st.title("AI-Based Research Grant Proposal Generator & Evaluator")
st.caption("Prototype: AI-assisted drafting and preliminary checks. Human verification is required.")

def save_text(label, text, filename):
    st.download_button(label, data=text, file_name=filename, mime="text/markdown")

with st.sidebar:
    st.header("1. Grant guideline")
    uploaded = st.file_uploader("Upload guideline PDF (optional)", type=["pdf"])
    pasted_guideline = st.text_area("Or paste guideline text", height=180)
    st.header("2. Project details")
    idea = st.text_area("Project idea *", placeholder="Describe the research problem and proposed solution.")
    organization = st.text_input("Applicant / organization")
    population = st.text_input("Target population")
    duration = st.text_input("Project duration", placeholder="e.g., 12 months")
    resources = st.text_area("Known resources / team / facilities")
    budget_cap = st.text_input("Budget cap (number only, optional)")
    currency = st.text_input("Currency", value="USD")

guideline_text = pasted_guideline
if uploaded:
    try:
        guideline_text = extract_pdf_text(uploaded.getvalue())
        st.sidebar.success("PDF text extracted.")
    except Exception as e:
        st.sidebar.error(str(e))

col1, col2 = st.columns(2)
with col1:
    st.subheader("Guideline Analysis")
    if st.button("Extract constraints", disabled=not guideline_text.strip()):
        with st.spinner("Analyzing guideline..."):
            st.session_state["constraints_summary"] = extract_constraints(guideline_text)
            st.session_state["constraint_data"] = extract_constraint_checklist(guideline_text)
    if "constraints_summary" in st.session_state:
        st.markdown(st.session_state["constraints_summary"])
        st.json(st.session_state.get("constraint_data", {}))
with col2:
    st.subheader("Budget & Timeline")
    if st.button("Generate budget and timeline", disabled=not idea.strip()):
        issues = validate_budget_inputs(budget_cap, duration)
        if issues:
            st.warning("\n".join(issues))
        else:
            st.session_state["budget_timeline"] = create_budget_timeline(
                idea, duration, budget_cap, currency,
                st.session_state.get("constraints_summary", guideline_text))
    if "budget_timeline" in st.session_state:
        st.markdown(st.session_state["budget_timeline"])
        save_text("Download budget & timeline", st.session_state["budget_timeline"], "budget_timeline.md")

st.divider()
st.subheader("Proposal Workflow")
if st.button("Generate proposal draft", disabled=not idea.strip()):
    with st.spinner("Drafting proposal..."):
        st.session_state["proposal"] = generate_proposal(
            idea, organization, population, duration, resources,
            st.session_state.get("constraints_summary", guideline_text))
if "proposal" in st.session_state:
    st.markdown(st.session_state["proposal"])
    save_text("Download proposal", st.session_state["proposal"], "grant_proposal.md")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Run AI evaluation"):
            with st.spinner("Evaluating..."):
                st.session_state["evaluation"] = evaluate_proposal(
                    st.session_state["proposal"],
                    st.session_state.get("constraints_summary", guideline_text))
    with c2:
        if st.button("Run rule-based QA"):
            cap = None
            try:
                cap = float(budget_cap) if budget_cap.strip() else None
            except ValueError:
                st.warning("Budget cap must be numeric.")
            report = run_quality_checks(st.session_state["proposal"], cap)
            st.session_state["qa"] = format_quality_report(report)
    with c3:
        if st.button("Refine proposal", disabled=not ("evaluation" in st.session_state and "qa" in st.session_state)):
            with st.spinner("Refining..."):
                st.session_state["revised"] = refine_proposal(
                    st.session_state["proposal"], st.session_state["evaluation"],
                    st.session_state["qa"],
                    st.session_state.get("constraints_summary", guideline_text))
    if "evaluation" in st.session_state:
        st.markdown("### AI Evaluation")
        st.markdown(st.session_state["evaluation"])
        save_text("Download evaluation", st.session_state["evaluation"], "evaluation.md")
    if "qa" in st.session_state:
        st.markdown(st.session_state["qa"])
    if "revised" in st.session_state:
        st.markdown("### Refined Proposal")
        st.markdown(st.session_state["revised"])
        st.json(compare_versions(st.session_state["proposal"], st.session_state["revised"]))
        save_text("Download refined proposal", st.session_state["revised"], "refined_proposal.md")

st.info("Workflow: Guideline/PDF → Constraint extraction → Proposal + Budget/Timeline → AI evaluation + deterministic QA → Refinement.")
