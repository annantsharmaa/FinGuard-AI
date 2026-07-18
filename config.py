"""
Central configuration for FinGuard AI.
Keep all thresholds/weights here so they're easy to justify and tune
in one place (and easy to point to in an interview as "versioned policy").
"""

import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "finguard.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "db", "schema.sql")

# --- Ollama / LLM settings ---
OLLAMA_MODEL = "llama3"
OLLAMA_HOST = "http://localhost:11434"
LLM_TIMEOUT_SECONDS = 60

# --- Risk scoring weights (deterministic, not LLM-generated) ---
RISK_WEIGHTS = {
    "missing_signature": 25,
    "missing_invoice_number": 15,
    "missing_gst": 20,
    "incorrect_payment_terms": 15,
    "amount_mismatch": 30,
    "missing_vendor_address": 10,
    "policy_violation": 20,
}

# Score at/above this threshold requires human review before clearing
REVIEW_THRESHOLD = 60

# --- Compliance rule config ---
ALLOWED_PAYMENT_TERMS = ["net 15", "net 30", "net 45", "net 60"]

# Indian GST number format: 2 digits, 5 letters, 4 digits, 1 letter, 1 digit, 1 'Z', 1 alphanumeric
GST_REGEX = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z\d]\b"

# --- Document type classification keywords ---
DOC_TYPE_KEYWORDS = {
    "invoice": ["invoice number", "invoice #", "bill to", "amount due", "gst"],
    "contract": ["agreement", "party of the first part", "hereinafter referred to",
                 "terms and conditions", "witnesseth"],
    "purchase_order": ["purchase order", "po number", "ship to"],
}
