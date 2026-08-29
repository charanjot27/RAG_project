"""Component 2 — Embeddings.

Turn text into vectors ("GPS coordinates for meaning") so we can find
chunks by *meaning*, not just matching words. The model is loaded lazily
so importing this module (e.g. in the API) is cheap until you actually embed.

After fine-tuning (Phase 4), set EMBEDDING_MODEL=models/finetuned-embeddings
and re-run evaluation to measure the improvement.
"""

from __future__ import annotations

from functools import lru_cache

from src.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL)


def embed(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    """Turn a list of texts into a list of L2-normalized vectors."""
    model = _get_model()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=batch_size,
        show_progress_bar=len(texts) > 256,
    )
    return vectors.tolist()


def embedding_dim() -> int:
    """Vector size for the active model (needed when creating the collection)."""
    return _get_model().get_sentence_embedding_dimension()
