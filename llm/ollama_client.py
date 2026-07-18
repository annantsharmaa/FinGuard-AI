"""
Thin wrapper around a local Ollama server. Kept isolated so every other
module can depend on a plain function (`call_llm`) instead of the Ollama
SDK directly — makes it trivial to mock in tests or swap providers later.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def call_llm(prompt, model=None, timeout=None):
    """
    Calls a local Ollama model and returns the text response.
    Raises RuntimeError with a clear message if Ollama isn't reachable —
    callers should catch this and fall back to deterministic behavior.
    """
    model = model or config.OLLAMA_MODEL
    timeout = timeout or config.LLM_TIMEOUT_SECONDS

    try:
        import requests
    except ImportError:
        raise RuntimeError("requests is not installed. Run: pip install requests")

    try:
        resp = requests.post(
            f"{config.OLLAMA_HOST}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    except Exception as e:
        raise RuntimeError(
            f"Could not reach Ollama at {config.OLLAMA_HOST}. "
            f"Is it running? (`ollama serve`, `ollama pull {model}`). Original error: {e}"
        )
