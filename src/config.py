"""Central configuration for VeriFin.

Everything tunable lives here so components stay in sync and the whole
pipeline can be reconfigured from environment variables (handy for
Docker / cloud deployment) without editing code.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:
    # python-dotenv is optional; env vars can also be set directly (e.g. in
    # Docker / the host dashboard). Missing .env support is not fatal.
    pass

# --- Paths -----------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = Path(os.getenv("RAW_DIR", ROOT / "data" / "raw"))
PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", ROOT / "data" / "processed"))
CHUNKS_CACHE = PROCESSED_DIR / "chunks.json"

# --- Chunking --------------------------------------------------------------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "400"))      # words per chunk
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))  # overlap in words

# --- Embeddings ------------------------------------------------------------
# Point EMBEDDING_MODEL at "models/finetuned-embeddings" after Phase 4 to
# measure what fine-tuning bought you.
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

# --- Vector store ----------------------------------------------------------
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_URL = os.getenv("QDRANT_URL")          # e.g. Qdrant Cloud URL (overrides host/port)
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")  # Qdrant Cloud key
COLLECTION = os.getenv("QDRANT_COLLECTION", "verifin")

# --- Retrieval / rerank ----------------------------------------------------
RETRIEVE_K = int(os.getenv("RETRIEVE_K", "20"))  # candidates from hybrid search
TOP_N = int(os.getenv("TOP_N", "5"))             # chunks kept after reranking
RERANKER_MODEL = os.getenv(
    "RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# --- Generation ------------------------------------------------------------
# Which LLM writes the final answer. Only this step calls an LLM — the rest of
# the pipeline is free/local.
#   "groq"      -> free, fast, OpenAI-compatible (default). Needs GROQ_API_KEY.
#   "anthropic" -> Claude API (paid). Needs ANTHROPIC_API_KEY.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
GEN_MAX_TOKENS = int(os.getenv("GEN_MAX_TOKENS", "800"))

# Groq model id — see https://console.groq.com/docs/models for current options.
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Anthropic model id (used only when LLM_PROVIDER=anthropic).
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# --- Faithfulness / verification ------------------------------------------
NLI_MODEL = os.getenv("NLI_MODEL", "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
# Entailment score above which a sentence counts as "grounded".
ENTAILMENT_THRESHOLD = float(os.getenv("ENTAILMENT_THRESHOLD", "0.5"))

# --- API -------------------------------------------------------------------
# Comma-separated list of allowed CORS origins for the browser UI.
# "*" allows any origin (fine for a demo; lock this down for real use).
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()
]

# Document formats the ingester will read from RAW_DIR.
DOC_GLOBS = ("*.pdf", "*.txt", "*.md")
