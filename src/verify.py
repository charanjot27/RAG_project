"""Per-sentence faithfulness check with an NLI model."""

from __future__ import annotations

import re
from functools import lru_cache

from src.config import ENTAILMENT_THRESHOLD, NLI_MODEL


@lru_cache(maxsize=1)
def _get_nli():
    from transformers import pipeline

    return pipeline("text-classification", model=NLI_MODEL, top_k=None)


# Strip citation markers (【1†…】, [2]) and odd unicode spaces before checking —
# they carry no meaning but drag down entailment scores.
_CITATION_MARKERS = re.compile("[【†][^】]*】|\\[\\d+[^\\]]*\\]|️")
_WEIRD_SPACES = re.compile("[   ​]")


def clean_text(text: str) -> str:
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
    return [{"sentence": s, **verify_sentence(s, chunks)} for s in split_sentences(answer)]
