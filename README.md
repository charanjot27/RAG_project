# VeriFin — Self-Auditing RAG Assistant

> An AI that answers questions from real documents, shows its sources, and flags its own
> unsupported statements at the sentence level — built for high-stakes domains like finance
> and regulation.

Every sentence in an answer is either **backed by a clickable source** or **flagged red as
"unverified."** That single feature — the AI catching and flagging its own hallucinations —
is what turns this from "another chatbot" into a real project.

📖 **Full design doc & learning guide:** [`DOCUMENTATION.md`](DOCUMENTATION.md)

---

## How it works

```
question → hybrid retrieval → cross-encoder rerank → LLM generation
         → per-sentence NLI faithfulness check → citations + red/green flags
```

The three deep-learning components you can train yourself: the **embedding model**
(retrieval), the **cross-encoder reranker**, and the **NLI faithfulness checker**.

## Project layout

| Path | Component |
|---|---|
| `src/ingest.py` | 1 — load + chunk PDFs |
| `src/embeddings.py` | 2 — text → vectors |
| `src/retrieval.py` | 3 — hybrid (dense + BM25) search |
| `src/rerank.py` | 4 — cross-encoder reranker |
| `src/generate.py` | 5 — LLM answer (grounded in sources) |
| `src/verify.py` | 6 — NLI faithfulness check |
| `src/citations.py` | 7 — bind citations + flags |
| `src/pipeline.py` | glue: ties every component together |
| `training/` | fine-tune the embedding model & reranker |
| `eval/` | RAGAS scoreboard |
| `api/main.py` | FastAPI backend |
| `app/app.py` | Streamlit frontend |

## Quickstart

```bash
# 1. Environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# 2. Secrets
cp .env.example .env               # then edit .env and add your ANTHROPIC_API_KEY

# 3. Add documents
#    Drop 5–20 PDFs into data/raw/  (SEC EDGAR filings, tax/regulatory PDFs, etc.)

# 4. Start the vector DB (local Qdrant via Docker)
docker run -p 6333:6333 qdrant/qdrant

# 5. Ingest + build the vector index
python -m src.ingest
python -m src.index_build

# 6. Try the pipeline from the command line
python -m src.pipeline "What is the penalty for late tax filing?"

# 7. Run the API + UI (two terminals)
uvicorn api.main:app --reload --port 8000
streamlit run app/app.py
```

### One-command local stack (API + Qdrant)

```bash
cp .env.example .env               # fill in ANTHROPIC_API_KEY
docker compose up --build          # API on :8000, Qdrant on :6333
# then, once, build the index against the running Qdrant:
python -m src.index_build
```

## Configuration

Everything tunable is read from environment variables (see [`.env.example`](.env.example)
and [`src/config.py`](src/config.py)): the generation model, embedding/reranker/NLI models,
the entailment threshold, chunk size, retrieval depth, and local-vs-cloud Qdrant.

## Training your own models (Phase 4)

```bash
python -m src.ingest                        # ensure chunks exist
python -m scripts.gen_training_pairs        # LLM-generate Q/passage pairs
python -m training.train_embeddings         # → models/finetuned-embeddings
# then set EMBEDDING_MODEL=models/finetuned-embeddings in .env, rebuild the index, re-eval
```

## Evaluation

```bash
python -m eval.run_eval    # faithfulness, answer relevance, context precision/recall
```

Run it after every phase and record the numbers — the before/after table is the most
convincing slide in the final presentation.

## Build order (one semester)

1. Naive RAG (chunk → embed → retrieve → generate) + baseline eval.
2. Add hybrid retrieval + reranker.
3. Add NLI faithfulness check + sentence citations.
4. Fine-tune your own embedding model (and optionally the reranker).
5. Eval dashboard + polished UI + deployment.

> **Golden rule:** finish Phase 1 end-to-end (ugly but working) before improving anything.

See [`DOCUMENTATION.md`](DOCUMENTATION.md) for the full walkthrough, the reverse-engineering
ablation guide, deployment steps, and the glossary.
