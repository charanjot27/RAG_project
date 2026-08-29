"""Answer generation. Backend is Groq (free) or Anthropic (paid)."""

from __future__ import annotations

import os
from functools import lru_cache

from src.config import ANTHROPIC_MODEL, GEN_MAX_TOKENS, GROQ_MODEL, LLM_PROVIDER

SYSTEM = """You answer ONLY using the provided sources.
- Every claim must be supported by the sources.
- If the sources don't contain the answer, say: "The provided sources do not cover this."
- Write in clear, short, single-fact sentences (this makes fact-checking reliable).
- Do not add outside knowledge.
- Write plain prose only. Do NOT include citation markers, footnotes, bracketed
  reference numbers (e.g. [1], 【1】), or special/unicode spacing — the system adds
  citations itself afterward."""


@lru_cache(maxsize=1)
def _groq_client():
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys."
        )
    return Groq(api_key=api_key)


def _complete_groq(system: str, user: str, max_tokens: int) -> str:
    resp = _groq_client().chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content


@lru_cache(maxsize=1)
def _anthropic_client():
    from anthropic import Anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set (or use LLM_PROVIDER=groq).")
    return Anthropic(api_key=api_key)


def _complete_anthropic(system: str, user: str, max_tokens: int) -> str:
    msg = _anthropic_client().messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


def complete(user: str, system: str = SYSTEM, max_tokens: int = GEN_MAX_TOKENS) -> str:
    if LLM_PROVIDER == "anthropic":
        return _complete_anthropic(system, user, max_tokens)
    if LLM_PROVIDER == "groq":
        return _complete_groq(system, user, max_tokens)
    raise RuntimeError(f"Unknown LLM_PROVIDER={LLM_PROVIDER!r}. Use 'groq' or 'anthropic'.")


def format_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[{i + 1}] (source: {c['source']} p.{c['page']})\n{c['text']}"
        for i, c in enumerate(chunks)
    )


def generate_answer(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return "The provided sources do not cover this."
    return complete(f"Sources:\n{format_context(chunks)}\n\nQuestion: {query}")


NAIVE_SYSTEM = (
    "You are a helpful assistant. Use the sources if relevant, but answer the "
    "question either way. Always give a direct answer."
)


def generate_answer_naive(query: str, chunks: list[dict]) -> str:
    """Unconstrained baseline used only by the hallucination benchmark."""
    context = format_context(chunks) if chunks else "(no sources)"
    return complete(f"Sources:\n{context}\n\nQuestion: {query}", system=NAIVE_SYSTEM)
