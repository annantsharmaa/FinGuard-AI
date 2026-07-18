"""
Agent 1 (part 1): Document text extraction.
Deterministic — no LLM involved. Supports PDF, DOCX, TXT.
"""

import os


def extract_text(file_path):
    """Return raw text from a PDF, DOCX, or TXT file."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == ".pdf":
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            raise ImportError(
                "PyPDF2 is not installed. Run: pip install PyPDF2"
            )
        reader = PdfReader(file_path)
        text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
        return "\n".join(text)

    elif ext == ".docx":
        try:
            import docx
        except ImportError:
            raise ImportError(
                "python-docx is not installed. Run: pip install python-docx"
            )
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .pdf, .docx, or .txt")
