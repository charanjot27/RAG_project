"""Load documents (PDF/TXT/MD) and split them into overlapping chunks."""

from __future__ import annotations

import json
from pathlib import Path

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CHUNKS_CACHE,
    DOC_GLOBS,
    PROCESSED_DIR,
    RAW_DIR,
)


def load_pdf(path: str) -> list[dict]:
    from pypdf import PdfReader

    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({"source": Path(path).name, "page": i + 1, "text": text})
    return pages


def load_text_file(path: str) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    return [{"source": Path(path).name, "page": 1, "text": text}]


def load_document(path: Path) -> list[dict]:
    if path.suffix.lower() == ".pdf":
        return load_pdf(str(path))
    return load_text_file(str(path))


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    if not words:
        return []
    step = max(size - overlap, 1)
    chunks, start = [], 0
    while start < len(words):
        chunk = " ".join(words[start : start + size]).strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks


def build_chunks(pdf_dir: str | Path = RAW_DIR) -> list[dict]:
    all_chunks: list[dict] = []
    paths = sorted(p for g in DOC_GLOBS for p in Path(pdf_dir).glob(g))
    for doc in paths:
        for page in load_document(doc):
            for j, chunk in enumerate(chunk_text(page["text"])):
                all_chunks.append(
                    {
                        "id": f"{page['source']}-p{page['page']}-c{j}",
                        "source": page["source"],
                        "page": page["page"],
                        "text": chunk,
                    }
                )
    return all_chunks


def load_chunks(rebuild: bool = False) -> list[dict]:
    if not rebuild and CHUNKS_CACHE.exists():
        return json.loads(CHUNKS_CACHE.read_text())
    chunks = build_chunks()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_CACHE.write_text(json.dumps(chunks, ensure_ascii=False, indent=2))
    return chunks


if __name__ == "__main__":
    chunks = load_chunks(rebuild=True)
    print(f"Built {len(chunks)} chunks -> {CHUNKS_CACHE}")
