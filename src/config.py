"""Central configuration for VeriFin.

Everything tunable lives here so components stay in sync and the whole
pipeline can be reconfigured from environment variables (handy for
Docker / cloud deployment) without editing code.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

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
# claude-sonnet-4-6 is a solid, cost-effective default for RAG. Override with
# ANTHROPIC_MODEL to try a more capable model (e.g. claude-opus-5) or a cheaper
# one (e.g. claude-haiku-4-5).
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
GEN_MAX_TOKENS = int(os.getenv("GEN_MAX_TOKENS", "800"))

# --- Faithfulness / verification ------------------------------------------
NLI_MODEL = os.getenv("NLI_MODEL", "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
# Entailment score above which a sentence counts as "grounded".
ENTAILMENT_THRESHOLD = float(os.getenv("ENTAILMENT_THRESHOLD", "0.5"))
