"""FastAPI backend. Run: uvicorn api.main:app --port 8000"""

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

app = FastAPI(title="VeriFin API", version="1.0.0")
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
    mode: str | None = None


def _index_status(mode: str) -> dict:
    if mode in ("web", "web_cached"):
        return {"index_ready": True, "mode": mode}
    try:
        from src.qdrant import get_client

        info = get_client().get_collection(COLLECTION)
        count = getattr(info, "points_count", None)
        return {"index_ready": bool(count), "mode": "local", "collection": COLLECTION, "chunks": count}
    except Exception as exc:
        return {"index_ready": False, "mode": "local", "collection": COLLECTION, "error": str(exc)}


@app.get("/health")
def health():
    return {"status": "ok", **_index_status(RETRIEVAL_MODE)}


@app.get("/config")
def config():
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
                "`python -m src.ingest && python -m src.index_build`, or switch to web mode. "
                f"Details: {status.get('error', 'empty collection')}"
            ),
        )

    try:
        return answer_question(question, mode=mode)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
