"""
Agent 1 (part 2): Document type classification.
Simple, explainable keyword scoring — deliberately not an LLM call.
Fast, deterministic, and you can defend exactly why a doc got its label.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def classify_doc_type(text):
    text_lower = text.lower()
    scores = {}
    for doc_type, keywords in config.DOC_TYPE_KEYWORDS.items():
        scores[doc_type] = sum(1 for kw in keywords if kw in text_lower)

    best_type = max(scores, key=scores.get)
    if scores[best_type] == 0:
        return "unknown"
    return best_type
