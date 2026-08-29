"""Qdrant client factory (embedded, cloud, or server)."""

from __future__ import annotations

from functools import lru_cache

from src.config import (
    QDRANT_API_KEY,
    QDRANT_HOST,
    QDRANT_PATH,
    QDRANT_PORT,
    QDRANT_URL,
)


@lru_cache(maxsize=1)
def get_client():
    from qdrant_client import QdrantClient

    if QDRANT_PATH:
        return QdrantClient(path=QDRANT_PATH)
    if QDRANT_URL:
        return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
