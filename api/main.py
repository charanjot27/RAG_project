"""Backend API — wraps the pipeline in a web service.

Run it:
    uvicorn api.main:app --reload --port 8000
Then open http://localhost:8000/docs for an interactive test page.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import (
    ABSTAIN_THRESHOLD,
    ALLOWED_ORIGINS,
    COLLECTION,
    LLM_PROVIDER,
    RETRIEVAL_MODE,
)
from src.pipeline import answer_question

app = FastAPI(
    title="VeriFin API",
    description="Self-auditing RAG: every sentence is cited or flagged unverified.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_MODES = {"local", "web", "web_cached"}


class Query(BaseModel):
    question: str
    mode: str | None = None  # override RETRIEVAL_MODE per request (local/web/web_cached)


def _index_status(mode: str) -> dict:
    """Report whether the vector index exists and how many chunks it holds."""
    if mode in ("web", "web_cached"):
        # Web modes need no prebuilt index — the internet is the knowledge base
        # (web_cached builds its own Qdrant cache on the fly).
        return {"index_ready": True, "mode": mode}
    try:
        from src.qdrant import get_client

        info = get_client().get_collection(COLLECTION)
        count = getattr(info, "points_count", None)
        return {"index_ready": bool(count), "mode": "local",
                "collection": COLLECTION, "chunks": count}
    except Exception as exc:  # collection missing / DB unreachable
        return {"index_ready": False, "mode": "local",
                "collection": COLLECTION, "error": str(exc)}


@app.get("/health")
def health():
    """Liveness + index readiness (use this to confirm a deploy is usable)."""
    return {"status": "ok", **_index_status(RETRIEVAL_MODE)}


@app.get("/config")
def config():
    """Public, non-secret config so the UI can render available options."""
    return {
        "default_mode": RETRIEVAL_MODE,
        "modes": sorted(VALID_MODES),
        "llm_provider": LLM_PROVIDER,
        "abstain_threshold": ABSTAIN_THRESHOLD,
    }


@app.post("/ask")
def ask(q: Query):
    question = q.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    mode = (q.mode or RETRIEVAL_MODE).lower()
    if mode not in VALID_MODES:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Use one of {sorted(VALID_MODES)}.")

    status = _index_status(mode)
    if not status.get("index_ready"):
        raise HTTPException(
            status_code=503,
            detail=(
                "Vector index is not ready. Add documents to data/raw/ and run "
                "`python -m src.ingest && python -m src.index_build`, or switch to "
                f"web mode. Details: {status.get('error', 'empty collection')}"
            ),
        )

    try:
        return answer_question(question, mode=mode)
    except Exception as exc:  # surface a clean error instead of a 500 stack trace
        raise HTTPException(status_code=500, detail=str(exc)) from exc
