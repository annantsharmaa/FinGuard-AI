"""
FinGuard AI — Streamlit UI.
Run with: streamlit run app.py
"""

import os
import sys
import tempfile

import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db import db
from agents.pipeline import run_pipeline
from reporting.generate_report import build_markdown_report
from ui import theme

st.set_page_config(page_title="FinGuard AI", page_icon="📑", layout="wide")
theme.inject_css()
db.init_db()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown(
        """
        <div style="font-family:'Newsreader',serif;font-size:1.4rem;font-weight:600;
                    color:#F4F5F7;margin-bottom:0;">FinGuard AI</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;
                    letter-spacing:0.12em;text-transform:uppercase;color:#9AA3BC;
                    margin-bottom:1.1rem;">Compliance &amp; Audit Assistant</div>
        """,
        unsafe_allow_html=True,
    )
    page = st.radio("NAVIGATE", ["Upload & Analyze", "Review Queue", "Audit Log", "All Documents"],
                     label_visibility="visible")
    st.markdown("<hr/>", unsafe_allow_html=True)
    USE_LLM = st.checkbox("Use local LLM (Ollama)", value=True,
                           help="Uncheck to run with deterministic checks only — useful if Ollama isn't running.")
    st.markdown(
        """
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#7C86A3;
                    margin-top:1.5rem;line-height:1.5;">
        Deterministic logic decides every fact.<br/>The LLM only explains it.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------- Upload & Analyze ----------------
if page == "Upload & Analyze":
    theme.page_header("Upload a Document", "Stage 1 · Parser → Compliance → Risk → Report")

    col_upload, col_spacer = st.columns([2, 1])
    with col_upload:
        uploaded = st.file_uploader("PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
        run_clicked = st.button("Run Analysis", type="primary", disabled=uploaded is None)

    if uploaded and run_clicked:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        with st.spinner("Running Parser → Compliance → Risk → Report agents..."):
            try:
                doc_id, _ = run_pipeline(tmp_path, use_llm=USE_LLM)
                st.session_state["last_doc_id"] = doc_id
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
            finally:
                os.unlink(tmp_path)

    if st.session_state.get("last_doc_id"):
        doc_id = st.session_state["last_doc_id"]
        doc = db.get_document(doc_id)
        findings = db.get_findings(doc_id)
        risk = db.get_risk_score(doc_id)
        log = db.get_agent_log(doc_id)

        if doc and risk:
            issues = [f for f in findings if not f["passed"]]

            theme.page_header(doc["filename"], f"Document #{doc_id} · {doc['doc_type']}")

            left, right = st.columns([1, 1.6])

            with left:
                theme.card_start("Risk Assessment")
                theme.stamp(risk["score"], risk["status"],
                            caption=f"{len(issues)} issue(s) of {len(findings)} checks")
                st.markdown("**Reasons**")
                st.markdown(risk["reasons_text"] or "N/A")
                theme.card_end()

                with st.expander("Agent Actions"):
                    theme.render_agent_log(log)

            with right:
                theme.card_start("Compliance Findings")
                theme.render_findings(findings)
                theme.card_end()

                if issues:
                    theme.card_start("Recommendations")
                    st.markdown("\n".join(
                        f"- Resolve **{f['rule_name'].replace('_', ' ')}** before final approval."
                        for f in issues
                    ))
                    theme.card_end()

            st.download_button(
                "Download Markdown Report",
                data=build_markdown_report(doc_id),
                file_name=f"finguard_report_{doc_id}.md",
                mime="text/markdown",
            )

# ---------------- Review Queue ----------------
elif page == "Review Queue":
    theme.page_header("Pending Human Review", "Documents scoring ≥ 60 require sign-off")
    pending = db.list_pending_review()

    if not pending:
        theme.card_start()
        st.markdown("Queue is empty — nothing currently needs review.")
        theme.card_end()

    for item in pending:
        doc = db.get_document(item["id"])
        findings = db.get_findings(item["id"])
        risk = db.get_risk_score(item["id"])

        with st.expander(f"#{item['id']} · {item['filename']} · Risk {item['score']}/100"):
            col_a, col_b = st.columns([1, 1.6])
            with col_a:
                theme.stamp(risk["score"], risk["status"])
                st.markdown(risk["reasons_text"] or "")
            with col_b:
                theme.render_findings(findings)

            reviewer = st.text_input("Reviewer name", key=f"reviewer_{item['id']}")
            notes = st.text_input("Notes (optional)", key=f"notes_{item['id']}")
            c1, c2 = st.columns(2)
            if c1.button("Approve", key=f"approve_{item['id']}", type="primary"):
                db.insert_human_review(item["id"], reviewer or "unknown", "approved", notes)
                st.rerun()
            if c2.button("Reject", key=f"reject_{item['id']}"):
                db.insert_human_review(item["id"], reviewer or "unknown", "rejected", notes)
                st.rerun()

# ---------------- Audit Log ----------------
elif page == "Audit Log":
    theme.page_header("Audit Log", "Every agent input/output, per document")
    doc_id = st.number_input("Document ID", min_value=1, step=1)
    if st.button("Load Log"):
        log = db.get_agent_log(doc_id)
        theme.card_start(f"Document #{doc_id}")
        theme.render_agent_log(log)
        theme.card_end()

# ---------------- All Documents ----------------
elif page == "All Documents":
    theme.page_header("All Documents", "Full processing history")
    docs = db.list_all_documents()
    theme.card_start()
    theme.render_documents_table(docs)
    theme.card_end()
