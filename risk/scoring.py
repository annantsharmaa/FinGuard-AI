"""
Agent 3: Risk scoring.
The SCORE is always deterministic math — never LLM-generated. The LLM is only
ever used (optionally) to turn the failed-rule list into a readable narrative.
This separation is the single most defensible design decision in the project.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def compute_risk_score(findings):
    """
    findings: list of dicts with keys rule_name, passed, detail
    Returns (score, breakdown) where breakdown maps rule_name -> points added.
    """
    breakdown = {}
    for f in findings:
        if not f["passed"]:
            points = config.RISK_WEIGHTS.get(f["rule_name"], 0)
            if points:
                breakdown[f["rule_name"]] = points

    score = min(100, sum(breakdown.values()))
    return score, breakdown


def determine_status(score):
    return "pending_review" if score >= config.REVIEW_THRESHOLD else "auto_cleared"


def build_reasons_fallback(breakdown, findings):
    """
    Deterministic fallback narrative (used if no LLM is available/running).
    Bullet list of failed rules with their detail text — always accurate
    because it's built directly from the findings, not generated.
    """
    if not breakdown:
        return "No compliance issues detected."
    detail_map = {f["rule_name"]: f["detail"] for f in findings}
    lines = [f"- {rule.replace('_', ' ').title()}: {detail_map.get(rule, '')}" for rule in breakdown]
    return "\n".join(lines)


def build_reasons_llm(breakdown, findings, llm_call_fn):
    """
    Optional LLM narrative pass. Takes the already-computed breakdown/findings
    (facts) and asks the LLM only to phrase them clearly — it cannot change
    the score or invent new issues.
    """
    if not breakdown:
        return "No compliance issues detected."
    detail_map = {f["rule_name"]: f["detail"] for f in findings}
    facts = "\n".join(f"- {rule}: {detail_map.get(rule, '')}" for rule in breakdown)
    prompt = (
        "Rewrite the following compliance issues as a short, clear bulleted list "
        "for a financial audit report. Do not add any issues that are not listed, "
        "and do not remove any.\n\n" + facts
    )
    try:
        return llm_call_fn(prompt).strip()
    except Exception:
        return build_reasons_fallback(breakdown, findings)
