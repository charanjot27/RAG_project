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
# Three modes, in priority order:
#   1. QDRANT_PATH  -> embedded, on-disk Qdrant (no server, no Docker) — easiest
#   2. QDRANT_URL   -> Qdrant Cloud (URL + API key)
#   3. host/port    -> a Qdrant server (e.g. `docker run qdrant/qdrant`)
QDRANT_PATH = os.getenv("QDRANT_PATH")        # e.g. "qdrant_data" for embedded mode
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_URL = os.getenv("QDRANT_URL")          # e.g. Qdrant Cloud URL (overrides host/port)
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")  # Qdrant Cloud key
COLLECTION = os.getenv("QDRANT_COLLECTION", "verifin")

# --- Retrieval / rerank ----------------------------------------------------
# Where answers are grounded:
#   "local" -> your indexed documents in Qdrant (add PDFs/txt to data/raw)
#   "web"   -> live web search: the knowledge base is the internet, no manual
#              uploads. Every sentence is still verified + cited to a URL.
RETRIEVAL_MODE = os.getenv("RETRIEVAL_MODE", "local").lower()
RETRIEVE_K = int(os.getenv("RETRIEVE_K", "20"))  # candidates from hybrid search
TOP_N = int(os.getenv("TOP_N", "5"))             # chunks kept after reranking

# Web mode: how many search results to fetch, and how many chunks to keep per page.
WEB_RESULTS = int(os.getenv("WEB_RESULTS", "5"))
WEB_MAX_CHUNKS_PER_PAGE = int(os.getenv("WEB_MAX_CHUNKS_PER_PAGE", "6"))

# Web-cache mode ("web_cached"): fetched web chunks are embedded into Qdrant so
# repeat/related questions are answered instantly from the growing index; the
# web is only hit when the cache can't cover the question.
WEB_CACHE_COLLECTION = os.getenv("WEB_CACHE_COLLECTION", "verifin_web")
# If the cache already returns this many hits at/above the similarity floor,
# skip the live web fetch entirely (instant answer).
WEB_CACHE_MIN_HITS = int(os.getenv("WEB_CACHE_MIN_HITS", "5"))
WEB_CACHE_SIM_THRESHOLD = float(os.getenv("WEB_CACHE_SIM_THRESHOLD", "0.55"))
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

# Groq model id. Groq rotates its catalog, so list what your key can use with
#   python -c "from groq import Groq; [print(m.id) for m in Groq().models.list().data]"
# openai/gpt-oss-120b is capable and widely available; gpt-oss-20b is faster.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Anthropic model id (used only when LLM_PROVIDER=anthropic).
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# --- Faithfulness / verification ------------------------------------------
NLI_MODEL = os.getenv("NLI_MODEL", "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
# Entailment score above which a sentence counts as "grounded".
ENTAILMENT_THRESHOLD = float(os.getenv("ENTAILMENT_THRESHOLD", "0.5"))
# Abstention: if the answer's faithfulness score is below this, refuse to answer
# ("knows when it doesn't know"). 0.0 disables abstention; 0.5 is a good start.
ABSTAIN_THRESHOLD = float(os.getenv("ABSTAIN_THRESHOLD", "0.0"))

# --- API -------------------------------------------------------------------
# Comma-separated list of allowed CORS origins for the browser UI.
# "*" allows any origin (fine for a demo; lock this down for real use).
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()
]

# Document formats the ingester will read from RAW_DIR.
DOC_GLOBS = ("*.pdf", "*.txt", "*.md")
