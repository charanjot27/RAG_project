"""Encode text into normalized vectors. The model loads lazily."""

from __future__ import annotations

from functools import lru_cache

from src.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL)


def embed(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    vectors = _get_model().encode(
        texts,
        normalize_embeddings=True,
        batch_size=batch_size,
        show_progress_bar=len(texts) > 256,
    )
    return vectors.tolist()


def embedding_dim() -> int:
    return _get_model().get_sentence_embedding_dimension()
