# FinGuard AI — Multi-Agent Compliance & Audit Assistant

A multi-agent system that parses financial documents, runs deterministic
compliance checks, computes a transparent risk score, and generates an
audit report — with a full, queryable audit trail and human-in-the-loop
approval for high-risk documents.

## Design principle

**Deterministic logic owns every fact. The LLM only ever explains facts in
prose — it never decides the risk score or invents compliance findings.**
Every check is regex/keyword-based and logged; the optional Ollama/Llama 3
pass is used only to (a) flag unusual policy language regex can't catch and
(b) turn a list of failed rules into readable narrative text.

This is why the pipeline works correctly even with the LLM completely
disabled (`--no-llm` flag / unchecked box in the UI) — see `agents/pipeline.py`.

## Status

The core pipeline (parsing → compliance → risk scoring → reporting → audit
log → human review) is implemented, tested, and has been run end-to-end
against the sample documents in `data/sample_docs/`. See `tests/test_rules.py`
for the passing test suite.

`agents/crew.py` wraps the same pipeline functions as a CrewAI `Crew` with
sequential task handoff. It requires `crewai` and a running local Ollama
server to exercise the LLM-reasoning parts; the underlying pipeline in
`agents/pipeline.py` has no such requirement and is what the Streamlit app
and test suite call directly.

## Setup

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Only needed if you want the LLM narrative/policy-check pass:
# 1. Install Ollama: https://ollama.com
# 2. ollama pull llama3
# 3. ollama serve
```

## Run the CLI pipeline

```bash
python agents/pipeline.py data/sample_docs/invoice_clean.txt
python agents/pipeline.py data/sample_docs/invoice_broken.txt --no-llm
```

## Run the tests

```bash
python -m unittest tests.test_rules -v
```

## Run the Streamlit app

```bash
streamlit run app.py
```

Pages:
- **Upload & Analyze** — upload a PDF/DOCX/TXT, run the full pipeline, view the report
- **Review Queue** — approve/reject documents flagged `pending_review` (score ≥ 60)
- **Audit Log** — inspect every agent's input/output for a given document ID
- **All Documents** — table of every processed document and its status

## Project structure

```
finguard-ai/
├── app.py                     Streamlit UI
├── config.py                  weights, thresholds, model settings
├── db/                        SQLite schema + access layer
├── parsing/                   text extraction + doc-type classification
├── compliance/                deterministic rule checks (+ optional LLM policy pass)
├── risk/                      transparent point-based scoring
├── reporting/                 Markdown report generation
├── agents/
│   ├── pipeline.py            plain-Python orchestrator (no CrewAI needed)
│   └── crew.py                CrewAI Agent/Task wrapper around the same pipeline
├── llm/ollama_client.py       thin wrapper around local Ollama calls
├── data/sample_docs/          sample clean/broken invoices + a contract
└── tests/test_rules.py        unit tests for rules + scoring
```

## Risk scoring weights

Defined in `config.py`, versioned like any other policy:

| Rule | Points |
|---|---|
| Amount mismatch | 30 |
| Missing signature | 25 |
| Missing GST | 20 |
| Policy violation (LLM-flagged) | 20 |
| Missing invoice number | 15 |
| Incorrect payment terms | 15 |
| Missing vendor address | 10 |

Score ≥ 60 → routed to the Review Queue for human approval before being
marked cleared.

## What I'd change for production

- Postgres instead of SQLite; add auth to the review queue
- Retry/timeout + circuit breaker around Ollama calls
- Versioned rule sets (so an auditor can see which policy version scored a
  given document)
- OCR fallback for scanned PDFs
