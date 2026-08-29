"""Live web retrieval — the internet as the knowledge base.

Instead of manually adding PDFs, search the web for the question, fetch the
top pages, extract their main text, and chunk it on the fly. The result is a
list of chunk records identical in shape to the local retriever's output, so
it flows through the SAME rerank -> generate -> verify -> cite pipeline. Every
sentence is still fact-checked, and citations point to real URLs.

Free and keyless: DuckDuckGo for search, trafilatura for clean text extraction.

Runs anywhere with open internet (your laptop, most cloud hosts). Some locked-down
sandboxes block outbound web fetch — that's an environment limit, not a code issue.
"""

from __future__ import annotations

from src.config import (
    WEB_MAX_CHUNKS_PER_PAGE,
    WEB_RESULTS,
)
from src.ingest import chunk_text


def search_urls(query: str, max_results: int = WEB_RESULTS) -> list[dict]:
    """Return [{title, url}] for the top web results (DuckDuckGo, no API key)."""
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
    """Download a page and extract its main article text (no nav/ads/boilerplate)."""
    import trafilatura

    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return ""
    text = trafilatura.extract(
        downloaded, include_comments=False, include_tables=True, favor_recall=True
    )
    return text or ""


def web_search_chunks(query: str, num_results: int = WEB_RESULTS) -> list[dict]:
    """Search the web for ``query`` and return chunk records grounded in real pages."""
    chunks: list[dict] = []
    for hit in search_urls(query, num_results):
        url = hit["url"]
        try:
            text = fetch_main_text(url)
        except Exception:
            continue  # skip pages that fail to download/parse
        if not text:
            continue
        for j, chunk in enumerate(chunk_text(text)[:WEB_MAX_CHUNKS_PER_PAGE]):
            chunks.append(
                {
                    "id": f"{url}#c{j}",
                    "source": url,
                    "title": hit["title"],
                    "page": j + 1,  # "section" within the page
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
