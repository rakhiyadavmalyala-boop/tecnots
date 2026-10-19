"""LLM integration — Claude via Anthropic SDK.

Stubbed by default. Set ANTHROPIC_API_KEY in .env to enable real calls.
"""

import time
from typing import Optional

from config import settings

# Lazy-loaded client
_client = None


def _get_client():
    """Return Anthropic client, creating it on first use."""
    global _client
    if _client is None:
        from anthropic import Anthropic
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


def is_configured() -> bool:
    """Check whether a real API key is set."""
    key = settings.anthropic_api_key
    return bool(key) and not key.startswith("sk-ant-your")


def ask(
    prompt: str,
    system: str = "",
    model: Optional[str] = None,
    max_tokens: int = 1024,
) -> dict:
    """Send a prompt to Claude and return the response with metadata.

    Returns:
        {
            "answer": str,
            "model": str,
            "latency_ms": float,
            "input_tokens": int,
            "output_tokens": int,
        }

    Falls back to a stub response when API key is not configured.
    """
    chosen_model = model or settings.primary_model

    if not is_configured():
        return _stub_response(prompt, chosen_model)

    client = _get_client()
    messages = [{"role": "user", "content": prompt}]
    system_msg = system or None

    start = time.perf_counter()
    response = client.messages.create(
        model=chosen_model,
        max_tokens=max_tokens,
        system=system_msg if system_msg else "",
        messages=messages,
    )
    latency = (time.perf_counter() - start) * 1000

    answer_text = response.content[0].text if response.content else ""

    return {
        "answer": answer_text,
        "model": chosen_model,
        "latency_ms": round(latency, 1),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


def _stub_response(prompt: str, model: str) -> dict:
    """Return a placeholder when no API key is set."""
    return {
        "answer": (
            "[STUB] Claude API not configured. "
            "Set ANTHROPIC_API_KEY in .env to enable real responses. "
            f"Received prompt of length {len(prompt)}."
        ),
        "model": model,
        "latency_ms": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
    }
