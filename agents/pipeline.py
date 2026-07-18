"""
Plain-Python pipeline — no CrewAI dependency. This is deliberately kept
working on its own: it's the "MVP checkpoint" from the build plan, it's
what the test suite runs against, and it's the fallback if CrewAI/Ollama
aren't available in a given environment. crew.py wraps these same
functions as CrewAI agents/tasks — it does not duplicate logic.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import db
from parsing.extract import extract_text
from parsing.classify import classify_doc_type
from compliance import rules
from risk import scoring
from llm.ollama_client import call_llm


def run_pipeline(file_path, use_llm=True):
    """
    Runs all four stages sequentially and returns the document_id.
    use_llm=False skips all Ollama calls and uses deterministic fallbacks
    only — useful for testing or offline environments with no model pulled.
    """
    filename = os.path.basename(file_path)

    # --- Agent 1: Parser ---
    raw_text = extract_text(file_path)
    doc_type = classify_doc_type(raw_text)
    document_id = db.insert_document(filename, doc_type, raw_text)
    db.insert_agent_log(
        document_id, "ParserAgent",
        input_summary=f"file={filename}",
        output_summary=f"doc_type={doc_type}, chars_extracted={len(raw_text)}",
    )

    # --- Agent 2: Compliance ---
    findings = rules.run_all_checks(raw_text)

    if use_llm:
        try:
            policy_finding = rules.run_llm_policy_check(raw_text, call_llm)
        except RuntimeError:
            policy_finding = {"rule_name": "policy_violation", "passed": True,
                               "detail": "LLM unavailable — policy check skipped."}
    else:
        policy_finding = {"rule_name": "policy_violation", "passed": True,
                           "detail": "LLM disabled — policy check skipped."}
    findings.append(policy_finding)

    for f in findings:
        db.insert_finding(document_id, f["rule_name"], f["passed"], f["detail"])

    failed_rules = [f["rule_name"] for f in findings if not f["passed"]]
    db.insert_agent_log(
        document_id, "ComplianceAgent",
        input_summary=f"{len(findings)} rules checked",
        output_summary=f"failed: {failed_rules}" if failed_rules else "all checks passed",
    )

    # --- Agent 3: Risk ---
    score, breakdown = scoring.compute_risk_score(findings)
    status = scoring.determine_status(score)

    if use_llm and breakdown:
        try:
            reasons_text = scoring.build_reasons_llm(breakdown, findings, call_llm)
        except Exception:
            reasons_text = scoring.build_reasons_fallback(breakdown, findings)
    else:
        reasons_text = scoring.build_reasons_fallback(breakdown, findings)

    db.insert_risk_score(document_id, score, breakdown, reasons_text, status)
    db.insert_agent_log(
        document_id, "RiskAgent",
        input_summary=f"breakdown={breakdown}",
        output_summary=f"score={score}, status={status}",
    )

    # --- Agent 4: Report ---
    from reporting.generate_report import build_markdown_report
    report_md = build_markdown_report(document_id)
    db.insert_agent_log(
        document_id, "ReportAgent",
        input_summary=f"document_id={document_id}",
        output_summary="report generated",
    )

    return document_id, report_md


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <file_path> [--no-llm]")
        sys.exit(1)

    db.init_db()
    use_llm = "--no-llm" not in sys.argv
    doc_id, report = run_pipeline(sys.argv[1], use_llm=use_llm)
    print(f"\nDocument ID: {doc_id}\n")
    print(report)
