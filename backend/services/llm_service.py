"""
LLM Annotation Service — Gemini Free Tier (google-generativeai)
----------------------------------------------------------------
STRICT CONSTRAINT:
  All outputs are tagged evidence_type="ai_suggested_hypothesis".
  They are NEVER presented as biological fact and must always be
  cross-validated against BLAST/DIAMOND/HMMER results before use.

This service is advisory only. It never replaces wet-lab or
alignment-based annotation.
"""
from __future__ import annotations

import logging
from typing import Optional

from backend.core.config import settings

logger = logging.getLogger(__name__)

_gemini_model = None


def _get_model():
    """Lazy-load the Gemini generative model (import once)."""
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to .env to enable AI-assisted annotation."
        )
    try:
        import google.generativeai as genai  # type: ignore
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info("Gemini model '%s' initialised.", settings.GEMINI_MODEL)
        return _gemini_model
    except ImportError as exc:
        raise RuntimeError(
            "google-generativeai package not installed. "
            "Run: pip install google-generativeai"
        ) from exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

ANNOTATION_SYSTEM_PROMPT = """\
You are a bioinformatics annotation assistant for the GISAP platform.
Your task is to suggest plausible functional annotations for biological sequences.

RULES:
1. Prefix every annotation with "[AI-HYPOTHESIS]" to make clear it is NOT verified.
2. Never fabricate alignment scores, E-values, or database accession numbers.
3. Base suggestions only on sequence composition patterns you can reason about.
4. Always recommend the user validate with BLAST, DIAMOND, or HMMER.
5. Keep responses concise — 3-5 sentences maximum.
"""


def suggest_annotation(
    sequence: str,
    sequence_type: str = "nucleotide",
    context: Optional[str] = None,
    tenant_id: str = "unknown",
) -> dict:
    """
    Ask Gemini to suggest a functional annotation for a sequence.

    Returns:
        {
            "suggestion": str,
            "evidence_type": "ai_suggested_hypothesis",
            "model": str,
            "sequence_length": int,
            "tenant_id": str,
            "validation_required": True,
        }
    """
    model = _get_model()

    snippet = sequence[:200] if len(sequence) > 200 else sequence
    prompt_parts = [
        ANNOTATION_SYSTEM_PROMPT,
        f"\nSequence type: {sequence_type}",
        f"Sequence (first 200 nt/aa): {snippet}",
    ]
    if context:
        prompt_parts.append(f"Additional context: {context}")
    prompt_parts.append(
        "\nProvide a brief functional annotation hypothesis for this sequence."
    )

    full_prompt = "\n".join(prompt_parts)

    try:
        response = model.generate_content(full_prompt)
        suggestion = response.text.strip()
    except Exception as exc:
        logger.warning("Gemini API call failed: %s", exc)
        suggestion = (
            "[AI-HYPOTHESIS] Could not generate annotation — API error. "
            "Please validate using BLAST/DIAMOND/HMMER."
        )

    # Enforce evidence tag is always present in output
    if not suggestion.startswith("[AI-HYPOTHESIS]"):
        suggestion = f"[AI-HYPOTHESIS] {suggestion}"

    return {
        "suggestion": suggestion,
        "evidence_type": "ai_suggested_hypothesis",
        "model": settings.GEMINI_MODEL,
        "sequence_length": len(sequence),
        "tenant_id": tenant_id,
        "validation_required": True,
    }


def is_available() -> bool:
    """Return True if Gemini API key is configured and package is installed."""
    if not settings.GEMINI_API_KEY:
        return False
    try:
        import google.generativeai  # noqa: F401
        return True
    except ImportError:
        return False
