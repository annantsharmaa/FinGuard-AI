"""
Agent 2: Compliance checks.
All checks here are deterministic (regex/keyword) on purpose — reliability
matters more than nuance for "is a field present or not." Each check returns
a dict: {rule_name, passed, detail}. The optional LLM policy-violation pass
lives at the bottom, clearly separated from the deterministic checks.
"""

import re
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def check_signature(text):
    pattern = r"(signature|signed by|/s/|authorized signatory)"
    passed = bool(re.search(pattern, text, re.IGNORECASE))
    return {
        "rule_name": "missing_signature",
        "passed": passed,
        "detail": "Signature block found." if passed else "No signature block detected.",
    }


def check_invoice_number(text):
    pattern = r"invoice\s*#?\s*[:\-]?\s*[A-Za-z0-9\-]+"
    passed = bool(re.search(pattern, text, re.IGNORECASE))
    return {
        "rule_name": "missing_invoice_number",
        "passed": passed,
        "detail": "Invoice number found." if passed else "No invoice number detected.",
    }


def check_gst_number(text):
    passed = bool(re.search(config.GST_REGEX, text))
    return {
        "rule_name": "missing_gst",
        "passed": passed,
        "detail": "GST number found." if passed else "No valid GST number detected.",
    }


def check_payment_terms(text):
    text_lower = text.lower()
    found_terms = [term for term in config.ALLOWED_PAYMENT_TERMS if term in text_lower]
    has_any_payment_term_mention = bool(re.search(r"net\s*\d+", text_lower))

    if found_terms:
        passed = True
        detail = f"Approved payment term found: {found_terms[0]}"
    elif has_any_payment_term_mention:
        passed = False
        detail = "Payment term present but not in approved list (Net 15/30/45/60)."
    else:
        passed = False
        detail = "No payment terms found in document."
    return {
        "rule_name": "incorrect_payment_terms",
        "passed": passed,
        "detail": detail,
    }


def check_vendor_address(text):
    pattern = r"(vendor address|address\s*[:\-])"
    passed = bool(re.search(pattern, text, re.IGNORECASE))
    return {
        "rule_name": "missing_vendor_address",
        "passed": passed,
        "detail": "Vendor address found." if passed else "No vendor address detected.",
    }


def check_amount_mismatch(text):
    """
    Looks for a subtotal + tax + total pattern and verifies subtotal + tax == total
    (within a small tolerance). If the fields aren't present, we don't fail the
    check — we simply can't verify, and that's reported as passed with a caveat
    rather than a false positive.
    """
    amounts = re.findall(r"(subtotal|tax|total)\s*[:\-]?\s*\$?\s*([\d,]+\.?\d*)", text, re.IGNORECASE)
    values = {k.lower(): float(v.replace(",", "")) for k, v in amounts}

    if {"subtotal", "tax", "total"}.issubset(values.keys()):
        expected_total = values["subtotal"] + values["tax"]
        passed = abs(expected_total - values["total"]) < 0.01
        detail = (
            "Amounts reconcile."
            if passed
            else f"Mismatch: subtotal ({values['subtotal']}) + tax ({values['tax']}) "
                 f"!= total ({values['total']})."
        )
    else:
        passed = True
        detail = "Could not locate subtotal/tax/total triplet to verify — skipped."

    return {
        "rule_name": "amount_mismatch",
        "passed": passed,
        "detail": detail,
    }


DETERMINISTIC_CHECKS = [
    check_signature,
    check_invoice_number,
    check_gst_number,
    check_payment_terms,
    check_vendor_address,
    check_amount_mismatch,
]


def run_all_checks(text):
    """Run every deterministic rule and return a list of finding dicts."""
    return [check(text) for check in DETERMINISTIC_CHECKS]


def run_llm_policy_check(text, llm_call_fn):
    """
    Optional judgment pass. Only used for things regex genuinely can't catch,
    e.g. unusual indemnity/termination clauses. `llm_call_fn` is injected so
    this module has no hard dependency on Ollama being installed/running.
    Returns a finding dict; passed=True (no violation) unless the LLM flags one.
    """
    prompt = (
        "You are a compliance reviewer. Read the following document text and "
        "reply with either 'NONE' if there are no unusual or one-sided clauses, "
        "or a single short sentence describing the most concerning clause if one exists.\n\n"
        f"DOCUMENT:\n{text[:4000]}"
    )
    response = llm_call_fn(prompt).strip()
    if response.upper().startswith("NONE"):
        return {"rule_name": "policy_violation", "passed": True, "detail": "No policy issues flagged by LLM review."}
    return {"rule_name": "policy_violation", "passed": False, "detail": response}
