# VeriFin — Self-Auditing RAG Assistant
### Complete Project Documentation (Base → Deployment)

> An AI that answers questions from real documents, shows its sources, and flags its own lies at the sentence level — built for high-stakes domains like finance and regulation.

**Version:** 1.0
**Audience:** You (building this as a college project while learning to code)
**Reading style:** Every technical idea has a plain-English translation first. Every command is copy-paste ready.

---

## Table of Contents

1. [What this project is](#1-what-this-project-is)
2. [The problem statement](#2-the-problem-statement)
3. [Goals and non-goals](#3-goals-and-non-goals)
4. [How it works (plain English)](#4-how-it-works-plain-english)
5. [System architecture](#5-system-architecture)
6. [Tech stack (and why each piece)](#6-tech-stack-and-why-each-piece)
7. [Prerequisites](#7-prerequisites)
8. [Environment setup](#8-environment-setup)
9. [Project structure](#9-project-structure)
10. [Component 1 — Data ingestion & chunking](#10-component-1--data-ingestion--chunking)
11. [Component 2 — Embeddings (+ fine-tuning)](#11-component-2--embeddings--fine-tuning)
12. [Component 3 — Vector store & hybrid retrieval](#12-component-3--vector-store--hybrid-retrieval)
13. [Component 4 — The reranker (+ training)](#13-component-4--the-reranker--training)
14. [Component 5 — Generation](#14-component-5--generation)
15. [Component 6 — Faithfulness / hallucination detection](#15-component-6--faithfulness--hallucination-detection)
16. [Component 7 — Citations & final output](#16-component-7--citations--final-output)
17. [Evaluation harness (the report card)](#17-evaluation-harness-the-report-card)
18. [Backend API](#18-backend-api)
19. [Frontend](#19-frontend)
20. [The build plan (one semester)](#20-the-build-plan-one-semester)
21. [Deployment](#21-deployment)
22. [Monitoring & observability](#22-monitoring--observability)
23. [Reverse-engineering learning guide](#23-reverse-engineering-learning-guide)
24. [Troubleshooting](#24-troubleshooting)
25. [Roadmap](#25-roadmap)
26. [Glossary](#26-glossary)

---

## 1. What this project is

VeriFin is a question-answering system. You give it a pile of trustworthy documents (say, tax rules or a company's financial filings). A user asks a question. VeriFin answers — but unlike a normal chatbot, **every sentence in its answer is either backed by a source you can click, or flagged in red as "unverified."**

That single feature — the AI catching and flagging its own made-up statements — is what turns this from "another ChatGPT wrapper" into a real project. It's a problem that hackathons (Stanford's LLM×Law, HackerEarth's GenAI track, Smart India Hackathon 2026) and venture investors (Y Combinator's "trust layer" theme) are all actively chasing.

**Why it's a great learning project:** it forces you to build every real layer of a modern AI system, and each layer teaches you something concrete when you take it apart.

---

## 2. The problem statement

> LLMs can't be deployed for financial or regulatory advice because they **hallucinate** — they state made-up facts with full confidence — and users can't tell which sentences are grounded in real sources and which are invented. Build a Retrieval-Augmented Generation (RAG) system where every generated sentence is either backed by a retrieved citation or explicitly flagged as unverified, with a **measurable faithfulness score**.

**Hallucinate / hallucination:** when an AI confidently states something that isn't true or isn't in its sources.

**RAG (Retrieval-Augmented Generation):** instead of the AI answering from memory, it first *retrieves* relevant real documents, then *generates* an answer using only those. "Open-book exam" instead of "closed-book guessing."

---

## 3. Goals and non-goals

**Goals**
- Answer domain questions using a private document collection.
- Attach a real source citation to every grounded sentence.
- Detect and visibly flag ungrounded (hallucinated) sentences.
- Produce hard numbers proving the system works (an evaluation scoreboard).
- Include genuine deep-learning training (not just API calls).

**Non-goals (things you are NOT building — keep scope sane)**
- Not a general chatbot for any topic.
- Not real-time trading or giving actual financial advice to real users.
- Not multi-user accounts, billing, or a mobile app (those are optional stretch goals).
- Not training a large language model from scratch (you fine-tune small models, you don't build GPT).

---

## 4. How it works (plain English)

Six stages. Think of it as a careful research assistant:

1. **Question comes in.** "What's the penalty for late tax filing?"
2. **Retrieval — the librarian.** A system runs to your document pile and grabs the pages most likely to contain the answer.
3. **Embeddings — the meaning map.** Text is turned into numbers ("GPS coordinates for meaning") so the computer can find pages that *mean* the same thing as the question, not just pages with matching words.
4. **Reranker — the strict second librarian.** The first grab is fast but sloppy (~20 pages). The reranker carefully re-reads them against the question and pushes the truly best ones to the top.
5. **Generation — the open-book answer.** The AI writes an answer using *only* those top pages.
6. **Fact-checker — the lie detector.** The answer is split into sentences. Each sentence is checked against the sources: "Do these pages actually say this?" Yes → green + citation. No → red flag.

The user sees a color-coded answer. That's the demo.

---

## 5. System architecture

```
                         ┌─────────────────────────────┐
   User question  ─────► │  Query rewriter (optional)  │
                         └──────────────┬──────────────┘
                                        ▼
                    ┌───────────────────────────────────────┐
                    │  HYBRID RETRIEVAL                       │
                    │  • Dense search (embeddings)  ← DL      │
                    │  • Keyword search (BM25)                │
                    └───────────────────┬───────────────────┘
                                        ▼  (top ~20 chunks)
                    ┌───────────────────────────────────────┐
                    │  CROSS-ENCODER RERANKER       ← DL      │
                    └───────────────────┬───────────────────┘
                                        ▼  (top ~5 chunks)
                    ┌───────────────────────────────────────┐
                    │  GENERATOR (LLM, context-constrained)  │
                    └───────────────────┬───────────────────┘
                                        ▼  (draft answer)
                    ┌───────────────────────────────────────┐
                    │  FAITHFULNESS CHECK (NLI)     ← DL      │
                    │  per-sentence: entailed by sources?     │
                    └───────────────────┬───────────────────┘
                                        ▼
                    ┌───────────────────────────────────────┐
                    │  CITATION BINDING + FLAGS              │
                    │  green = cited · red = unverified       │
                    └───────────────────┬───────────────────┘
                                        ▼
                              Final answer to user
```

The three boxes marked **← DL** are your deep-learning components — the parts you can train yourself.

**Offline pipeline (runs once, ahead of time):**
```
Raw documents (PDF/HTML/CSV)
   → Text extraction
   → Chunking (split into passages)
   → Embed each chunk (turn into vectors)
   → Store vectors + text in the vector database
```

---

## 6. Tech stack (and why each piece)

| Layer | Tool | Why |
|---|---|---|
| Language | **Python 3.11** | The default language of AI; every library you need is here. |
| Embeddings & training | **sentence-transformers** | Lets you *use and fine-tune* embedding and reranker models easily. |
| Deep learning core | **PyTorch** | What sentence-transformers runs on; the standard DL framework. |
| Fact-checking | **HuggingFace Transformers** (an NLI model) | Ready-made "does the evidence support the claim?" models. |
| Vector database | **Qdrant** (or **pgvector** on Postgres) | Stores meaning-vectors and finds nearest matches fast. |
| Keyword search | **rank-bm25** | The keyword half of hybrid retrieval. |
| Generation | **Any LLM API** (Claude/OpenAI) or a local small model | Writes the answer from retrieved context. |
| Evaluation | **RAGAS** + custom scripts | Measures faithfulness, relevance, retrieval quality. |
| Backend | **FastAPI** | Turns your pipeline into a web API; fast, simple, auto-docs. |
| Frontend | **Streamlit** (fast) or **Next.js** (polished) | The screen users interact with. Start with Streamlit. |
| Packaging | **Docker** | Bundles everything so it runs identically anywhere. |
| Hosting | **Render / Railway / Fly.io** (app) + **Qdrant Cloud** (DB) | Free or cheap tiers, student-friendly. |

**Beginner tip:** Start with Streamlit and an LLM API. Swap to Next.js and a local model only if you have time. Don't let the "perfect" stack stop you from shipping the "working" one.

---

## 7. Prerequisites

- **Python 3.11+** installed (`python3 --version`)
- **Git** installed (`git --version`)
- A code editor — **Cursor** or **VS Code**
- ~10 GB free disk (models are large)
- An LLM API key (Anthropic or OpenAI) for the generation step
- Basic terminal comfort: `cd`, `ls`, running commands. That's enough to start.

No GPU required for Phases 1–3. You'll want one (Google Colab's free GPU is fine) only for the fine-tuning phases.

---

## 8. Environment setup

Run these in your terminal, one block at a time.

**Create the project and a virtual environment** (a "virtual environment" is an isolated box so this project's libraries don't clash with others):

```bash
mkdir verifin && cd verifin
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
```

**Install the core libraries:**

```bash
pip install \
  sentence-transformers \
  transformers \
  torch \
  qdrant-client \
  rank-bm25 \
  ragas \
  fastapi "uvicorn[standard]" \
  streamlit \
  pypdf \
  python-dotenv \
  anthropic
```

**Save your API key** in a file called `.env` (never commit this file to Git):

```bash
echo "ANTHROPIC_API_KEY=sk-your-key-here" > .env
echo ".env" >> .gitignore
echo ".venv/" >> .gitignore
```

**Initialize Git:**

```bash
git init
git add .
git commit -m "Initial project setup"
```

---

## 9. Project structure

Create this folder layout. Each folder maps to a component in this doc.

```
verifin/
├── data/
│   ├── raw/                 # original PDFs / source documents
│   └── processed/           # cleaned, chunked text
├── src/
│   ├── ingest.py            # Component 1: load + chunk documents
│   ├── embeddings.py        # Component 2: turn text into vectors
│   ├── retrieval.py         # Component 3: hybrid search
│   ├── rerank.py            # Component 4: cross-encoder reranker
│   ├── generate.py          # Component 5: LLM answer
│   ├── verify.py            # Component 6: NLI faithfulness check
│   ├── citations.py         # Component 7: bind citations + flags
│   └── pipeline.py          # ties all components together
├── training/
│   ├── train_embeddings.py  # fine-tune the embedding model
│   └── train_reranker.py    # fine-tune the reranker
├── eval/
│   ├── testset.json         # your question/answer test cases
│   └── run_eval.py          # the scoreboard
├── api/
│   └── main.py              # FastAPI backend
├── app/
│   └── app.py               # Streamlit frontend
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                     # secrets (never commit)
├── .gitignore
└── DOCUMENTATION.md         # this file
```

Generate `requirements.txt` any time with: `pip freeze > requirements.txt`

---

## 10. Component 1 — Data ingestion & chunking

**Goal:** turn messy PDFs into clean, bite-sized passages ("chunks").

**Why chunk?** A whole 100-page PDF is too big to feed the AI. And you want to cite the *exact* passage, not the whole document. So you split documents into small overlapping pieces (~300–500 words each).

**Plain-English rule of thumb:** chunks too big = imprecise citations; chunks too small = lost context. Start at ~400 words with ~50 words of overlap and tune later.

`src/ingest.py`:

```python
from pathlib import Path
from pypdf import PdfReader

def load_pdf(path: str) -> list[dict]:
    """Read a PDF and return a list of {page, text} records."""
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({"source": Path(path).name, "page": i + 1, "text": text})
    return pages

def chunk_text(text: str, size: int = 400, overlap: int = 50) -> list[str]:
    """Split text into overlapping word windows."""
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = start + size
        chunks.append(" ".join(words[start:end]))
        start = end - overlap
    return chunks

def build_chunks(pdf_dir: str = "data/raw") -> list[dict]:
    all_chunks = []
    for pdf in Path(pdf_dir).glob("*.pdf"):
        for page in load_pdf(str(pdf)):
            for j, chunk in enumerate(chunk_text(page["text"])):
                all_chunks.append({
                    "id": f"{page['source']}-p{page['page']}-c{j}",
                    "source": page["source"],
                    "page": page["page"],
                    "text": chunk,
                })
    return all_chunks

if __name__ == "__main__":
    chunks = build_chunks()
    print(f"Built {len(chunks)} chunks")
```

**Where to get documents (finance/regulatory, all free & legal):**
- Government tax/regulatory PDFs (public domain).
- Company annual reports / 10-K filings (SEC EDGAR is free).
- Central bank publications.

Drop 5–20 PDFs into `data/raw/` to start. You don't need thousands.

---

## 11. Component 2 — Embeddings (+ fine-tuning)

**Goal:** turn each chunk into a vector (list of numbers) so we can find chunks by *meaning*.

**Plain English:** An embedding model reads text and outputs a coordinate on a giant "meaning map." Similar meanings → nearby coordinates. To find relevant chunks, we embed the question and grab the nearest chunk-coordinates.

**Basic usage** — `src/embeddings.py`:

```python
from sentence_transformers import SentenceTransformer

# A solid, small starter model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = SentenceTransformer(MODEL_NAME)

def embed(texts: list[str]) -> list[list[float]]:
    """Turn a list of texts into a list of vectors."""
    return _model.encode(texts, normalize_embeddings=True).tolist()
```

### The deep-learning part: fine-tuning your own embedding model

**Why:** the starter model understands general English. Fine-tuning teaches it *your* domain's language (a general doctor → a specialist). This is real training and a highlight of the project.

**How it learns (contrastive learning, in plain English):** you show the model pairs that *should* be close (a question and the passage that answers it) and pairs that *should* be far apart. It nudges its internal weights until similar things sit close on the map. That "nudging weights based on examples" *is* deep learning.

You need training pairs like:
```json
[
  {"question": "penalty for late tax filing?", "positive": "A late filing attracts a penalty of..."},
  {"question": "what is the standard deduction?", "positive": "The standard deduction for the year is..."}
]
```
You can generate these semi-automatically: for each chunk, ask an LLM "write 2 questions this passage answers." That gives you hundreds of pairs cheaply.

`training/train_embeddings.py`:

```python
import json
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

pairs = json.load(open("training/embed_pairs.json"))
examples = [InputExample(texts=[p["question"], p["positive"]]) for p in pairs]

loader = DataLoader(examples, shuffle=True, batch_size=16)
loss = losses.MultipleNegativesRankingLoss(model)  # standard for Q/passage pairs

model.fit(
    train_objectives=[(loader, loss)],
    epochs=3,
    warmup_steps=100,
    output_path="models/finetuned-embeddings",
)
print("Saved fine-tuned model to models/finetuned-embeddings")
```

Run it on Google Colab's free GPU if your laptop is slow. Later, point `embeddings.py` at `models/finetuned-embeddings` and re-run your evaluation to measure the improvement.

---

## 12. Component 3 — Vector store & hybrid retrieval

**Goal:** store all chunk vectors and, at query time, fetch the most relevant chunks fast.

**Vector database:** a database built to answer "which stored vectors are closest to this one?" instantly, even with millions of chunks. We use Qdrant.

**Start Qdrant locally with Docker:**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Index your chunks** (run once after ingesting):

```python
# src/index_build.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from src.ingest import build_chunks
from src.embeddings import embed

client = QdrantClient("localhost", port=6333)
COLLECTION = "verifin"

def build_index():
    chunks = build_chunks()
    vectors = embed([c["text"] for c in chunks])
    dim = len(vectors[0])

    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )
    points = [
        PointStruct(id=i, vector=vectors[i], payload=chunks[i])
        for i in range(len(chunks))
    ]
    client.upsert(collection_name=COLLECTION, points=points)
    print(f"Indexed {len(points)} chunks")

if __name__ == "__main__":
    build_index()
```

### Hybrid retrieval: meaning + keywords

**Why hybrid?** Meaning-search (dense) is great for paraphrases but can miss exact terms like a specific law code "Section 234A." Keyword-search (BM25) nails exact terms but misses paraphrases. Combining both beats either alone.

`src/retrieval.py`:

```python
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi
from src.embeddings import embed
from src.ingest import build_chunks

client = QdrantClient("localhost", port=6333)
COLLECTION = "verifin"

# Prepare BM25 keyword index in memory
_chunks = build_chunks()
_bm25 = BM25Okapi([c["text"].split() for c in _chunks])

def dense_search(query: str, k: int = 20):
    vec = embed([query])[0]
    hits = client.search(collection_name=COLLECTION, query_vector=vec, limit=k)
    return [h.payload for h in hits]

def keyword_search(query: str, k: int = 20):
    scores = _bm25.get_scores(query.split())
    ranked = sorted(zip(_chunks, scores), key=lambda x: x[1], reverse=True)
    return [c for c, _ in ranked[:k]]

def hybrid_search(query: str, k: int = 20):
    """Merge dense + keyword results, de-duplicated."""
    combined, seen = [], set()
    for chunk in dense_search(query, k) + keyword_search(query, k):
        if chunk["id"] not in seen:
            seen.add(chunk["id"])
            combined.append(chunk)
    return combined
```

---

## 13. Component 4 — The reranker (+ training)

**Goal:** take the ~20–40 candidate chunks from retrieval and pick the true top ~5.

**Plain English:** retrieval is fast but rough. A *reranker* is slow but precise — it reads the question and each candidate *together* and scores how well they actually match. This one step is usually the single biggest quality jump in a RAG system.

**Bi-encoder vs cross-encoder (worth understanding):**
- The embedding model is a **bi-encoder** — it encodes question and passage *separately*, then compares. Fast, slightly blurry.
- A **cross-encoder** reads question and passage *together in one pass* — much more accurate, much slower. Perfect for reranking a short list.

`src/rerank.py`:

```python
from sentence_transformers import CrossEncoder

_reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query: str, chunks: list[dict], top_n: int = 5) -> list[dict]:
    pairs = [(query, c["text"]) for c in chunks]
    scores = _reranker.predict(pairs)
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return [c for c, _ in ranked[:top_n]]
```

### Fine-tuning the reranker (deep-learning component #2)

Train it on triples: a query, a passage that answers it (label 1), and passages that don't (label 0). `training/train_reranker.py`:

```python
import json
from sentence_transformers import CrossEncoder, InputExample
from torch.utils.data import DataLoader

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", num_labels=1)

data = json.load(open("training/rerank_pairs.json"))  # {query, passage, label}
examples = [InputExample(texts=[d["query"], d["passage"]], label=float(d["label"])) for d in data]
loader = DataLoader(examples, shuffle=True, batch_size=16)

model.fit(train_dataloader=loader, epochs=2, warmup_steps=100,
          output_path="models/finetuned-reranker")
```

---

## 14. Component 5 — Generation

**Goal:** write the answer using *only* the top chunks. The key is the prompt — you instruct the model to stick to the sources and to say "I don't know" when the sources don't cover it.

`src/generate.py`:

```python
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM = """You answer ONLY using the provided sources.
- Every claim must be supported by the sources.
- If the sources don't contain the answer, say: "The provided sources do not cover this."
- Write in clear, short sentences. Do not add outside knowledge."""

def generate_answer(query: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[{i+1}] (source: {c['source']} p.{c['page']})\n{c['text']}"
        for i, c in enumerate(chunks)
    )
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=SYSTEM,
        messages=[{"role": "user",
                   "content": f"Sources:\n{context}\n\nQuestion: {query}"}],
    )
    return msg.content[0].text
```

**Note:** the prompt reduces hallucination but never eliminates it. That's exactly why the next component exists — you never trust the generator alone.

---

## 15. Component 6 — Faithfulness / hallucination detection

**This is the heart of the project.** After the answer is written, you check every sentence against the sources.

**Plain English:** you use an **NLI model** (Natural Language Inference). Give it two pieces of text — a "premise" (your source chunks) and a "hypothesis" (one generated sentence) — and it tells you whether the premise *entails* (supports), *contradicts*, or is *neutral* toward the hypothesis. If the sources entail the sentence → grounded (green). Otherwise → unverified (red).

`src/verify.py`:

```python
import re
from transformers import pipeline

# An NLI model outputs: entailment / neutral / contradiction
_nli = pipeline("text-classification",
                model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
                top_k=None)

def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

def verify_sentence(sentence: str, chunks: list[dict]) -> dict:
    """Check one sentence against every source chunk; keep the best support."""
    best = {"label": "unverified", "score": 0.0, "source": None}
    for c in chunks:
        result = _nli(f"{c['text']} [SEP] {sentence}")[0]
        scores = {r["label"].lower(): r["score"] for r in result}
        ent = scores.get("entailment", 0.0)
        if ent > best["score"]:
            best = {"label": "grounded" if ent > 0.5 else "unverified",
                    "score": ent, "source": c}
    return best

def verify_answer(answer: str, chunks: list[dict]) -> list[dict]:
    return [{"sentence": s, **verify_sentence(s, chunks)}
            for s in split_sentences(answer)]
```

**Optional deep-learning upgrade (component #3):** fine-tune this NLI model on your own domain examples of "supported vs unsupported" claims to catch subtle domain-specific hallucinations. Same training pattern as the others.

---

## 16. Component 7 — Citations & final output

**Goal:** assemble the verified sentences into a final, color-coded, cited answer.

`src/citations.py`:

```python
def build_output(verified: list[dict]) -> dict:
    faithful = sum(1 for v in verified if v["label"] == "grounded")
    faithfulness = round(faithful / max(len(verified), 1), 3)
    rendered = []
    for v in verified:
        if v["label"] == "grounded":
            src = v["source"]
            rendered.append({
                "text": v["sentence"], "status": "grounded",
                "citation": f"{src['source']} p.{src['page']}",
                "confidence": round(v["score"], 2),
            })
        else:
            rendered.append({"text": v["sentence"], "status": "unverified",
                             "citation": None, "confidence": round(v["score"], 2)})
    return {"faithfulness_score": faithfulness, "sentences": rendered}
```

**Tie it all together** — `src/pipeline.py`:

```python
from src.retrieval import hybrid_search
from src.rerank import rerank
from src.generate import generate_answer
from src.verify import verify_answer
from src.citations import build_output

def answer_question(query: str) -> dict:
    candidates = hybrid_search(query, k=20)
    top = rerank(query, candidates, top_n=5)
    draft = generate_answer(query, top)
    verified = verify_answer(draft, top)
    return build_output(verified)

if __name__ == "__main__":
    import json
    print(json.dumps(answer_question("What is the penalty for late tax filing?"), indent=2))
```

---

## 17. Evaluation harness (the report card)

**Why this matters most for learning:** once you can measure quality, you can remove any component, watch the score change, and *understand what that component does*. That loop is your reverse-engineering education.

**Metrics (plain English):**
- **Faithfulness** — does the answer stick to the sources? (no made-up claims)
- **Answer relevance** — does the answer actually address the question?
- **Context precision** — of the chunks retrieved, how many were actually useful?
- **Context recall** — did retrieval find all the chunks needed?
- **Citation accuracy** — do the citations point to the right source?

**Build a test set** — `eval/testset.json`:
```json
[
  {"question": "What is the penalty for late tax filing?",
   "ground_truth": "A penalty of X% per month applies..."},
  {"question": "What is the standard deduction?",
   "ground_truth": "The standard deduction is..."}
]
```
Aim for 30–50 questions with known correct answers.

`eval/run_eval.py`:

```python
import json
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from src.retrieval import hybrid_search
from src.rerank import rerank
from src.generate import generate_answer

tests = json.load(open("eval/testset.json"))
rows = {"question": [], "answer": [], "contexts": [], "ground_truth": []}

for t in tests:
    top = rerank(t["question"], hybrid_search(t["question"], 20), 5)
    rows["question"].append(t["question"])
    rows["answer"].append(generate_answer(t["question"], top))
    rows["contexts"].append([c["text"] for c in top])
    rows["ground_truth"].append(t["ground_truth"])

result = evaluate(Dataset.from_dict(rows),
                  metrics=[faithfulness, answer_relevancy,
                           context_precision, context_recall])
print(result)
```

**Run it after every phase and write the numbers down.** The table of "score before vs after adding X" is the most impressive slide in your final presentation.

---

## 18. Backend API

Wrap the pipeline in a web API so the frontend (or anyone) can call it.

`api/main.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from src.pipeline import answer_question

app = FastAPI(title="VeriFin API")

class Query(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(q: Query):
    return answer_question(q.question)
```

Run it:
```bash
uvicorn api.main:app --reload --port 8000
```
Open `http://localhost:8000/docs` — FastAPI gives you an interactive test page for free.

---

## 19. Frontend

Start with Streamlit — a full UI in ~40 lines.

`app/app.py`:

```python
import streamlit as st
import requests

st.title("VeriFin — Verified Financial Answers")
st.caption("Green = backed by a source · Red = unverified, do not trust")

question = st.text_input("Ask a question:")
if st.button("Ask") and question:
    with st.spinner("Retrieving, answering, and fact-checking..."):
        res = requests.post("http://localhost:8000/ask",
                            json={"question": question}).json()

    st.metric("Faithfulness score", f"{res['faithfulness_score'] * 100:.0f}%")
    for s in res["sentences"]:
        if s["status"] == "grounded":
            st.markdown(f":green[{s['text']}]  \n"
                        f"<small>Source: {s['citation']} "
                        f"(confidence {s['confidence']})</small>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f":red[⚠ {s['text']}]  \n"
                        f"<small>Unverified — not found in sources</small>",
                        unsafe_allow_html=True)
```

Run it (with the API running in another terminal):
```bash
streamlit run app/app.py
```

That color-coded screen is your demo. If you have extra time, rebuild it in Next.js for polish — but this is enough to win.

---

## 20. The build plan (one semester)

Build worst-version-first. Each phase works on its own and produces a measurable result.

| Phase | What you build | You'll learn | Deliverable |
|---|---|---|---|
| **1** | Naive RAG: chunk → embed → retrieve → generate. No reranker, no checks. | The RAG skeleton; baseline numbers. | Working Q&A + baseline eval scores. |
| **2** | Add hybrid retrieval + cross-encoder reranker. | Why retrieval quality dominates everything. | Eval scores jump; before/after table. |
| **3** | Add NLI faithfulness check + sentence citations. | The core novelty; how hallucination detection works. | Color-coded, cited answers. |
| **4** | Fine-tune your own embedding model (and optionally the reranker). | How embedding models are actually *trained*. | Custom model + comparison to off-the-shelf. |
| **5** | Eval dashboard + polished UI + deployment. | Measurement, presentation, shipping. | Live URL + final report. |

**Golden rule:** finish Phase 1 end-to-end (ugly but working) before improving anything. A working ugly thing beats a beautiful half-thing.

---

## 21. Deployment

Goal: a public URL your professor can open.

### Step 1 — Containerize with Docker

**Why Docker:** it bundles your code + libraries + settings into one "container" that runs identically on your laptop and on a server. Ends "but it worked on my machine."

`Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`docker-compose.yml` (runs your app + Qdrant together):
```yaml
version: "3.8"
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - qdrant

volumes:
  qdrant_data:
```

Test locally:
```bash
docker compose up --build
```

### Step 2 — Host it

Cheapest student-friendly setup:

1. **Vector DB → Qdrant Cloud** (free tier). Create a cluster, copy its URL + API key into your `.env`.
2. **Backend API → Render or Railway or Fly.io.** Connect your GitHub repo; they build the Dockerfile automatically. Add your environment variables (API keys, Qdrant URL) in their dashboard.
3. **Frontend → Streamlit Community Cloud** (free) — point it at your GitHub repo, set the API URL as a secret.

### Step 3 — Pre-deployment checklist

- [ ] `requirements.txt` is up to date (`pip freeze > requirements.txt`)
- [ ] `.env` is in `.gitignore` (secrets never pushed to GitHub)
- [ ] Vector index has been built on the cloud DB (run your index script once against Qdrant Cloud)
- [ ] `/health` endpoint returns ok on the live URL
- [ ] Frontend points at the deployed API URL, not `localhost`
- [ ] A short demo script: 3 questions that show a green answer, a cited answer, and a red-flagged hallucination

### Step 4 — Deploy commands (Render example via CLI is optional; the dashboard flow is simplest)

Push to GitHub, connect the repo in Render, and it deploys on every push:
```bash
git add .
git commit -m "Deploy VeriFin"
git push origin main
```

---

## 22. Monitoring & observability

Even a college project looks professional with basic logging.

- **Log every query**: question, retrieved chunk IDs, faithfulness score, latency. Write to a file or a simple table.
- **Track the faithfulness score over time** — if it drops, something regressed.
- **Add timing** around each stage so you can show where the time goes (retrieval vs reranking vs generation vs verification).

Minimal logging example:
```python
import logging, time
logging.basicConfig(filename="verifin.log", level=logging.INFO)

def timed(stage, fn, *args):
    t = time.time()
    out = fn(*args)
    logging.info(f"{stage} took {time.time()-t:.2f}s")
    return out
```

---

## 23. Reverse-engineering learning guide

Your stated goal is to build it, then take it apart to learn. Here's the exact plan for that.

**The method: ablation.** Turn one component off, re-run the evaluation, explain the change.

| Experiment | What to do | What you'll learn |
|---|---|---|
| Kill the reranker | Return retrieval results directly to the generator | How much precision the reranker adds — usually a lot |
| Kill hybrid search | Use dense-only, then keyword-only | When meaning-search wins vs when keyword-search wins |
| Shrink the chunks | Re-chunk at 150 words, re-index, re-eval | The chunk-size tradeoff (precision vs context) |
| Swap embedding model | Off-the-shelf vs your fine-tuned one | What fine-tuning actually bought you |
| Weaken the prompt | Remove "only use sources" instruction | How much hallucination the prompt alone prevents |
| Turn off verification | Skip the NLI check | See the hallucinations that were being caught |

For each: **write one paragraph** — what you changed, what number moved, why. Those paragraphs become your project report and prove genuine understanding, not just wiring libraries together.

**Deep-dive reading order** (learn the theory *after* you've seen it work):
1. How embeddings/vectors represent meaning.
2. Bi-encoders vs cross-encoders (retrieval vs reranking).
3. Natural Language Inference (entailment) — the basis of your fact-checker.
4. Contrastive learning — how your fine-tuning actually trains the model.
5. RAG evaluation metrics — what faithfulness and context precision really measure.

---

## 24. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Retrieval returns junk | Chunks too big/small, or wrong embedding model | Re-chunk (~400 words), rebuild index |
| Everything flagged "unverified" | NLI threshold too high, or chunks not passed to verifier | Lower threshold to ~0.4; confirm `top` chunks reach `verify_answer` |
| Everything flagged "grounded" | Threshold too low | Raise threshold; inspect a few by hand |
| Qdrant connection refused | Qdrant not running | `docker run -p 6333:6333 qdrant/qdrant` |
| Generation ignores sources | Weak prompt | Strengthen the system prompt; reduce chunk count so context is focused |
| Fine-tuning is painfully slow | No GPU | Use Google Colab's free GPU |
| API key error | `.env` not loaded | Confirm `load_dotenv()` runs and key name matches |
| "Works locally, breaks deployed" | Env vars or index missing on cloud | Set all env vars in host dashboard; rebuild index against cloud DB |

---

## 25. Roadmap

Once the core works, credible extensions (mention these in your report as "future work"):
- Fine-tune the NLI verifier on domain-labeled claims.
- Add a query rewriter that decomposes complex questions.
- Multi-document reasoning (combine facts across sources).
- LoRA fine-tune a small local generator to reduce API cost and dependence.
- Feedback loop: let users flag wrong citations to build more training data.
- Swap the domain (legal, medical) to prove the architecture generalizes.

---

## 26. Glossary

- **RAG** — Retrieval-Augmented Generation: fetch real documents first, then answer from them.
- **Embedding / vector** — a list of numbers representing a text's meaning; similar meanings → nearby vectors.
- **Chunk** — a small passage a document is split into.
- **Vector database** — storage that finds the nearest vectors to a query vector, fast (Qdrant here).
- **BM25** — a classic keyword-matching search algorithm.
- **Hybrid retrieval** — combining meaning-search (dense) and keyword-search (BM25).
- **Bi-encoder** — encodes question and passage separately; fast, used for retrieval.
- **Cross-encoder** — reads question + passage together; accurate, used for reranking.
- **Reranker** — reorders retrieved candidates so the best ones are on top.
- **LLM** — Large Language Model; writes the answer (Claude, GPT, etc.).
- **Hallucination** — a confident but unsupported/false statement from the model.
- **NLI (Natural Language Inference)** — decides if text A supports (entails), contradicts, or is neutral to text B. Powers the fact-checker.
- **Faithfulness** — the share of answer sentences actually supported by sources.
- **Fine-tuning** — further training a model on your own examples to specialize it.
- **Contrastive learning** — training that pulls "similar" pairs together and pushes "different" pairs apart.
- **Ablation** — turning off one component to measure its contribution.
- **Docker / container** — a bundle of your app + everything it needs, so it runs identically anywhere.
- **API** — a web endpoint other programs (your frontend) can call.

---

*End of documentation. Build Phase 1 first, measure, then improve one layer at a time.*
