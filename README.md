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
cp .env.example .env               # add a free GROQ_API_KEY (console.groq.com/keys)
#    Generation uses Groq (free) by default. To use Claude instead, set
#    LLM_PROVIDER=anthropic and ANTHROPIC_API_KEY. Only this step calls an LLM —
#    embeddings, reranking and verification are all free & local.

# 3. Add documents
#    Try it instantly with the bundled sample doc:
make sample                        # copies examples/sample_docs/*.txt into data/raw/
#    ...or drop your own PDFs into data/raw/ (SEC EDGAR filings, tax PDFs, etc.)
#    Supported formats: .pdf, .txt, .md

# 4. Vector DB — no Docker needed: the default .env uses embedded Qdrant
#    (QDRANT_PATH=qdrant_data). Prefer a server? `docker run -p 6333:6333 qdrant/qdrant`
#    and comment out QDRANT_PATH in .env.

# 5. Ingest + build the vector index
python -m src.ingest
python -m src.index_build

# 6. Try the pipeline from the command line
python -m src.pipeline "What is the penalty for late tax filing?"

# 7. Run the API + UI (two terminals)
uvicorn api.main:app --reload --port 8000
streamlit run app/app.py
```

> Prefer shortcuts? A `Makefile` wraps every step — run `make help`.
> `GET /health` reports whether the vector index is built and how many chunks it holds.

### One-command local stack (API + Qdrant)

```bash
cp .env.example .env               # fill in ANTHROPIC_API_KEY
docker compose up --build          # API on :8000, Qdrant on :6333
# then, once, build the index against the running Qdrant:
python -m src.index_build
```

## Deploy to the cloud

Three pieces: **Qdrant Cloud** (DB) + **Render** (API) + **Streamlit Cloud** (UI).

1. **Qdrant Cloud** (free tier): create a cluster, note its URL + API key.
2. **Build the index once against it** — locally, with `QDRANT_URL` and
   `QDRANT_API_KEY` set, run `python -m src.index_build`. The live API only
   *reads* the index; it does not build it.
3. **API → Render:** this repo ships a [`render.yaml`](render.yaml) blueprint —
   New → Blueprint → pick the repo. Set `GROQ_API_KEY`, `QDRANT_URL`,
   `QDRANT_API_KEY` in the dashboard. The Dockerfile pre-bakes the models so
   there is no cold-start download.
4. **UI → Streamlit Community Cloud:** point it at `app/app.py` and set the
   `API_URL` secret to your Render URL.

> ⚠️ **Memory:** the API loads PyTorch + 3 transformer models (~1.5–2.5 GB RAM).
> Free 512 MB tiers OOM on boot — use Render's `standard` plan (set in `render.yaml`)
> or a host with ≥ 2 GB.

Confirm the deploy with `curl https://<your-api>/health` — `index_ready: true` means it's usable.

## Two knowledge sources: your docs **or** the live web

VeriFin can ground answers in either your uploaded documents *or* live web search —
same verification, same citations. Switch with one env var in `.env`:

```env
RETRIEVAL_MODE=local   # answer from your indexed PDFs/txt (default)
RETRIEVAL_MODE=web     # answer from LIVE WEB SEARCH — no uploads needed
```

**Web mode** turns the whole internet into the knowledge base: for each question it
searches the web (DuckDuckGo, no API key), fetches the top pages, extracts their main
text, and runs them through the *same* rerank → generate → **verify** → cite pipeline.
Every sentence is still fact-checked, and citations point to real URLs. No `data/raw`,
no index build, no Qdrant required:

```bash
# in .env: RETRIEVAL_MODE=web  and a GROQ_API_KEY
python -m src.web_source "What is the penalty for late tax filing in the US?"   # see raw fetch
python -m src.pipeline    "What is the penalty for late tax filing in the US?"  # full verified answer
```

> Web mode needs open internet (your laptop or a normal cloud host). It makes the
> reranker and the faithfulness check matter *more* — they filter and audit noisy
> web pages. For a scalable persistent index, keep `local` mode and bulk-ingest
> sources (SEC EDGAR, docs) into Qdrant Cloud.

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
