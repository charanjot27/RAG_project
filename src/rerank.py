"""Cross-encoder reranker: re-score candidates and keep the best."""

from __future__ import annotations

from functools import lru_cache

from src.config import RERANKER_MODEL, TOP_N


@lru_cache(maxsize=1)
def _get_reranker():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(RERANKER_MODEL)


def rerank(query: str, chunks: list[dict], top_n: int = TOP_N) -> list[dict]:
    if not chunks:
        return []
    scores = _get_reranker().predict([(query, c["text"]) for c in chunks])
    ranked = sorted(zip(chunks, scores, strict=False), key=lambda x: x[1], reverse=True)
    return [c for c, _ in ranked[:top_n]]
