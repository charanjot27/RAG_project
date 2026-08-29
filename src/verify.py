"""Component 6 — Faithfulness / hallucination detection.

The heart of the project. After the answer is written, check every
sentence against the sources with an NLI (Natural Language Inference)
model: given a premise (a source chunk) and a hypothesis (one generated
sentence), does the premise *entail* the sentence?

    sources entail the sentence  -> grounded  (green + citation)
    otherwise                    -> unverified (red flag)
"""

from __future__ import annotations

import re
from functools import lru_cache

from src.config import ENTAILMENT_THRESHOLD, NLI_MODEL


@lru_cache(maxsize=1)
def _get_nli():
    from transformers import pipeline

    # An NLI model outputs entailment / neutral / contradiction scores.
    return pipeline("text-classification", model=NLI_MODEL, top_k=None)


# Citation-marker / footnote artifacts some LLMs inject, e.g. the CJK bracket
# form with a dagger, or [2]. They carry no meaning but drag down NLI
# entailment, so strip them before checking. 【/】 = 【 】, † = †.
_CITATION_MARKERS = re.compile(r"[【†][^】]*】|\[\d+[^\]]*\]|️")
# Odd unicode spaces: no-break  , thin  , narrow no-break  ,
# zero-width ​. These break token matching in the verifier.
_WEIRD_SPACES = re.compile(r"[   ​]")


def clean_text(text: str) -> str:
    """Strip citation markers and normalize whitespace before verifying/displaying."""
    text = _CITATION_MARKERS.sub("", text)
    text = _WEIRD_SPACES.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    text = clean_text(text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _entailment_score(premise: str, hypothesis: str) -> float:
    result = _get_nli()({"text": premise, "text_pair": hypothesis})
    scores = {r["label"].lower(): r["score"] for r in result}
    return scores.get("entailment", 0.0)


def verify_sentence(sentence: str, chunks: list[dict]) -> dict:
    """Check one sentence against every source chunk; keep the best support."""
    best = {"label": "unverified", "score": 0.0, "source": None}
    for c in chunks:
        ent = _entailment_score(c["text"], sentence)
        if ent > best["score"]:
            best = {
                "label": "grounded" if ent >= ENTAILMENT_THRESHOLD else "unverified",
                "score": ent,
                "source": c,
            }
    return best


def verify_answer(answer: str, chunks: list[dict]) -> list[dict]:
    return [
        {"sentence": s, **verify_sentence(s, chunks)}
        for s in split_sentences(answer)
    ]
