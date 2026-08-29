"""Component 4 — The reranker.

Retrieval is fast but rough. A cross-encoder reranker reads the question
and each candidate *together in one pass* and scores how well they truly
match, pushing the best chunks to the top. This is usually the single
biggest quality jump in a RAG system.

    bi-encoder  (embeddings): encode Q and passage separately -> fast, blurry
    cross-encoder (reranker): read Q + passage together      -> slow, precise
"""

from __future__ import annotations

from functools import lru_cache

from src.config import RERANKER_MODEL, TOP_N


@lru_cache(maxsize=1)
def _get_reranker():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(RERANKER_MODEL)


def rerank(query: str, chunks: list[dict], top_n: int = TOP_N) -> list[dict]:
    """Re-score candidate chunks against the query; keep the top ``top_n``."""
    if not chunks:
        return []
    pairs = [(query, c["text"]) for c in chunks]
    scores = _get_reranker().predict(pairs)
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return [c for c, _ in ranked[:top_n]]
