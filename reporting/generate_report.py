"""
Agent 4: Report generation.
Pulls everything back out of the DB for a given document_id and renders the
Markdown report. Pure formatting — no new facts are introduced here.
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import db


def build_markdown_report(document_id):
    doc = db.get_document(document_id)
    findings = db.get_findings(document_id)
    risk = db.get_risk_score(document_id)
    agent_log = db.get_agent_log(document_id)

    if not doc:
        return f"# Error\nNo document found with id {document_id}."

    issues = [f for f in findings if not f["passed"]]
    passed = [f for f in findings if f["passed"]]

    lines = []
    lines.append(f"# Compliance Report — {doc['filename']}\n")
    lines.append(f"**Document Type:** {doc['doc_type']}  ")
    lines.append(f"**Document ID:** {doc['id']}  ")
    lines.append(f"**Uploaded At:** {doc['uploaded_at']}\n")

    lines.append("## Summary")
    if issues:
        lines.append(
            f"{len(issues)} issue(s) found out of {len(findings)} checks run. "
            f"Risk score: **{risk['score']}/100** ({risk['status'].replace('_', ' ')})."
        )
    else:
        lines.append(f"No issues found. Risk score: **{risk['score']}/100**.")
    lines.append("")

    lines.append("## Issues Found")
    if issues:
        for f in issues:
            lines.append(f"- **{f['rule_name'].replace('_', ' ').title()}**: {f['detail']}")
    else:
        lines.append("None.")
    lines.append("")

    lines.append("## Passed Checks")
    for f in passed:
        lines.append(f"- {f['rule_name'].replace('_', ' ').title()}")
    lines.append("")

    lines.append("## Risk Score")
    lines.append(f"**{risk['score']}/100**\n")
    lines.append("**Reasons:**")
    lines.append(risk["reasons_text"] or "N/A")
    lines.append("")

    lines.append("## Recommendations")
    if issues:
        for f in issues:
            lines.append(f"- Resolve: {f['rule_name'].replace('_', ' ')} before final approval.")
    else:
        lines.append("- No action required.")
    lines.append("")

    lines.append(f"## Timestamp\n{datetime.now().isoformat()}\n")

    lines.append("## Agent Actions")
    for entry in agent_log:
        lines.append(f"- `{entry['timestamp']}` **{entry['agent_name']}**: {entry['output_summary']}")

    return "\n".join(lines)


def save_report_to_file(document_id, output_dir="reports"):
    os.makedirs(output_dir, exist_ok=True)
    content = build_markdown_report(document_id)
    path = os.path.join(output_dir, f"report_{document_id}.md")
    with open(path, "w") as f:
        f.write(content)
    return path
