"""
All database access goes through this module. Every agent writes here,
which is what makes the "audit trail" claim on the resume literally true
rather than just a buzzword.
"""

import sqlite3
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def get_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    with open(config.SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def insert_document(filename, doc_type, raw_text):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO documents (filename, doc_type, raw_text) VALUES (?, ?, ?)",
        (filename, doc_type, raw_text),
    )
    conn.commit()
    doc_id = cur.lastrowid
    conn.close()
    return doc_id


def insert_finding(document_id, rule_name, passed, detail=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO findings (document_id, rule_name, passed, detail) VALUES (?, ?, ?, ?)",
        (document_id, rule_name, passed, detail),
    )
    conn.commit()
    conn.close()


def insert_risk_score(document_id, score, breakdown, reasons_text, status):
    conn = get_connection()
    conn.execute(
        """INSERT INTO risk_scores (document_id, score, breakdown_json, reasons_text, status)
           VALUES (?, ?, ?, ?, ?)""",
        (document_id, score, json.dumps(breakdown), reasons_text, status),
    )
    conn.commit()
    conn.close()


def insert_agent_log(document_id, agent_name, input_summary, output_summary):
    conn = get_connection()
    conn.execute(
        """INSERT INTO agent_log (document_id, agent_name, input_summary, output_summary)
           VALUES (?, ?, ?, ?)""",
        (document_id, agent_name, str(input_summary)[:2000], str(output_summary)[:2000]),
    )
    conn.commit()
    conn.close()


def insert_human_review(document_id, reviewer, decision, notes=""):
    conn = get_connection()
    conn.execute(
        """INSERT INTO human_review (document_id, reviewer, decision, notes)
           VALUES (?, ?, ?, ?)""",
        (document_id, reviewer, decision, notes),
    )
    conn.execute(
        "UPDATE risk_scores SET status = ? WHERE document_id = ?",
        (decision, document_id),
    )
    conn.commit()
    conn.close()


def get_document(document_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_findings(document_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM findings WHERE document_id = ?", (document_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_risk_score(document_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM risk_scores WHERE document_id = ? ORDER BY id DESC LIMIT 1",
        (document_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_agent_log(document_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM agent_log WHERE document_id = ? ORDER BY id ASC", (document_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_pending_review():
    conn = get_connection()
    rows = conn.execute(
        """SELECT d.id, d.filename, r.score, r.status
           FROM documents d JOIN risk_scores r ON d.id = r.document_id
           WHERE r.status = 'pending_review'
           ORDER BY r.score DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_all_documents():
    conn = get_connection()
    rows = conn.execute(
        """SELECT d.id, d.filename, d.doc_type, d.uploaded_at, r.score, r.status
           FROM documents d LEFT JOIN risk_scores r ON d.id = r.document_id
           ORDER BY d.id DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
