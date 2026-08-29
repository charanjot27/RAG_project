"""Backend API — wraps the pipeline in a web service.

Run it:
    uvicorn api.main:app --reload --port 8000
Then open http://localhost:8000/docs for an interactive test page.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.pipeline import answer_question

app = FastAPI(
    title="VeriFin API",
    description="Self-auditing RAG: every sentence is cited or flagged unverified.",
    version="1.0.0",
)


class Query(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(q: Query):
    question = q.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")
    try:
        return answer_question(question)
    except Exception as exc:  # surface a clean error instead of a 500 stack trace
        raise HTTPException(status_code=500, detail=str(exc)) from exc
