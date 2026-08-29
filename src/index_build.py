"""Build the Qdrant vector index. Run after ingesting: python -m src.index_build"""

from __future__ import annotations

from qdrant_client.models import Distance, PointStruct, VectorParams

from src.config import COLLECTION
from src.embeddings import embed
from src.ingest import load_chunks
from src.qdrant import get_client


def build_index(rebuild_chunks: bool = True) -> int:
    client = get_client()
    chunks = load_chunks(rebuild=rebuild_chunks)
    if not chunks:
        raise SystemExit("No chunks found. Add documents to data/raw/ and re-run.")

    vectors = embed([c["text"] for c in chunks])
    dim = len(vectors[0])

    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    points = [PointStruct(id=i, vector=vectors[i], payload=chunks[i]) for i in range(len(chunks))]
    for start in range(0, len(points), 256):
        client.upsert(collection_name=COLLECTION, points=points[start : start + 256])

    print(f"Indexed {len(points)} chunks into '{COLLECTION}' (dim={dim})")
    return len(points)


if __name__ == "__main__":
    build_index()
