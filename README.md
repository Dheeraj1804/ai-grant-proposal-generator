# AI Grant Proposal Generator — Deep Modular Version

## Architecture
- `guideline_agent.py`: PDF text extraction, cleanup, keyword section signals, guideline analysis.
- `constraint_agent.py`: JSON checklist extraction, schema sanity checks, proposal-vs-constraint review.
- `proposal_agent.py`: PromptTemplate-driven sectioned draft.
- `budget_timeline_agent.py`: separate budget and milestone plan.
- `evaluation_agent.py`: AI rubric review (six criteria, 0–5 each).
- `qa_agent.py`: deterministic completeness, placeholder, word-count, and cautious budget checks.
- `refinement_agent.py`: revision loop and version metrics.
- `utils/llm_client.py`: shared OpenRouter client with bounded token request.
- `app.py`: Streamlit UI/orchestration.

This is sequential Python orchestration, not CrewAI/LangGraph. LLM scores are preliminary, not validated funder scores. QA budget parsing is heuristic and needs human review. Scanned PDFs may require OCR.

## Windows setup (VS Code terminal / PowerShell)
1. Extract the ZIP.
2. Open the extracted project folder in VS Code.
3. Create virtual environment:
   `py -3.12 -m venv venv`
   If Python 3.12 launcher is unavailable, use `python -m venv venv`.
4. Activate:
   `.\venv\Scripts\Activate.ps1`
   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.
5. Install:
   `python -m pip install --upgrade pip`
   `python -m pip install -r requirements.txt`
6. Copy `.env.example` to `.env` in the same folder as `app.py`.
7. Add your OpenRouter key and model to `.env`. Never commit/share `.env`.
8. Start:
   `python -m streamlit run app.py`
9. Open the local URL shown in the terminal (usually http://localhost:8501).

## Troubleshooting
- 402/payment/credits: check OpenRouter credits/model; this is not necessarily a bad API key.
- Missing key: ensure `.env` is beside `app.py`, key has no quotes/spaces, and restart Streamlit.
- PDF has no text: likely scanned; OCR is not included.
- Avoid pasting confidential grant or personal data into a third-party LLM without approval.
