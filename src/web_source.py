"""Live web retrieval: search, fetch, and chunk pages on the fly.

Keyless — DuckDuckGo for search, trafilatura for text extraction. Needs
open internet.
"""

from __future__ import annotations

from src.config import WEB_MAX_CHUNKS_PER_PAGE, WEB_RESULTS
from src.ingest import chunk_text


def search_urls(query: str, max_results: int = WEB_RESULTS) -> list[dict]:
    from ddgs import DDGS

    out, seen = [], set()
    for r in DDGS().text(query, max_results=max_results * 2):
        url = r.get("href") or r.get("url")
        if url and url not in seen:
            seen.add(url)
            out.append({"title": r.get("title", url), "url": url})
        if len(out) >= max_results:
            break
    return out


def fetch_main_text(url: str) -> str:
    import trafilatura

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return ""
    text = trafilatura.extract(
        downloaded, include_comments=False, include_tables=True, favor_recall=True
    )
    return text or ""


def web_search_chunks(query: str, num_results: int = WEB_RESULTS) -> list[dict]:
    chunks: list[dict] = []
    for hit in search_urls(query, num_results):
        url = hit["url"]
        try:
            text = fetch_main_text(url)
        except Exception:
            continue
        if not text:
            continue
        for j, chunk in enumerate(chunk_text(text)[:WEB_MAX_CHUNKS_PER_PAGE]):
            chunks.append(
                {
                    "id": f"{url}#c{j}",
                    "source": url,
                    "title": hit["title"],
                    "page": j + 1,
                    "text": chunk,
                }
            )
    return chunks


if __name__ == "__main__":
    import json
    import sys

    q = " ".join(sys.argv[1:]) or "What is the penalty for late tax filing in the US?"
    found = web_search_chunks(q)
    print(f"Fetched {len(found)} chunks from {len({c['source'] for c in found})} pages")
    print(json.dumps(found[:2], indent=2)[:1500])
