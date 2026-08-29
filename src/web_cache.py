"""Web cache — make live web retrieval scalable.

Live web search is great for breadth but slow (a network round-trip per
question) and stateless (it re-fetches every time). This module caches every
fetched web chunk into Qdrant, embedded, so:

  * repeat or related questions are answered INSTANTLY from the index, and
  * the knowledge base GROWS as the system is used.

Flow for a query:
  1. Dense-search the cache collection.
  2. If it already returns enough strong hits -> return them (no web call).
  3. Otherwise fetch fresh web results, embed + upsert them (deduped by a
     stable id), and return the combined set.

Requires a Qdrant (embedded QDRANT_PATH, local server, or Qdrant Cloud).
"""

from __future__ import annotations

import uuid

from src.config import (
    WEB_CACHE_COLLECTION,
    WEB_CACHE_MIN_HITS,
    WEB_CACHE_SIM_THRESHOLD,
    WEB_RESULTS,
)
from src.embeddings import embed, embedding_dim
from src.qdrant import get_client
from src.web_source import web_search_chunks

_NAMESPACE = uuid.UUID("6f1b7c2e-0000-4000-8000-000000000000")


def _point_id(chunk_id: str) -> str:
    """Deterministic UUID from a chunk's string id, so re-caching de-duplicates."""
    return str(uuid.uuid5(_NAMESPACE, chunk_id))


def _ensure_collection() -> None:
    from qdrant_client.models import Distance, VectorParams

    client = get_client()
    existing = {c.name for c in client.get_collections().collections}
    if WEB_CACHE_COLLECTION not in existing:
        client.create_collection(
            collection_name=WEB_CACHE_COLLECTION,
            vectors_config=VectorParams(size=embedding_dim(), distance=Distance.COSINE),
        )


def _search_cache(query_vec: list[float], k: int) -> list[tuple[dict, float]]:
    hits = get_client().query_points(
        collection_name=WEB_CACHE_COLLECTION, query=query_vec, limit=k, with_payload=True
    ).points
    return [(h.payload, h.score) for h in hits]


def _upsert(chunks: list[dict]) -> None:
    from qdrant_client.models import PointStruct

    vectors = embed([c["text"] for c in chunks])
    points = [
        PointStruct(id=_point_id(c["id"]), vector=vectors[i], payload=c)
        for i, c in enumerate(chunks)
    ]
    for start in range(0, len(points), 128):
        get_client().upsert(
            collection_name=WEB_CACHE_COLLECTION, points=points[start : start + 128]
        )


def cached_web_search(query: str, k: int = WEB_RESULTS * 4) -> list[dict]:
    """Return web-grounded chunks, using the Qdrant cache before hitting the web."""
    _ensure_collection()
    query_vec = embed([query])[0]

    # 1. Try the cache first.
    cached = _search_cache(query_vec, k)
    strong = [payload for payload, score in cached if score >= WEB_CACHE_SIM_THRESHOLD]
    if len(strong) >= WEB_CACHE_MIN_HITS:
        return strong  # instant: fully served from the growing index

    # 2. Cache miss -> fetch fresh, cache it, and merge.
    fresh = web_search_chunks(query)
    if fresh:
        _upsert(fresh)

    merged, seen = [], set()
    for chunk in fresh + [p for p, _ in cached]:
        if chunk["id"] not in seen:
            seen.add(chunk["id"])
            merged.append(chunk)
    return merged
