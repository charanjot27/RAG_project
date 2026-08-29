"""Download the ML models at Docker build time so the first request is fast."""

from __future__ import annotations

from src.config import EMBEDDING_MODEL, NLI_MODEL, RERANKER_MODEL


def main() -> None:
    from sentence_transformers import CrossEncoder, SentenceTransformer
    from transformers import pipeline

    print(f"Preloading embedding model: {EMBEDDING_MODEL}")
    SentenceTransformer(EMBEDDING_MODEL)

    print(f"Preloading reranker: {RERANKER_MODEL}")
    CrossEncoder(RERANKER_MODEL)

    print(f"Preloading NLI model: {NLI_MODEL}")
    pipeline("text-classification", model=NLI_MODEL, top_k=None)

    print("All models cached.")


if __name__ == "__main__":
    main()
