"""Hybrid retrieval: dense (embeddings) + BM25 keyword search."""

from __future__ import annotations

from functools import lru_cache

from src.config import COLLECTION, RETRIEVE_K
from src.embeddings import embed
from src.ingest import load_chunks
from src.qdrant import get_client


@lru_cache(maxsize=1)
def _bm25_index():
    from rank_bm25 import BM25Okapi

    chunks = load_chunks()
    return chunks, BM25Okapi([c["text"].lower().split() for c in chunks])


def dense_search(query: str, k: int = RETRIEVE_K) -> list[dict]:
    vec = embed([query])[0]
    hits = get_client().query_points(collection_name=COLLECTION, query=vec, limit=k).points
    return [h.payload for h in hits]


def keyword_search(query: str, k: int = RETRIEVE_K) -> list[dict]:
    chunks, bm25 = _bm25_index()
    scores = bm25.get_scores(query.lower().split())
    ranked = sorted(zip(chunks, scores, strict=False), key=lambda x: x[1], reverse=True)
    return [c for c, score in ranked[:k] if score > 0]


def hybrid_search(query: str, k: int = RETRIEVE_K) -> list[dict]:
    combined: list[dict] = []
    seen: set[str] = set()
    for chunk in dense_search(query, k) + keyword_search(query, k):
        if chunk["id"] not in seen:
            seen.add(chunk["id"])
            combined.append(chunk)
    return combined


if __name__ == "__main__":
    import json
    import sys

    q = " ".join(sys.argv[1:]) or "What is the penalty for late filing?"
    print(json.dumps(hybrid_search(q), indent=2)[:2000])
