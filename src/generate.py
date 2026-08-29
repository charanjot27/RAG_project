"""Component 5 — Generation.

Write the answer using *only* the top chunks. The system prompt forces
the model to stick to the sources and to say "I don't know" when the
sources don't cover the question. This reduces hallucination but never
eliminates it — which is exactly why Component 6 (verification) exists.
You never trust the generator alone.
"""

from __future__ import annotations

import os
from functools import lru_cache

from src.config import ANTHROPIC_MODEL, GEN_MAX_TOKENS

SYSTEM = """You answer ONLY using the provided sources.
- Every claim must be supported by the sources.
- If the sources don't contain the answer, say: "The provided sources do not cover this."
- Write in clear, short, single-fact sentences (this makes fact-checking reliable).
- Do not add outside knowledge."""


@lru_cache(maxsize=1)
def _get_client():
    from anthropic import Anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to your .env file "
            "(see .env.example) or the host's environment."
        )
    return Anthropic(api_key=api_key)


def format_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[{i + 1}] (source: {c['source']} p.{c['page']})\n{c['text']}"
        for i, c in enumerate(chunks)
    )


def generate_answer(query: str, chunks: list[dict]) -> str:
    """Ask the LLM to answer ``query`` grounded in ``chunks``."""
    if not chunks:
        return "The provided sources do not cover this."

    context = format_context(chunks)
    msg = _get_client().messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=GEN_MAX_TOKENS,
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Sources:\n{context}\n\nQuestion: {query}",
            }
        ],
    )
    return msg.content[0].text
