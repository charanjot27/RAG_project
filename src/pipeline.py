"""Ties all components together.

    question -> hybrid retrieval -> rerank -> generate -> verify -> cite

Basic per-stage timing is logged so you can see where the time goes
(retrieval vs reranking vs generation vs verification).
"""

from __future__ import annotations

import logging
import time

from src.citations import build_output
from src.config import RETRIEVE_K, TOP_N
from src.generate import generate_answer
from src.rerank import rerank
from src.retrieval import hybrid_search
from src.verify import verify_answer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("verifin")


def _timed(stage: str, fn, *args):
    t = time.time()
    out = fn(*args)
    log.info("%-12s %5.2fs", stage, time.time() - t)
    return out


def answer_question(query: str) -> dict:
    candidates = _timed("retrieval", hybrid_search, query, RETRIEVE_K)
    top = _timed("rerank", rerank, query, candidates, TOP_N)
    draft = _timed("generation", generate_answer, query, top)
    verified = _timed("verification", verify_answer, draft, top)
    result = build_output(verified)
    result["sources_used"] = [
        {"id": c["id"], "source": c["source"], "page": c["page"]} for c in top
    ]
    return result


if __name__ == "__main__":
    import json
    import sys

    q = " ".join(sys.argv[1:]) or "What is the penalty for late tax filing?"
    print(json.dumps(answer_question(q), indent=2))
