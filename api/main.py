"""Backend API — wraps the pipeline in a web service.

Run it:
    uvicorn api.main:app --reload --port 8000
Then open http://localhost:8000/docs for an interactive test page.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import ALLOWED_ORIGINS, COLLECTION
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


class Query(BaseModel):
    question: str


def _index_status() -> dict:
    """Report whether the vector index exists and how many chunks it holds."""
    try:
        from src.qdrant import get_client

        info = get_client().get_collection(COLLECTION)
        count = getattr(info, "points_count", None)
        return {"index_ready": bool(count), "collection": COLLECTION, "chunks": count}
    except Exception as exc:  # collection missing / DB unreachable
        return {"index_ready": False, "collection": COLLECTION, "error": str(exc)}


@app.get("/health")
def health():
    """Liveness + index readiness (use this to confirm a deploy is usable)."""
    status = _index_status()
    return {"status": "ok", **status}


@app.post("/ask")
def ask(q: Query):
    question = q.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    status = _index_status()
    if not status.get("index_ready"):
        raise HTTPException(
            status_code=503,
            detail=(
                "Vector index is not ready. Add documents to data/raw/ and run "
                "`python -m src.ingest && python -m src.index_build` against this "
                f"deployment's Qdrant. Details: {status.get('error', 'empty collection')}"
            ),
        )

    try:
        return answer_question(question)
    except Exception as exc:  # surface a clean error instead of a 500 stack trace
        raise HTTPException(status_code=500, detail=str(exc)) from exc
