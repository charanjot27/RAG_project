"""Configuration, driven by environment variables (see .env.example)."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:
    pass

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = Path(os.getenv("RAW_DIR", ROOT / "data" / "raw"))
PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", ROOT / "data" / "processed"))
CHUNKS_CACHE = PROCESSED_DIR / "chunks.json"

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Point at models/finetuned-embeddings after training to use your own model.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Vector store: QDRANT_PATH (embedded) > QDRANT_URL (cloud) > host/port (server).
QDRANT_PATH = os.getenv("QDRANT_PATH")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION = os.getenv("QDRANT_COLLECTION", "verifin")

# Retrieval: "local" | "web" | "web_cached".
RETRIEVAL_MODE = os.getenv("RETRIEVAL_MODE", "local").lower()
RETRIEVE_K = int(os.getenv("RETRIEVE_K", "20"))
TOP_N = int(os.getenv("TOP_N", "5"))

WEB_RESULTS = int(os.getenv("WEB_RESULTS", "5"))
WEB_MAX_CHUNKS_PER_PAGE = int(os.getenv("WEB_MAX_CHUNKS_PER_PAGE", "6"))
WEB_CACHE_COLLECTION = os.getenv("WEB_CACHE_COLLECTION", "verifin_web")
WEB_CACHE_MIN_HITS = int(os.getenv("WEB_CACHE_MIN_HITS", "5"))
WEB_CACHE_SIM_THRESHOLD = float(os.getenv("WEB_CACHE_SIM_THRESHOLD", "0.55"))

RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# Generation: "groq" (free) or "anthropic" (paid).
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
GEN_MAX_TOKENS = int(os.getenv("GEN_MAX_TOKENS", "800"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

NLI_MODEL = os.getenv("NLI_MODEL", "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
ENTAILMENT_THRESHOLD = float(os.getenv("ENTAILMENT_THRESHOLD", "0.5"))
# Refuse to answer when faithfulness falls below this (0.0 disables it).
ABSTAIN_THRESHOLD = float(os.getenv("ABSTAIN_THRESHOLD", "0.0"))

ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
DOC_GLOBS = ("*.pdf", "*.txt", "*.md")
