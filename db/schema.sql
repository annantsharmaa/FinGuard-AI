CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    doc_type TEXT,
    raw_text TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    rule_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    detail TEXT
);

CREATE TABLE IF NOT EXISTS risk_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    score INTEGER NOT NULL,
    breakdown_json TEXT,
    reasons_text TEXT,
    status TEXT NOT NULL DEFAULT 'auto_cleared',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    agent_name TEXT NOT NULL,
    input_summary TEXT,
    output_summary TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS human_review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    reviewer TEXT,
    decision TEXT NOT NULL,
    notes TEXT,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
