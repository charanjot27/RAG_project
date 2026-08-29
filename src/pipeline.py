"""Ties all components together.

    question -> hybrid retrieval -> rerank -> generate -> verify -> cite

Basic per-stage timing is logged so you can see where the time goes
(retrieval vs reranking vs generation vs verification).
"""

from __future__ import annotations

import logging
import time

from src.citations import build_output
from src.config import RETRIEVAL_MODE, RETRIEVE_K, TOP_N
from src.generate import generate_answer
from src.rerank import rerank
from src.verify import verify_answer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("verifin")


def _timed(stage: str, timings: dict, fn, *args):
    t = time.time()
    out = fn(*args)
    dt = round(time.time() - t, 3)
    timings[stage] = dt
    log.info("%-12s %5.2fs", stage, dt)
    return out


def _retrieve(query: str, mode: str | None = None) -> list[dict]:
    """Get candidate chunks — from the local index, live web, or cached web."""
    mode = (mode or RETRIEVAL_MODE).lower()
    if mode == "web":
        from src.web_source import web_search_chunks

        return web_search_chunks(query)
    if mode == "web_cached":
        from src.web_cache import cached_web_search

        return cached_web_search(query)
    from src.retrieval import hybrid_search

    return hybrid_search(query, RETRIEVE_K)


def answer_question(query: str, mode: str | None = None) -> dict:
    timings: dict[str, float] = {}
    active_mode = (mode or RETRIEVAL_MODE).lower()
    candidates = _timed("retrieval", timings, _retrieve, query, active_mode)
    top = _timed("rerank", timings, rerank, query, candidates, TOP_N)
    draft = _timed("generation", timings, generate_answer, query, top)
    verified = _timed("verification", timings, verify_answer, draft, top)
    result = build_output(verified)
    result["mode"] = active_mode
    result["timings"] = timings
    result["draft_answer"] = draft
    result["sources_used"] = [
        {
            "id": c["id"],
            "source": c["source"],
            "page": c["page"],
            "title": c.get("title"),
        }
        for c in top
    ]
    return result


if __name__ == "__main__":
    import json
    import sys

    q = " ".join(sys.argv[1:]) or "What is the penalty for late tax filing?"
    print(json.dumps(answer_question(q), indent=2))
