"""Component 1 — Data ingestion & chunking.

Turn messy PDFs in ``data/raw/`` into clean, bite-sized, overlapping
passages ("chunks") that can be cited precisely. Results are cached to
``data/processed/chunks.json`` so the rest of the pipeline doesn't
re-read every PDF on import.
"""

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
    """Read a PDF and return a list of {source, page, text} records."""
    from pypdf import PdfReader  # imported lazily so importing this module is cheap

    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({"source": Path(path).name, "page": i + 1, "text": text})
    return pages


def load_text_file(path: str) -> list[dict]:
    """Read a .txt / .md file as a single-page record (handy for quick testing)."""
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    return [{"source": Path(path).name, "page": 1, "text": text}]


def load_document(path: Path) -> list[dict]:
    """Dispatch to the right loader based on file extension."""
    if path.suffix.lower() == ".pdf":
        return load_pdf(str(path))
    return load_text_file(str(path))


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping word windows.

    Chunks too big -> imprecise citations; too small -> lost context.
    Defaults (~400 words, ~50 overlap) are a sane starting point — tune later.
    """
    words = text.split()
    if not words:
        return []
    step = max(size - overlap, 1)  # guard against overlap >= size (infinite loop)
    chunks, start = [], 0
    while start < len(words):
        end = start + size
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks


def build_chunks(pdf_dir: str | Path = RAW_DIR) -> list[dict]:
    """Read every supported document under ``pdf_dir`` (PDF/TXT/MD).

    Returns a flat list of chunk records.
    """
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
    """Return cached chunks, building (and caching) them on first use.

    Set ``rebuild=True`` after adding or changing PDFs.
    """
    if not rebuild and CHUNKS_CACHE.exists():
        return json.loads(CHUNKS_CACHE.read_text())
    chunks = build_chunks()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_CACHE.write_text(json.dumps(chunks, ensure_ascii=False, indent=2))
    return chunks


if __name__ == "__main__":
    chunks = load_chunks(rebuild=True)
    print(f"Built {len(chunks)} chunks -> {CHUNKS_CACHE}")
